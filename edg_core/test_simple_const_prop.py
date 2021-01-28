import unittest

from . import *
from edg_core.ScalaCompilerInterface import ScalaCompiler
from .CompilerUtils import *


class TestConstPropInternal(Block):
  def __init__(self) -> None:
    super().__init__()

    self.float_param = self.Parameter(FloatExpr())
    self.range_param = self.Parameter(RangeExpr())


class TestParameterConstProp(Block):
  def __init__(self) -> None:
    super().__init__()

    self.float_const = self.Parameter(FloatExpr())
    self.float_param = self.Parameter(FloatExpr())

    self.range_const = self.Parameter(RangeExpr())
    self.range_param = self.Parameter(RangeExpr())

  def contents(self):
    self.assign(self.float_const, 2.0)
    self.assign(self.float_param, self.float_const)

    self.assign(self.range_const, (1.0, 42.0))
    self.assign(self.range_param, self.range_const)

    self.block = self.Block(TestConstPropInternal())
    self.assign(self.block.float_param, self.float_param)
    self.assign(self.block.range_param, self.range_param)


class ConstPropTestCase(unittest.TestCase):
  def setUp(self) -> None:
    compiled_design = ScalaCompiler.compile(TestParameterConstProp)
    self.solved = designSolvedValues(compiled_design)

  def test_float_prop(self) -> None:
    self.assertIn(makeSolved(['float_const'], 2.0), self.solved)
    self.assertIn(makeSolved(['block', 'float_param'], 2.0), self.solved)

  def test_range_prop(self) -> None:
    self.assertIn(makeSolved(['range_const'], (1.0, 42.0)), self.solved)
    self.assertIn(makeSolved(['block', 'range_param'], (1.0, 42.0)), self.solved)


class TestPortConstPropLink(Link):
  def __init__(self) -> None:
    super().__init__()

    self.a = self.Port(TestPortConstPropPort())
    self.b = self.Port(TestPortConstPropPort())

    self.assign(self.b.float_param, self.a.float_param)  # first connected is source


class TestPortConstPropPort(Port[TestPortConstPropLink]):
  def __init__(self) -> None:
    super().__init__()
    self.link_type = TestPortConstPropLink
    self.float_param = self.Parameter(FloatExpr())


class TestPortConstPropInnerBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    self.port = self.Port(TestPortConstPropPort(), optional=True)


class TestPortConstPropOuterBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    self.inner = self.Block(TestPortConstPropInnerBlock())
    self.port = self.Port(TestPortConstPropPort())
    self.connect(self.inner.port, self.port)


class TestPortConstPropTopBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    self.block1 = self.Block(TestPortConstPropInnerBlock())
    self.block2 = self.Block(TestPortConstPropOuterBlock())
    self.link = self.connect(self.block1.port, self.block2.port)
    self.assign(self.block1.port.float_param, 3.5)


class ConstPropPortTestCase(unittest.TestCase):
  def setUp(self) -> None:
    compiled_design = ScalaCompiler.compile(TestPortConstPropTopBlock)
    self.solved = designSolvedValues(compiled_design)

  def test_port_param_prop(self) -> None:
    self.assertIn(makeSolved(['block1', 'port', 'float_param'], 3.5), self.solved)
    self.assertIn(makeSolved(['link', 'a', 'float_param'], 3.5), self.solved)
    self.assertIn(makeSolved(['link', 'b', 'float_param'], 3.5), self.solved)
    self.assertIn(makeSolved(['block2', 'port', 'float_param'], 3.5), self.solved)
    self.assertIn(makeSolved(['block2', 'inner', 'port', 'float_param'], 3.5), self.solved)

  def test_connected_link(self) -> None:
    self.assertIn(makeSolved(['block1', 'port', edgir.IS_CONNECTED], True), self.solved)
    self.assertIn(makeSolved(['block2', 'port', edgir.IS_CONNECTED], True), self.solved)
    self.assertIn(makeSolved(['block2', 'inner', 'port', edgir.IS_CONNECTED], True), self.solved)


class TestDisconnectedTopBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    self.block1 = self.Block(TestPortConstPropInnerBlock())
    self.assign(self.block1.port.float_param, 3.5)


class DisconnectedPortTestCase(unittest.TestCase):
  def setUp(self) -> None:
    compiled_design = ScalaCompiler.compile(TestDisconnectedTopBlock)
    self.solved = designSolvedValues(compiled_design)

  def test_disconnected_link(self) -> None:
    self.assertIn(makeSolved(['block1', 'port', edgir.IS_CONNECTED], False), self.solved)


class TestPortConstPropBundleLink(Link):
  def __init__(self) -> None:
    super().__init__()

    self.a = self.Port(TestPortConstPropBundle())
    self.b = self.Port(TestPortConstPropBundle())

    self.elt1_link = self.connect(self.a.elt1, self.b.elt1)
    self.elt2_link = self.connect(self.a.elt2, self.b.elt2)


class TestPortConstPropBundle(Bundle[TestPortConstPropBundleLink]):
  def __init__(self) -> None:
    super().__init__()
    self.link_type = TestPortConstPropBundleLink

    self.elt1 = self.Port(TestPortConstPropPort())
    self.elt2 = self.Port(TestPortConstPropPort())


class TestPortConstPropBundleInnerBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    self.port = self.Port(TestPortConstPropBundle())


class TestPortConstPropBundleTopBlock(Block):
  def __init__(self) -> None:
    super().__init__()

  def contents(self) -> None:
    self.block1 = self.Block(TestPortConstPropBundleInnerBlock())
    self.block2 = self.Block(TestPortConstPropBundleInnerBlock())
    self.link = self.connect(self.block1.port, self.block2.port)

    self.assign(self.block1.port.elt1.float_param, 3.5)
    self.assign(self.block1.port.elt2.float_param, 6.0)


class ConstPropBundleTestCase(unittest.TestCase):
  def setUp(self) -> None:
    compiled_design = ScalaCompiler.compile(TestPortConstPropBundleTopBlock)
    self.solved = designSolvedValues(compiled_design)

  def test_port_param_prop(self) -> None:
    self.assertIn(makeSolved(['block1', 'port', 'elt1', 'float_param'], 3.5), self.solved)
    self.assertIn(makeSolved(['block1', 'port', 'elt2', 'float_param'], 6.0), self.solved)

    self.assertIn(makeSolved(['link', 'a', 'elt1', 'float_param'], 3.5), self.solved)
    self.assertIn(makeSolved(['link', 'a', 'elt2', 'float_param'], 6.0), self.solved)

    self.assertIn(makeSolved(['link', 'elt1_link', 'a', 'float_param'], 3.5), self.solved)
    self.assertIn(makeSolved(['link', 'elt2_link', 'a', 'float_param'], 6.0), self.solved)

    self.assertIn(makeSolved(['link', 'elt1_link', 'b', 'float_param'], 3.5), self.solved)
    self.assertIn(makeSolved(['link', 'elt2_link', 'b', 'float_param'], 6.0), self.solved)

    self.assertIn(makeSolved(['link', 'b', 'elt1', 'float_param'], 3.5), self.solved)
    self.assertIn(makeSolved(['link', 'b', 'elt2', 'float_param'], 6.0), self.solved)

    self.assertIn(makeSolved(['block2', 'port', 'elt1', 'float_param'], 3.5), self.solved)
    self.assertIn(makeSolved(['block2', 'port', 'elt2', 'float_param'], 6.0), self.solved)

  def test_connected_link(self) -> None:
    self.assertIn(makeSolved(['block1', 'port', edgir.IS_CONNECTED], True), self.solved)
    self.assertIn(makeSolved(['block2', 'port', edgir.IS_CONNECTED], True), self.solved)

    self.assertIn(makeSolved(['block1', 'port', 'elt1', edgir.IS_CONNECTED], True), self.solved)
    self.assertIn(makeSolved(['block1', 'port', 'elt2', edgir.IS_CONNECTED], True), self.solved)

    self.assertIn(makeSolved(['block2', 'port', 'elt1', edgir.IS_CONNECTED], True), self.solved)
    self.assertIn(makeSolved(['block2', 'port', 'elt2', edgir.IS_CONNECTED], True), self.solved)

    self.assertIn(makeSolved(['link', 'a', edgir.IS_CONNECTED], True), self.solved)
    self.assertIn(makeSolved(['link', 'b', edgir.IS_CONNECTED], True), self.solved)

    self.assertIn(makeSolved(['link', 'a', 'elt1', edgir.IS_CONNECTED], True), self.solved)
    self.assertIn(makeSolved(['link', 'a', 'elt2', edgir.IS_CONNECTED], True), self.solved)
    self.assertIn(makeSolved(['link', 'b', 'elt1', edgir.IS_CONNECTED], True), self.solved)
    self.assertIn(makeSolved(['link', 'b', 'elt2', edgir.IS_CONNECTED], True), self.solved)

    self.assertIn(makeSolved(['link', 'elt1_link', 'a', edgir.IS_CONNECTED], True), self.solved)
    self.assertIn(makeSolved(['link', 'elt1_link', 'b', edgir.IS_CONNECTED], True), self.solved)
    self.assertIn(makeSolved(['link', 'elt2_link', 'a', edgir.IS_CONNECTED], True), self.solved)
    self.assertIn(makeSolved(['link', 'elt2_link', 'b', edgir.IS_CONNECTED], True), self.solved)
