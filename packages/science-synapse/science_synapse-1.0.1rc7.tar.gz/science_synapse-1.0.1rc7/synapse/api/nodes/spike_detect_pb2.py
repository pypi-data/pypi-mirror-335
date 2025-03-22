"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/nodes/spike_detect.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1capi/nodes/spike_detect.proto\x12\x07synapse"\xdb\x01\n\x11SpikeDetectConfig\x128\n\x04mode\x18\x01 \x01(\x0e2*.synapse.SpikeDetectConfig.SpikeDetectMode\x12\x14\n\x0cthreshold_uV\x18\x02 \x01(\r\x12\x13\n\x0btemplate_uV\x18\x03 \x03(\r\x12\x0c\n\x04sort\x18\x04 \x01(\x08\x12\x13\n\x0bbin_size_ms\x18\x05 \x01(\r">\n\x0fSpikeDetectMode\x12\x0e\n\nkThreshold\x10\x00\x12\r\n\tkTemplate\x10\x01\x12\x0c\n\x08kWavelet\x10\x02b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.nodes.spike_detect_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_SPIKEDETECTCONFIG']._serialized_start = 42
    _globals['_SPIKEDETECTCONFIG']._serialized_end = 261
    _globals['_SPIKEDETECTCONFIG_SPIKEDETECTMODE']._serialized_start = 199
    _globals['_SPIKEDETECTCONFIG_SPIKEDETECTMODE']._serialized_end = 261