from spiral.proto._ import scandal as scandal_

from spiral.proto._.scandal import (
    Connectivity,
    Delete,
    DeleteRequest,
    DeleteResponse,
    Fetch,
    FetchRequest,
    FetchResponse,
    Metadata,
    MetadataParquet,
    Put,
    PutRequest,
    PutResponse,
    ScandalServiceStub,
    ScandalServiceBase,
    ServiceBase,
    Sink,
    Source,
)

__all__ = [
    "Connectivity",
    "Delete",
    "DeleteRequest",
    "DeleteResponse",
    "Fetch",
    "FetchRequest",
    "FetchResponse",
    "Metadata",
    "MetadataParquet",
    "Put",
    "PutRequest",
    "PutResponse",
    "ScandalServiceStub",
    "ScandalServiceBase",
    "ServiceBase",
    "Sink",
    "Source",
]

from spiral.proto.util import patch_protos

patch_protos(scandal_, globals())
