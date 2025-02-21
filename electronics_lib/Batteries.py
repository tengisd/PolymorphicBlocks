from electronics_abstract_parts import *


class Cr2032(Battery, FootprintBlock):
  def __init__(self):
    # This actually initializes in the parent, TODO unhackify this by removing spec processing, see issue #28
    super().__init__(voltage=(2.0, 3.0)*Volt)

  def contents(self):
    super().contents()

    # TODO can this be assigned self.pwr == VoltageSource(...) directly?
    self.assign(self.pwr.current_limits, (0, 10)*mAmp)  # arbitrary from https://www.mouser.com/catalog/additional/Adafruit_3262.pdf
    self.assign(self.capacity, (210, 210)*mAmp)  # TODO bounds of a few CR2032 cells; should be A*h

    self.footprint(
      'U', 'Battery:BatteryHolder_Keystone_106_1x20mm',
      {
        '1': self.pwr,
        '2': self.gnd,
      },
      mfr='Keystone', part='106'
    )


class Li18650(Battery, FootprintBlock):
  @init_in_parent
  def __init__(self, voltage=Default((2.5, 4.2))): # TODO this is broken if we add * Volt here
    # This actually initializes in the parent, TODO unhackify this by removing spec processing, see issue #28
    super().__init__(voltage=voltage)

  def contents(self):
    super().contents()

    # TODO can this be assigned self.pwr == VoltageSource(...) directly?
    self.assign(self.pwr.current_limits, (0, 2)*Amp)  # arbitrary assuming low capacity, 1 C discharge
    self.assign(self.capacity, (2, 3.6)*Amp)  # TODO should be A*h

    self.footprint(
      'U', 'Battery:BatteryHolder_Keystone_1042_1x18650',
      {
        '1': self.pwr,
        '2': self.gnd,
      },
      mfr='Keystone', part='1042'
    )

class AABattery(Battery, FootprintBlock):
  def __init__(self):
    # This actually initializes in the parent, TODO unhackify this by removing spec processing, see issue #28
    super().__init__(voltage=(1.3, 1.7)*Volt)

  def contents(self):
    super().contents()

    # TODO can this be assigned self.pwr == VoltageSource(...) directly?
    self.assign(self.pwr.current_limits, (0, 1)*Amp)
    self.assign(self.capacity, (2, 3)*Amp)  # TODO should be A*h

    self.footprint(
      'U', 'Battery:BatteryHolder_Keystone_2460_1xAA',
      {
        '1': self.pwr,
        '2': self.gnd,
      },
      mfr='Keystone', part='2461'
    )
