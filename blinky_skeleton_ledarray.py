from edg import *


class BlinkyExample(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.jack = self.Block(Pj_102a(voltage_out=3.3*Volt(tol=0.05)))
    self.mcu = self.Block(Lpc1549_48())
    self.connect(self.jack.pwr, self.mcu.pwr)
    self.connect(self.mcu.gnd, self.jack.gnd)
    self.led = ElementDict()
    for i in range(4):
      self.led[i] = self.Block(IndicatorLed())
      self.connect(self.led[i].signal, self.mcu.digital[i])
      self.connect(self.led[i].gnd, self.mcu.gnd)
    # your implementation here


if __name__ == "__main__":
  compile_board_inplace(BlinkyExample)
