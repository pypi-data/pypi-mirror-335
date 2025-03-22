from tracdap.rt._impl.grpc.tracdap.metadata import object_id_pb2 as _object_id_pb2
from tracdap.rt._impl.grpc.tracdap.metadata import job_pb2 as _job_pb2
from tracdap.rt._impl.grpc.tracdap.metadata import object_pb2 as _object_pb2
from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RuntimeListJobsRequest(_message.Message):
    __slots__ = ("limit",)
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    limit: int
    def __init__(self, limit: _Optional[int] = ...) -> None: ...

class RuntimeListJobsResponse(_message.Message):
    __slots__ = ("jobs",)
    JOBS_FIELD_NUMBER: _ClassVar[int]
    jobs: _containers.RepeatedCompositeFieldContainer[RuntimeJobStatus]
    def __init__(self, jobs: _Optional[_Iterable[_Union[RuntimeJobStatus, _Mapping]]] = ...) -> None: ...

class RuntimeJobInfoRequest(_message.Message):
    __slots__ = ("jobSelector", "jobKey")
    JOBSELECTOR_FIELD_NUMBER: _ClassVar[int]
    JOBKEY_FIELD_NUMBER: _ClassVar[int]
    jobSelector: _object_id_pb2.TagSelector
    jobKey: str
    def __init__(self, jobSelector: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ..., jobKey: _Optional[str] = ...) -> None: ...

class RuntimeJobStatus(_message.Message):
    __slots__ = ("jobId", "statusCode", "statusMessage", "errorDetail")
    JOBID_FIELD_NUMBER: _ClassVar[int]
    STATUSCODE_FIELD_NUMBER: _ClassVar[int]
    STATUSMESSAGE_FIELD_NUMBER: _ClassVar[int]
    ERRORDETAIL_FIELD_NUMBER: _ClassVar[int]
    jobId: _object_id_pb2.TagHeader
    statusCode: _job_pb2.JobStatusCode
    statusMessage: str
    errorDetail: str
    def __init__(self, jobId: _Optional[_Union[_object_id_pb2.TagHeader, _Mapping]] = ..., statusCode: _Optional[_Union[_job_pb2.JobStatusCode, str]] = ..., statusMessage: _Optional[str] = ..., errorDetail: _Optional[str] = ...) -> None: ...

class RuntimeJobResult(_message.Message):
    __slots__ = ("jobId", "statusCode", "statusMessage", "results")
    class ResultsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _object_pb2.ObjectDefinition
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_object_pb2.ObjectDefinition, _Mapping]] = ...) -> None: ...
    JOBID_FIELD_NUMBER: _ClassVar[int]
    STATUSCODE_FIELD_NUMBER: _ClassVar[int]
    STATUSMESSAGE_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    jobId: _object_id_pb2.TagHeader
    statusCode: _job_pb2.JobStatusCode
    statusMessage: str
    results: _containers.MessageMap[str, _object_pb2.ObjectDefinition]
    def __init__(self, jobId: _Optional[_Union[_object_id_pb2.TagHeader, _Mapping]] = ..., statusCode: _Optional[_Union[_job_pb2.JobStatusCode, str]] = ..., statusMessage: _Optional[str] = ..., results: _Optional[_Mapping[str, _object_pb2.ObjectDefinition]] = ...) -> None: ...
