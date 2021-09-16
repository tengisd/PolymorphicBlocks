from edg import *


class BlinkyExample(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.mcu = self.Block(Lpc1549_48())
    self.led = self.Block(IndicatorLed())
    self.connect(self.led.signal, self.mcu.digital[0])
    self.connect(self.led.gnd, self.mcu.gnd)
    # your implementation here


if __name__ == "__main__":
  compile_board_inplace(BlinkyExample)
