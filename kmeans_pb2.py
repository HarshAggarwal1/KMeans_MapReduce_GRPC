# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: kmeans.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0ckmeans.proto\x12\x06kmeans\"g\n\x0bMasterInput\x12\x13\n\x0bnum_mappers\x18\x01 \x01(\x05\x12\x14\n\x0cnum_reducers\x18\x02 \x01(\x05\x12\x15\n\rnum_centroids\x18\x03 \x01(\x05\x12\x16\n\x0enum_iterations\x18\x04 \x01(\x05\"4\n\nInputSplit\x12\x13\n\x0bstart_index\x18\x02 \x01(\x05\x12\x11\n\tend_index\x18\x03 \x01(\x05\"\x1d\n\x05Point\x12\t\n\x01x\x18\x01 \x01(\x02\x12\t\n\x01y\x18\x02 \x01(\x02\"U\n\x08MapInput\x12\'\n\x0binput_split\x18\x01 \x01(\x0b\x32\x12.kmeans.InputSplit\x12 \n\tcentroids\x18\x02 \x03(\x0b\x32\r.kmeans.Point\"W\n\x0bMappedPoint\x12\x16\n\x0e\x63\x65ntroid_index\x18\x01 \x01(\x05\x12!\n\ndata_point\x18\x02 \x01(\x0b\x32\r.kmeans.Point\x12\r\n\x05\x63ount\x18\x03 \x01(\x05\"7\n\tMapOutput\x12*\n\rmapped_points\x18\x01 \x03(\x0b\x32\x13.kmeans.MappedPoint\"R\n\x0ePartitionInput\x12*\n\rmapped_points\x18\x01 \x03(\x0b\x32\x13.kmeans.MappedPoint\x12\x14\n\x0cnum_reducers\x18\x02 \x01(\x05\"\"\n\x0fPartitionOutput\x12\x0f\n\x07success\x18\x01 \x01(\x08\"L\n\x0bReduceInput\x12\x18\n\x0b\x63\x65ntroid_id\x18\x01 \x01(\x05H\x00\x88\x01\x01\x12\x13\n\x0bnum_mappers\x18\x02 \x01(\x05\x42\x0e\n\x0c_centroid_id\"]\n\x0cReduceOutput\x12\x13\n\x0b\x63\x65ntroid_id\x18\x01 \x01(\x05\x12\'\n\x10updated_centroid\x18\x02 \x01(\x0b\x32\r.kmeans.Point\x12\x0f\n\x07success\x18\x03 \x01(\x08\"H\n\x18\x43\x65ntroidCompilationInput\x12,\n\x0ereduce_outputs\x18\x01 \x03(\x0b\x32\x14.kmeans.ReduceOutput\"=\n\x19\x43\x65ntroidCompilationOutput\x12 \n\tcentroids\x18\x01 \x03(\x0b\x32\r.kmeans.Point\"3\n\x14MapperToReducerInput\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\x12\n\n\x02id\x18\x02 \x01(\t\"C\n\x15MapperToReducerOutput\x12*\n\rmapped_points\x18\x01 \x03(\x0b\x32\x13.kmeans.MappedPoint2\x9b\x03\n\x06KMeans\x12?\n\x03Run\x12\x13.kmeans.MasterInput\x1a!.kmeans.CentroidCompilationOutput\"\x00\x12,\n\x03Map\x12\x10.kmeans.MapInput\x1a\x11.kmeans.MapOutput\"\x00\x12>\n\tPartition\x12\x16.kmeans.PartitionInput\x1a\x17.kmeans.PartitionOutput\"\x00\x12\x35\n\x06Reduce\x12\x13.kmeans.ReduceInput\x1a\x14.kmeans.ReduceOutput\"\x00\x12Y\n\x10\x43ompileCentroids\x12 .kmeans.CentroidCompilationInput\x1a!.kmeans.CentroidCompilationOutput\"\x00\x12P\n\x0fMapperToReducer\x12\x1c.kmeans.MapperToReducerInput\x1a\x1d.kmeans.MapperToReducerOutput\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'kmeans_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_MASTERINPUT']._serialized_start=24
  _globals['_MASTERINPUT']._serialized_end=127
  _globals['_INPUTSPLIT']._serialized_start=129
  _globals['_INPUTSPLIT']._serialized_end=181
  _globals['_POINT']._serialized_start=183
  _globals['_POINT']._serialized_end=212
  _globals['_MAPINPUT']._serialized_start=214
  _globals['_MAPINPUT']._serialized_end=299
  _globals['_MAPPEDPOINT']._serialized_start=301
  _globals['_MAPPEDPOINT']._serialized_end=388
  _globals['_MAPOUTPUT']._serialized_start=390
  _globals['_MAPOUTPUT']._serialized_end=445
  _globals['_PARTITIONINPUT']._serialized_start=447
  _globals['_PARTITIONINPUT']._serialized_end=529
  _globals['_PARTITIONOUTPUT']._serialized_start=531
  _globals['_PARTITIONOUTPUT']._serialized_end=565
  _globals['_REDUCEINPUT']._serialized_start=567
  _globals['_REDUCEINPUT']._serialized_end=643
  _globals['_REDUCEOUTPUT']._serialized_start=645
  _globals['_REDUCEOUTPUT']._serialized_end=738
  _globals['_CENTROIDCOMPILATIONINPUT']._serialized_start=740
  _globals['_CENTROIDCOMPILATIONINPUT']._serialized_end=812
  _globals['_CENTROIDCOMPILATIONOUTPUT']._serialized_start=814
  _globals['_CENTROIDCOMPILATIONOUTPUT']._serialized_end=875
  _globals['_MAPPERTOREDUCERINPUT']._serialized_start=877
  _globals['_MAPPERTOREDUCERINPUT']._serialized_end=928
  _globals['_MAPPERTOREDUCEROUTPUT']._serialized_start=930
  _globals['_MAPPERTOREDUCEROUTPUT']._serialized_end=997
  _globals['_KMEANS']._serialized_start=1000
  _globals['_KMEANS']._serialized_end=1411
# @@protoc_insertion_point(module_scope)
