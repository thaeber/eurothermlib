# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: service.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rservice.proto\x1a\x1fgoogle/protobuf/timestamp.proto\"\x07\n\x05\x45mpty\"\r\n\x0bStopRequest\"\x1c\n\x1aStreamProcessValuesRequest\"-\n\x17GetProcessValuesRequest\x12\x12\n\ndeviceName\x18\x01 \x01(\t\"\xfd\x01\n\rProcessValues\x12\x12\n\ndeviceName\x18\x01 \x01(\t\x12-\n\ttimestamp\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x0e\n\x06status\x18\x03 \x01(\x05\x12\x14\n\x0cprocessValue\x18\x04 \x01(\x01\x12\x10\n\x08setpoint\x18\x05 \x01(\x01\x12\x17\n\x0fworkingSetpoint\x18\x06 \x01(\x01\x12\x16\n\x0eremoteSetpoint\x18\x07 \x01(\x01\x12\x15\n\rworkingOutput\x18\x08 \x01(\x01\x12)\n\nrampStatus\x18\t \x01(\x0e\x32\x15.TemperatureRampState\"V\n\x1bToggleRemoteSetpointRequest\x12\x12\n\ndeviceName\x18\x01 \x01(\t\x12#\n\x05state\x18\x02 \x01(\x0e\x32\x14.RemoteSetpointState\"=\n\x18SetRemoteSetpointRequest\x12\x12\n\ndeviceName\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x01\"O\n\x1bStartTemperatureRampRequest\x12\x12\n\ndeviceName\x18\x01 \x01(\t\x12\x0e\n\x06target\x18\x02 \x01(\x01\x12\x0c\n\x04rate\x18\x03 \x01(\x01\";\n\x14TemperatureRampValue\x12\x12\n\ndeviceName\x18\x01 \x01(\t\x12\x0f\n\x07\x63urrent\x18\x02 \x01(\x01\"0\n\x1aStopTemperatureRampRequest\x12\x12\n\ndeviceName\x18\x01 \x01(\t\"1\n\x1b\x41\x63knowlegdeAllAlarmsRequest\x12\x12\n\ndeviceName\x18\x01 \x01(\t*k\n\x14TemperatureRampState\x12\x0e\n\nTRS_NORAMP\x10\x00\x12\x0f\n\x0bTRS_RAMPING\x10\x01\x12\x0f\n\x0bTRS_HOLDING\x10\x02\x12\x0f\n\x0bTRS_STOPPED\x10\x03\x12\x10\n\x0cTRS_FINISHED\x10\x04*0\n\x13RemoteSetpointState\x12\x0c\n\x08\x44ISABLED\x10\x00\x12\x0b\n\x07\x45NABLED\x10\x01\x32\xa9\x04\n\tEurotherm\x12$\n\nStopServer\x12\x0c.StopRequest\x1a\x06.Empty\"\x00\x12%\n\x11ServerHealthCheck\x12\x06.Empty\x1a\x06.Empty\"\x00\x12\x46\n\x13StreamProcessValues\x12\x1b.StreamProcessValuesRequest\x1a\x0e.ProcessValues\"\x00\x30\x01\x12>\n\x10GetProcessValues\x12\x18.GetProcessValuesRequest\x1a\x0e.ProcessValues\"\x00\x12>\n\x14ToggleRemoteSetpoint\x12\x1c.ToggleRemoteSetpointRequest\x1a\x06.Empty\"\x00\x12\x38\n\x11SetRemoteSetpoint\x12\x19.SetRemoteSetpointRequest\x1a\x06.Empty\"\x00\x12O\n\x14StartTemperatureRamp\x12\x1c.StartTemperatureRampRequest\x1a\x15.TemperatureRampValue\"\x00\x30\x01\x12<\n\x13StopTemperatureRamp\x12\x1b.StopTemperatureRampRequest\x1a\x06.Empty\"\x00\x12>\n\x14\x41\x63knowledgeAllAlarms\x12\x1c.AcknowlegdeAllAlarmsRequest\x1a\x06.Empty\"\x00\x42\x03\x90\x01\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\220\001\001'
  _globals['_TEMPERATURERAMPSTATE']._serialized_start=801
  _globals['_TEMPERATURERAMPSTATE']._serialized_end=908
  _globals['_REMOTESETPOINTSTATE']._serialized_start=910
  _globals['_REMOTESETPOINTSTATE']._serialized_end=958
  _globals['_EMPTY']._serialized_start=50
  _globals['_EMPTY']._serialized_end=57
  _globals['_STOPREQUEST']._serialized_start=59
  _globals['_STOPREQUEST']._serialized_end=72
  _globals['_STREAMPROCESSVALUESREQUEST']._serialized_start=74
  _globals['_STREAMPROCESSVALUESREQUEST']._serialized_end=102
  _globals['_GETPROCESSVALUESREQUEST']._serialized_start=104
  _globals['_GETPROCESSVALUESREQUEST']._serialized_end=149
  _globals['_PROCESSVALUES']._serialized_start=152
  _globals['_PROCESSVALUES']._serialized_end=405
  _globals['_TOGGLEREMOTESETPOINTREQUEST']._serialized_start=407
  _globals['_TOGGLEREMOTESETPOINTREQUEST']._serialized_end=493
  _globals['_SETREMOTESETPOINTREQUEST']._serialized_start=495
  _globals['_SETREMOTESETPOINTREQUEST']._serialized_end=556
  _globals['_STARTTEMPERATURERAMPREQUEST']._serialized_start=558
  _globals['_STARTTEMPERATURERAMPREQUEST']._serialized_end=637
  _globals['_TEMPERATURERAMPVALUE']._serialized_start=639
  _globals['_TEMPERATURERAMPVALUE']._serialized_end=698
  _globals['_STOPTEMPERATURERAMPREQUEST']._serialized_start=700
  _globals['_STOPTEMPERATURERAMPREQUEST']._serialized_end=748
  _globals['_ACKNOWLEGDEALLALARMSREQUEST']._serialized_start=750
  _globals['_ACKNOWLEGDEALLALARMSREQUEST']._serialized_end=799
  _globals['_EUROTHERM']._serialized_start=961
  _globals['_EUROTHERM']._serialized_end=1514
_builder.BuildServices(DESCRIPTOR, 'service_pb2', _globals)
# @@protoc_insertion_point(module_scope)
