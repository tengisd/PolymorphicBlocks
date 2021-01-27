import os
import unittest
import sys

if __name__ == '__main__':  # to allow this to be executed in repo root without import errors
  import os
  sys.path.append(os.getcwd())

from edg import *
from edg import TransformUtil as tfu


class TestBlinkyBasic(Block):
  def contents(self):
    super().contents()
    self.mcu = self.Block(Nucleo_F303k8())

    self.led = self.Block(IndicatorLed())
    self.connect(self.mcu.gnd, self.led.gnd)
    self.connect(self.mcu.new_io(DigitalBidir), self.led.signal)


class TestBlinkySimple(Block):
  def contents(self):
    super().contents()
    self.mcu = self.Block(Nucleo_F303k8())

    with self.implicit_connect(
        ImplicitConnect(self.mcu.gnd, [Common]),
    ) as imp:
      self.led = imp.Block(IndicatorLed())
      self.sw = imp.Block(DigitalSwitch())

    self.connect(self.mcu.new_io(DigitalBidir), self.led.signal)
    self.connect(self.sw.out, self.mcu.new_io(DigitalBidir))


class TestBlinkySimpleChain(Block):
  def contents(self):
    super().contents()
    self.mcu = self.Block(Nucleo_F303k8())

    with self.implicit_connect(
        ImplicitConnect(self.mcu.gnd, [Common]),
    ) as imp:
      (self.led, ), _ = self.chain(self.mcu.new_io(DigitalBidir), imp.Block(IndicatorLed()))
      (self.sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.new_io(DigitalBidir))


class TestBlinkyBroken(Block):
  def contents(self):
    super().contents()
    self.usb = self.Block(UsbDeviceCReceptacle())

    self.vusb = self.connect(self.usb.pwr)
    self.gnd = self.connect(self.usb.gnd)

    with self.implicit_connect(
        ImplicitConnect(self.usb.pwr, [Power]),
        ImplicitConnect(self.usb.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(Lpc1549_48())
      (self.swd, ), _ = self.chain(imp.Block(SwdCortexTargetHeader()), self.mcu.swd)


class TestBlinkyFlattened(Block):
  def contents(self):
    super().contents()
    self.usb = self.Block(UsbDeviceCReceptacle())

    self.vusb = self.connect(self.usb.pwr)
    self.gnd = self.connect(self.usb.gnd)

    with self.implicit_connect(
        ImplicitConnect(self.usb.pwr, [Power]),
        ImplicitConnect(self.usb.gnd, [Common]),
    ) as imp:
      self.usb_reg = imp.Block(BuckConverter(output_voltage=3.3*Volt(tol=0.05)))

    self.v3v3 = self.connect(self.usb_reg.pwr_out)

    with self.implicit_connect(
        ImplicitConnect(self.usb_reg.pwr_out, [Power]),
        ImplicitConnect(self.usb.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(Lpc1549_48())
      (self.swd, ), _ = self.chain(imp.Block(SwdCortexTargetHeader()), self.mcu.swd)

      (self.led, ), _ = self.chain(self.mcu.new_io(DigitalBidir), imp.Block(IndicatorLed()))
      (self.sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.new_io(DigitalBidir))


class Mcp9700_Device(CircuitBlock):
  def __init__(self) -> None:
    super().__init__()
    # block boundary (ports, parameters) definition here
    self.vdd = self.Port(ElectricalSink(
      voltage_limits=(2.3, 5.5)*Volt, current_draw=(0, 15)*uAmp
    ), [Power])
    self.vout = self.Port(AnalogSource(
      voltage_out=(0.1, 2), current_limits=(0, 100)*uAmp,
      impedance=(20, 20)*Ohm
    ), [Output])
    self.gnd = self.Port(Ground(), [Common])

  def contents(self) -> None:
    super().contents()
    # block implementation (subblocks, internal connections, footprint) here
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23',
      {
        '1': self.vdd,
        '2': self.vout,
        '3': self.gnd,
      },
      mfr='Microchip Technology', part='MCP9700T-E/TT',
      datasheet='http://ww1.microchip.com/downloads/en/DeviceDoc/20001942G.pdf'
    )


class Mcp9700(Block):
  def __init__(self) -> None:
    super().__init__()
    self.ic = self.Block(Mcp9700_Device())
    self.pwr = self.Export(self.ic.vdd)
    self.gnd = self.Export(self.ic.gnd)
    self.out = self.Export(self.ic.vout)

  def contents(self) -> None:
    super().contents()
    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      self.vdd_cap = imp.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))


class TestBlinkyComplete(Block):
  def contents(self):
    super().contents()
    self.usb = self.Block(UsbDeviceCReceptacle())

    self.vusb = self.connect(self.usb.pwr)
    self.gnd = self.connect(self.usb.gnd)

    with self.implicit_connect(
        ImplicitConnect(self.usb.pwr, [Power]),
        ImplicitConnect(self.usb.gnd, [Common]),
    ) as imp:
      self.usb_reg = imp.Block(BuckConverter(output_voltage=3.3*Volt(tol=0.05)))

    self.v3v3 = self.connect(self.usb_reg.pwr_out)

    with self.implicit_connect(
        ImplicitConnect(self.usb_reg.pwr_out, [Power]),
        ImplicitConnect(self.usb.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(Lpc1549_48())
      (self.swd, ), _ = self.chain(imp.Block(SwdCortexTargetHeader()), self.mcu.swd)

      self.led = ElementDict[IndicatorLed]()
      for i in range(8):
        (self.led[i], ), _ = self.chain(self.mcu.new_io(DigitalBidir), imp.Block(IndicatorLed()))

      (self.sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.new_io(DigitalBidir))
      (self.temp, ), _ = self.chain(imp.Block(Mcp9700()), self.mcu.new_io(AnalogSink))


class BlinkyTestCase(unittest.TestCase):
  def test_design_basic(self) -> None:
    ElectronicsDriver([sys.modules[__name__]]).generate_write_block(
      TestBlinkyBasic(),
      os.path.splitext(__file__)[0] + '_basic'
    )

  def test_design_simple(self) -> None:
    ElectronicsDriver([sys.modules[__name__]]).generate_write_block(
      TestBlinkySimple(),
      os.path.splitext(__file__)[0] + '_simple'
    )

  def test_design_simple_chain(self) -> None:
    ElectronicsDriver([sys.modules[__name__]]).generate_write_block(
      TestBlinkySimpleChain(),
      os.path.splitext(__file__)[0] + '_simple_chain'
    )

  def test_design_broken(self) -> None:
    with self.assertRaises(InvalidNetlistBlockException):
      ElectronicsDriver([sys.modules[__name__]]).generate_write_block(
        TestBlinkyBroken(),
        os.path.splitext(__file__)[0] + '_broken'
      )

  def test_design_flat(self) -> None:
    ElectronicsDriver([sys.modules[__name__]]).generate_write_block(
      TestBlinkyFlattened(),
      os.path.splitext(__file__)[0] + '_flat',
      instance_refinements={
        tfu.Path.empty().append_block('usb_reg'): Tps561201,
      }
    )

  def test_design_complete(self) -> None:
    ElectronicsDriver([sys.modules[__name__]]).generate_write_block(
      TestBlinkyComplete(),
      os.path.splitext(__file__)[0] + '_complete',
      instance_refinements={
        tfu.Path.empty().append_block('usb_reg'): Tps561201,
      }
    )

if __name__ == '__main__':
  from edg_core.ScalaCompilerInterface import ScalaCompiler
  import grpc  # type: ignore
  from edg_core import HdlInterface, edgrpc
  from concurrent import futures
  from edg_core.HdlInterfaceServer import CachedLibrary

  # server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
  # edgrpc.add_HdlInterfaceServicer_to_server(HdlInterface(CachedLibrary()), server)  # type: ignore
  # server.add_insecure_port('[::]:50051')
  # print("started server")
  # server.start()
  # server.wait_for_termination()

  compiler = ScalaCompiler()
  compiled_design = compiler.compile(TestBlinkyBasic)
