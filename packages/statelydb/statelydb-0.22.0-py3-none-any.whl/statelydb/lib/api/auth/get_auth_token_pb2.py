# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: auth/get_auth_token.proto
# Protobuf Python Version: 5.29.3
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    3,
    '',
    'auth/get_auth_token.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x19\x61uth/get_auth_token.proto\x12\x0cstately.auth\"B\n\x13GetAuthTokenRequest\x12\x1f\n\naccess_key\x18\x01 \x01(\tH\x00R\taccessKeyB\n\n\x08identity\"W\n\x14GetAuthTokenResponse\x12\x1d\n\nauth_token\x18\x01 \x01(\tR\tauthToken\x12 \n\x0c\x65xpires_in_s\x18\x02 \x01(\x04R\nexpiresInSBv\n\x10\x63om.stately.authB\x11GetAuthTokenProtoP\x01\xa2\x02\x03SAX\xaa\x02\x0cStately.Auth\xca\x02\x0cStately\\Auth\xe2\x02\x18Stately\\Auth\\GPBMetadata\xea\x02\rStately::Authb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'auth.get_auth_token_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n\020com.stately.authB\021GetAuthTokenProtoP\001\242\002\003SAX\252\002\014Stately.Auth\312\002\014Stately\\Auth\342\002\030Stately\\Auth\\GPBMetadata\352\002\rStately::Auth'
  _globals['_GETAUTHTOKENREQUEST']._serialized_start=43
  _globals['_GETAUTHTOKENREQUEST']._serialized_end=109
  _globals['_GETAUTHTOKENRESPONSE']._serialized_start=111
  _globals['_GETAUTHTOKENRESPONSE']._serialized_end=198
# @@protoc_insertion_point(module_scope)
