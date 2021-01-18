package edg.wir

import edg.elem.elem
import edg.expr.expr
import edg.init.init
import edg.ref.ref

import scala.collection.mutable


trait BlockLike extends Pathable

/**
  * "Wrapper" around a HierarchyBlock. Sub-trees of blocks and links are contained as a mutable map in this object
  * (instead of the proto), while everything else is kept in the proto.
  * BlockLike / LinkLike lib_elem are kept in the proto, unmodified.
  * This is to allow efficient transformation at any point in the design tree without re-writing the root.
  */
class Block(pb: elem.HierarchyBlock, superclasses: Seq[ref.LibraryPath]) extends BlockLike
    with HasMutablePorts with HasMutableBlocks with HasMutableLinks with HasMutableConstraints {
  override protected val ports: mutable.Map[String, PortLike] = parsePorts(pb.ports)
  override protected val blocks: mutable.Map[String, BlockLike] = parseBlocks(pb.blocks)
  override protected val links: mutable.Map[String, LinkLike] = parseLinks(pb.links)
  override protected val constraints: mutable.Map[String, expr.ValueExpr] = mutable.HashMap() ++ pb.constraints

  override def isElaborated: Boolean = true


  def getParams: Map[String, init.ValInit] = pb.params  // immutable

  override def resolve(suffix: Seq[String]): Pathable = suffix match {
    case Seq() => this
    case Seq(subname, tail@_*) =>
      if (ports.contains(subname)) {
        ports(subname).resolve(tail)
      } else if (blocks.contains(subname)) {
        blocks(subname).resolve(tail)
      } else if (links.contains(subname)) {
        links(subname).resolve(tail)
      } else {
        throw new InvalidPathException(s"No element $subname in Block")
      }
  }

  def toPb: elem.HierarchyBlock = {
    require(getUnelaboratedPorts.isEmpty && getUnelaboratedBlocks.isEmpty && getUnelaboratedLinks.isEmpty)
    pb.copy(
      superclasses=superclasses,
      ports=ports.view.mapValues {
        case port: Port => elem.PortLike(is=elem.PortLike.Is.Port(port.toPb))
        case port => throw new IllegalArgumentException(s"Unexpected port $port in serializing block")
      }.toMap,
      blocks=blocks.view.mapValues {
        case block: Block => elem.BlockLike(`type`=elem.BlockLike.Type.Hierarchy(block.toPb))
        case block => throw new IllegalArgumentException(s"Unexpected block $block in serializing block")
      }.toMap,
      links=links.view.mapValues {
        case link: Link => elem.LinkLike(`type`=elem.LinkLike.Type.Link(link.toPb))
        case link => throw new IllegalArgumentException(s"Unexpected block $link in serializing block")
      }.toMap,
      constraints=constraints.toMap,
    )
  }
}
