from collections import defaultdict, deque
import numpy as np


class DataInputError(Exception):
    """Exception raised for errors in Excel file input.

    Attributes:
        message (str): Description of the error.
        file (str, optional): The file path of the Excel document.
        worksheet (str, optional): The worksheet where the error occurred.
        column (str, optional): The column that caused the issue.
        values (list, optional): The specific values that generated the error.
    """

    def __init__(self, message, file=None, worksheet=None, column=None, values=None):
        super().__init__(message)
        self.file = file
        self.worksheet = worksheet
        self.column = column
        self.values = values

    def __str__(self):
        details = [
            f"File: {self.file}" if self.file else None,
            f"Worksheet: {self.worksheet}" if self.worksheet else None,
            f"Column: {self.column}" if self.column else None,
            f"Values: {repr(self.values)}" if self.values else None
        ]
        details_str = "\n".join(filter(None, details))  # Remove None values
        return f"{self.args[0]}\n{details_str}" if details_str else self.args[0]


def compute_all_conversions(conversions):
    """
    Computes all possible conversion ratios between units based on direct conversions from a base unit.

    The function assumes that the input dictionary provides conversion factors from a single base unit
    to other units. It then derives reciprocal conversions and indirect conversions using the base unit
    as an intermediary.

    Args:
        conversions (dict): A dictionary where the key is the base unit, and the value is a dictionary
                            mapping other units to their conversion factors from the base unit.

    Returns:
        dict: A nested dictionary where each unit maps to another unit with a computed conversion ratio.

    Example:
        Input:
        conversions = {
            'm3': {'cft': 35.3147, 'l': 1000}
        }

        Output:
        {
            'm3':  {'m3': 1.0, 'cft': 35.3147,  'l': 1000},
            'cft': {'cft': 1.0, 'm3': 0.0283168, 'l': 28.3168},
            'l':   {'l': 1.0,   'm3': 0.001,     'cft': 0.0353147}
        }

    Explanation:
    - Direct conversions are taken from the input.
    - Self-conversions are added (e.g., 1 m3 = 1 m3).
    - Reciprocal values are calculated (e.g., 1 cft = 1/35.3147 m3).
    - Indirect conversions are derived using the base unit as a bridge
      (e.g., 1 cft → m3 → l is computed as (1/35.3147) * 1000).
    """

    # Identify the base unit and its conversion factors
    base_unit = next(iter(conversions))  # Assume the first key is the base unit
    base_factors = conversions[base_unit]

    # Prepare the output dictionary
    result = {base_unit: base_factors.copy()}

    # Initialize entries for each unit other than the base
    for unit in base_factors:
        result[unit] = {}

    # Fill in self-conversions (unit -> unit = 1.0)
    result[base_unit][base_unit] = 1.0  # Base unit to itself is always 1.0
    for unit in base_factors:
        result[unit][unit] = 1.0  # Each unit to itself is 1.0

    # Fill in reciprocal conversions (other unit -> base unit)
    for unit, factor in base_factors.items():
        result[unit][base_unit] = 1.0 / factor

    # Fill in indirect conversions between all non-base units
    for unit_i, factor_i in base_factors.items():         # base -> unit_i factor
        for unit_j, factor_j in base_factors.items():     # base -> unit_j factor
            if unit_i == unit_j:
                continue  # Skip same unit since we already set self-conversions
            # unit_i -> unit_j = (unit_i -> base) * (base -> unit_j)
            result[unit_i][unit_j] = (1.0 / factor_i) * factor_j

    return result


def standardize_ratio_key(x: str):
    """
    Converts ratio key into a standardized format by replacing 'per' with '/'
    and removing spaces.

    Examples:
    >>> standardize_ratio_key('m3 per lb')
    'm3/lb'
    >>> standardize_ratio_key('m3 / kg')
    'm3/kg'

    :param x: The ratio key as string. Exmaple: m3 per lb, kg/pal.
    :type x: str
    :return: A standardized ratio string.
    :rtype: str
    """
    return str(x).replace('per', '/').replace(' ', '')


def compute_all_conversions_between_units_in_ratios(ratios, keep_none=True):
    """
    Generate a dictionary containing conversion ratios between all pairs of units.

    Parameters:
    - ratios (dict): Dictionary of direct conversion ratios with keys in the form 'unit_a/unit_b'.
    Input conventions for ratios: 'x/y' or 'x / y', 'x per y'
    - keep_none (bool): If True, include pairs with no possible conversion as None; if False, exclude them.

    Returns:
    - dict: Nested dictionary of conversion ratios.

    Example1:
    >>> ratios = ratios = {'kg/m3': 200}
    >>> compute_all_conversions_between_units_in_ratios(ratioss, keep_none=True)
    {'kg': {'kg': 1, 'm3': 200}, 'm3': {'kg': 0.005, 'm3': 1}}

    Example2:
    >>> ratios = {'kg/m3': 200, 'ol per ol': 1}
    >>> compute_all_conversions_between_units_in_ratios(ratios, keep_none=True)
    {'kg': {'kg': 1, 'm3': 200, 'ol': None},
     'm3': {'kg': 0.005, 'm3': 1, 'ol': None},
     'ol': {'kg': None, 'm3': None, 'ol': 1}}
    >>> compute_all_conversions_between_units_in_ratios(ratios, keep_none=False)
    {'kg': {'kg': 1, 'm3': 200},
     'm3': {'kg': 0.005, 'm3': 1},
     'ol': {'ol': 1}}

    Example3:
    >>> ratios = {'kg per m3': 200, 'm3 per pal': 1.5, 'eur per pln': 0.25}
    >>> compute_all_conversions_between_units_in_ratios(ratios, keep_none=False)
    {'eur': {'eur': 1, 'pln': 0.25},
     'kg': {'kg': 1, 'm3': 200, 'pal': 300.0},
     'm3': {'kg': 0.005, 'm3': 1, 'pal': 1.5},
     'pal': {'kg': 0.00333, 'm3': 0.6666, 'pal': 1},
     'pln': {'eur': 4.0, 'pln': 1}}
    """
    conversions = defaultdict(dict)

    # Populate direct conversions
    for ratio, value in ratios.items():
        ratio = standardize_ratio_key(ratio)  # Remove per and spaces
        unit_a, unit_b = ratio.split('/')
        if value is not None and value is not np.nan:
            conversions[unit_a][unit_b] = value
            conversions[unit_b][unit_a] = 1 / value

    units = set(conversions.keys())

    # Use BFS to find indirect conversions
    def find_ratio(start, end):
        if start == end:
            return 1
        visited = set()
        queue = deque([(start, 1)])

        while queue:
            current, acc_ratio = queue.popleft()
            if current == end:
                return acc_ratio
            visited.add(current)

            for neighbor, neighbor_ratio in conversions[current].items():
                if neighbor not in visited:
                    queue.append((neighbor, acc_ratio * neighbor_ratio))

        return None

    # Create full conversion dictionary
    result = defaultdict(dict)
    for unit_from in units:
        for unit_to in units:
            ratio = find_ratio(unit_from, unit_to)
            if keep_none or ratio is not None:
                result[unit_from][unit_to] = ratio

    return dict(result)
