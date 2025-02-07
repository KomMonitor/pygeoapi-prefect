"""Schemas used internally by the process manager."""

import datetime as dt
import enum
from typing import Any, Dict, List, Optional, Union

import pydantic

from pygeoapi.util import JobStatus


class Link(pydantic.BaseModel):
    href: str
    type_: Optional[str] = pydantic.Field(None, alias="type")
    rel: Optional[str] = None
    title: Optional[str] = None
    href_lang: Optional[str] = pydantic.Field(None, alias="hreflang")

    def as_link_header(self) -> str:
        result = f"<{self.href}>"
        fields = (
            "rel",
            "title",
            "type_",
            "href_lang",
        )
        for field_name in fields:
            value = getattr(self, field_name, None)
            if value is not None:
                fragment = f'{self.model_fields[field_name].alias}="{value}"'
                result = "; ".join((result, fragment))
        return result


class ProcessExecutionMode(enum.Enum):
    sync_execute = "sync-execute"
    async_execute = "async-execute"


class RequestedProcessExecutionMode(enum.Enum):
    wait = "wait"
    respond_async = "respond-async"


class ProcessOutputTransmissionMode(enum.Enum):
    VALUE = "value"
    REFERENCE = "reference"


class ProcessResponseType(enum.Enum):
    document = "document"
    raw = "raw"


class ProcessJobControlOption(enum.Enum):
    SYNC_EXECUTE = "sync-execute"
    ASYNC_EXECUTE = "async-execute"
    DISMISS = "dismiss"


class ProcessIOType(enum.Enum):
    ARRAY = "array"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    NUMBER = "number"
    OBJECT = "object"
    STRING = "string"


class ProcessIOFormat(enum.Enum):
    # this is built from:
    # - the jsonschema spec at: https://json-schema.org/draft/2020-12/json-schema-validation.html#name-defined-formats  # noqa: E501
    # - the OAPI - Processes spec (table 13) at: https://docs.ogc.org/is/18-062r2/18-062r2.html#ogc_process_description  # noqa: E501
    DATE_TIME = "date-time"
    DATE = "date"
    TIME = "time"
    DURATION = "duration"
    EMAIL = "email"
    HOSTNAME = "hostname"
    IPV4 = "ipv4"
    IPV6 = "ipv6"
    URI = "uri"
    URI_REFERENCE = "uri-reference"
    # left out `iri` and `iri-reference` as valid URIs are also valid IRIs
    UUID = "uuid"
    URI_TEMPLATE = "uri-template"
    JSON_POINTER = "json-pointer"
    RELATIVE_JSON_POINTER = "relative-json-pointer"
    REGEX = "regex"
    # the below `binary` entry does not seem to be defined in the jsonschema spec  # noqa: E501
    # nor in OAPI - Processes - but it is mentioned in OAPI - Processes spec as an example  # noqa: E501
    BINARY = "binary"
    GEOJSON_FEATURE_COLLECTION_URI = (
        "http://www.opengis.net/def/format/ogcapi-processes/0/"
        "geojson-feature-collection"
    )
    GEOJSON_FEATURE_URI = (
        "http://www.opengis.net/def/format/ogcapi-processes/0/geojson-feature"
    )
    GEOJSON_GEOMETRY_URI = (
        "http://www.opengis.net/def/format/ogcapi-processes/0/" "geojson-geometry"
    )
    OGC_BBOX_URI = "http://www.opengis.net/def/format/ogcapi-processes/0/ogc-bbox"
    GEOJSON_FEATURE_COLLECTION_SHORT_CODE = "geojson-feature-collection"
    GEOJSON_FEATURE_SHORT_CODE = "geojson-feature"
    GEOJSON_GEOMETRY_SHORT_CODE = "geojson-geometry"
    OGC_BBOX_SHORT_CODE = "ogc-bbox"


# this is a 'pydantification' of the schema.yml fragment, as shown
# on the OAPI - Processes spec
class ProcessIOSchema(pydantic.BaseModel):
    title: Optional[str] = None
    multiple_of: Optional[float] = pydantic.Field(None, alias="multipleOf")
    maximum: Optional[float] = None
    exclusive_maximum: Optional[bool] = pydantic.Field(False, alias="exclusiveMaximum")
    minimum: Optional[float] = None
    exclusive_minimum: Optional[bool] = pydantic.Field(False, alias="exclusiveMinimum")
    max_length: int = pydantic.Field(None, ge=0, alias="maxLength")
    min_length: int = pydantic.Field(0, ge=0, alias="minLength")
    pattern: Optional[str] = None
    max_items: Optional[int] = pydantic.Field(None, ge=0, alias="maxItems")
    min_items: Optional[int] = pydantic.Field(0, ge=0, alias="minItems")
    unique_items: Optional[bool] = pydantic.Field(False, alias="uniqueItems")
    max_properties: Optional[int] = pydantic.Field(None, ge=0, alias="maxProperties")
    min_properties: Optional[int] = pydantic.Field(0, ge=0, alias="minProperties")
    required: Optional[  # type: ignore [valid-type]
        pydantic.conset(str, min_length=1)
    ] = None
    enum: Optional[  # type: ignore [valid-type]
        pydantic.conset(Any, min_length=1)
    ] = None
    type_: Optional[ProcessIOType] = pydantic.Field(None, alias="type")
    not_: Optional["ProcessIOSchema"] = pydantic.Field(None, alias="not")
    allOf: Optional[List["ProcessIOSchema"]] = None
    oneOf: Optional[List["ProcessIOSchema"]] = None
    anyOf: Optional[List["ProcessIOSchema"]] = None
    items: Optional[List["ProcessIOSchema"]] = None
    properties: Optional["ProcessIOSchema"] = None
    additional_properties: Optional[Union[bool, "ProcessIOSchema"]] = pydantic.Field(
        True, alias="additionalProperties"
    )
    description: Optional[str] = None
    format_: Optional[ProcessIOFormat] = pydantic.Field(None, alias="format")
    default: Optional[pydantic.Json[dict]] = None
    nullable: Optional[bool] = False
    read_only: Optional[bool] = pydantic.Field(False, alias="readOnly")
    write_only: Optional[bool] = pydantic.Field(False, alias="writeOnly")
    example: Optional[pydantic.Json[dict]] = None
    deprecated: Optional[bool] = False
    content_media_type: Optional[str] = pydantic.Field(None, alias="contentMediaType")
    content_encoding: Optional[str] = pydantic.Field(None, alias="contentEncoding")
    content_schema: Optional[str] = pydantic.Field(None, alias="contentSchema")

    class Config:
        use_enum_values = True


class ProcessOutput(pydantic.BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    schema_: ProcessIOSchema = pydantic.Field(alias="schema")


class ProcessMetadata(pydantic.BaseModel):
    title: Optional[str] = None
    role: Optional[str] = None
    href: Optional[str] = None


class AdditionalProcessIOParameters(ProcessMetadata):
    name: str
    value: List[Union[str, float, int, List[Dict], Dict]]

    class Config:
        pass


class ProcessInput(ProcessOutput):
    keywords: Optional[List[str]] = None
    metadata: Optional[List[ProcessMetadata]] = None
    min_occurs: int = pydantic.Field(1, alias="minOccurs")
    max_occurs: Optional[Union[int, str]] = pydantic.Field(1, alias="maxOccurs")
    additional_parameters: Optional[AdditionalProcessIOParameters] = None


class ProcessSummary(pydantic.BaseModel):
    version: str
    id: str
    title: Optional[Union[Dict[str, str], str]] = None
    description: Optional[Union[Dict[str, str], str]] = None
    keywords: Optional[List[str]] = None
    job_control_options: Optional[List[ProcessJobControlOption]] = pydantic.Field(
        [ProcessJobControlOption.SYNC_EXECUTE], alias="jobControlOptions"
    )
    output_transmission: Optional[List[ProcessOutputTransmissionMode]] = pydantic.Field(
        [ProcessOutputTransmissionMode.VALUE], alias="outputTransmission"
    )
    links: Optional[List[Link]] = None

    class Config:
        use_enum_values = True


class ProcessDescription(ProcessSummary):
    inputs: Dict[str, ProcessInput]
    outputs: Dict[str, ProcessOutput]
    example: Optional[dict]


class ExecutionInputBBox(pydantic.BaseModel):
    bbox: List[float] = pydantic.Field(..., min_length=4, max_length=4)
    crs: Optional[str] = "http://www.opengis.net/def/crs/OGC/1.3/CRS84"


class ExecutionInputValueNoObjectArray(pydantic.RootModel):
    root: List[
        Union[ExecutionInputBBox, int, str, "ExecutionInputValueNoObjectArray"]
    ]


class ExecutionInputValueNoObject(pydantic.RootModel):
    """Models the `inputValueNoObject.yml` schema defined in OAPIP."""

    root: Union[
        ExecutionInputBBox,
        bool,
        float,
        int,
        ExecutionInputValueNoObjectArray,
        str,
    ]


class ExecutionFormat(pydantic.BaseModel):
    """Models the `format.yml` schema defined in OAPIP."""

    media_type: Optional[str] = pydantic.Field(None, alias="mediaType")
    encoding: Optional[str]
    schema_: Optional[Union[str, dict]] = pydantic.Field(None, alias="schema")


class ExecutionQualifiedInputValue(pydantic.BaseModel):
    """Models the `qualifiedInputValue.yml` schema defined in OAPIP."""

    value: Union[ExecutionInputValueNoObject, dict]
    format_: Optional[ExecutionFormat] = None


class ExecutionOutput(pydantic.BaseModel):
    """Models the `output.yml` schema defined in OAPIP."""

    format_: Optional[ExecutionFormat] = pydantic.Field(None, alias="format")
    transmission_mode: Optional[ProcessOutputTransmissionMode] = pydantic.Field(
        ProcessOutputTransmissionMode.VALUE.value, alias="transmissionMode"
    )

    class Config:
        use_enum_values = True


class ExecutionSubscriber(pydantic.BaseModel):
    """Models the `subscriber.yml` schema defined in OAPIP."""

    success_uri: str = pydantic.Field(..., alias="successUri")
    in_progress_uri: Optional[str] = pydantic.Field(None, alias="inProgressUri")
    failed_uri: Optional[str] = pydantic.Field(None, alias="failedUri")


class ExecuteRequest(pydantic.BaseModel):
    """Models the `execute.yml` schema defined in OAPIP."""

    inputs: Optional[
        Dict[
            str,
            Union[
                ExecutionInputValueNoObject,
                ExecutionQualifiedInputValue,
                Link,
                List[
                    Union[
                        ExecutionInputValueNoObject,
                        ExecutionQualifiedInputValue,
                        Link,
                    ]
                ],
            ],
        ]
    ] = None
    outputs: Optional[Dict[str, ExecutionOutput]] = None
    response: Optional[ProcessResponseType] = ProcessResponseType.raw
    subscriber: Optional[ExecutionSubscriber] = None

    # Custom additional properties not strictly specified by OAPIP
    properties: Dict[str, Any] = {}

    class Config:
        use_enum_values = True


class OutputExecutionResultInternal(pydantic.BaseModel):
    location: str
    media_type: str


class ExecutionDocumentSingleOutput(pydantic.RootModel):
    root: Union[
        ExecutionInputValueNoObject,
        ExecutionQualifiedInputValue,
        Link,
    ]


class ExecutionDocumentResult(pydantic.RootModel):
    root: Dict[str, ExecutionDocumentSingleOutput]


class JobStatusInfoBase(pydantic.BaseModel):
    job_id: str = pydantic.Field(..., alias="jobID")
    process_id: Optional[str] = pydantic.Field(None, alias="processID")
    status: JobStatus
    message: Optional[str] = None
    created: Optional[dt.datetime] = None
    started: Optional[dt.datetime] = None
    finished: Optional[dt.datetime] = None
    updated: Optional[dt.datetime] = None
    progress: Optional[int] = pydantic.Field(None, ge=0, le=100)


class JobStatusInfoInternal(JobStatusInfoBase):
    negotiated_execution_mode: Optional[ProcessExecutionMode] = None
    requested_response_type: Optional[ProcessResponseType] = None
    requested_outputs: Optional[Dict[str, ExecutionOutput]] = None
    generated_outputs: Optional[Dict[str, Any]] = None
