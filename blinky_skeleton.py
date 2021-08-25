from edg import *


class BlinkyExample(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.jack = self.Block(Pj_102a(voltage_out=3.3*Volt(tol=0.05)))
    self.mcu = self.Block(Lpc1549_48())
    self.connect(self.jack.pwr, self.mcu.pwr)
    self.led = self.Block(IndicatorLed())
    self.connect(self.led.signal, self.mcu.digital[0])
    self.connect(self.led.gnd, self.mcu.gnd, self.jack.gnd)
    # your implementation here


if __name__ == "__main__":
  compile_board_inplace(BlinkyExample)
