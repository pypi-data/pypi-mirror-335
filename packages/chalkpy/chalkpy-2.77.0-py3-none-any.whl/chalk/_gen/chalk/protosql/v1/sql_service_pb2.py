# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chalk/protosql/v1/sql_service.proto
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
    b'\n#chalk/protosql/v1/sql_service.proto\x12\x11\x63halk.protosql.v1\x1a\x1f\x63halk/auth/v1/permissions.proto".\n\x16\x45xecuteSqlQueryRequest\x12\x14\n\x05query\x18\x01 \x01(\tR\x05query"[\n\x17\x45xecuteSqlQueryResponse\x12\x19\n\x08query_id\x18\x01 \x01(\tR\x07queryId\x12\x1a\n\x07parquet\x18\x02 \x01(\x0cH\x00R\x07parquetB\t\n\x07payload"+\n\x13PlanSqlQueryRequest\x12\x14\n\x05query\x18\x01 \x01(\tR\x05query"9\n\x14PlanSqlQueryResponse\x12!\n\x0clogical_plan\x18\x01 \x01(\tR\x0blogicalPlan2\xe1\x01\n\nSqlService\x12m\n\x0f\x45xecuteSqlQuery\x12).chalk.protosql.v1.ExecuteSqlQueryRequest\x1a*.chalk.protosql.v1.ExecuteSqlQueryResponse"\x03\x80}\x03\x12\x64\n\x0cPlanSqlQuery\x12&.chalk.protosql.v1.PlanSqlQueryRequest\x1a\'.chalk.protosql.v1.PlanSqlQueryResponse"\x03\x80}\x03\x42\x8e\x01\n\x15\x63om.chalk.protosql.v1B\x0fSqlServiceProtoP\x01\xa2\x02\x03\x43PX\xaa\x02\x11\x43halk.Protosql.V1\xca\x02\x11\x43halk\\Protosql\\V1\xe2\x02\x1d\x43halk\\Protosql\\V1\\GPBMetadata\xea\x02\x13\x43halk::Protosql::V1b\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "chalk.protosql.v1.sql_service_pb2", _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals["DESCRIPTOR"]._options = None
    _globals[
        "DESCRIPTOR"
    ]._serialized_options = b"\n\025com.chalk.protosql.v1B\017SqlServiceProtoP\001\242\002\003CPX\252\002\021Chalk.Protosql.V1\312\002\021Chalk\\Protosql\\V1\342\002\035Chalk\\Protosql\\V1\\GPBMetadata\352\002\023Chalk::Protosql::V1"
    _globals["_SQLSERVICE"].methods_by_name["ExecuteSqlQuery"]._options = None
    _globals["_SQLSERVICE"].methods_by_name["ExecuteSqlQuery"]._serialized_options = b"\200}\003"
    _globals["_SQLSERVICE"].methods_by_name["PlanSqlQuery"]._options = None
    _globals["_SQLSERVICE"].methods_by_name["PlanSqlQuery"]._serialized_options = b"\200}\003"
    _globals["_EXECUTESQLQUERYREQUEST"]._serialized_start = 91
    _globals["_EXECUTESQLQUERYREQUEST"]._serialized_end = 137
    _globals["_EXECUTESQLQUERYRESPONSE"]._serialized_start = 139
    _globals["_EXECUTESQLQUERYRESPONSE"]._serialized_end = 230
    _globals["_PLANSQLQUERYREQUEST"]._serialized_start = 232
    _globals["_PLANSQLQUERYREQUEST"]._serialized_end = 275
    _globals["_PLANSQLQUERYRESPONSE"]._serialized_start = 277
    _globals["_PLANSQLQUERYRESPONSE"]._serialized_end = 334
    _globals["_SQLSERVICE"]._serialized_start = 337
    _globals["_SQLSERVICE"]._serialized_end = 562
# @@protoc_insertion_point(module_scope)
