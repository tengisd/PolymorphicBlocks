from edg import *


class Lf21215tmr(FootprintBlock):
  def __init__(self) -> None:
    super().__init__()
    self.vcc = self.Port(
      VoltageSink(voltage_limits=(1.8, 5.5)*Volt, current_draw=(0, 1.5)*uAmp),
      [Power])

    self.gnd = self.Port(
      VoltageSink(model=None, voltage_limits=Default(RangeExpr.ALL), current_draw=Default(RangeExpr.ZERO)),
      [Common])

    self.vout = self.Port(DigitalSource.from_supply(
      self.gnd, self.vcc,
      output_threshold_offset=(0.2, -0.3)
    ))
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23',
      {'1': self.vcc, '2': self.vout, '3': self.gnd},
      mfr='[Manufacturer]', part='[Part]',
      datasheet='[Datasheet URL]'
    )
