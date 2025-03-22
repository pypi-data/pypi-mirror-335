from tracdap.rt._impl.grpc.tracdap.metadata import type_pb2 as _type_pb2
from tracdap.rt._impl.grpc.tracdap.metadata import object_id_pb2 as _object_id_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SchemaType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SCHEMA_TYPE_NOT_SET: _ClassVar[SchemaType]
    TABLE: _ClassVar[SchemaType]
    STRUCT: _ClassVar[SchemaType]

class PartType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PART_ROOT: _ClassVar[PartType]
    PART_BY_RANGE: _ClassVar[PartType]
    PART_BY_VALUE: _ClassVar[PartType]
SCHEMA_TYPE_NOT_SET: SchemaType
TABLE: SchemaType
STRUCT: SchemaType
PART_ROOT: PartType
PART_BY_RANGE: PartType
PART_BY_VALUE: PartType

class FieldSchema(_message.Message):
    __slots__ = ("fieldName", "fieldOrder", "fieldType", "label", "businessKey", "categorical", "notNull", "formatCode")
    FIELDNAME_FIELD_NUMBER: _ClassVar[int]
    FIELDORDER_FIELD_NUMBER: _ClassVar[int]
    FIELDTYPE_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    BUSINESSKEY_FIELD_NUMBER: _ClassVar[int]
    CATEGORICAL_FIELD_NUMBER: _ClassVar[int]
    NOTNULL_FIELD_NUMBER: _ClassVar[int]
    FORMATCODE_FIELD_NUMBER: _ClassVar[int]
    fieldName: str
    fieldOrder: int
    fieldType: _type_pb2.BasicType
    label: str
    businessKey: bool
    categorical: bool
    notNull: bool
    formatCode: str
    def __init__(self, fieldName: _Optional[str] = ..., fieldOrder: _Optional[int] = ..., fieldType: _Optional[_Union[_type_pb2.BasicType, str]] = ..., label: _Optional[str] = ..., businessKey: bool = ..., categorical: bool = ..., notNull: bool = ..., formatCode: _Optional[str] = ...) -> None: ...

class TableSchema(_message.Message):
    __slots__ = ("fields",)
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    fields: _containers.RepeatedCompositeFieldContainer[FieldSchema]
    def __init__(self, fields: _Optional[_Iterable[_Union[FieldSchema, _Mapping]]] = ...) -> None: ...

class StructField(_message.Message):
    __slots__ = ("fieldType", "label", "businessKey", "categorical", "notNull", "formatCode", "defaultValue", "structType")
    FIELDTYPE_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    BUSINESSKEY_FIELD_NUMBER: _ClassVar[int]
    CATEGORICAL_FIELD_NUMBER: _ClassVar[int]
    NOTNULL_FIELD_NUMBER: _ClassVar[int]
    FORMATCODE_FIELD_NUMBER: _ClassVar[int]
    DEFAULTVALUE_FIELD_NUMBER: _ClassVar[int]
    STRUCTTYPE_FIELD_NUMBER: _ClassVar[int]
    fieldType: _type_pb2.TypeDescriptor
    label: str
    businessKey: bool
    categorical: bool
    notNull: bool
    formatCode: str
    defaultValue: _type_pb2.Value
    structType: str
    def __init__(self, fieldType: _Optional[_Union[_type_pb2.TypeDescriptor, _Mapping]] = ..., label: _Optional[str] = ..., businessKey: bool = ..., categorical: bool = ..., notNull: bool = ..., formatCode: _Optional[str] = ..., defaultValue: _Optional[_Union[_type_pb2.Value, _Mapping]] = ..., structType: _Optional[str] = ...) -> None: ...

class StructSchema(_message.Message):
    __slots__ = ("fields", "namedTypes")
    class FieldsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: StructField
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[StructField, _Mapping]] = ...) -> None: ...
    class NamedTypesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: StructSchema
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[StructSchema, _Mapping]] = ...) -> None: ...
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    NAMEDTYPES_FIELD_NUMBER: _ClassVar[int]
    fields: _containers.MessageMap[str, StructField]
    namedTypes: _containers.MessageMap[str, StructSchema]
    def __init__(self, fields: _Optional[_Mapping[str, StructField]] = ..., namedTypes: _Optional[_Mapping[str, StructSchema]] = ...) -> None: ...

class SchemaDefinition(_message.Message):
    __slots__ = ("schemaType", "partType", "table", "struct")
    SCHEMATYPE_FIELD_NUMBER: _ClassVar[int]
    PARTTYPE_FIELD_NUMBER: _ClassVar[int]
    TABLE_FIELD_NUMBER: _ClassVar[int]
    STRUCT_FIELD_NUMBER: _ClassVar[int]
    schemaType: SchemaType
    partType: PartType
    table: TableSchema
    struct: StructSchema
    def __init__(self, schemaType: _Optional[_Union[SchemaType, str]] = ..., partType: _Optional[_Union[PartType, str]] = ..., table: _Optional[_Union[TableSchema, _Mapping]] = ..., struct: _Optional[_Union[StructSchema, _Mapping]] = ...) -> None: ...

class PartKey(_message.Message):
    __slots__ = ("opaqueKey", "partType", "partValues", "partRangeMin", "partRangeMax")
    OPAQUEKEY_FIELD_NUMBER: _ClassVar[int]
    PARTTYPE_FIELD_NUMBER: _ClassVar[int]
    PARTVALUES_FIELD_NUMBER: _ClassVar[int]
    PARTRANGEMIN_FIELD_NUMBER: _ClassVar[int]
    PARTRANGEMAX_FIELD_NUMBER: _ClassVar[int]
    opaqueKey: str
    partType: PartType
    partValues: _containers.RepeatedCompositeFieldContainer[_type_pb2.Value]
    partRangeMin: _type_pb2.Value
    partRangeMax: _type_pb2.Value
    def __init__(self, opaqueKey: _Optional[str] = ..., partType: _Optional[_Union[PartType, str]] = ..., partValues: _Optional[_Iterable[_Union[_type_pb2.Value, _Mapping]]] = ..., partRangeMin: _Optional[_Union[_type_pb2.Value, _Mapping]] = ..., partRangeMax: _Optional[_Union[_type_pb2.Value, _Mapping]] = ...) -> None: ...

class DataDefinition(_message.Message):
    __slots__ = ("schemaId", "schema", "parts", "storageId")
    class Delta(_message.Message):
        __slots__ = ("deltaIndex", "dataItem")
        DELTAINDEX_FIELD_NUMBER: _ClassVar[int]
        DATAITEM_FIELD_NUMBER: _ClassVar[int]
        deltaIndex: int
        dataItem: str
        def __init__(self, deltaIndex: _Optional[int] = ..., dataItem: _Optional[str] = ...) -> None: ...
    class Snap(_message.Message):
        __slots__ = ("snapIndex", "deltas")
        SNAPINDEX_FIELD_NUMBER: _ClassVar[int]
        DELTAS_FIELD_NUMBER: _ClassVar[int]
        snapIndex: int
        deltas: _containers.RepeatedCompositeFieldContainer[DataDefinition.Delta]
        def __init__(self, snapIndex: _Optional[int] = ..., deltas: _Optional[_Iterable[_Union[DataDefinition.Delta, _Mapping]]] = ...) -> None: ...
    class Part(_message.Message):
        __slots__ = ("partKey", "snap")
        PARTKEY_FIELD_NUMBER: _ClassVar[int]
        SNAP_FIELD_NUMBER: _ClassVar[int]
        partKey: PartKey
        snap: DataDefinition.Snap
        def __init__(self, partKey: _Optional[_Union[PartKey, _Mapping]] = ..., snap: _Optional[_Union[DataDefinition.Snap, _Mapping]] = ...) -> None: ...
    class PartsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: DataDefinition.Part
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[DataDefinition.Part, _Mapping]] = ...) -> None: ...
    SCHEMAID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    PARTS_FIELD_NUMBER: _ClassVar[int]
    STORAGEID_FIELD_NUMBER: _ClassVar[int]
    schemaId: _object_id_pb2.TagSelector
    schema: SchemaDefinition
    parts: _containers.MessageMap[str, DataDefinition.Part]
    storageId: _object_id_pb2.TagSelector
    def __init__(self, schemaId: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ..., schema: _Optional[_Union[SchemaDefinition, _Mapping]] = ..., parts: _Optional[_Mapping[str, DataDefinition.Part]] = ..., storageId: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ...) -> None: ...
