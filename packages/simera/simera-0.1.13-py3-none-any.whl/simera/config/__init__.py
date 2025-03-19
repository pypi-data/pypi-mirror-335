import yaml
from pathlib import Path
from simera.utils import DataInputError, compute_all_conversions, compute_all_conversions_between_units_in_ratios

# wise - Config url_resources via os.environ to resources on company sharepoint for local employees use.


class Config:
    """Handles configuration file loading and resource path management."""

    def __init__(self, url_resources=None):
        self.path = self._Path(url_resources)
        self.config = self._Config(self.path)

    class _Path:
        """Handles directory paths for resources and configurations."""

        def __init__(self, url_resources):
            self.base_dir = Path.cwd().resolve()
            self.resources = Path(url_resources).resolve() if url_resources else self.base_dir / 'simera_resources'
            self.config = Path(__file__).resolve().parent

            # For running and resting with interactive interpreter __file__ is <input>:
            if __file__.startswith('<'):
                self.config = Path.cwd() / 'simera/config'

    class _Config:
        """Loads and manages configuration settings from YAML files."""

        def __init__(self, path):
            self._path = path

            # Country attributes
            self.country = self._read_yaml(self._path.config / 'country.yaml')

            # Currency default and rates
            self._currency_resources = self._read_yaml(self._path.resources / 'config' / 'currency.yaml')
            self.currency = self.setup_currency()

            # Units of Measure
            self._units_of_measure_builtin = self._read_yaml(self._path.config / 'units_of_measure.yaml')
            self._units_of_measure_resources = self._read_yaml(self._path.resources / 'config' / 'units_of_measure.yaml')
            self.units_of_measure = self.setup_units_of_measure()

            # Transport setup
            self.transport = self._read_yaml(self._path.resources / 'transport' / 'transport.yaml')
            self.setup_transport_shipment_and_package_size_max()

            # Warehouse setup
            self.warehouse = self._read_yaml(self._path.resources / 'warehouse' / 'sites.yaml')

        @staticmethod
        def _read_yaml(file_path):
            """Reads a YAML configuration file and returns its contents."""
            try:
                with file_path.open('r', encoding='utf-8') as file:
                    return yaml.safe_load(file) or {}
            except FileNotFoundError:
                print(f"Warning: {file_path.name} not found at {file_path}. Returning an empty dictionary.")
                return {}
            except yaml.YAMLError as e:
                print(f"Error parsing {file_path}: {e}")
                return {}

        def setup_currency(self):
            """Consolidate builtin and resource config for currency. """

            # Default currency
            default_currency = self._currency_resources.get('default', 'EUR')
            default = {'default': default_currency}

            # Exchange rates
            rates = self._currency_resources.get('rates', {default_currency: {default_currency: 1}})  # if no input found, set EUR/EUR=1

            rates = {'rates': rates}
            currency_attributes = {}
            currency_attributes.update(default)
            currency_attributes.update(rates)
            return currency_attributes

        def setup_units_of_measure(self):
            """Consolidate builtin and resource config for units_of_measure. """

            # Default
            default_builtin = self._units_of_measure_builtin.get('default')
            default_resources = self._units_of_measure_resources.get('default')
            default_builtin.update(default_resources)

            # Conversions
            conversions = self._units_of_measure_builtin.get('conversions')
            for key, value in conversions.items():
                conversions.update({key: compute_all_conversions_between_units_in_ratios(value)})

            # Choices based on keys in conversions
            choices = {key: list(value.keys()) for key, value in conversions.items()}

            # Custom ratios
            custom_ratios = self._units_of_measure_resources.get('custom_ratios')
            custom_ratios = compute_all_conversions_between_units_in_ratios(custom_ratios, keep_none=True)

            # Consolidate all
            units_of_measure = {}
            units_of_measure.update({'default': default_builtin})
            units_of_measure.update({'choices': choices})
            units_of_measure.update({'conversions': conversions})
            units_of_measure.update({'custom_ratios': custom_ratios})

            # Validation - default uom is in list of choices for given category
            for key, value in units_of_measure.get('default').items():
                if value not in (choices_list := units_of_measure.get('choices').get(key)):
                    raise DataInputError(f"Default Unit of Measure for '{key}': '{value}' is not on choices list '{choices_list}'"
                                         f"\nChange 'default' value or update 'choices' and 'conversions' in file: ",
                                         file=f"{self._path.resources / 'config' / 'units_of_measure.yaml'}",
                                         values=f"{value}, allowed: {choices_list}")
            return units_of_measure

        def setup_transport_shipment_and_package_size_max(self):
            """
            Initial transport setting for shipment_max_size and package_max_size are converted to
            single value for weight and volume in default units of measure. This is to align with transport ratesheet
            setup.
            """

            default_uom_volume = self.units_of_measure.get('default').get('volume')
            default_uom_weight = self.units_of_measure.get('default').get('weight')
            config_volume_choices = self.units_of_measure.get('choices').get('volume')
            config_weight_choices = self.units_of_measure.get('choices').get('weight')
            config_all_choices = config_volume_choices + config_weight_choices

            attributes = ['shipment_size_max', 'package_size_max']
            for attribute in attributes:
                attribute_size_max = self.transport.get(attribute)

                # Process per each transport mode separately
                for trpmode, trpmode_values_per_uom in attribute_size_max.get('trpmode').items():
                    volume_init = {}
                    weight_init = {}
                    for uom, value in trpmode_values_per_uom.items():
                        if uom not in config_all_choices:
                            raise DataInputError(f"Invalid Unit '{uom}'. Available weight & volume choices: '{config_all_choices}'.",
                                                 file=self._path.resources / 'transport' / 'transport.yaml',
                                                 values=f"<{attribute}><trpmode><{trpmode}><{uom}:{value}>"
                                                 )
                        if uom in config_volume_choices and value is not None:
                            volume_init.update({uom: value})
                        if uom in config_weight_choices and value is not None:
                            weight_init.update({uom: value})

                    # Calculate values for weight and volume in default_uom
                    volume_converted_to_default_uom = {f'{default_uom_volume} <= {k}': round(self.units_of_measure['conversions']['volume'][k][default_uom_volume] * v, 5) for k, v in volume_init.items()}
                    weight_converted_to_default_uom = {f'{default_uom_weight} <= {k}': round(self.units_of_measure['conversions']['weight'][k][default_uom_weight] * v, 5) for k, v in weight_init.items()}

                    # Get minimum values for shipment size (if more than 1 value provided for uom)
                    volume_size = min(volume_converted_to_default_uom.values()) if volume_converted_to_default_uom else None
                    weight_size = min(weight_converted_to_default_uom.values()) if weight_converted_to_default_uom else None

                    # Set attributes that will be used in script
                    trpmode_values_per_uom['volume'] = volume_size
                    trpmode_values_per_uom['volume_uom'] = default_uom_volume
                    trpmode_values_per_uom['volume_origin'] = f'Transport.yaml config {volume_converted_to_default_uom}' if volume_converted_to_default_uom else None

                    trpmode_values_per_uom['weight'] = weight_size
                    trpmode_values_per_uom['weight_uom'] = default_uom_weight
                    trpmode_values_per_uom['weight_origin'] = f'Transport.yaml config {weight_converted_to_default_uom}' if weight_converted_to_default_uom else None

                    # Remove all initial keys
                    for uom in config_all_choices:
                        if uom in trpmode_values_per_uom:
                            del trpmode_values_per_uom[uom]


if __name__ == '__main__':
    sc = Config()
