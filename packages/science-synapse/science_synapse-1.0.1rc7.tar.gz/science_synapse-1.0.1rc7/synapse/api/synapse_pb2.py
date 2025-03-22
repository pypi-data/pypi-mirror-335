"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/synapse.proto')
_sym_db = _symbol_database.Default()
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from ..api import node_pb2 as api_dot_node__pb2
from ..api import query_pb2 as api_dot_query__pb2
from ..api import status_pb2 as api_dot_status__pb2
from ..api import files_pb2 as api_dot_files__pb2
from ..api import logging_pb2 as api_dot_logging__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11api/synapse.proto\x12\x07synapse\x1a\x1bgoogle/protobuf/empty.proto\x1a\x0eapi/node.proto\x1a\x0fapi/query.proto\x1a\x10api/status.proto\x1a\x0fapi/files.proto\x1a\x11api/logging.proto"\xed\x01\n\nPeripheral\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0e\n\x06vendor\x18\x02 \x01(\t\x12\x15\n\rperipheral_id\x18\x03 \x01(\r\x12&\n\x04type\x18\x04 \x01(\x0e2\x18.synapse.Peripheral.Type\x12\x0f\n\x07address\x18\x05 \x01(\t"q\n\x04Type\x12\x0c\n\x08kUnknown\x10\x00\x12\x14\n\x10kBroadbandSource\x10\x01\x12\x1a\n\x16kElectricalStimulation\x10\x02\x12\x17\n\x13kOpticalStimulation\x10\x03\x12\x10\n\x0ckSpikeSource\x10\x04"\xdd\x01\n\nDeviceInfo\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0e\n\x06serial\x18\x02 \x01(\t\x12\x17\n\x0fsynapse_version\x18\x03 \x01(\r\x12\x18\n\x10firmware_version\x18\x04 \x01(\r\x12\x1f\n\x06status\x18\x05 \x01(\x0b2\x0f.synapse.Status\x12(\n\x0bperipherals\x18\x06 \x03(\x0b2\x13.synapse.Peripheral\x123\n\rconfiguration\x18\x07 \x01(\x0b2\x1c.synapse.DeviceConfiguration"g\n\x13DeviceConfiguration\x12"\n\x05nodes\x18\x01 \x03(\x0b2\x13.synapse.NodeConfig\x12,\n\x0bconnections\x18\x02 \x03(\x0b2\x17.synapse.NodeConnection2\xbb\x05\n\rSynapseDevice\x125\n\x04Info\x12\x16.google.protobuf.Empty\x1a\x13.synapse.DeviceInfo"\x00\x12<\n\tConfigure\x12\x1c.synapse.DeviceConfiguration\x1a\x0f.synapse.Status"\x00\x122\n\x05Start\x12\x16.google.protobuf.Empty\x1a\x0f.synapse.Status"\x00\x121\n\x04Stop\x12\x16.google.protobuf.Empty\x1a\x0f.synapse.Status"\x00\x128\n\x05Query\x12\x15.synapse.QueryRequest\x1a\x16.synapse.QueryResponse"\x00\x12A\n\tListFiles\x12\x16.google.protobuf.Empty\x1a\x1a.synapse.ListFilesResponse"\x00\x12D\n\tWriteFile\x12\x19.synapse.WriteFileRequest\x1a\x1a.synapse.WriteFileResponse"\x00\x12C\n\x08ReadFile\x12\x18.synapse.ReadFileRequest\x1a\x19.synapse.ReadFileResponse"\x000\x01\x12G\n\nDeleteFile\x12\x1a.synapse.DeleteFileRequest\x1a\x1b.synapse.DeleteFileResponse"\x00\x12@\n\x07GetLogs\x12\x18.synapse.LogQueryRequest\x1a\x19.synapse.LogQueryResponse"\x00\x12;\n\x08TailLogs\x12\x18.synapse.TailLogsRequest\x1a\x11.synapse.LogEntry"\x000\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.synapse_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_PERIPHERAL']._serialized_start = 147
    _globals['_PERIPHERAL']._serialized_end = 384
    _globals['_PERIPHERAL_TYPE']._serialized_start = 271
    _globals['_PERIPHERAL_TYPE']._serialized_end = 384
    _globals['_DEVICEINFO']._serialized_start = 387
    _globals['_DEVICEINFO']._serialized_end = 608
    _globals['_DEVICECONFIGURATION']._serialized_start = 610
    _globals['_DEVICECONFIGURATION']._serialized_end = 713
    _globals['_SYNAPSEDEVICE']._serialized_start = 716
    _globals['_SYNAPSEDEVICE']._serialized_end = 1415