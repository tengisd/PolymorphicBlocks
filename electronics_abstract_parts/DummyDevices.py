from electronics_model import *
from .AbstractPassives import *
from .Categories import *


class VoltageLoad(DummyDevice):
  @init_in_parent
  def __init__(self, voltage_limit: RangeLike = Default(RangeExpr.ALL),
               current_draw: RangeLike = Default(RangeExpr.ZERO)) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink(
      voltage_limits=voltage_limit,
      current_draw=current_draw
    ), [Power])


class ForcedVoltageCurrentDraw(DummyDevice, NetBlock):
  @init_in_parent
  def __init__(self, forced_current_draw: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.pwr_in = self.Port(VoltageSink(
      current_draw=forced_current_draw,
      voltage_limits=RangeExpr.ALL
    ), [Input])

    self.pwr_out = self.Port(VoltageSource(
      voltage_out=self.pwr_in.link().voltage,
      current_limits=RangeExpr.ALL
    ), [Output])


class ForcedDigitalSinkCurrentDraw(DummyDevice, NetBlock):
  @init_in_parent
  def __init__(self, forced_current_draw: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.pwr_in = self.Port(DigitalSink(
      current_draw=forced_current_draw,
      voltage_limits=RangeExpr.ALL,
      input_thresholds=RangeExpr.EMPTY_DIT
    ), [Input])

    self.pwr_out = self.Port(DigitalSource(
      voltage_out=self.pwr_in.link().voltage,
      current_limits=RangeExpr.ALL,
      output_thresholds=self.pwr_in.link().output_thresholds
    ), [Output])


class MergedVoltageSource(DummyDevice, NetBlock):
  def __init__(self) -> None:
    super().__init__()

    self.source = self.Port(VoltageSource(
      voltage_out=RangeExpr(),
      current_limits=RangeExpr.ALL
    ))
    self.sink1 = self.Port(VoltageSink(voltage_limits=RangeExpr.ALL,
                                       current_draw=self.source.link().current_drawn))
    self.sink2 = self.Port(VoltageSink(voltage_limits=RangeExpr.ALL,
                                       current_draw=self.source.link().current_drawn))

    self.assign(self.source.voltage_out, (
      self.sink1.link().voltage.lower().min(self.sink2.link().voltage.lower()),
      self.sink1.link().voltage.upper().max(self.sink2.link().voltage.upper())))


class DummyAnalogSink(DummyDevice):
  @init_in_parent
  def __init__(self, voltage_limit: RangeLike = Default(RangeExpr.ALL),
               current_draw: RangeLike = Default(RangeExpr.ZERO),
               impedance: RangeLike = Default(RangeExpr.INF)) -> None:
    super().__init__()

    self.io = self.Port(AnalogSink(
      voltage_limits=voltage_limit,
      current_draw=current_draw,
      impedance=impedance
    ))

class DummyCapacitor(DummyDevice, Capacitor, CircuitBlock, GeneratorBlock):

  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.footprint_spec = self.Parameter(StringExpr(""))

    # Default to be overridden on a per-device basis
    self.single_nominal_capacitance = self.Parameter(RangeExpr((0, (22e-6)*1.25)))  # maximum capacitance in a single part

    self.generator(self.select_capacitor, self.capacitance, self.voltage, self.single_nominal_capacitance,
                   self.part_spec, self.footprint_spec)

    # Output values
    self.selected_capacitance = self.Parameter(RangeExpr())
    self.selected_derated_capacitance = self.Parameter(RangeExpr())
    self.selected_voltage_rating = self.Parameter(RangeExpr())

  DERATE_VOLTCO = {  # in terms of %capacitance / V over 3.6
    #  'Capacitor_SMD:C_0603_1608Metric'  # not supported, should not generate below 1uF
    'Capacitor_SMD:C_0805_2012Metric': 0.08,
    'Capacitor_SMD:C_1206_3216Metric': 0.04,
  }

  PACKAGES = [
    'Capacitor_SMD:C_0603_1608Metric',
    'Capacitor_SMD:C_0805_2012Metric',
    'Capacitor_SMD:C_1206_3216Metric'
  ]

  def select_capacitor(self, capacitance: RangeVal, voltage: RangeVal,
                                     single_nominal_capacitance: RangeVal,
                                     part_spec: str, footprint_spec: str) -> None:

    if (capacitance[0] + capacitance[1]) / 2 > 11e-6:
      self.min_package_size = self.PACKAGES[2]
    elif (capacitance[0] + capacitance[1]) / 2 > 1.1e-6:
      self.min_package_size = self.PACKAGES[1]
    else:
      self.min_package_size = self.PACKAGES[0]

    if self.get(self.footprint_spec) == "":
      self.footprint_spec = self.min_package_size

    self.assign(self.selected_capacitance, capacitance)
    self.assign(self.selected_derated_capacitance, capacitance)

    self.footprint(
      'C', self.footprint_spec,
      {
        '1': self.pos,
        '2': self.neg,
      },
      value=f'{UnitUtils.num_to_prefix(capacitance[0], 3)}F'
      # TODO mfr, part, datasheet
    )