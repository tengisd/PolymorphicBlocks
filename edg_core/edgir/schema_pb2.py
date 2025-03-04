# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: schema.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import common_pb2 as common__pb2
from . import elem_pb2 as elem__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='schema.proto',
  package='edg.schema',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x0cschema.proto\x12\nedg.schema\x1a\x0c\x63ommon.proto\x1a\nelem.proto\"\x87\x04\n\x07Library\x12(\n\x02id\x18\x01 \x01(\x0b\x32\x1c.edg.schema.Library.LibIdent\x12\x0f\n\x07imports\x18\x02 \x03(\t\x12$\n\x04root\x18\n \x01(\x0b\x32\x16.edg.schema.Library.NS\x12\"\n\x04meta\x18\x7f \x01(\x0b\x32\x14.edg.common.Metadata\x1a\xdc\x02\n\x02NS\x12\x34\n\x07members\x18\x01 \x03(\x0b\x32#.edg.schema.Library.NS.MembersEntry\x1a\xd3\x01\n\x03Val\x12\x1e\n\x04port\x18\n \x01(\x0b\x32\x0e.edg.elem.PortH\x00\x12\"\n\x06\x62undle\x18\x0b \x01(\x0b\x32\x10.edg.elem.BundleH\x00\x12\x33\n\x0fhierarchy_block\x18\r \x01(\x0b\x32\x18.edg.elem.HierarchyBlockH\x00\x12\x1e\n\x04link\x18\x0e \x01(\x0b\x32\x0e.edg.elem.LinkH\x00\x12+\n\tnamespace\x18\x14 \x01(\x0b\x32\x16.edg.schema.Library.NSH\x00\x42\x06\n\x04type\x1aJ\n\x0cMembersEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12)\n\x05value\x18\x02 \x01(\x0b\x32\x1a.edg.schema.Library.NS.Val:\x02\x38\x01\x1a\x18\n\x08LibIdent\x12\x0c\n\x04name\x18\x01 \x01(\t\"4\n\x06\x44\x65sign\x12*\n\x08\x63ontents\x18\x02 \x01(\x0b\x32\x18.edg.elem.HierarchyBlockb\x06proto3')
  ,
  dependencies=[common__pb2.DESCRIPTOR,elem__pb2.DESCRIPTOR,])




_LIBRARY_NS_VAL = _descriptor.Descriptor(
  name='Val',
  full_name='edg.schema.Library.NS.Val',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='port', full_name='edg.schema.Library.NS.Val.port', index=0,
      number=10, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='bundle', full_name='edg.schema.Library.NS.Val.bundle', index=1,
      number=11, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='hierarchy_block', full_name='edg.schema.Library.NS.Val.hierarchy_block', index=2,
      number=13, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='link', full_name='edg.schema.Library.NS.Val.link', index=3,
      number=14, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='namespace', full_name='edg.schema.Library.NS.Val.namespace', index=4,
      number=20, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='type', full_name='edg.schema.Library.NS.Val.type',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=261,
  serialized_end=472,
)

_LIBRARY_NS_MEMBERSENTRY = _descriptor.Descriptor(
  name='MembersEntry',
  full_name='edg.schema.Library.NS.MembersEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='edg.schema.Library.NS.MembersEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='edg.schema.Library.NS.MembersEntry.value', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=474,
  serialized_end=548,
)

_LIBRARY_NS = _descriptor.Descriptor(
  name='NS',
  full_name='edg.schema.Library.NS',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='members', full_name='edg.schema.Library.NS.members', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_LIBRARY_NS_VAL, _LIBRARY_NS_MEMBERSENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=200,
  serialized_end=548,
)

_LIBRARY_LIBIDENT = _descriptor.Descriptor(
  name='LibIdent',
  full_name='edg.schema.Library.LibIdent',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='edg.schema.Library.LibIdent.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=550,
  serialized_end=574,
)

_LIBRARY = _descriptor.Descriptor(
  name='Library',
  full_name='edg.schema.Library',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='edg.schema.Library.id', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='imports', full_name='edg.schema.Library.imports', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='root', full_name='edg.schema.Library.root', index=2,
      number=10, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='meta', full_name='edg.schema.Library.meta', index=3,
      number=127, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_LIBRARY_NS, _LIBRARY_LIBIDENT, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=55,
  serialized_end=574,
)


_DESIGN = _descriptor.Descriptor(
  name='Design',
  full_name='edg.schema.Design',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='contents', full_name='edg.schema.Design.contents', index=0,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=576,
  serialized_end=628,
)

_LIBRARY_NS_VAL.fields_by_name['port'].message_type = elem__pb2._PORT
_LIBRARY_NS_VAL.fields_by_name['bundle'].message_type = elem__pb2._BUNDLE
_LIBRARY_NS_VAL.fields_by_name['hierarchy_block'].message_type = elem__pb2._HIERARCHYBLOCK
_LIBRARY_NS_VAL.fields_by_name['link'].message_type = elem__pb2._LINK
_LIBRARY_NS_VAL.fields_by_name['namespace'].message_type = _LIBRARY_NS
_LIBRARY_NS_VAL.containing_type = _LIBRARY_NS
_LIBRARY_NS_VAL.oneofs_by_name['type'].fields.append(
  _LIBRARY_NS_VAL.fields_by_name['port'])
_LIBRARY_NS_VAL.fields_by_name['port'].containing_oneof = _LIBRARY_NS_VAL.oneofs_by_name['type']
_LIBRARY_NS_VAL.oneofs_by_name['type'].fields.append(
  _LIBRARY_NS_VAL.fields_by_name['bundle'])
_LIBRARY_NS_VAL.fields_by_name['bundle'].containing_oneof = _LIBRARY_NS_VAL.oneofs_by_name['type']
_LIBRARY_NS_VAL.oneofs_by_name['type'].fields.append(
  _LIBRARY_NS_VAL.fields_by_name['hierarchy_block'])
_LIBRARY_NS_VAL.fields_by_name['hierarchy_block'].containing_oneof = _LIBRARY_NS_VAL.oneofs_by_name['type']
_LIBRARY_NS_VAL.oneofs_by_name['type'].fields.append(
  _LIBRARY_NS_VAL.fields_by_name['link'])
_LIBRARY_NS_VAL.fields_by_name['link'].containing_oneof = _LIBRARY_NS_VAL.oneofs_by_name['type']
_LIBRARY_NS_VAL.oneofs_by_name['type'].fields.append(
  _LIBRARY_NS_VAL.fields_by_name['namespace'])
_LIBRARY_NS_VAL.fields_by_name['namespace'].containing_oneof = _LIBRARY_NS_VAL.oneofs_by_name['type']
_LIBRARY_NS_MEMBERSENTRY.fields_by_name['value'].message_type = _LIBRARY_NS_VAL
_LIBRARY_NS_MEMBERSENTRY.containing_type = _LIBRARY_NS
_LIBRARY_NS.fields_by_name['members'].message_type = _LIBRARY_NS_MEMBERSENTRY
_LIBRARY_NS.containing_type = _LIBRARY
_LIBRARY_LIBIDENT.containing_type = _LIBRARY
_LIBRARY.fields_by_name['id'].message_type = _LIBRARY_LIBIDENT
_LIBRARY.fields_by_name['root'].message_type = _LIBRARY_NS
_LIBRARY.fields_by_name['meta'].message_type = common__pb2._METADATA
_DESIGN.fields_by_name['contents'].message_type = elem__pb2._HIERARCHYBLOCK
DESCRIPTOR.message_types_by_name['Library'] = _LIBRARY
DESCRIPTOR.message_types_by_name['Design'] = _DESIGN
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Library = _reflection.GeneratedProtocolMessageType('Library', (_message.Message,), dict(

  NS = _reflection.GeneratedProtocolMessageType('NS', (_message.Message,), dict(

    Val = _reflection.GeneratedProtocolMessageType('Val', (_message.Message,), dict(
      DESCRIPTOR = _LIBRARY_NS_VAL,
      __module__ = 'schema_pb2'
      # @@protoc_insertion_point(class_scope:edg.schema.Library.NS.Val)
      ))
    ,

    MembersEntry = _reflection.GeneratedProtocolMessageType('MembersEntry', (_message.Message,), dict(
      DESCRIPTOR = _LIBRARY_NS_MEMBERSENTRY,
      __module__ = 'schema_pb2'
      # @@protoc_insertion_point(class_scope:edg.schema.Library.NS.MembersEntry)
      ))
    ,
    DESCRIPTOR = _LIBRARY_NS,
    __module__ = 'schema_pb2'
    # @@protoc_insertion_point(class_scope:edg.schema.Library.NS)
    ))
  ,

  LibIdent = _reflection.GeneratedProtocolMessageType('LibIdent', (_message.Message,), dict(
    DESCRIPTOR = _LIBRARY_LIBIDENT,
    __module__ = 'schema_pb2'
    # @@protoc_insertion_point(class_scope:edg.schema.Library.LibIdent)
    ))
  ,
  DESCRIPTOR = _LIBRARY,
  __module__ = 'schema_pb2'
  # @@protoc_insertion_point(class_scope:edg.schema.Library)
  ))
_sym_db.RegisterMessage(Library)
_sym_db.RegisterMessage(Library.NS)
_sym_db.RegisterMessage(Library.NS.Val)
_sym_db.RegisterMessage(Library.NS.MembersEntry)
_sym_db.RegisterMessage(Library.LibIdent)

Design = _reflection.GeneratedProtocolMessageType('Design', (_message.Message,), dict(
  DESCRIPTOR = _DESIGN,
  __module__ = 'schema_pb2'
  # @@protoc_insertion_point(class_scope:edg.schema.Design)
  ))
_sym_db.RegisterMessage(Design)


_LIBRARY_NS_MEMBERSENTRY._options = None
# @@protoc_insertion_point(module_scope)
