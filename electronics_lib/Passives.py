import csv
from functools import reduce
import math
import os

from electronics_abstract_parts import *
from .ProductTableUtils import *


def zigzag_range(start: int, end: int) -> Sequence[int]:
  if start >= end:
    return []

  center = int((start + end - 1) / 2)
  lower = list(range(start, center))
  upper = list(range(center + 1, end))
  output = [center]

  while lower or upper:
    if lower:
      output.append(lower.pop(0))
    if upper:
      output.append(upper.pop(0))

  return output

# from https://stackoverflow.com/questions/3410976/how-to-round-a-number-to-significant-figures-in-python
# TODO DEDUP w/ ResistiveDivider.py
def round_sig(x: float, sig: int) -> float:
  return round(x, sig-int(math.floor(math.log10(abs(x))))-1)

def choose_preferred_number(range: Tuple[float, float], tolerance: float, series: List[float], sig: int) ->\
    Optional[float]:
  lower_pow10 = math.floor(math.log10(range[0]))
  upper_pow10 = math.ceil(math.log10(range[1]))

  powers = zigzag_range(lower_pow10, upper_pow10)  # prefer the center power first, then zigzag away from it
  # TODO given the tolerance we can actually bound this further

  for value in series:
    for power in powers:
      pow10_mult = math.pow(10, power)
      value_mult = round_sig(value * pow10_mult, sig)  # this prevents floating point weirdness, eg 819.999
      value_tol = value_mult * tolerance
      if value_mult - value_tol >= range[0] and value_mult + value_tol <= range[1]:
        return value_mult

  return None


@abstract_block
class ESeriesResistor(Resistor, CircuitBlock, GeneratorBlock):
  TOLERANCE: float
  PACKAGE_POWER: List[Tuple[float, str]]

  @init_in_parent
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.power_rated = self.Parameter(RangeExpr())

  """Default generator that automatically picks resistors.
  For value, preferentially picks the lowest-step E-series (E1 before E3 before E6 ...) value meeting the needs,
  at +/- 1% tolerance. If an E24 resistor at 1% cannot be found, tries to midpoint of the resistance range to pick an
  exact value at 1%.
  If below 1% tolerance is needed, fails. TODO: non-preferentially pick tolerances down to 0.1%, though pricey!
  Picks the minimum (down to 0603, up to 2512) SMD size for the power requirement. TODO: consider PTH types"""
  def generate(self) -> None:
    resistance = self.get(self.resistance)
    value = choose_preferred_number(resistance, self.TOLERANCE, self.E24_SERIES_ZIGZAG, 2)

    if value is None:  # failed to find a preferred resistor, choose the center within tolerance
      center = (resistance[0] + resistance[1]) / 2
      min_tolerance = center * self.TOLERANCE
      if (center - resistance[0]) < min_tolerance or (resistance[1] - center < min_tolerance):
        # TODO should there be a better way of communicating generator failures?
        raise ValueError(f"Cannot generate 1% resistor within {resistance}")
      value = center

    constr_packages = self.get_opt(self.footprint_name)  # TODO support separators
    _, reqd_power_min = self.get(self.power)
    # TODO we only need the first really so this is a bit inefficient
    suitable_packages = [(power, package) for power, package in self.PACKAGE_POWER
                         if power >= reqd_power_min and (constr_packages is None or package == constr_packages)]
    if not suitable_packages:
      raise ValueError(f"Cannot find suitable package for resistor needing {reqd_power_min} W power")

    self.constrain(self.resistance == value * Ohm(tol=self.TOLERANCE))
    self.constrain(self.power_rated == suitable_packages[0][0])

    self.footprint(
      'R', suitable_packages[0][1],
      {
        '1': self.a,
        '2': self.b,
      },
      # TODO mfr and part number
      value=f'{UnitUtils.num_to_prefix(value, 3)}, {self.TOLERANCE * 100:0.3g}%, {suitable_packages[0][0]}W',
    )


class ChipResistor(ESeriesResistor):
  TOLERANCE = 0.01
  PACKAGE_POWER = [  # sorted by order of preference (lowest power to highest power)
    # picked based on the most common power rating for a size at 100ohm on Digikey
    # (1.0/32, '01005'),  # KiCad doesn't seem to have a default footprint this small
    # (1.0/20, 'Resistor_SMD:R_0201_0603Metric'),
    # (1.0/16, 'Resistor_SMD:R_0402_1005Metric'),
    (1.0/10, 'Resistor_SMD:R_0603_1608Metric'),
    (1.0/8, 'Resistor_SMD:R_0805_2012Metric'),
    (1.0/4, 'Resistor_SMD:R_1206_3216Metric'),
    # (1.0/2, 'Resistor_SMD:R_1210_3225Metric'),  # actually not that common
    # (3.0/4, 'Resistor_SMD:R_2010_5025Metric'),  # actually not that common
    (1.0, 'Resistor_SMD:R_2512_6332Metric'),  # a good portion are also rated for 2W
  ]


class AxialResistor(ESeriesResistor):
  TOLERANCE = 0.01
  PACKAGE_POWER = [  # sorted by order of preference (lowest power to highest power)
    # picked based on the most common power rating for a size at 100ohm on Digikey
    (1.0/8, 'Resistor_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P5.08mm_Horizontal'),
    (1.0/4, 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal'),
    (1.0/2, 'Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal'),
    (1.0, 'Resistor_THT:R_Axial_DIN0411_L9.9mm_D3.6mm_P12.70mm_Horizontal'),
    (2.0, 'Resistor_THT:R_Axial_DIN0414_L11.9mm_D4.5mm_P15.24mm_Horizontal'),
  ]


class AxialVerticalResistor(ESeriesResistor):
  TOLERANCE = 0.01
  PACKAGE_POWER = [  # sorted by order of preference (lowest power to highest power)
    # picked based on the most common power rating for a size at 100ohm on Digikey
    (1.0/8, 'Resistor_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P1.90mm_Vertical'),
    (1.0/4, 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical'),
    (1.0/2, 'Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P2.54mm_Vertical'),
    (1.0, 'Resistor_THT:R_Axial_DIN0411_L9.9mm_D3.6mm_P5.08mm_Vertical'),
    (2.0, 'Resistor_THT:R_Axial_DIN0414_L11.9mm_D4.5mm_P5.08mm_Vertical'),
  ]


def generate_mlcc_table(TABLES: List[str]) -> ProductTable:
  tables = []
  for filename in TABLES:
    path = os.path.join(os.path.dirname(__file__), 'resources', filename)
    with open(path, newline='', encoding='utf-8') as csvfile:
      reader = csv.reader(csvfile)
      tables.append(ProductTable(next(reader), [row for row in reader]))
  table = reduce(lambda x, y: x+y, tables)

  # TODO maybe do voltage derating
  # TODO also consider minimum symmetric voltage
  return table.derived_column('capacitance',
                               RangeFromTolerance(ParseValue(Column('Capacitance'), 'F'), Column('Tolerance')),
                               missing='discard') \
    .derived_column('nominal_capacitance',
                     ParseValue(Column('Capacitance'), 'F'),
                     missing='discard') \
    .derived_column('voltage',
                    RangeFromUpper(ParseValue(Column('Voltage - Rated'), 'V'))) \
    .derived_column('footprint',
                    MapDict(Column('Package / Case'), {
                      '0603 (1608 Metric)': 'Capacitor_SMD:C_0603_1608Metric',
                      '0805 (2012 Metric)': 'Capacitor_SMD:C_0805_2012Metric',
                      '1206 (3216 Metric)': 'Capacitor_SMD:C_1206_3216Metric',
                    }), missing='discard') \


class SmtCeramicCapacitor(Capacitor, CircuitBlock, GeneratorBlock):
  TOLERANCE = 0.01
  PACKAGE_VOLTAGE_RATING = [  # sorted by order of preference (lowest voltage to highest voltage)
    # picked based on the maximum voltage rating that takes up 5% of the spectrum for X5R || X7R on Digikey
    # 10v, 16v, 25v, 50v, 100v, 250v
    # (16, 'Capacitor_SMD:C_0201_0603Metric'),
    # (16, 'Capacitor_SMD:C_0402_1005Metric'),
    (50, 'Capacitor_SMD:C_0603_1608Metric'),
    (200, 'Capacitor_SMD:C_0805_2012Metric'),
    (500, 'Capacitor_SMD:C_1206_3216Metric'),
    (1000, 'Capacitor_SMD:C_1812_4532Metric')
    # (50, 'Capacitor_SMD:C_2512_6332Metric')
  ]

  @init_in_parent
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.single_nominal_capacitance = self.Parameter(RangeExpr())
    self.nominal_capacitance = self.Parameter(RangeExpr())
    # defaulted to true in generate logic, since this doesn't exist in Capacitor and during instantiation replacement
    self.voltage_rating = self.Parameter(RangeExpr())

  """Default generator that automatically picks capacitors.
  For value, preferentially picks the lowest-step E-series (E1 before E3 before E6 ...) value meeting the needs,
  at +/- 1% tolerance. If an E24 resistor at 1% cannot be found, tries to midpoint of the resistance range to pick an
  exact value at 1%.
  If below 1% tolerance is needed, fails. TODO: non-preferentially pick tolerances down to 0.1%, though pricey!
  Picks the minimum (down to 0603, up to 2512) SMD size for the power requirement. TODO: consider PTH types"""
  def generate(self) -> None:
    (voltage_lower, voltage_upper) = self.get(self.voltage)
    if self._has(self.capacitance):
      cap_low, cap_high = self.get(self.capacitance)
    else:
      assert self._has(self.part), "must specify either capacitance or part number"
      cap_low = -float('inf')
      cap_high = float('inf')

    if self._has(self.single_nominal_capacitance):
      single_cap_max = self.get(self.single_nominal_capacitance.upper()) * 1.2  # TODO tolerance elsewhere
    else:
      single_cap_max = float('inf')

    capacitance = (cap_low, cap_high)
    value = choose_preferred_number(capacitance, self.TOLERANCE, self.E24_SERIES_ZIGZAG, 2)

    if value is None:  # failed to find a preferred capacitor, choose the center within tolerance
      center = (capacitance[0] + capacitance[1]) / 2
      min_tolerance = center * self.TOLERANCE
      if (center - capacitance[0]) < min_tolerance or (capacitance[1] - center < min_tolerance):
        # TODO should there be a better way of communicating generator failures?
        raise ValueError(f"Cannot generate 1% capacitor within {capacitance}")
      value = center

    constr_packages = self.get_opt(self.footprint_name)  # TODO support separators
    _, reqd_power_min = self.get(self.power)
    # TODO we only need the first really so this is a bit inefficient
    # Chosen by a rough scan over available parts on Digikey
    suitable_packages = [(voltage, package) for voltage, package in self.PACKAGE_POWER
                         if voltage >= self.voltage_rating and (constr_packages is None or package == constr_packages)]
    if not suitable_packages:
      raise ValueError(f"Cannot find suitable package for capacitor needing {voltage_upper} V voltage rating")

    self.constrain(self.capacitance == value * Farad(tol=self.TOLERANCE))
    self.constrain(self.voltage_rating == suitable_packages[0][0])

    self.footprint(
      'C', suitable_packages[0][1],
      {
        '1': self.a,
        '2': self.b,
      },
      # TODO mfr and part number
      value=f'{UnitUtils.num_to_prefix(value, 3)}, {self.TOLERANCE * 100:0.3g}%, {suitable_packages[0][0]}W',
    )

def generate_inductor_table(TABLES: List[str]) -> ProductTable:
  tables = []
  for filename in TABLES:
    path = os.path.join(os.path.dirname(__file__), 'resources', filename)
    with open(path, newline='', encoding='utf-8') as csvfile:
      reader = csv.reader(csvfile)
      tables.append(ProductTable(next(reader), [row for row in reader]))
  table = reduce(lambda x, y: x+y, tables)

  # TODO: take min of current rating and saturation current
  # TODO maybe 10x the frequency to be safe
  return table.derived_column('inductance',
                               RangeFromTolerance(ParseValue(Column('Inductance'), 'H'), Column('Tolerance'))) \
    .derived_column('frequency',
                    RangeFromUpper(ParseValue(Column('Frequency - Self Resonant'), 'Hz')),
                    missing='discard') \
    .derived_column('current',
                    RangeFromUpper(ParseValue(Column('Current Rating (Amps)'), 'A'))) \
    .derived_column('dc_resistance',
                    RangeFromUpper(ParseValue(Column('DC Resistance (DCR)'), 'Ohm')),
                    missing='discard') \
    .derived_column('footprint',
                    ChooseFirst(
                      MapDict(Column('Package / Case'), {
                        '0603 (1608 Metric)': 'Inductor_SMD:L_0603_1608Metric',
                        '0805 (2012 Metric)': 'Inductor_SMD:L_0805_2012Metric',
                        # Kicad does not have stock 1008 footprint
                      }),
                      MapDict(Column('Series'), {
                        'SRR1015': 'Inductor_SMD:L_Bourns-SRR1005',
                        'SRR1210': 'Inductor_SMD:L_Bourns_SRR1210A',
                        'SRR1210A': 'Inductor_SMD:L_Bourns_SRR1210A',
                        'SRR1260': 'Inductor_SMD:L_Bourns_SRR1260',
                        'SRR1260A': 'Inductor_SMD:L_Bourns_SRR1260',
                        # Kicad does not have stock 1008 footprint
                      }),
                      # parse of the form NR3015T100M
                      FormatRegex(Column('Manufacturer Part Number'), 'NR(\d\d).*', 'Inductor_SMD:L_Taiyo-Yuden_NR-{0}xx'),
                    ), missing='discard') \


class SmtInductor(Inductor, CircuitBlock, GeneratorBlock):
  product_table = generate_inductor_table([
    'Digikey_Inductors_TdkMlz.csv',
    'Digikey_Inductors_MurataDfe.csv',
    'Digikey_Inductors_TaiyoYudenNr.csv',
    'Digikey_Inductors_Shielded_BournsSRR_1005_1210_1260.csv',
  ])

  @init_in_parent
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.current_rating = self.Parameter(RangeExpr())
    self.frequency_rating = self.Parameter(RangeExpr())

  def generate(self) -> None:
    # TODO eliminate arbitrary DCR limit in favor of exposing max DCR to upper levels
    parts = self.product_table.filter(RangeContains(Lit(self.get(self.inductance)), Column('inductance'))) \
        .filter(RangeContains(Lit((-float('inf'), 1)), Column('dc_resistance'))) \
        .filter(RangeContains(Column('frequency'), Lit(self.get(self.frequency)))) \
        .filter(RangeContains(Column('current'), Lit(self.get(self.current)))) \
        .filter(ContainsString(Column('Manufacturer Part Number'), self.get_opt(self.part))) \
        .filter(ContainsString(Column('footprint'), self.get_opt(self.footprint_name))) \
        .sort(Column('footprint'))  \
        .sort(Column('Unit Price (USD)'))

    part = parts.first(err=f"no inductors in {self.get(self.inductance)} H, {self.get(self.current)} A, {self.get(self.frequency)} Hz")

    self.constrain(self.inductance == part['inductance'])
    self.constrain(self.current_rating == part['current'])
    self.constrain(self.frequency_rating == part['frequency'])

    self.footprint(
      'L', part['footprint'],
      {
        '1': self.a,
        '2': self.b,
      },
      mfr=part['Manufacturer'], part=part['Manufacturer Part Number'],
      value=f"{part['Inductance']}, {part['Current Rating (Amps)']}",
      datasheet=part['Datasheets']
    )
