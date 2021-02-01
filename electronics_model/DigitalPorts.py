from __future__ import annotations

from typing import Optional, Union
from edg_core import *
from .CircuitBlock import CircuitLink, CircuitPortBridge, CircuitPortAdapter
from .ElectricalPorts import CircuitPort, ElectricalSink, ElectricalSource
from .Units import Volt


class DigitalLink(CircuitLink):  # can't subclass ElectricalLink because the constraint behavior is slightly different with presence of Bidir
  def __init__(self) -> None:
    super().__init__()

    self.source = self.Port(DigitalSource(), optional=True)
    self.single_sources = self.Port(Vector(DigitalSingleSource()), optional=True)
    self.sinks = self.Port(Vector(DigitalSink()), optional=True)
    self.bidirs = self.Port(Vector(DigitalBidir()), optional=True)

    # TODO RangeBuilder initializer for voltage
    self.voltage = self.Parameter(RangeExpr())

    self.voltage_limits = self.Parameter(RangeExpr())

    self.current_drawn = self.Parameter(RangeExpr())
    self.current_limits = self.Parameter(RangeExpr())

    self.output_thresholds = self.Parameter(RangeExpr())
    self.input_thresholds = self.Parameter(RangeExpr())
    self.input_low_threshold = self.Parameter(FloatExpr())
    self.input_high_threshold = self.Parameter(FloatExpr())

    self.pullup_capable = self.Parameter(BoolExpr())
    self.pulldown_capable = self.Parameter(BoolExpr())
    self.has_low_signal_driver = self.Parameter(BoolExpr())
    self.has_high_signal_driver = self.Parameter(BoolExpr())

  def contents(self):
    super().contents()

    self.constrain(self.source.is_connected() | self.single_sources.is_connected() | self.bidirs.is_connected(), "DigitalLink must have some kind of source")

    # TODO RangeBuilder initializer for voltage
    self.assign(self.voltage, (
      self.source.voltage_out.lower().min(
        self.bidirs.min(lambda x: x.voltage_out)).min(
        self.single_sources.min(lambda x: x.voltage_out)),
      self.source.voltage_out.upper().max(
        self.bidirs.max(lambda x: x.voltage_out)).max(
        self.single_sources.max(lambda x: x.voltage_out))
    ))

    self.assign(self.voltage_limits,
      self.sinks.intersection(lambda x: x.voltage_limits).intersect(self.bidirs.intersection(lambda x: x.voltage_limits))
    )
    self.constrain(self.voltage_limits.contains(self.voltage))

    self.assign(self.current_drawn,
      self.sinks.sum(lambda x: x.current_draw) + self.bidirs.sum(lambda x: x.current_draw)
    )
    self.assign(self.current_limits,
      self.source.current_limits.intersect(self.bidirs.intersection(lambda x: x.current_limits))
    )
    self.constrain(self.current_limits.contains(self.current_drawn))

    self.assign(self.output_thresholds, self.source.output_thresholds.intersect(
        self.bidirs.intersection(lambda x: x.output_thresholds).intersect(
        self.single_sources.intersection(lambda x: x.output_thresholds))))
    self.assign(self.input_thresholds, (
      self.sinks.min(lambda x: x.input_thresholds).min(self.bidirs.min(lambda x: x.input_thresholds)),
      self.sinks.max(lambda x: x.input_thresholds).max(self.bidirs.max(lambda x: x.input_thresholds))
    ))
    self.constrain(self.output_thresholds.contains(self.input_thresholds))

    self.assign(self.pullup_capable , self.bidirs.any(lambda x: x.pullup_capable) |
                   self.single_sources.any(lambda x: x.pullup_capable))
    self.assign(self.pulldown_capable, self.bidirs.any(lambda x: x.pulldown_capable) |
                   self.single_sources.any(lambda x: x.pulldown_capable))
    self.assign(self.has_low_signal_driver, self.single_sources.any(lambda x: x.low_signal_driver))
    self.assign(self.has_high_signal_driver, self.single_sources.any(lambda x: x.high_signal_driver))
    self.constrain(self.has_low_signal_driver.implies(self.pullup_capable))
    self.constrain(self.has_high_signal_driver.implies(self.pulldown_capable))

class DigitalBase(CircuitPort[DigitalLink]):
  def __init__(self) -> None:
    super().__init__()

    self.link_type = DigitalLink


class DigitalSink(DigitalBase):
  @staticmethod
  def from_supply(neg: ElectricalSink, pos: ElectricalSink,
                  voltage_limit_tolerance: RangeLike = (0, 0)*Volt,
                  current_draw: RangeLike = RangeExpr(),
                  input_threshold_abs: Optional[RangeLike] = None) -> DigitalSink:
    if input_threshold_abs is not None:
      input_threshold_abs = RangeExpr._to_expr_type(input_threshold_abs)  # TODO avoid internal functions?
      return DigitalSink(  # TODO get rid of to_expr_type w/ dedicated Range conversion
        voltage_limits=(neg.link().voltage.upper(), pos.link().voltage.lower()) +
                       RangeExpr._to_expr_type(voltage_limit_tolerance),
        current_draw=current_draw,
        input_thresholds=input_threshold_abs
      )
    else:
      raise ValueError("no input threshold specified")

  def __init__(self, model: Optional[Union[DigitalSink, DigitalBidir]] = None,
               voltage_limits: RangeLike = RangeExpr(), current_draw: RangeLike = RangeExpr(),
               input_thresholds: RangeLike = RangeExpr()) -> None:
    super().__init__()
    self.bridge_type = DigitalSinkBridge

    if model is not None:
      # TODO check that both model and individual parameters aren't overdefined
      voltage_limits = model.voltage_limits
      current_draw = model.current_draw
      input_thresholds = model.input_thresholds

    self.voltage_limits: RangeExpr = self.Parameter(RangeExpr(voltage_limits))
    self.current_draw: RangeExpr = self.Parameter(RangeExpr(current_draw))
    self.input_thresholds: RangeExpr = self.Parameter(RangeExpr(input_thresholds))


class DigitalSourceBridge(CircuitPortBridge):
  def __init__(self) -> None:
    super().__init__()

    self.outer_port = self.Port(DigitalSource())
    self.inner_link = self.Port(DigitalSink())

  def contents(self) -> None:
    super().contents()

    # Here we ignore the voltage_limits of the inner port, instead relying on the main link to handle it
    # The outer port's current_limits is untouched and should be defined in tte port def.
    # TODO: it's a slightly optimization to handle them here. Should it be done?
    # TODO: or maybe current_limits / voltage_limits shouldn't be a port, but rather a block property?
    self.assign(self.inner_link.voltage_limits, (-float('inf'), float('inf')))

    self.assign(self.outer_port.voltage_out, self.inner_link.link().voltage)
    self.assign(self.outer_port.link().current_drawn, self.inner_link.current_draw)

    self.assign(self.outer_port.output_thresholds, self.inner_link.link().output_thresholds)


class DigitalSinkBridge(CircuitPortBridge):
  def __init__(self) -> None:
    super().__init__()

    self.outer_port = self.Port(DigitalSink())
    self.inner_link = self.Port(DigitalSource())

  def contents(self) -> None:
    super().contents()

    # TODO can we actually define something here? as a pseudoport, this doesn't have limits
    self.assign(self.inner_link.current_limits, (-float('inf'), float('inf')))

    self.assign(self.outer_port.current_draw, self.inner_link.link().current_drawn)
    self.assign(self.inner_link.voltage_out, self.outer_port.link().voltage)

    self.assign(self.inner_link.output_thresholds, self.outer_port.link().output_thresholds)
    self.assign(self.outer_port.input_thresholds, (
      self.inner_link.link().input_low_threshold,
      self.inner_link.link().input_high_threshold
    ))


class DigitalSourceAdapterElectricalSource(CircuitPortAdapter[ElectricalSource]):
  @init_in_parent
  def __init__(self):
    super().__init__()
    self.src = self.Port(DigitalSink())
    self.dst = self.Port(ElectricalSource(
      voltage_out=self.src.link().voltage,
      current_limits=(-float('inf'), float('inf'))))
    self.assign(self.src.current_draw, self.dst.link().current_drawn)


class DigitalSource(DigitalBase):
  @staticmethod
  def from_supply(neg: ElectricalSink, pos: ElectricalSink, current_limits: RangeLike = RangeExpr()) -> DigitalSource:
    return DigitalSource(
      voltage_out=(neg.link().voltage.lower(), pos.link().voltage.upper()),
      current_limits=current_limits,
      output_thresholds=(neg.link().voltage.upper(), pos.link().voltage.lower())
    )

  def __init__(self, model: Optional[Union[DigitalSource, DigitalBidir]] = None,
               voltage_out: RangeLike = RangeExpr(), current_limits: RangeLike = RangeExpr(),
               output_thresholds: RangeLike = RangeExpr()) -> None:
    super().__init__()
    self.bridge_type = DigitalSourceBridge
    self.adapter_types = [DigitalSourceAdapterElectricalSource]

    if model is not None:
      # TODO check that both model and individual parameters aren't overdefined
      voltage_out = model.voltage_out
      current_limits = model.current_limits
      output_thresholds = model.output_thresholds

    self.voltage_out: RangeExpr = self.Parameter(RangeExpr(voltage_out))
    self.current_limits: RangeExpr = self.Parameter(RangeExpr(current_limits))
    self.output_thresholds: RangeExpr = self.Parameter(RangeExpr(output_thresholds))

  def as_electrical_source(self) -> ElectricalSource:
    return self._convert(DigitalSourceAdapterElectricalSource())


class DigitalBidir(DigitalBase):
  @staticmethod
  def from_supply(neg: ElectricalSink, pos: ElectricalSink,
                  voltage_limit_tolerance: RangeLike = (0, 0)*Volt,
                  current_draw: RangeLike = RangeExpr(),
                  current_limits: RangeLike = RangeExpr(), *,
                  input_threshold_factor: Optional[RangeLike] = None,
                  input_threshold_abs: Optional[RangeLike] = None,
                  output_threshold_factor: Optional[RangeLike] = None,
                  pullup_capable: BoolLike = False, pulldown_capable: BoolLike = False) -> DigitalBidir:
    input_threshold: RangeLike
    if input_threshold_factor is not None:
      assert input_threshold_abs is None, "can only specify one input threshold type"
      input_threshold_factor = RangeExpr._to_expr_type(input_threshold_factor)  # TODO avoid internal functions?
      input_threshold = (input_threshold_factor.lower() * pos.link().voltage.lower(),
                         input_threshold_factor.upper() * pos.link().voltage.upper())
    elif input_threshold_abs is not None:
      assert input_threshold_factor is None, "can only specify one input threshold type"
      input_threshold = RangeExpr._to_expr_type(input_threshold_abs)  # TODO avoid internal functions?
    else:
      raise ValueError("no input threshold specified")

    if output_threshold_factor is not None:
      output_threshold_factor = RangeExpr._to_expr_type(output_threshold_factor)
      output_threshold = (output_threshold_factor.lower() * pos.link().voltage.upper(),
                          output_threshold_factor.upper() * pos.link().voltage.lower())
    else:
      raise ValueError("no output threshold specified")

    return DigitalBidir(  # TODO get rid of to_expr_type w/ dedicated Range conversion
      voltage_limits=(neg.link().voltage.upper(), pos.link().voltage.lower()) +
                     RangeExpr._to_expr_type(voltage_limit_tolerance),
      current_draw=current_draw,
      voltage_out=(neg.link().voltage.upper(), pos.link().voltage.lower()),
      current_limits=current_limits,
      input_thresholds=input_threshold,
      output_thresholds=output_threshold,
      pullup_capable=pullup_capable, pulldown_capable=pulldown_capable
    )

  def __init__(self, model: Optional[DigitalBidir] = None,
               voltage_limits: RangeLike = RangeExpr(), current_draw: RangeLike = RangeExpr(),
               voltage_out: RangeLike = RangeExpr(), current_limits: RangeLike = RangeExpr(),
               input_thresholds: RangeLike = RangeExpr(), output_thresholds: RangeLike = RangeExpr(), *,
               pullup_capable: BoolLike = BoolExpr(), pulldown_capable: BoolLike = BoolExpr()) -> None:
    super().__init__()
    self.bridge_type = DigitalBidirBridge

    if model is not None:
      # TODO check that both model and individual parameters aren't overdefined
      voltage_limits = model.voltage_limits
      current_draw = model.current_draw
      voltage_out = model.voltage_out
      current_limits = model.current_limits
      input_thresholds = model.input_thresholds
      output_thresholds = model.output_thresholds
      pullup_capable = model.pullup_capable
      pulldown_capable = model.pulldown_capable

    self.voltage_limits: RangeExpr = self.Parameter(RangeExpr(voltage_limits))
    self.current_draw: RangeExpr = self.Parameter(RangeExpr(current_draw))
    self.voltage_out: RangeExpr = self.Parameter(RangeExpr(voltage_out))
    self.current_limits: RangeExpr = self.Parameter(RangeExpr(current_limits))
    self.input_thresholds: RangeExpr = self.Parameter(RangeExpr(input_thresholds))
    self.output_thresholds: RangeExpr = self.Parameter(RangeExpr(output_thresholds))

    self.pullup_capable: BoolExpr = self.Parameter(BoolExpr(pullup_capable))
    self.pulldown_capable: BoolExpr = self.Parameter(BoolExpr(pulldown_capable))


class DigitalBidirBridge(CircuitPortBridge):
  def __init__(self) -> None:
    super().__init__()

    self.outer_port = self.Port(DigitalBidir())
    self.inner_link = self.Port(DigitalBidir())

  def contents(self) -> None:
    super().contents()

    # TODO can we actually define something here? as a pseudoport, this doesn't have limits
    self.assign(self.inner_link.voltage_limits, (-float('inf'), float('inf')))
    self.assign(self.inner_link.current_limits, (-float('inf'), float('inf')))

    self.assign(self.outer_port.voltage_out, self.inner_link.link().voltage)
    self.assign(self.outer_port.current_draw, self.inner_link.link().current_drawn)

    self.assign(self.outer_port.output_thresholds, self.inner_link.link().output_thresholds)
    self.assign(self.outer_port.input_thresholds, (
      self.inner_link.link().input_low_threshold,
      self.inner_link.link().input_high_threshold
    ))


class DigitalSingleSource(DigitalBase):
  @staticmethod
  def pull_low_from_supply(neg: ElectricalSink) -> DigitalSingleSource:
    return DigitalSingleSource(
      voltage_out=neg.link().voltage,
      output_thresholds=(neg.link().voltage.upper(), float('inf')),
      pulldown_capable=True,
      low_signal_driver=True
    )

  @staticmethod
  def pull_high_from_supply(pos: ElectricalSink) -> DigitalSingleSource:
    return DigitalSingleSource(
      voltage_out=pos.link().voltage,
      output_thresholds=(-float('inf'), pos.link().voltage.lower()),
      pullup_capable=True,
      high_signal_driver=False
    )

  @staticmethod
  def low_from_supply(neg: ElectricalSink) -> DigitalSingleSource:
    return DigitalSingleSource(
      voltage_out=neg.link().voltage,
      output_thresholds=(neg.link().voltage.upper(), float('inf')),
      pulldown_capable=False,
      low_signal_driver=True
    )

  @staticmethod
  def high_from_supply(pos: ElectricalSink) -> DigitalSingleSource:
    return DigitalSingleSource(
      voltage_out=pos.link().voltage,
      output_thresholds=(-float('inf'), pos.link().voltage.lower()),
      pullup_capable=False,
      high_signal_driver=True
    )

  def __init__(self, voltage_out: RangeLike = RangeExpr(),
               output_thresholds: RangeLike = RangeExpr(), *,
               pullup_capable: BoolLike = BoolExpr(), pulldown_capable: BoolLike = BoolExpr(),
               low_signal_driver: BoolLike = BoolExpr(), high_signal_driver: BoolLike = BoolExpr()) -> None:
    super().__init__()

    self.voltage_out: RangeExpr = self.Parameter(RangeExpr(voltage_out))
    self.output_thresholds: RangeExpr = self.Parameter(RangeExpr(output_thresholds))

    self.pullup_capable = self.Parameter(BoolExpr(pullup_capable))
    self.pulldown_capable = self.Parameter(BoolExpr(pulldown_capable))

    self.low_signal_driver = self.Parameter(BoolExpr(low_signal_driver))
    self.high_signal_driver = self.Parameter(BoolExpr(high_signal_driver))
