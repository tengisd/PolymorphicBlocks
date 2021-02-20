from typing import *

from electronics_model.PinAssignmentUtil import leaf_circuit_ports, PinName, ConcretePinName
from electronics_model import *


@non_library
class AssignablePinBlock(GeneratorBlock):
  """Provides two features common to microcontrollers:
  new_io(tpe): returns a fresh IO port of type tpe
  suggest_pin(port, str): suggests a pinmap
  TODO should these be separate?"""
  def __init__(self):
    super().__init__()

    self._all_assignable_ios: List[Port] = []
    self._remaining_assignable_ios: Dict[Type[Port], List[Port]] = {}

    self.pin_assigns = self.Parameter(StringExpr())

  # TODO type signature could be enhanced to only allow iterable pin with Bundle type
  PortType = TypeVar('PortType', bound=Union[CircuitPort, Bundle])
  def new_io(self, tpe: Type[PortType], *, pin: Optional[Union[PinName, Iterable[PinName]]] = None) -> PortType:
    # TODO maybe tpe should be a connectable type? or should this be an assign-and-connect op?
    assert tpe in self._remaining_assignable_ios, f"{type(self)} has no IOs of type {tpe}"
    remaining_list = self._remaining_assignable_ios[tpe]
    assert remaining_list, f"{type(self)} has no more IOs of type {tpe}"
    port = remaining_list.pop()

    return port  # type: ignore

  def _add_assignable_io(self, port: Port):
    self._all_assignable_ios.append(port)
    self._remaining_assignable_ios.setdefault(type(port), []).append(port)

  def _get_suggested_pin_maps(self, assigns_str: str) -> IdentityDict[CircuitPort, PinName]:
    assigns_per_pin = [pin_str.split('=') for pin_str in assigns_str.split(';')]
    assigns_by_pin = {pin_str[0]: pin_str[1] for pin_str in assigns_per_pin}

    pinmap: IdentityDict[CircuitPort, PinName] = IdentityDict()
    for top_port in self._all_assignable_ios:
      if self.get(top_port.is_connected()):
        port_name = self.get(top_port.link().name())
        for leaf_postfix, leaf_port in leaf_circuit_ports("", top_port):
          leaf_name = port_name + leaf_postfix
          if leaf_name in assigns_by_pin:
            assign_target_str = assigns_by_pin[leaf_name]
            if assign_target_str == 'NC':
              pinmap[leaf_port] = NotConnectedPin
            else:
              pinmap[leaf_port] = assign_target_str
            print(f"{leaf_name}={assigns_by_pin[leaf_name]}")

    return pinmap
