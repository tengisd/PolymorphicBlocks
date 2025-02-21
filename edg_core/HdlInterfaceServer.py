from types import ModuleType
from typing import Optional, Set, Dict, Type, cast, List, Any

import builtins
import importlib
import inspect
import sys

from . import edgrpc, edgir
from .Core import builder, LibraryElement
from .Blocks import Link
from .HierarchyBlock import Block, GeneratorBlock
from .DesignTop import DesignTop
from .Ports import Port, Bundle


# Index of module(s) recursively, and providing protobuf LibraryPath to class resolution.
class LibraryElementResolver():
  def __init__(self):
    self.seen_modules: Set[ModuleType] = set()
    self.lib_class_map: Dict[str, Type[LibraryElement]] = {}

    # Every time we reload, we need to get a fresh handle to the relevant base classes
    self.LibraryElementType = getattr(importlib.import_module("edg_core"), "LibraryElement")
    self.PortType = getattr(importlib.import_module("edg_core"), "Port")

  def load_module(self, module: ModuleType) -> None:
    """Loads a module and indexes the contained library elements so they can be accesed by LibraryPath.
    Avoids re-loading previously loaded modules with cacheing.
    """
    self._search_module(module)

  def _search_module(self, module: ModuleType) -> None:
    # avoid repeated work and re-indexing modules
    if (module.__name__ in sys.builtin_module_names
        or not hasattr(module, '__file__')  # apparently load six.moves breaks
        or module in self.seen_modules):
      return
    self.seen_modules.add(module)

    for (name, member) in inspect.getmembers(module):
      if inspect.ismodule(member):  # recurse into visible modules
        self._search_module(member)

      if inspect.isclass(member) and issubclass(member, self.LibraryElementType) \
          and (member, 'non_library') not in member._elt_properties:  # process elements
        name = member._static_def_name()
        if name in self.lib_class_map:
          assert self.lib_class_map[name] == member, f"different redefinition of {name} in {module.__name__}"
          continue  # don't need to re-index

        for mro in member.mro():
          self._search_module(importlib.import_module(mro.__module__))

        if issubclass(member, self.PortType):  # TODO for some reason, Links not in __init__ are sometimes not found
          obj = member()  # TODO can these be class definitions?
          if hasattr(obj, 'link_type'):
            self._search_module(importlib.import_module(obj.link_type.__module__))

        self.lib_class_map[name] = member

  def class_from_path(self, path: edgir.LibraryPath) -> Optional[Type[LibraryElement]]:
    """Assuming modules have been loaded, retrieves a LibraryElement class by LibraryPath."""
    dict_key = path.target.name
    return self.lib_class_map.get(dict_key, None)


class HdlInterface():  # type: ignore
  def __init__(self):
    self.library = LibraryElementResolver()  # dummy empty resolver

  def IndexModule(self, request: edgrpc.ModuleName) -> List[edgir.LibraryPath]:
    module = importlib.import_module(request.name)
    self.library.load_module(module)
    return [edgir.LibraryPath(target=edgir.LocalStep(name=indexed))
            for indexed in self.library.lib_class_map.keys()]

  @staticmethod
  def _elaborate_class(elt_cls: Type[LibraryElement]) -> edgir.Library.NS.Val:
    obj = elt_cls()
    if isinstance(obj, Block):
      block_proto = builder.elaborate_toplevel(obj, f"in elaborating library block {elt_cls}")
      return edgir.Library.NS.Val(hierarchy_block=block_proto)
    elif isinstance(obj, Link):
      link_proto = builder.elaborate_toplevel(obj, f"in elaborating library link {elt_cls}")
      assert isinstance(link_proto, edgir.Link)  # TODO this needs to be cleaned up
      return edgir.Library.NS.Val(link=link_proto)
    elif isinstance(obj, Bundle):  # TODO: note Bundle extends Port, so this must come first
      return edgir.Library.NS.Val(bundle=obj._def_to_proto())
    elif isinstance(obj, Port):
      return edgir.Library.NS.Val(port=cast(edgir.Port, obj._def_to_proto()))
    else:
      raise RuntimeError(f"didn't match type of library element {elt_cls}")

  def GetLibraryElement(self, request: edgrpc.LibraryRequest) -> edgrpc.LibraryResponse:
    response = edgrpc.LibraryResponse()
    try:
      cls = self.library.class_from_path(request.element)
      if cls is None:
        response.error = f"No library elt {request.element}"
      else:
        response.element.CopyFrom(self._elaborate_class(cls))
        if issubclass(cls, DesignTop):  # TODO don't create another instance, perhaps refinements should be static?
          cls().refinements().populate_proto(response.refinements)
    except BaseException as e:
      import traceback
      # exception formatting from https://stackoverflow.com/questions/4564559/get-exception-description-and-stack-trace-which-caused-an-exception-all-as-a-st
      response.error = "".join(traceback.TracebackException.from_exception(e).format())
    return response

  def ElaborateGenerator(self, request: edgrpc.GeneratorRequest) -> edgrpc.GeneratorResponse:
    response = edgrpc.GeneratorResponse()
    try:
      generator_type = self.library.class_from_path(request.element)
      assert generator_type is not None, f"no generator {request.element}"
      assert issubclass(generator_type, GeneratorBlock)
      generator_obj = generator_type()
      generator_values_raw = [(value.path, edgir.valuelit_to_lit(value.value))
                              for value in request.values]
      generator_values = [(path, value)  # purge None from values to make the typer happy
                          for (path, value) in generator_values_raw
                          if value is not None]
      response.generated.CopyFrom(builder.elaborate_toplevel(
        generator_obj, f"in generate {request.fn} for {request.element}",
        generate_fn_name=request.fn, generate_values=generator_values))
    except BaseException as e:
      import traceback
      # exception formatting from https://stackoverflow.com/questions/4564559/get-exception-description-and-stack-trace-which-caused-an-exception-all-as-a-st
      response.error = "".join(traceback.TracebackException.from_exception(e).format())

    return response
