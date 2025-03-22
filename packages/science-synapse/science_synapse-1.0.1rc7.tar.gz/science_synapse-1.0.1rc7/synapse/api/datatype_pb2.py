"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/datatype.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12api/datatype.proto\x12\x07synapse*h\n\x08DataType\x12\x14\n\x10kDataTypeUnknown\x10\x00\x12\x08\n\x04kAny\x10\x01\x12\x0e\n\nkBroadband\x10\x02\x12\x0f\n\x0bkSpiketrain\x10\x03\x12\x0f\n\x0bkTimestamps\x10\x04\x12\n\n\x06kImage\x10\x05b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.datatype_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_DATATYPE']._serialized_start = 31
    _globals['_DATATYPE']._serialized_end = 135