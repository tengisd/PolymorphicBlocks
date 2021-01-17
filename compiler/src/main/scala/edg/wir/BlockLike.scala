package edg.wir

import edg.elem.elem
import edg.expr.expr
import edg.init.init
import edg.ref.ref

import scala.collection.mutable


class InvalidPathException(message: String) extends Exception(message)

/**
  * Base trait for any element that can be resolved from a path, a wrapper around types in elem.proto and parameters.
  * Non-mutable, changes should be copy the object and return a new one.
  */
trait Pathable {
  /**
    * Resolves a LocalPath from here, returning the absolute path and the target element.
    * The target element must exist as an elaborated element (and not lib_elem).
    */
  def resolve(suffix: Seq[String]): Pathable

  /** Returns whether this object is elaborated, or a library.
    * For containers, returns whether its contained element is elaborarted.
    * Only returns the status of this object, but it may contain unelaborated subtree(s).
    */
  def isElaborated: Boolean

  // Disallow equals since it's probably not useful, and full subtree matches are expensive.
  // But can be allowed in the future, since the current behavior is strict.
  override def equals(that: Any): Boolean = throw new NotImplementedError("Can't do equality comparison on Pathable")
}

trait PortLike extends Pathable
trait BlockLike extends Pathable
trait LinkLike extends Pathable

class LibraryElement(target: ref.LibraryPath) extends PortLike with BlockLike with LinkLike {
  def resolve(suffix: Seq[String]): Pathable = throw new InvalidPathException("Can't resolve LibraryElement")
  override def isElaborated: Boolean = false
}


trait HasMutablePorts {
  protected val ports: mutable.Map[String, PortLike]

  def getUnelaboratedPorts: Map[String, PortLike] = ports.toMap.filter(_._2.isElaborated)
  def elaborate(name: String, port: PortLike): Unit = {
    require(!ports(name).isElaborated && port.isElaborated)
    ports.put(name, port)
  }

  protected def parsePorts(pb: Map[String, elem.PortLike]): mutable.Map[String, PortLike] =
    mutable.HashMap[String, PortLike]() ++ pb.mapValues { _.`is` match {
      case elem.PortLike.Is.LibElem(like) => new LibraryElement(like)
      case like => throw new NotImplementedError(s"Non-library sub-port $like")
    }}
}

trait HasMutableBlocks {
  protected val blocks: mutable.Map[String, BlockLike]

  def getUnelaboratedBlocks: Map[String, BlockLike] = blocks.toMap.filter(_._2.isElaborated)
  def elaborate(name: String, block: BlockLike): Unit = {
    require(!blocks(name).isElaborated && block.isElaborated)
    blocks.put(name, block)
  }

  protected def parseBlocks(pb: Map[String, elem.BlockLike]): mutable.Map[String, BlockLike] =
    mutable.HashMap[String, BlockLike]() ++ pb.mapValues { _.`type` match {
      case elem.BlockLike.Type.LibElem(like) => new LibraryElement(like)
      case like => throw new NotImplementedError(s"Non-library sub-block $like")
    }}
}

trait HasMutableLinks {
  protected val links: mutable.Map[String, LinkLike]

  def getUnelaboratedLinks: Map[String, LinkLike] = links.toMap.filter(_._2.isElaborated)
  def elaborate(name: String, link: LinkLike): Unit = {
    require(!links(name).isElaborated && link.isElaborated)
    links.put(name, link)
  }

  protected def parseLinks(pb: Map[String, elem.LinkLike]): mutable.Map[String, LinkLike] =
    mutable.HashMap[String, LinkLike]() ++ pb.mapValues { _.`type` match {
      case elem.LinkLike.Type.LibElem(like) => new LibraryElement(like)
      case like => throw new NotImplementedError(s"Non-library sub-link $like")
    }}
}


/**
  * "Wrapper" around a HierarchyBlock. Sub-trees of blocks and links are contained as a mutable map in this object
  * (instead of the proto), while everything else is kept in the proto.
  * BlockLike / LinkLike lib_elem are kept in the proto, unmodified.
  * This is to allow efficient transformation at any point in the design tree without re-writing the root.
  */
class Block(pb: elem.HierarchyBlock) extends BlockLike with HasMutablePorts with HasMutableBlocks with HasMutableLinks {
  override protected val ports: mutable.Map[String, PortLike] = parsePorts(pb.ports)
  override protected val blocks: mutable.Map[String, BlockLike] = parseBlocks(pb.blocks)
  override protected val links: mutable.Map[String, LinkLike] = parseLinks(pb.links)

  override def isElaborated: Boolean = true


  private val constraints = mutable.HashMap[String, expr.ValueExpr]() ++ pb.constraints

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

  // Serializes this to protobuf
  def toPb: elem.HierarchyBlock = {
    require(getUnelaboratedPorts.isEmpty && getUnelaboratedBlocks.isEmpty && getUnelaboratedLinks.isEmpty)
    ???
  }
}

/**
  * Similar to Block, see documentation there.
  */
class Link(var pb: elem.Link) extends LinkLike with HasMutablePorts with HasMutableLinks {
  override protected val ports: mutable.Map[String, PortLike] = parsePorts(pb.ports)
  override protected val links: mutable.Map[String, LinkLike] = parseLinks(pb.links)

  override def isElaborated: Boolean = true


  override def resolve(suffix: Seq[String]): Pathable = suffix match {
    case Seq() => this
    case Seq(subname, tail@_*) =>
      if (ports.contains(subname)) {
        ports(subname).resolve(tail)
      } else if (links.contains(subname)) {
        links(subname).resolve(tail)
      } else {
        throw new InvalidPathException(s"No element $subname in Block")
      }
  }

  // Serializes this to protobuf
  def toPb: elem.Link = {
    require(getUnelaboratedPorts.isEmpty && getUnelaboratedLinks.isEmpty)
    ???
  }
}


class Design {
  val root: Pathable = ???  // TODO define me

  def resolve(path: DesignPath): Pathable = {
    root.resolve(path.steps)
  }
}
