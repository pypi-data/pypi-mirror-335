from pathlib import Path

import numpy as np
import pandas as pd
from simera import Config
from simera.utils import DataInputError, compute_all_conversions, compute_all_conversions_between_units_in_ratios

sc = Config()


class TransportRatesheet:
    def __init__(self, file, worksheet):
        self.source = self._Source(file, worksheet)
        self.meta = self._Meta(self.source)

    class _Source:
        def __init__(self, file, worksheet):
            self.file = file
            self.worksheet = worksheet
            self.data_raw = self.read_worksheet()
            self.data_meta = self.get_meta_data()
            self.data_lane = self.get_lane_data()

        def __repr__(self):
            return f"Source(file='{self.file.parts[-1]}', worksheet='{self.worksheet}')"

        def read_worksheet(self):
            """Read ratesheet all raw data"""
            dtypes = {'<dest_ctry>': 'str', '<dest_zip>': 'str', '<dest_zone>': 'str', '<dest_leadtime>': np.float64}
            return pd.read_excel(io=self.file, sheet_name=self.worksheet,
                                 dtype=dtypes, engine='calamine').dropna(how='all')

        def get_meta_data(self):
            # Get clean rawdata for meta
            df = self.data_raw[['<meta>', '<meta_value>']].dropna(subset=['<meta>'], ignore_index=True)
            df.columns = df.columns.str.replace(r'[<>]', '', regex=True)
            df['meta'] = df['meta'].astype('str').str.replace(r'[*]', '', regex=True)
            return df

        def get_lane_data(self):
            df = self.data_raw[['<dest_ctry>', '<dest_zip>',
                                '<dest_zone>', '<transit_time>']].dropna(how='all', ignore_index=True)
            return df

    class _Meta:
        def __init__(self, source):
            self._source = source
            self.get_initial_ratesheet_meta_attributes()
            self.set_final_ratesheet_meta_attributes()

        def __repr__(self):
            return f"Meta(file='{self._source.file.parts[-1]}', worksheet='{self._source.worksheet}')"

        def get_initial_ratesheet_meta_attributes(self):
            """Convert <meta> and <meta_value> columns of ratesheet and sets all <group_name> as meta attribute.
            Meta and meta_value is converted to dict.
            Example: <source> url, file.xlsx it set as Ratesheet.meta.source. {'url': 'file.xlsx'}"""

            # Get rawdata for meta
            df = self._source.data_meta

            # Set all <groups> as meta attributes
            df_meta = df[df['meta'].str.contains('<.+>', regex=True)].copy()
            df_meta['idx_from'] = df_meta.index + 1
            df_meta['idx_to'] = (df_meta.idx_from.shift(-1) - 2).fillna(df.shape[0] - 1).astype(int)
            df_meta['meta_value'] = df_meta['meta'].str.replace(r'[<>]', '', regex=True)
            for _, row in df_meta.iterrows():
                attr_dict = df[row.idx_from:row.idx_to + 1].set_index('meta')['meta_value'].to_dict()
                setattr(self, row.meta_value, attr_dict)

        def set_final_ratesheet_meta_attributes(self):
            """Convert initial ratesheet meta attributes to fixed and clean input."""

            # ==========================================================================================================
            # Functions and variables
            # ==========================================================================================================
            def get_or_default(group, group_item, required=False, default_value=None, allowed: list = None, format_func=None):
                """ Sets attribute values based on ratesheet input, default and allowed options.
                group: attribute name of a group. Example: <filters>
                group_item: item in group. Example in <filters>: <carrier>
                required: if True, field can not get None
                default_value: value set if group_item value is np.nan/None
                allowed: list of allowed values.
                format_func: function used on item
                """

                # If group does not exist in ratesheet, create it.
                if not hasattr(self, group):
                    setattr(self, group, {})
                x = getattr(self, group).get(group_item)

                if x is None or x is np.nan:
                    x = default_value
                if allowed is not None:
                    if x not in allowed:
                        raise DataInputError(f"Wrong input: '{x}'. Allowed: {allowed}",
                                             file=self._source.file,
                                             worksheet=self._source.worksheet,
                                             column=f'<meta><{group}><{group_item}>',
                                             values=x)
                if format_func is not None and x is not None:
                    x = format_func(x)
                if required and x is None:
                    raise DataInputError(f"Wrong input: '{x}'. Value is required and can not return None",
                                         file=self._source.file,
                                         worksheet=self._source.worksheet,
                                         column=f'<meta><{group}><{group_item}>',
                                         values=x)
                return x

            # Get defaults and choices
            default_uom_volume = sc.config.units_of_measure.get('default').get('volume')
            default_uom_weight = sc.config.units_of_measure.get('default').get('weight')
            config_volume_choices = sc.config.units_of_measure.get('choices').get('volume')
            config_weight_choices = sc.config.units_of_measure.get('choices').get('weight')
            config_all_choices = config_volume_choices + config_weight_choices

            # ==========================================================================================================
            # Origin File
            # ==========================================================================================================
            allowed_type = [None, 'downstream_standard', 'mainstream_standard']
            self.origin['type'] = get_or_default('origin', 'type', default_value='downstream_standard', allowed=allowed_type)
            self.origin['url'] = get_or_default('origin', 'url')

            # ==========================================================================================================
            # Validity
            # ==========================================================================================================
            validity_formal = pd.to_datetime
            self.validity['valid_from'] = get_or_default('validity', 'valid_from', format_func=validity_formal)
            self.validity['valid_to'] = get_or_default('validity', 'valid_to', format_func=validity_formal)

            # ==========================================================================================================
            # Currency
            # ==========================================================================================================
            default_simera_currency = sc.config.currency.get('default')
            self.currency['currency'] = get_or_default('currency', 'currency', required=True)

            if self.currency['currency'] == default_simera_currency:
                self.currency['currency_rate'] = 1
            else:
                rate = sc.config.currency.get('rates').get(default_simera_currency).get(self.currency['currency'])
                if rate is None:
                    raise DataInputError(f"Unknown currency exchange rate for '{self.currency['currency']}'"
                                         f"\nUpdate 'rates':'{default_simera_currency}':'{self.currency['currency']}' "
                                         f"in simera_resources/config/currency.yaml",
                                         file=self._source.file,
                                         worksheet=self._source.worksheet,
                                         column=f'<meta><currency><currency>',
                                         values=self.currency['currency'])
                else:
                    self.currency['currency_rate'] = rate

            # ==========================================================================================================
            # Filters
            # ==========================================================================================================
            values_true = [True, 'True', 'TRUE', 'true', 'Yes', 'Y']
            values_false = [False, 'False', 'FALSE', 'false', 'No', 'N']
            format_func = lambda x: True if x in values_true else False if x in values_false else x
            self.filters['default_ratesheet'] = get_or_default('filters', 'default_ratesheet', default_value=True, allowed=values_true + values_false, format_func=format_func)

            self.filters['carrier'] = get_or_default('filters', 'carrier', required=True, format_func=str.upper)
            self.filters['trpmode'] = get_or_default('filters', 'trpmode', required=True, format_func=str.upper)
            self.filters['service'] = get_or_default('filters', 'service', format_func=str.upper)
            self.filters['src_site'] = get_or_default('filters', 'src_site', required=True, format_func=str.upper)
            self.filters['src_region'] = get_or_default('filters', 'src_region', format_func=str.upper)
            self.filters['src_ctry'] = get_or_default('filters', 'src_ctry', format_func=str.upper)
            self.filters['src_zip'] = get_or_default('filters', 'src_zip', format_func=str.upper)
            self.filters['src_zone'] = get_or_default('filters', 'src_zone', format_func=str.upper)

            # ==========================================================================================================
            # Shipment and Package Size Max
            # ==========================================================================================================
            def set_max_size(attribute):
                """
                Process initial values for shipment_size_max and package_size_max and converts that into
                weight and volumes in default units of measures
                :param attribute: shipment_size_max or package_size_max
                :return: None (set shipment_size_max and package_size_max dicts as attribute to ratesheet meta)
                """

                # If attribute (e.g. shipment_size_max) is not in ratesheet, set it up with empty dict as value
                if not hasattr(self, attribute):
                    setattr(self, attribute, {})

                # Get initial values for attribute (if exist). If ratesheet has uoms not in choices, raise error.
                volume_init = {}
                weight_init = {}
                for uom, value in getattr(self, attribute).items():
                    # Check if uom is in choices. If not, raise error
                    if uom not in config_all_choices:
                        raise DataInputError(f"Invalid Unit '{uom}' for '<{attribute}>'. Available weight & volume choices: '{config_all_choices}'.",
                                             file=self._source.file, worksheet=self._source.worksheet, column='<meta>',
                                             values=f"<{attribute}><{uom}:{value}>")
                    if uom in config_volume_choices and value is not None and value is not np.nan:
                        volume_init.update({uom: value})
                    if uom in config_weight_choices and value is not None and value is not np.nan:
                        weight_init.update({uom: value})

                # Calculate values for weight and volume in default_uom
                volume_converted_to_default_uom = {f'{default_uom_volume} <= {k}': round(
                    sc.config.units_of_measure['conversions']['volume'][k][default_uom_volume] * v, 5) for k, v in
                                                   volume_init.items()}
                weight_converted_to_default_uom = {f'{default_uom_weight} <= {k}': round(
                    sc.config.units_of_measure['conversions']['weight'][k][default_uom_weight] * v, 5) for k, v in
                                                   weight_init.items()}

                # Get minimum values for shipment size (if more than 1 value provided for uom)
                volume_size = min(volume_converted_to_default_uom.values()) if volume_converted_to_default_uom else None
                weight_size = min(weight_converted_to_default_uom.values()) if weight_converted_to_default_uom else None

                # Set attributes that will be used in script
                getattr(self, attribute).update({'volume': volume_size})
                getattr(self, attribute).update({'volume_uom': default_uom_volume})
                volume_msg = f'Ratesheet {volume_converted_to_default_uom}' if volume_converted_to_default_uom else None
                getattr(self, attribute).update({'volume_origin': volume_msg})
                getattr(self, attribute).update({'volume_ratesheet_input': volume_init})

                getattr(self, attribute).update({'weight': weight_size})
                getattr(self, attribute).update({'weight_uom': default_uom_weight})
                weight_msg = f'Ratesheet {weight_converted_to_default_uom}' if weight_converted_to_default_uom else None
                getattr(self, attribute).update({'weight_origin': weight_msg})
                getattr(self, attribute).update({'weight_ratesheet_input': weight_init})

                # Remove all initial keys
                for uom in config_all_choices:
                    if uom in getattr(self, attribute).keys():
                        getattr(self, attribute).pop(uom)

                # If volume & weights are None, try to get values based on transport.yaml configuration file (if exist)
                ratesheet_trpmode = getattr(self, 'filters').get('trpmode')
                if getattr(self, attribute)['volume'] is None and getattr(self, attribute)['weight'] is None:
                    try:
                        volume = sc.config.transport.get(attribute).get('trpmode').get(ratesheet_trpmode).get('volume')
                        if volume is not None:
                            getattr(self, attribute).update({'volume': volume})
                            volume_origin = sc.config.transport.get(attribute).get('trpmode').get(ratesheet_trpmode).get('volume_origin')
                            getattr(self, attribute).update({'volume_origin': volume_origin})
                    except AttributeError:  # Transport mode in config may not be present
                        pass
                    try:
                        weight = sc.config.transport.get(attribute).get('trpmode').get(ratesheet_trpmode).get('weight')
                        if weight is not None:
                            getattr(self, attribute).update({'weight': weight})
                            weight_origin = sc.config.transport.get(attribute).get('trpmode').get(ratesheet_trpmode).get('weight_origin')
                            getattr(self, attribute).update({'weight_origin': weight_origin})
                    except AttributeError:  # Transport mode in config may not be present
                        pass

            # Execute functions
            set_max_size('shipment_size_max')
            set_max_size('package_size_max')

            # ==========================================================================================================
            # Chargeable ratios
            # ==========================================================================================================
            def set_chargeable_ratios(attribute='chargeable_ratios'):

                # If attribute (e.g. chargeable_ratios) is not in ratesheet, set it up with empty dict as value
                if not hasattr(self, attribute):
                    setattr(self, attribute, {})

                # Check: Only one entry allowed with value (other than None)
                ratios_init = getattr(self, attribute).copy()
                if ratios_init:
                    valid_ratios = 0
                    for k, v in ratios_init.items():
                        if v is not None and v is not np.nan:
                            valid_ratios += 1
                    if valid_ratios > 1:
                        raise DataInputError(f"Only one chargeable ratio allowed! Received ratios: '{list(ratios_init.keys())}'",
                                             file=self._source.file, worksheet=self._source.worksheet, column='<meta>',
                                             values=f"<{attribute}><{ratios_init}>")

                # Get initial and clean values for ratios (if exist) and unify input to x:{y: value}
                ratios_clean = {}
                if ratios_init:
                    for key, value in ratios_init.items():
                        # Remove spaces and 'per'. Keep unit as x/y.
                        key_clean = key.replace('per', '/').replace(' ', '')
                        try:
                            key_from, key_to = key_clean.split('/')
                        except ValueError:
                            raise DataInputError(f"Wrong entry for chargeable ratio '{key}'. "
                                                 f"Allowed options: weight to volume or volume to weight ratios. "
                                                 f"Exmaples: `m3 per kg`, `lb per m3`, `in3/kg`, `kg/m3`, `m3 / kg`, `kg / m3`.",
                                                 file=self._source.file, worksheet=self._source.worksheet, column='<meta>',
                                                 values=f"<{attribute}><{key}:{value}>"
                                                 )
                        # Only for ratios with value
                        if value is not None and value is not np.nan:
                            # Check if uoms are defined in config units of measurements
                            if key_from not in config_all_choices or key_to not in config_all_choices:
                                raise DataInputError(f"One of units '{key_from}' or '{key_to}' is invalid for '<{attribute}> choices'. "
                                                     f"Available weight & volume choices: '{config_all_choices}'.",
                                                     file=self._source.file, worksheet=self._source.worksheet, column='<meta>',
                                                     values=f"<{attribute}><{key}:{value}>"
                                                     )
                            # Check if ratios is properly formulated: weight to volume or volume to weight and
                            if key_from in config_volume_choices and key_to in config_volume_choices or \
                                    key_from in config_weight_choices and key_to in config_weight_choices:
                                raise DataInputError(f"Units '{key_from}' & '{key_to}' for '<{attribute}> "
                                                     f"belong to same category (weight or volume). "
                                                     f"Both weight and volume categories must be present in ratio. "
                                                     f"\nAvailable weight choices '{config_weight_choices}' "
                                                     f"\nAvailable volume choices: '{config_volume_choices}'.",
                                                     file=self._source.file, worksheet=self._source.worksheet, column='<meta>',
                                                     values=f"<{attribute}><{key}:{value}>"
                                                     )
                            # If all ok, generate clean dict with single from to value
                            ratios_clean.update({key_from: {key_to: float(value)}})

                # Get weight and volume uom from ratios clean.
                if ratios_clean:
                    key_from = next(iter(ratios_clean))
                    key_to = next(iter(ratios_clean[key_from]))
                    volume_uom_init = key_from if key_from in config_volume_choices else key_to
                    weight_uom_init = key_from if key_from in config_weight_choices else key_to
                    # Convert valid ratio to default uoms
                    # All combinations
                    ratios_clean = compute_all_conversions(ratios_clean)
                    weight_to_volume_value_init_ratio = ratios_clean[weight_uom_init][volume_uom_init]
                    # Get ratios to default_uom
                    ratio_to_default_volume = sc.config.units_of_measure['conversions']['volume'][volume_uom_init][default_uom_volume]
                    ratio_to_default_weight = sc.config.units_of_measure['conversions']['weight'][weight_uom_init][default_uom_weight]
                    weight_to_volume_value_default_uom_ratio = weight_to_volume_value_init_ratio * ratio_to_default_weight /ratio_to_default_volume
                    msg = f'Ratesheet ({default_uom_weight}/{default_uom_volume}: {weight_to_volume_value_default_uom_ratio:,.3f} <= {key_from}/{key_to}: {ratios_clean[key_from][key_to]})'

                # If not ratio exist, get default uoms and None as value
                else:
                    weight_to_volume_value_default_uom_ratio = None
                    msg = None

                # Set attributes
                getattr(self, attribute).update({'value': weight_to_volume_value_default_uom_ratio})
                getattr(self, attribute).update({'uom': f'{default_uom_weight} per {default_uom_volume}'})
                getattr(self, attribute).update({'origin': msg})
                getattr(self, attribute).update({'ratesheet_input': ratios_init})

                # # Remove all initial keys
                all_uoms = list(getattr(self, attribute).keys())
                for uom in all_uoms:
                    if uom not in ['value', 'uom', 'origin', 'ratesheet_input']:
                        getattr(self, attribute).pop(uom)

            # Execute
            set_chargeable_ratios(attribute='chargeable_ratios')

            # ==========================================================================================================
            # Custom ratios
            # ==========================================================================================================
            # If not in ratesheet, make empty dict.
            if not hasattr(self, 'custom_ratios'):
                setattr(self, 'custom_ratios', {})
            ratios_init = getattr(self, 'custom_ratios').copy()

            setattr(self, 'custom_ratios', compute_all_conversions_between_units_in_ratios(ratios_init))
            getattr(self, 'custom_ratios').update({'ratesheet_input': ratios_init})

            # todo - rename/refactor/drop completly function compute_all_conversions - only used in chargreable ratios now

            # How to connect that to build in custom_ratios
            # How to translate that to default uoms
            # todo custom_ratios can not contain standard units of measure conversions (as defined in `simera/config/unites_of_measure.yaml /conversions`)


if __name__ == '__main__':
    test_dir = Path(r'C:\Users\plr03474\NoOneDrive\Python\Simera\simera_inputs\transport')
    test_rs = 'Simera Transport Ratesheet Template_v0.4.1.xlsb'
    test_file = test_dir / test_rs
    test_worksheet = "_0.4.1"
    test_worksheet = "dev"

    rs = TransportRatesheet(test_file, test_worksheet)
    # sc.config.transport.get('shipment_size_max').get('trpmode').get('FTL')
    # sc.config.currency.get('rates').get('EUR').get('PLN')
    # sc.config.currency.get('rates').get('PLN').get('EUR')

    # sc.config.units_of_measure.get('default').get('volume')
    #
    # a = sc.config.units_of_measure.get('conversions').get('volume')
    # compute_all_conversions(a)
