# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chalk/server/v1/manager.proto
# Protobuf Python Version: 4.25.3
"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from chalk._gen.chalk.auth.v1 import permissions_pb2 as chalk_dot_auth_dot_v1_dot_permissions__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1d\x63halk/server/v1/manager.proto\x12\x0f\x63halk.server.v1\x1a\x1f\x63halk/auth/v1/permissions.proto"B\n\x1dGetClusterEnvironmentsRequest\x12!\n\x0c\x63luster_name\x18\x01 \x01(\tR\x0b\x63lusterName"I\n\x1eGetClusterEnvironmentsResponse\x12\'\n\x0f\x65nvironment_ids\x18\x01 \x03(\tR\x0e\x65nvironmentIds2\x94\x01\n\x0eManagerService\x12\x81\x01\n\x16GetClusterEnvironments\x12..chalk.server.v1.GetClusterEnvironmentsRequest\x1a/.chalk.server.v1.GetClusterEnvironmentsResponse"\x06\x90\x02\x01\x80}\x02\x42\x95\x01\n\x13\x63om.chalk.server.v1B\x0cManagerProtoP\x01Z\x12server/v1;serverv1\xa2\x02\x03\x43SX\xaa\x02\x0f\x43halk.Server.V1\xca\x02\x0f\x43halk\\Server\\V1\xe2\x02\x1b\x43halk\\Server\\V1\\GPBMetadata\xea\x02\x11\x43halk::Server::V1b\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "chalk.server.v1.manager_pb2", _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals["DESCRIPTOR"]._options = None
    _globals[
        "DESCRIPTOR"
    ]._serialized_options = b"\n\023com.chalk.server.v1B\014ManagerProtoP\001Z\022server/v1;serverv1\242\002\003CSX\252\002\017Chalk.Server.V1\312\002\017Chalk\\Server\\V1\342\002\033Chalk\\Server\\V1\\GPBMetadata\352\002\021Chalk::Server::V1"
    _globals["_MANAGERSERVICE"].methods_by_name["GetClusterEnvironments"]._options = None
    _globals["_MANAGERSERVICE"].methods_by_name["GetClusterEnvironments"]._serialized_options = b"\220\002\001\200}\002"
    _globals["_GETCLUSTERENVIRONMENTSREQUEST"]._serialized_start = 83
    _globals["_GETCLUSTERENVIRONMENTSREQUEST"]._serialized_end = 149
    _globals["_GETCLUSTERENVIRONMENTSRESPONSE"]._serialized_start = 151
    _globals["_GETCLUSTERENVIRONMENTSRESPONSE"]._serialized_end = 224
    _globals["_MANAGERSERVICE"]._serialized_start = 227
    _globals["_MANAGERSERVICE"]._serialized_end = 375
# @@protoc_insertion_point(module_scope)
