# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chalk/server/v1/performance_summary.proto
# Protobuf Python Version: 4.25.3
"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n)chalk/server/v1/performance_summary.proto\x12\x0f\x63halk.server.v1\x1a\x1cgoogle/protobuf/struct.proto"\xc2\x01\n\x17ShardPerformanceSummary\x12!\n\x0coperation_id\x18\x01 \x01(\tR\x0boperationId\x12\x19\n\x08shard_id\x18\x02 \x01(\x03R\x07shardId\x12i\n%performance_summary_with_query_config\x18\x03 \x01(\x0b\x32\x17.google.protobuf.StructR!performanceSummaryWithQueryConfig"V\n2ListOfflineQueryShardPerformanceSummariesPageToken\x12 \n\x0cshard_id_hwm\x18\x01 \x01(\x03R\nshardIdHwm"\x8a\x01\n0ListOfflineQueryShardPerformanceSummariesRequest\x12!\n\x0coperation_id\x18\x01 \x01(\tR\x0boperationId\x12\x14\n\x05limit\x18\x02 \x01(\x03R\x05limit\x12\x1d\n\npage_token\x18\x03 \x01(\tR\tpageToken"\xba\x01\n1ListOfflineQueryShardPerformanceSummariesResponse\x12]\n\x15performance_summaries\x18\x01 \x03(\x0b\x32(.chalk.server.v1.ShardPerformanceSummaryR\x14performanceSummaries\x12&\n\x0fnext_page_token\x18\x02 \x01(\tR\rnextPageTokenB\xa0\x01\n\x13\x63om.chalk.server.v1B\x17PerformanceSummaryProtoP\x01Z\x12server/v1;serverv1\xa2\x02\x03\x43SX\xaa\x02\x0f\x43halk.Server.V1\xca\x02\x0f\x43halk\\Server\\V1\xe2\x02\x1b\x43halk\\Server\\V1\\GPBMetadata\xea\x02\x11\x43halk::Server::V1b\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "chalk.server.v1.performance_summary_pb2", _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals["DESCRIPTOR"]._options = None
    _globals[
        "DESCRIPTOR"
    ]._serialized_options = b"\n\023com.chalk.server.v1B\027PerformanceSummaryProtoP\001Z\022server/v1;serverv1\242\002\003CSX\252\002\017Chalk.Server.V1\312\002\017Chalk\\Server\\V1\342\002\033Chalk\\Server\\V1\\GPBMetadata\352\002\021Chalk::Server::V1"
    _globals["_SHARDPERFORMANCESUMMARY"]._serialized_start = 93
    _globals["_SHARDPERFORMANCESUMMARY"]._serialized_end = 287
    _globals["_LISTOFFLINEQUERYSHARDPERFORMANCESUMMARIESPAGETOKEN"]._serialized_start = 289
    _globals["_LISTOFFLINEQUERYSHARDPERFORMANCESUMMARIESPAGETOKEN"]._serialized_end = 375
    _globals["_LISTOFFLINEQUERYSHARDPERFORMANCESUMMARIESREQUEST"]._serialized_start = 378
    _globals["_LISTOFFLINEQUERYSHARDPERFORMANCESUMMARIESREQUEST"]._serialized_end = 516
    _globals["_LISTOFFLINEQUERYSHARDPERFORMANCESUMMARIESRESPONSE"]._serialized_start = 519
    _globals["_LISTOFFLINEQUERYSHARDPERFORMANCESUMMARIESRESPONSE"]._serialized_end = 705
# @@protoc_insertion_point(module_scope)
