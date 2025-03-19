# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chalk/artifacts/v1/export.proto
# Protobuf Python Version: 4.25.3
"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from chalk._gen.chalk.artifacts.v1 import cdc_pb2 as chalk_dot_artifacts_dot_v1_dot_cdc__pb2
from chalk._gen.chalk.artifacts.v1 import chart_pb2 as chalk_dot_artifacts_dot_v1_dot_chart__pb2
from chalk._gen.chalk.artifacts.v1 import cron_query_pb2 as chalk_dot_artifacts_dot_v1_dot_cron__query__pb2
from chalk._gen.chalk.common.v1 import chalk_error_pb2 as chalk_dot_common_dot_v1_dot_chalk__error__pb2
from chalk._gen.chalk.graph.v1 import graph_pb2 as chalk_dot_graph_dot_v1_dot_graph__pb2
from chalk._gen.chalk.lsp.v1 import lsp_pb2 as chalk_dot_lsp_dot_v1_dot_lsp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1f\x63halk/artifacts/v1/export.proto\x12\x12\x63halk.artifacts.v1\x1a\x1c\x63halk/artifacts/v1/cdc.proto\x1a\x1e\x63halk/artifacts/v1/chart.proto\x1a#chalk/artifacts/v1/cron_query.proto\x1a!chalk/common/v1/chalk_error.proto\x1a\x1a\x63halk/graph/v1/graph.proto\x1a\x16\x63halk/lsp/v1/lsp.proto"\xb0\x02\n\x13\x45nvironmentSettings\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12\x1d\n\x07runtime\x18\x02 \x01(\tH\x00R\x07runtime\x88\x01\x01\x12\'\n\x0crequirements\x18\x03 \x01(\tH\x01R\x0crequirements\x88\x01\x01\x12#\n\ndockerfile\x18\x04 \x01(\tH\x02R\ndockerfile\x88\x01\x01\x12+\n\x11requires_packages\x18\x05 \x03(\tR\x10requiresPackages\x12.\n\x10platform_version\x18\x06 \x01(\tH\x03R\x0fplatformVersion\x88\x01\x01\x42\n\n\x08_runtimeB\x0f\n\r_requirementsB\r\n\x0b_dockerfileB\x13\n\x11_platform_version"\xc0\x01\n\x0fProjectSettings\x12\x18\n\x07project\x18\x01 \x01(\tR\x07project\x12K\n\x0c\x65nvironments\x18\x02 \x03(\x0b\x32\'.chalk.artifacts.v1.EnvironmentSettingsR\x0c\x65nvironments\x12\x46\n\nvalidation\x18\x03 \x01(\x0b\x32&.chalk.artifacts.v1.ValidationSettingsR\nvalidation"@\n\x10MetadataSettings\x12\x12\n\x04name\x18\x01 \x01(\tR\x04name\x12\x18\n\x07missing\x18\x02 \x01(\tR\x07missing"S\n\x0f\x46\x65\x61tureSettings\x12@\n\x08metadata\x18\x01 \x03(\x0b\x32$.chalk.artifacts.v1.MetadataSettingsR\x08metadata"T\n\x10ResolverSettings\x12@\n\x08metadata\x18\x01 \x03(\x0b\x32$.chalk.artifacts.v1.MetadataSettingsR\x08metadata"\x95\x01\n\x12ValidationSettings\x12=\n\x07\x66\x65\x61ture\x18\x01 \x01(\x0b\x32#.chalk.artifacts.v1.FeatureSettingsR\x07\x66\x65\x61ture\x12@\n\x08resolver\x18\x02 \x01(\x0b\x32$.chalk.artifacts.v1.ResolverSettingsR\x08resolver"a\n\x0c\x46\x61iledImport\x12\x1b\n\tfile_name\x18\x01 \x01(\tR\x08\x66ileName\x12\x16\n\x06module\x18\x02 \x01(\tR\x06module\x12\x1c\n\ttraceback\x18\x03 \x01(\tR\ttraceback"O\n\x0b\x43halkpyInfo\x12\x18\n\x07version\x18\x01 \x01(\tR\x07version\x12\x1b\n\x06python\x18\x02 \x01(\tH\x00R\x06python\x88\x01\x01\x42\t\n\x07_python"\x8c\x01\n\rValidationLog\x12\x16\n\x06header\x18\x01 \x01(\tR\x06header\x12\x1c\n\tsubheader\x18\x02 \x01(\tR\tsubheader\x12\x45\n\x08severity\x18\x03 \x01(\x0e\x32).chalk.artifacts.v1.ValidationLogSeverityR\x08severity"\xb5\x04\n\x06\x45xport\x12+\n\x05graph\x18\x01 \x01(\x0b\x32\x15.chalk.graph.v1.GraphR\x05graph\x12\x33\n\x05\x63rons\x18\x02 \x03(\x0b\x32\x1d.chalk.artifacts.v1.CronQueryR\x05\x63rons\x12\x31\n\x06\x63harts\x18\x03 \x03(\x0b\x32\x19.chalk.artifacts.v1.ChartR\x06\x63harts\x12>\n\x0b\x63\x64\x63_sources\x18\x04 \x03(\x0b\x32\x1d.chalk.artifacts.v1.CDCSourceR\ncdcSources\x12;\n\x06\x63onfig\x18\x05 \x01(\x0b\x32#.chalk.artifacts.v1.ProjectSettingsR\x06\x63onfig\x12\x39\n\x07\x63halkpy\x18\x06 \x01(\x0b\x32\x1f.chalk.artifacts.v1.ChalkpyInfoR\x07\x63halkpy\x12\x38\n\x06\x66\x61iled\x18\x07 \x03(\x0b\x32 .chalk.artifacts.v1.FailedImportR\x06\x66\x61iled\x12\x35\n\x04logs\x18\x08 \x03(\x0b\x32!.chalk.artifacts.v1.ValidationLogR\x04logs\x12#\n\x03lsp\x18\t \x01(\x0b\x32\x11.chalk.lsp.v1.LSPR\x03lsp\x12H\n\x11\x63onversion_errors\x18\n \x03(\x0b\x32\x1b.chalk.common.v1.ChalkErrorR\x10\x63onversionErrors*\xaa\x01\n\x15ValidationLogSeverity\x12\'\n#VALIDATION_LOG_SEVERITY_UNSPECIFIED\x10\x00\x12 \n\x1cVALIDATION_LOG_SEVERITY_INFO\x10\x04\x12#\n\x1fVALIDATION_LOG_SEVERITY_WARNING\x10\x08\x12!\n\x1dVALIDATION_LOG_SEVERITY_ERROR\x10\x0c\x42\x8f\x01\n\x16\x63om.chalk.artifacts.v1B\x0b\x45xportProtoP\x01\xa2\x02\x03\x43\x41X\xaa\x02\x12\x43halk.Artifacts.V1\xca\x02\x12\x43halk\\Artifacts\\V1\xe2\x02\x1e\x43halk\\Artifacts\\V1\\GPBMetadata\xea\x02\x14\x43halk::Artifacts::V1b\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "chalk.artifacts.v1.export_pb2", _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals["DESCRIPTOR"]._options = None
    _globals[
        "DESCRIPTOR"
    ]._serialized_options = b"\n\026com.chalk.artifacts.v1B\013ExportProtoP\001\242\002\003CAX\252\002\022Chalk.Artifacts.V1\312\002\022Chalk\\Artifacts\\V1\342\002\036Chalk\\Artifacts\\V1\\GPBMetadata\352\002\024Chalk::Artifacts::V1"
    _globals["_VALIDATIONLOGSEVERITY"]._serialized_start = 2024
    _globals["_VALIDATIONLOGSEVERITY"]._serialized_end = 2194
    _globals["_ENVIRONMENTSETTINGS"]._serialized_start = 242
    _globals["_ENVIRONMENTSETTINGS"]._serialized_end = 546
    _globals["_PROJECTSETTINGS"]._serialized_start = 549
    _globals["_PROJECTSETTINGS"]._serialized_end = 741
    _globals["_METADATASETTINGS"]._serialized_start = 743
    _globals["_METADATASETTINGS"]._serialized_end = 807
    _globals["_FEATURESETTINGS"]._serialized_start = 809
    _globals["_FEATURESETTINGS"]._serialized_end = 892
    _globals["_RESOLVERSETTINGS"]._serialized_start = 894
    _globals["_RESOLVERSETTINGS"]._serialized_end = 978
    _globals["_VALIDATIONSETTINGS"]._serialized_start = 981
    _globals["_VALIDATIONSETTINGS"]._serialized_end = 1130
    _globals["_FAILEDIMPORT"]._serialized_start = 1132
    _globals["_FAILEDIMPORT"]._serialized_end = 1229
    _globals["_CHALKPYINFO"]._serialized_start = 1231
    _globals["_CHALKPYINFO"]._serialized_end = 1310
    _globals["_VALIDATIONLOG"]._serialized_start = 1313
    _globals["_VALIDATIONLOG"]._serialized_end = 1453
    _globals["_EXPORT"]._serialized_start = 1456
    _globals["_EXPORT"]._serialized_end = 2021
# @@protoc_insertion_point(module_scope)
