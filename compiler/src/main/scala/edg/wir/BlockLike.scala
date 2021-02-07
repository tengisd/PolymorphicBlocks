package edg.wir

import edg.common.common
import edg.elem.elem
import edg.expr.expr
import edg.init.init
import edg.ref.ref

import scala.collection.mutable


trait BlockLike extends Pathable {
  def toPb: elem.BlockLike
}

case class Generator(dependencies: Seq[ref.LocalPath])

/**
  * "Wrapper" around a HierarchyBlock. Sub-trees of blocks and links are contained as a mutable map in this object
  * (instead of the proto), while everything else is kept in the proto.
  * BlockLike / LinkLike lib_elem are kept in the proto, unmodified.
  * This is to allow efficient transformation at any point in the design tree without re-writing the root.
  */
class Block(pb: elem.HierarchyBlock, superclasses: Seq[ref.LibraryPath],
            unrefinedType: Option[ref.LibraryPath]) extends BlockLike
    with HasMutablePorts with HasMutableBlocks with HasMutableLinks with HasMutableConstraints with HasParams {
  private var nameOrder = ProtoUtil.getNameOrder(pb.meta)
  override protected val ports: mutable.SeqMap[String, PortLike] = parsePorts(pb.ports, nameOrder)
  override protected val blocks: mutable.SeqMap[String, BlockLike] = parseBlocks(pb.blocks, nameOrder)
  override protected val links: mutable.SeqMap[String, LinkLike] = parseLinks(pb.links, nameOrder)
  override protected val constraints: mutable.SeqMap[String, expr.ValueExpr] = parseConstraints(pb.constraints, nameOrder)
  protected val meta: mutable.SeqMap[String, common.Metadata] = mutable.SeqMap() ++ pb.getMeta.getMembers.node

  protected val generators: mutable.SeqMap[String, Generator] = {
    MapSort(pb.generators.mapValues { generatorPb =>
      require(generatorPb.conditions.length <= 1, "TODO: support OR-ing of conditions")
      val prereqs = generatorPb.conditions.headOption.getOrElse(elem.Generator.GeneratorCondition()).prereqs
      Generator(prereqs)
    }.toMap, nameOrder)
  }

  def getGenerators: Map[String, Generator] = generators.toMap
  def removeGenerator(name: String): Unit = generators.remove(name)

  /** Appends the contents of another block onto this block. Used to combine generator results.
    * Elements must not overlap.
    */
  def append(that: Block): this.type = {
    nameOrder = nameOrder ++ that.nameOrder
    require(that.ports.keySet.intersect(ports.keySet).isEmpty, "Block append ports must not overlap")
    ports ++= that.ports
    require(that.blocks.keySet.intersect(blocks.keySet).isEmpty, "Block append blocks must not overlap")
    blocks ++= that.blocks
    require(that.links.keySet.intersect(links.keySet).isEmpty, "Block append links must not overlap")
    links ++= that.links
    require(that.constraints.keySet.intersect(constraints.keySet).isEmpty, "Block append constraints must not overlap")
    constraints ++= that.constraints
    require(that.meta.keySet.intersect(meta.keySet).isEmpty, "Block append meta must not overlap")
    meta ++= that.meta
    this
  }

  /** Removes duplicate fields for an elaborated (but not recursively elaborated) block,
    * against the original block definition (excluding .append'd items).
    * This block may be in any state of elaboration.
    */
  def dedupGeneratorPb(that: elem.HierarchyBlock): elem.HierarchyBlock = {
    val filteredMeta = that.getMeta.getMembers.node.filter { case (key, value) => value.meta match {
      case common.Metadata.Meta.NamespaceOrder(meta) => false  // TODO merge namespace metadata in future?
      case _ if key == "_sourcelocator" => false // TODO merge source locators in future
      case meta if pb.getMeta.getMembers.node.contains(key) =>
        require(meta == pb.getMeta.getMembers.node(key).meta, s"metadata mismatch at $key")
        true
      case meta => true
    }}
    val dedupedMeta = filteredMeta -- pb.getMeta.getMembers.node.keys

    val newPb = that.copy(
      params = that.params -- pb.params.keys,
      ports = that.ports -- pb.ports.keys,
      blocks = that.blocks -- pb.blocks.keys,
      links = that.links -- pb.links.keys,
      constraints = that.constraints -- pb.constraints.keys,
      generators = that.generators -- pb.generators.keys,
      meta = if (dedupedMeta.isEmpty) {
        None
      } else {
        Some(common.Metadata(meta=common.Metadata.Meta.Members(common.Metadata.Members(
        dedupedMeta))))
      }
    )
    // TODO check consistency of intersection keys
    require(newPb.ports.isEmpty, "generators may not introduce new ports")
    require(newPb.params.isEmpty, "generators may not introduce new params")
    require(newPb.generators.isEmpty, "generators may not introduce new generators")
    newPb
  }

  def getBlockClass: ref.LibraryPath = {
    require(superclasses.length == 1)
    superclasses.head
  }
  override def isElaborated: Boolean = true

  override def getParams: Map[String, init.ValInit] = pb.params

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

  def toEltPb: elem.HierarchyBlock = {
    // TODO also (re)serialize NameOrder?
    pb.copy(
      superclasses=superclasses,
      prerefineClass=unrefinedType,
      ports=ports.view.mapValues(_.toPb).toMap,
      blocks=blocks.view.mapValues(_.toPb).toMap,
      links=links.view.mapValues(_.toPb).toMap,
      constraints=constraints.toMap,
      generators=Map(),
      meta=if (meta.isEmpty) {
        None
      } else {
        Some(common.Metadata(meta = common.Metadata.Meta.Members(common.Metadata.Members(
          meta.toMap))))
      },
    )
  }

  override def toPb: elem.BlockLike = {
    elem.BlockLike(`type`=elem.BlockLike.Type.Hierarchy(toEltPb))
  }
}

case class BlockLibrary(target: ref.LibraryPath) extends BlockLike {
  def resolve(suffix: Seq[String]): Pathable = throw new InvalidPathException(s"Can't resolve into library $target")
  def toPb: elem.BlockLike = elem.BlockLike(elem.BlockLike.Type.LibElem(target))
  override def isElaborated: Boolean = false
}
