# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: db/service.proto
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
    'db/service.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import continue_list_pb2 as db_dot_continue__list__pb2
from . import continue_scan_pb2 as db_dot_continue__scan__pb2
from . import delete_pb2 as db_dot_delete__pb2
from . import get_pb2 as db_dot_get__pb2
from . import list_pb2 as db_dot_list__pb2
from . import put_pb2 as db_dot_put__pb2
from . import scan_pb2 as db_dot_scan__pb2
from . import scan_root_paths_pb2 as db_dot_scan__root__paths__pb2
from . import sync_list_pb2 as db_dot_sync__list__pb2
from . import transaction_pb2 as db_dot_transaction__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10\x64\x62/service.proto\x12\nstately.db\x1a\x16\x64\x62/continue_list.proto\x1a\x16\x64\x62/continue_scan.proto\x1a\x0f\x64\x62/delete.proto\x1a\x0c\x64\x62/get.proto\x1a\rdb/list.proto\x1a\x0c\x64\x62/put.proto\x1a\rdb/scan.proto\x1a\x18\x64\x62/scan_root_paths.proto\x1a\x12\x64\x62/sync_list.proto\x1a\x14\x64\x62/transaction.proto2\x8c\x06\n\x0f\x44\x61tabaseService\x12;\n\x03Put\x12\x16.stately.db.PutRequest\x1a\x17.stately.db.PutResponse\"\x03\x90\x02\x02\x12;\n\x03Get\x12\x16.stately.db.GetRequest\x1a\x17.stately.db.GetResponse\"\x03\x90\x02\x01\x12\x44\n\x06\x44\x65lete\x12\x19.stately.db.DeleteRequest\x1a\x1a.stately.db.DeleteResponse\"\x03\x90\x02\x02\x12J\n\tBeginList\x12\x1c.stately.db.BeginListRequest\x1a\x18.stately.db.ListResponse\"\x03\x90\x02\x01\x30\x01\x12P\n\x0c\x43ontinueList\x12\x1f.stately.db.ContinueListRequest\x1a\x18.stately.db.ListResponse\"\x03\x90\x02\x01\x30\x01\x12J\n\tBeginScan\x12\x1c.stately.db.BeginScanRequest\x1a\x18.stately.db.ListResponse\"\x03\x90\x02\x01\x30\x01\x12P\n\x0c\x43ontinueScan\x12\x1f.stately.db.ContinueScanRequest\x1a\x18.stately.db.ListResponse\"\x03\x90\x02\x01\x30\x01\x12L\n\x08SyncList\x12\x1b.stately.db.SyncListRequest\x1a\x1c.stately.db.SyncListResponse\"\x03\x90\x02\x01\x30\x01\x12T\n\x0bTransaction\x12\x1e.stately.db.TransactionRequest\x1a\x1f.stately.db.TransactionResponse\"\x00(\x01\x30\x01\x12Y\n\rScanRootPaths\x12 .stately.db.ScanRootPathsRequest\x1a!.stately.db.ScanRootPathsResponse\"\x03\x90\x02\x01\x42g\n\x0e\x63om.stately.dbB\x0cServiceProtoP\x01\xa2\x02\x03SDX\xaa\x02\nStately.Db\xca\x02\nStately\\Db\xe2\x02\x16Stately\\Db\\GPBMetadata\xea\x02\x0bStately::Dbb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'db.service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n\016com.stately.dbB\014ServiceProtoP\001\242\002\003SDX\252\002\nStately.Db\312\002\nStately\\Db\342\002\026Stately\\Db\\GPBMetadata\352\002\013Stately::Db'
  _globals['_DATABASESERVICE'].methods_by_name['Put']._loaded_options = None
  _globals['_DATABASESERVICE'].methods_by_name['Put']._serialized_options = b'\220\002\002'
  _globals['_DATABASESERVICE'].methods_by_name['Get']._loaded_options = None
  _globals['_DATABASESERVICE'].methods_by_name['Get']._serialized_options = b'\220\002\001'
  _globals['_DATABASESERVICE'].methods_by_name['Delete']._loaded_options = None
  _globals['_DATABASESERVICE'].methods_by_name['Delete']._serialized_options = b'\220\002\002'
  _globals['_DATABASESERVICE'].methods_by_name['BeginList']._loaded_options = None
  _globals['_DATABASESERVICE'].methods_by_name['BeginList']._serialized_options = b'\220\002\001'
  _globals['_DATABASESERVICE'].methods_by_name['ContinueList']._loaded_options = None
  _globals['_DATABASESERVICE'].methods_by_name['ContinueList']._serialized_options = b'\220\002\001'
  _globals['_DATABASESERVICE'].methods_by_name['BeginScan']._loaded_options = None
  _globals['_DATABASESERVICE'].methods_by_name['BeginScan']._serialized_options = b'\220\002\001'
  _globals['_DATABASESERVICE'].methods_by_name['ContinueScan']._loaded_options = None
  _globals['_DATABASESERVICE'].methods_by_name['ContinueScan']._serialized_options = b'\220\002\001'
  _globals['_DATABASESERVICE'].methods_by_name['SyncList']._loaded_options = None
  _globals['_DATABASESERVICE'].methods_by_name['SyncList']._serialized_options = b'\220\002\001'
  _globals['_DATABASESERVICE'].methods_by_name['ScanRootPaths']._loaded_options = None
  _globals['_DATABASESERVICE'].methods_by_name['ScanRootPaths']._serialized_options = b'\220\002\001'
  _globals['_DATABASESERVICE']._serialized_start=224
  _globals['_DATABASESERVICE']._serialized_end=1004
# @@protoc_insertion_point(module_scope)
