package edg

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._
import edg.schema.schema
import edg.wir.DesignPath


class ElemModifierTest extends AnyFlatSpec {
  behavior of "ElemModifier"

  val design: schema.Design = Design(Block.Block("topDesign",
    blocks = Map (
      "inner" -> Block.Block(selfClass="original")
    )
  ).getHierarchy)

  it should "be able to add blocks in design root" in {
    val inserted = Block.Block(selfClass="new")
    val transformed = ElemModifier.modifyBlock(DesignPath(), design) { block =>
      block.update(
        _.blocks :+= ("testInserted", inserted)
      )
    }
    transformed.getContents.blocks.get("testInserted") should equal(Some(inserted))
    // make sure it didn't touch the original one
    transformed.getContents.blocks.get("inner") should equal(Some(design.getContents.blocks("inner")))
  }

  it should "be able to add blocks in nested blocks" in {
    val inserted = Block.Block(selfClass="new")
    val transformed = ElemModifier.modifyBlock(DesignPath() + "inner", design) { block =>
      block.update(
        _.blocks :+= ("innerInserted", inserted)
      )
    }
    transformed.getContents.blocks("inner").getHierarchy.blocks.get("innerInserted") should equal(Some(inserted))
    transformed.getContents.blocks("inner").getHierarchy.getSelfClass should equal(
      design.getContents.blocks("inner").getHierarchy.getSelfClass)
  }
}
