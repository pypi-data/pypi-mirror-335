import os
from datetime import date, datetime, timedelta
from time import perf_counter
from glob import glob
from itertools import product, chain
from string import digits, ascii_uppercase
from blachnio.ds import read_excel
import ast
import hashlib
import pickle
import math
from tqdm import tqdm
import pandas as pd
import numpy as np
from warnings import warn
from app.paths import PATH_DIR_TRANSPORT_RATES_DOWNSTREAM, PATH_FILE_MASTER_MAPPER
from app.utils import expand_df_with_list_input
tqdm.pandas()


class TransportRateSheet:
    TEMPLATE_VERSION_LATEST = '0.3.0'
    STANDARD_UOM = {'lbs/kg': 2.20462, 'cft/m3': 35.3147}
    MISSING_RANGE_VALUE_DEFAULT = 1e8
    MAX_SHIPMENT_SIZE_ALLOWED_FTL = {'m3': 80}
    MAX_SHIPMENT_SIZE_ALLOWED_PAR = {'kg': 35}
    ratesheet_last_id = 0

    def __init__(self, io, worksheet, master_mapper):
        """Transport Rate Sheet data"""
        # General
        self.master_mapper = master_mapper
        self.source_io = io
        self.source_worksheet = worksheet
        self.source_df_raw_ratesheet = self._get_ratesheet_raw_data()

        # Meta
        # todo - convert meta into class within class, to make it more transparent
        self.meta_df_raw = self._meta_get_df_raw()
        self.meta_url = getattr(self.meta_df_raw, 'url')
        self.meta_valid_from = date.fromisoformat(getattr(self.meta_df_raw, 'valid_from'))
        self.meta_currency, self.meta_currency_eur_rate = self._meta_get_ratesheet_currency_and_rate_to_eur()
        self.meta_carrier = getattr(self.meta_df_raw, 'carrier')
        self.meta_trpmode = getattr(self.meta_df_raw, 'trpmode')
        self.meta_service = getattr(self.meta_df_raw, 'service')
        self.meta_src = getattr(self.meta_df_raw, 'src')
        self.meta_dest = getattr(self.meta_df_raw, 'dest')
        self.meta_zone_zip_range = getattr(self.meta_df_raw, 'zone_zip_range')
        self.meta_max_shipment_size = self._meta_get_max_shipment_size()
        self.meta_ratio_cost_chargeable = self._meta_get_chargeable_ratios()
        self.meta_ratio_cost_uom = ast.literal_eval(getattr(self.meta_df_raw, 'ratio_cost_uom'))
        self.meta_template_version = self._get_meta_template_version()
        # todo - meta_ratesheet_id_hash seems not to be unique; make if from whole source_df_raw_ratesheet
        self.meta_ratesheet_id, self.meta_ratesheet_id_hash, self.meta_ratesheet_id_human = self._meta_get_ratesheet_id()

        # Zone
        self.zone_df_raw = self._zone_get_raw_df()
        self.zone_df_zone, self.zone_df_leadtime, self.zone_df_debug_details = self._zone_get_df_zone_and_leadtime()
        self.ratesheet_countries = self._zone_get_ratesheet_countries()
        self.ratesheet_reference_ids = self._zone_get_ratesheet_reference_ids()

        # Cost
        self.cost_df_raw = self._cost_get_df_raw()
        self.cost_zones = self._cost_get_zones()
        self.cost_df = self._cost_get_df()
        self.cost_df_uoms_ratios = self._cost_get_and_check_cost_ratios()
        self.cost_uoms_required = self._get_all_required_cost_uoms_for_ratesheet()

    def __str__(self):
        return f'{self.meta_ratesheet_id}_{self.meta_trpmode}_{self.meta_carrier}_{self.meta_service}_{self.source_worksheet}'

    def __repr__(self):
        return f'{self.meta_ratesheet_id}_{self.meta_trpmode}_{self.meta_carrier}_{self.meta_service}_{self.source_worksheet}'

    # Data -------------------------------------------------------------------------------------------------------------
    def _get_ratesheet_raw_data(self):
        """Read all data in ratesheet to be later split into meta, zone and cost"""
        # todo: cache mechanism to speed up
        dtypes = {'zone_zip': 'str', 'zone_id': 'str', 'zone_lt': np.float64}
        return pd.read_excel(io=self.source_io, sheet_name=self.source_worksheet, dtype=dtypes, engine='calamine').dropna(how='all')
        # return read_excel(io=self.source_io, sheet_name=self.source_worksheet, dtype=dtypes).dropna(how='all')

    # Meta -------------------------------------------------------------------------------------------------------------
    def _meta_get_df_raw(self) -> pd.Series:
        """Returns Series with meta info from rate_sheet"""
        df = self.source_df_raw_ratesheet[['meta_item', 'meta_id']].dropna(how='all').set_index('meta_item')
        return pd.Series(data=df.meta_id, index=df.index)

    def _get_meta_template_version(self):
        """Warn if template not in latest version"""
        if (template_version_used := getattr(self.meta_df_raw, 'template_version')) != self.TEMPLATE_VERSION_LATEST:
            warn(f'Rate sheet not in latest template version!\n{'File: ':25}{self.source_io}\n'
                 f'{'Worksheet: ':25}{self.source_worksheet}\n{'Used Template version: ':25}{template_version_used}'
                 f'\n{'Latest Template version: ':25}{self.TEMPLATE_VERSION_LATEST}')
        return template_version_used

    def _meta_get_ratesheet_currency_and_rate_to_eur(self, default_currency='EUR'):
        """Checks if master_mapper have currency rate to eur for currency used in ratesheet.
        Default currency is set to default_currency."""
        cur = getattr(self.meta_df_raw, 'currency')
        if cur is np.nan or cur == default_currency:
            return default_currency, 1
        if cur not in self.master_mapper.mapper_eur_exchange_rates:
            raise DataInputError(message='Unknown currency used in ratesheet.\nChange currency in ratesheet or'
                                         'add it to master_mapper (worksheet_currency)', io=self.source_io,
                                 worksheet=self.source_worksheet, column='meta_item',
                                 values=f'currency: {cur}')
        rate_to_eur = round(1 / self.master_mapper.mapper_eur_exchange_rates.get(cur), 8)
        return cur, rate_to_eur

    def _meta_get_ratesheet_id(self):
        """Generate unique rate sheet id based on few meta attributes"""
        id_human = self.meta_url + self.meta_valid_from.isoformat() + self.meta_currency + self.meta_carrier + \
                   self.meta_trpmode + self.meta_service + self.meta_src
        id_hash = hashlib.md5(id_human.encode('utf-8')).hexdigest()
        id_number = TransportRateSheet.ratesheet_last_id
        TransportRateSheet.ratesheet_last_id += 1
        return id_number, id_hash, id_human

    def _meta_get_chargeable_ratios(self):
        """Only one chargeable ratio allowed."""
        chargeable_ratios = getattr(self.meta_df_raw, 'ratio_cost_chargeable')
        if chargeable_ratios is not np.nan:
            chargeable_ratios = ast.literal_eval(chargeable_ratios)
            if len(chargeable_ratios) > 1:
                raise DataInputError(message='Too many chargeable ratios specified. Only 1 allowed', io=self.source_io,
                                     worksheet=self.source_worksheet, column='meta_item',
                                     values=f'ratio_cost_chargreable: {chargeable_ratios}')
        else:
            return None
        return chargeable_ratios

    def _meta_get_max_shipment_size(self):
        """Only one key: value pair allowed for now. If empy use MAX_SHIPMENT_SIZE"""
        max_shipment_size = getattr(self.meta_df_raw, 'max_shipment_size')
        if max_shipment_size is np.nan:
            if self.meta_trpmode == 'PAR':
                return self.MAX_SHIPMENT_SIZE_ALLOWED_PAR
            else:
                return self.MAX_SHIPMENT_SIZE_ALLOWED_FTL
        else:
            return ast.literal_eval(getattr(self.meta_df_raw, 'max_shipment_size'))

    # Zone -------------------------------------------------------------------------------------------------------------
    def _zone_get_raw_df(self) -> pd.DataFrame:
        """Returns DataFrame with zone info from ratesheet"""
        return self.source_df_raw_ratesheet[['zone_ctry', 'zone_zip', 'zone_id', 'zone_lt']].dropna(how='all')

    def _zone_get_zip_format(self, df):
        # Adding zip format
        mapper_ctry_zip_format = {ctry: self.master_mapper.get_country_zipcode_formats(ctry) for ctry in df['zone_ctry'].unique()}
        df['zip_format'] = df['zone_ctry'].map(mapper_ctry_zip_format)
        return df

    @staticmethod
    def _zone_classify_input(df):
        """Classifies input. Check if zone and lead-times are added.
        Remove entries without zone or leadtime"""
        df[['exist_zip', 'exist_zone', 'exist_leadtime']] = False
        df.loc[df.zone_zip.notna(), 'exist_zip'] = True
        df.loc[df.zone_id.notna(), 'exist_zone'] = True
        df.loc[df.zone_lt.notna(), 'exist_leadtime'] = True

        # Classify input into categories (separately for each country)
        df['input_class'] = pd.Series(np.nan, dtype='object')
        # (1) - contains: ctry, zip, zone, leadtime -> if only this exists, normal workflow can be applied
        df.loc[df.input_class.isna() & df.exist_zip & df.exist_zone & df.exist_leadtime, 'input_class'] = '1-zip-zone-lt_' + df['zone_ctry']
        # (2) - contains: ctry, zip, zone
        df.loc[df.input_class.isna() & df.exist_zip & df.exist_zone, 'input_class'] = '2-zip-zone_' + df['zone_ctry']
        # (3) - contains: ctry, zip, leadtime
        df.loc[df.input_class.isna() & df.exist_zip & df.exist_leadtime, 'input_class'] = '3-zip-lt_' + df['zone_ctry']
        # (4) - contains: ctry, zone, leadtime
        df.loc[df.input_class.isna() & df.exist_zone & df.exist_leadtime, 'input_class'] = '4-zone-lt_' + df['zone_ctry']
        # (5) - contains: ctry, zone
        df.loc[df.input_class.isna() & df.exist_zone, 'input_class'] = '5-zone_' + df['zone_ctry']
        # (6) - contains: ctry, leadtime
        df.loc[df.input_class.isna() & df.exist_leadtime, 'input_class'] = '6-lt_' + df['zone_ctry']
        # (7) - contains: ctry
        df.loc[df.input_class.isna(), 'input_class'] = '7_' + df['zone_ctry']

        # Drop in both zone and leadtime are not provided
        df = df[df.exist_zone | df.exist_leadtime].copy()
        return df

    @staticmethod
    def _zone_fill_nan_zip_with_first_char_in_format(df):
        """When zone_zip is not provided (e.g. for parcels, zone cover whole country), replace nan with first zip
        character from zip_format"""
        converter = {'9': '0', 'L': 'A', 'A': '0'}
        df.loc[df.zone_zip.isna(), 'zone_zip'] = df['zip_format'].str.slice(0, 1).map(converter)
        return df

    @staticmethod
    def _zone_clean_zipcodes(df, zipcode_column='zone_zip'):
        """Clean zipcode from raw data."""
        # replace list indicators (e.g. ';') with comma
        df[zipcode_column] = df[zipcode_column].str.replace(r'[;.]', ',', regex=True)
        # Keep only a-z, A_Z, 0-9, '-', ','
        df[zipcode_column] = df[zipcode_column].str.replace(r'[^a-zA-Z0-9,-]', '', regex=True)
        # Remove ',' if no chars/number follows it
        df[zipcode_column] = df[zipcode_column].str.replace(r',(?=\s|$|[^a-zA-Z0-9])', '', regex=True)
        return df

    @staticmethod
    def _zone_expand_df_with_list_input(df_to_expand, column_with_list_input, list_sep=','):
        """Convert pd.DataFrame into expanded version. Values given as list (e.g. 10, 11, 12) in single cell, will be
        appended as single rows. Created to handle zip-code inputs given as list"""
        mask_values_as_list = df_to_expand[column_with_list_input].str.contains(list_sep)
        df_with_list = df_to_expand[mask_values_as_list].copy()
        df_expanded = df_to_expand[~mask_values_as_list].copy()
        for ix, zone_row in df_with_list.iterrows():
            values_in_list = zone_row[column_with_list_input].split(list_sep)
            # print(values_in_list)
            for item in values_in_list:
                zone_row[column_with_list_input] = item
                # print(zone_row)
                df_expanded = df_expanded._append(zone_row)
        df_expanded.sort_index(inplace=True)
        df_expanded.reset_index(inplace=True)
        df_expanded.rename(columns={'index': '_initial_index'}, inplace=True)
        df_expanded.sort_values(by=['zone_ctry', 'zone_zip'], inplace=True)
        return df_expanded

    def _zone_get_zip_from_to_and_format(self, df):
        """Converts zone_zip to zip_from and zip_to. Differentiated behaviour based on input type (range vs normal)"""
        # Check if zone_zip given as range
        df['zip_as_range'] = df['zone_zip'].str.contains(rf'^[a-zA-Z0-9]+-[a-zA-Z0-9]+$')

        # Create zip_from and zip_to. If range exist, apply split; otherwise use shift per country
        if df['zip_as_range'].any():
            df[['zip_from', 'zip_to']] = df['zone_zip'].str.split('-', expand=True).fillna(np.nan)
        else:
            df['zip_from'] = df['zone_zip']
            df['zip_to'] = pd.Series(np.nan, dtype='object')
        with pd.option_context('future.no_silent_downcasting', True):
            df.loc[df['zip_to'].isna(), 'zip_to'] = df.groupby(['zone_ctry'])['zip_from'].transform(pd.Series.shift, -1).fillna(np.nan)

        # Get zip_to range type (include-to) or (exclude-to). Range has it set in meta_zone_zip_range
        df['zip_to_type'] = 'to-is-max'
        df.loc[df['zip_as_range'], 'zip_to_type'] = self.meta_zone_zip_range
        return df

    @staticmethod
    def _zone_extend_starting_zip_to_full_format(row, **kwargs):
        """Convert abbreviated zip to full format when zip is given as starting.
        E.g. 10 in format 9999 is 1099; AA in format AA99 is AA00"""
        zip_input = row[kwargs['zip_column']]
        zip_format = row['zip_format']

        # If zip_input is None or not in type string return np.nan
        if isinstance(zip_input, str):
            # Converter translates digits (9), letters (L) and alphanumeric (A) to first/last zip character
            converter_from = {'9': '0', 'L': 'A', 'A': '0'}
            zip_full = [converter_from[i] for i in zip_format]
            for i, val in enumerate(zip_input):
                zip_full[i] = val
            return ''.join(zip_full)
        else:
            return np.nan

    @staticmethod
    def _zone_extend_ending_zip_to_full_format_max(row, **kwargs):
        """Convert abbreviated zip to full format when zip is given as ending and the previous (zip-1) is needed.
        E.g. 10 in format 9999 is 0999, AA in format AA00 is A900"""
        zip_input = row[kwargs['zip_column']]
        zip_format = row['zip_format']

        def get_previous_zip(zip_input, zip_format):
            """Returns zip-1 version of zip code in any alphanumeric format. Example: 10 -> 09, ZZZ -> ZZY."""

            all_possibilities_to_format_items = {'9': digits, 'L': ascii_uppercase, 'A': digits+ascii_uppercase}
            input_to_combinations = [all_possibilities_to_format_items[i] for i in zip_format[:len(zip_input)]]
            combinations_in = product(*input_to_combinations)
            combinations_out = product(*input_to_combinations)
            next(combinations_in)  # Removes first entry from generator
            mapper_previous_zip = dict(zip(combinations_in, combinations_out))
            outcome_tuple = mapper_previous_zip.get(tuple(','.join(zip_input).split(',')))
            if outcome_tuple:
                # If found - convert tuple to string
                return ''.join(outcome_tuple)
            else:
                return np.nan

        # If zip_input is None or not  in type string return np.nan
        if isinstance(zip_input, str):
            zip_input_prev = get_previous_zip(zip_input, zip_format)

            # Convert unknown part
            converter_to = {'9': '9', 'L': 'Z', 'A': 'Z'}
            zip_full = [converter_to[i] for i in zip_format]

            if isinstance(zip_input_prev, str):
                # Apply previous zip code to initial zipcode range
                for i, val in enumerate(zip_input_prev):
                    zip_full[i] = val
                return ''.join(zip_full)
            else:
                return np.nan
        else:
            return np.nan

    @staticmethod
    def _zone_extend_ending_zip_to_full_format_min(row, **kwargs):
        """Convert abbreviated zip to full format when zip is given as ending and the last zip is needed.
        E.g. 10-14 in format 99999 is 10000-14999, AA in format AA99 is AA99"""
        zip_input = row[kwargs['zip_column']]
        zip_format = row['zip_format']

        # If zip_input is None or not  in type string return np.nan
        if isinstance(zip_input, str):
            # Convert unknown part
            converter_to = {'9': '9', 'L': 'Z', 'A': 'Z'}
            zip_full = [converter_to[i] for i in zip_format]
            for i, val in enumerate(zip_input):
                zip_full[i] = val
            return ''.join(zip_full)
        else:
            return np.nan

    @staticmethod
    def _zone_get_last_zip_code_in_format(row, **kwargs):
        """Covers missing last zip_to entry"""
        zip_input = row[kwargs['zip_column']]
        zip_format = row['zip_format']
        converter_to = {'9': '9', 'L': 'Z', 'A': 'Z'}
        return ''.join([converter_to[i] for i in zip_format])

    def _zone_process_input_with_zipcodes(self, df):
        """Takes input that has any-form zipcode and convert it into zip ranges."""
        df = self._zone_fill_nan_zip_with_first_char_in_format(df)
        df = self._zone_clean_zipcodes(df, zipcode_column='zone_zip')
        df = self._zone_expand_df_with_list_input(df, 'zone_zip')
        df = self._zone_get_zip_from_to_and_format(df)

        # # Convert zip_from and zip_to to full zipcode format
        # # Step 1 - zip_from to full format (00-12 -> 00000-...)
        df['zip_from_full'] = df[df.zip_from.notna()].apply(self._zone_extend_starting_zip_to_full_format, axis=1, zip_column='zip_from')
        # Step 2 - zip_to to min full format (00-12 -> ...-11000)
        mask_zip_to_min = df.zip_to.notna() & (df.zip_to_type == 'to-is-min')
        df['zip_to_full'] = df[mask_zip_to_min].apply(self._zone_extend_ending_zip_to_full_format_min, axis=1, zip_column='zip_to').astype('object')
        # Step 3 - zip_to to max full format (00-12 -> ...-11999)
        # wise - this is to improve speed when full zip ig given as input.
        # Processing only rows without full zipcode zip_to.len != zip_format.len
        mask_zip_to_max = df.zip_to.notna() & (df.zip_to_type == 'to-is-max') & (df.zip_to.str.len() != df.zip_format.str.len())
        df.loc[df['zip_to_full'].isna(), 'zip_to_full'] = df[mask_zip_to_max].apply(self._zone_extend_ending_zip_to_full_format_max, axis=1, zip_column='zip_to')
        mask_zip_to_max_manual = df.zip_to.notna() & (df.zip_to_type == 'to-is-max') & (df.zip_to.str.len() == df.zip_format.str.len())
        df.loc[df['zip_to_full'].isna() & mask_zip_to_max_manual, 'zip_to_full'] = df['zip_from_full']
        # Step 4 - zip_to to last full format (00-12 -> ...-12999)
        mask_zip_to_missing = df.zip_to_full.isna()
        df.loc[df['zip_to_full'].isna(), 'zip_to_full'] = df[mask_zip_to_missing].apply(self._zone_get_last_zip_code_in_format, axis=1, zip_column='zip_to_full')
        return df

    def _zone_get_df_zone_and_leadtime(self):
        """Return clean zone dataframe"""
        df = self._zone_classify_input(self.zone_df_raw)
        df = self._zone_get_zip_format(df)

        # Split input dataframe into parts
        # All Parts are processed separately  with function _zone_process_input_with_zipcodes
        zip_classes = [input_class for input_class in df.input_class.unique()]
        df_parts = [df[df['input_class'] == input_class].copy() for input_class in zip_classes]
        # Process zip coded inputs
        dfs_parts_processed = []
        for df_part in df_parts:
            dfs_parts_processed.append(self._zone_process_input_with_zipcodes(df_part))
        df = pd.concat(dfs_parts_processed)

        # Final split between lead-time and zone_id per country-zip combinations
        df_zone = []
        df_leadtime = []
        for ctry in df.zone_ctry.unique():
            df_zone.append(df[(df.zone_ctry == ctry) & (df.zone_id.notna())][['zone_ctry', 'zip_from_full', 'zip_to_full', 'zone_id']].copy())
            df_leadtime.append(df[(df.zone_ctry == ctry) & (df.zone_lt.notna())][['zone_ctry', 'zip_from_full', 'zip_to_full', 'zone_lt']].copy())
        df_zone = pd.concat(df_zone)
        df_leadtime = pd.concat(df_leadtime)
        column_names = {'zip_from_full': 'zip_from', 'zip_to_full': 'zip_to'}
        df_zone.rename(columns=column_names, inplace=True)
        df_leadtime.rename(columns=column_names, inplace=True)
        return df_zone, df_leadtime, df

    def _zone_get_ratesheet_countries(self):
        """Return unique list of countries in used in ratesheet"""
        return self.zone_df_zone.zone_ctry.unique()

    def _zone_get_ratesheet_reference_ids(self):
        """Return dict with reference key and ratesheet_id.
        {'PL|DC_EUR_CEE_PL_Pila|LTL|Raben|Groupage': ratesheet_id}
        """
        reference_dict = {}
        for ctry in self.ratesheet_countries:
            _key = f'{ctry}|{self.meta_src}|{self.meta_trpmode}|{self.meta_carrier}|{self.meta_service}'
            reference_dict[_key] = self.meta_ratesheet_id
        return reference_dict

    # Cost -------------------------------------------------------------------------------------------------------------
    def _cost_get_df_raw(self, ):
        """Returns DataFrame with cost-related input for ratesheet"""
        df = self.source_df_raw_ratesheet.loc[:, 'cost_type':].copy().dropna(how='all')
        df.columns = df.columns.astype(str)
        # Drop empty columns starting with 'Unnamed:'
        columns_to_drop = df.columns[df.columns.str.startswith('Unnamed:')]
        df.drop(columns=columns_to_drop, inplace=True)
        return df

    def _cost_get_zones(self):
        """Returns all zones from cost part."""
        cost_standard_columns = ['cost_type', 'cost_per', 'range_value', 'range_uom', 'range_value_from', 'range_value_to']
        cost_zones = [col for col in self.cost_df_raw.columns if col not in cost_standard_columns]
        return cost_zones

    def _cost_get_df(self, fillna_range_value=MISSING_RANGE_VALUE_DEFAULT, fillna_range_uom='m3'):
        """Return clean version of cost data improved by:
        - currency conversion to EUR
        - filling nan range value and uom
        - proper sorting
        - adding range_from_values to make easy lookup
        """
        df = self.cost_df_raw.copy()

        # Convert cost (except for fuel_surcharge) in all zones into EURO
        df.loc[df.cost_type != 'fsc', self.cost_zones] *= self.meta_currency_eur_rate

        # Missing range values are filled with 1e3 (default), missing uom - with 'm3'
        df['range_value'] = df['range_value'].fillna(fillna_range_value)
        df['range_uom'] = df['range_uom'].fillna(fillna_range_uom)
        # Adding 'range_value_from' for lookups
        df.insert(list(df.columns).index('range_value'), 'range_value_from', pd.Series(np.nan, dtype='object'))

        # Get range_value_from
        def get_range_from(df, df_mask, sort_by, shift_group):
            """For each group in database find range_from using shift & sort mechanism."""
            for cost_type in df[df_mask]['cost_type']:
                df.loc[df_mask & (df['cost_type'] == cost_type)] = df.loc[df_mask & (df['cost_type'] == cost_type)].sort_values(by=sort_by).set_index(df.loc[df_mask & (df['cost_type'] == cost_type)].index)
            with pd.option_context('future.no_silent_downcasting', True):
                df.loc[df_mask, 'range_value_from'] = df[df_mask].groupby(shift_group)['range_value'].transform(pd.Series.shift, 1).fillna(0)
            return df

        # Variable cost must be differently processed than costs like min, fix, fsc.
        # Get range to 'var'.
        df = get_range_from(df, df_mask=(df.cost_type == 'var'), sort_by=['range_value'], shift_group=['cost_type'])
        # get range to 'non-var' (min, fix, ext, etc)
        df = get_range_from(df, df_mask=(df.cost_type != 'var'), sort_by=['cost_type', 'cost_per', 'range_value'], shift_group=['cost_type', 'cost_per'])
        return df

    def _cost_get_and_check_cost_ratios(self):
        """Check if all needed meta_ratio_cost_uom are available for cost_per and range_uom.
        Initial improvement/enhancement:
        1. Extends initial meta_ratio_cost_uom with reverse items {'kg/m3': 167 => 'm3/kg': 1/167}
        2. Extends initial meta_ratio_cost_uom with per shipments (always gets one) {'m3/shipment': 1}
        3. Extends initial meta_ratio_cost_uom with same uom like {'m3/m3': 1}
        4. Extends with uom standard uom ratios
        """
        def get_unique_ratios_from_dataset(df):
            """Returns all used ratios (range_value/cost_per) from cost dataset and extend it with standard uom.
            And extend that with chargeable ratio."""
            ratios = list((df.range_uom + '/' + df.cost_per).unique())
            if self.meta_ratio_cost_chargeable is not None:
                ratios_chargeable = list(set(self.meta_ratio_cost_chargeable.keys()))
                ratios.extend(ratios_chargeable)
            return ratios

        def extend_ratios_with_standard(current_ratios, new_ratios):
            # Simply extend current_ratios with standard uom ratios:
            if new_ratios:
                for ratio, value in new_ratios.items():
                    if not current_ratios.get(ratio):
                        current_ratios.update({ratio: value})

        def extend_ratios_with_reversed(ratios_dict):
            # Extend ratios with reversed items: {'kg/m3': 100} -> {'kg/m3': 100, 'm3/kg': 1/100}
            new_ratios = {}
            for k, v in ratios_dict.items():
                range_uom, cost_per = k.split('/')
                new_ratio = f'{cost_per}/{range_uom}'
                if not ratios_dict.get(new_ratio):
                    new_ratios[new_ratio] = 1 / v
            ratios_dict.update(new_ratios)

        def extend_ratios_with_fixed_value(current_ratios, new_ratios, value=1):
            # Simply extend non-empty new ratios (with value=1) if item not in current_ratios:
            if new_ratios:
                for ratio in new_ratios:
                    if not current_ratios.get(ratio):
                        current_ratios.update({ratio: value})

        # Extend all ratios.
        df_all = self.cost_df.copy()
        ratio_all = get_unique_ratios_from_dataset(df_all)

        new_meta_ratio_cost_uom = self.meta_ratio_cost_uom.copy()
        extend_ratios_with_standard(new_meta_ratio_cost_uom, self.STANDARD_UOM)
        extend_ratios_with_reversed(new_meta_ratio_cost_uom)
        ratio_all_same = [ratio for ratio in ratio_all if ratio.split('/')[0] == ratio.split('/')[1]]
        extend_ratios_with_fixed_value(new_meta_ratio_cost_uom, ratio_all_same, value=1)

        # Check if all potentially needed ratios are provided. This is in case ratios are needed and not specified on
        # shipment level input.
        # Ratios with '/shipment' are excluded from list. Shipment = 1 will be always given in shipment_kwargs.
        for ratio in ratio_all:
            if ratio not in new_meta_ratio_cost_uom and '/shipment' not in ratio:
                raise DataInputError(message='Missing ratio_cost_uom to process cost info.', io=self.source_io,
                                     worksheet=self.source_worksheet, column='meta_item',
                                     values=f'ratio_cost_uom: {ratio}')

        # Convert new_meta_ratio_cost_uom into DataFrame
        def change_ratios_dict_to_dataframe(ratios_dict):
            """Changes cost ratios dict to DataFrame to easier find missing shipment drivers needed for ratesheet."""
            df_ratios = pd.DataFrame(ratios_dict, index=['value']).T.reset_index()
            df_ratios[['uom_from', 'uom_to']] = df_ratios['index'].str.split('/', expand=True)
            df_ratios = df_ratios[['index', 'uom_from', 'uom_to', 'value']].rename(columns={'index': 'ratio'}).sort_values(by='uom_to')
            df_ratios['value'] = np.round(df_ratios['value'],  8)
            return df_ratios
        new_meta_ratio_cost_uom = change_ratios_dict_to_dataframe(new_meta_ratio_cost_uom)

        return new_meta_ratio_cost_uom

    def _get_all_required_cost_uoms_for_ratesheet(self):
        """Get unique list of all required cost drivers from cost_per and range_value to calculate shipment kwargs."""

        required_ratios = list(np.unique(np.concatenate([self.cost_df.cost_per.unique(), self.cost_df.range_uom.unique()])))
        # Extend list of required uoms with chargeable rates
        if self.meta_ratio_cost_chargeable is not None:
            ratios_chargeable = list(set(self.meta_ratio_cost_chargeable.keys()))
            chargeable_uoms = []
            for ratio in ratios_chargeable:
                chargeable_uoms.extend(ratio.split('/'))
            ratios_chargeable = list(set(chargeable_uoms))
            required_ratios.extend(ratios_chargeable)
        # Extend list of required uoms with max_shipment_size
        if self.meta_max_shipment_size is not None:
            max_uom, max_val = next(iter(self.meta_max_shipment_size.items()))
            required_ratios.extend([max_uom])
        return list(set(required_ratios))
