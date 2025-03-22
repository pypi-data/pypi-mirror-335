import datetime
import enum
import uuid
from typing import Literal

from pydantic import AwareDatetime, BaseModel, Field, model_validator


class DatasetType(str, enum.Enum):
    RASTER = "raster"
    VECTOR = "vector"


class VersionCheckResponse(BaseModel):
    is_supported: bool
    newest_supported_version: int

    is_deprecated: bool = False
    will_be_removed_after: datetime.date | None = None
    deprecation_message: str | None = None


class DatasetLabel(BaseModel):
    """Dataset attribute as a key-value pair"""

    name: str
    value: str


class SimpleDatasetMetadata(BaseModel):
    """Simplified metadata with only essential fields"""

    description: str | None = None
    thumbnail_url: str | None = None
    attributes: list[DatasetLabel] = Field(default_factory=list)
    license: str | None = None


class FilenameBandPattern(BaseModel):
    """Pattern for mapping filename patterns to band names"""

    pattern: str
    band: str


class BaseAddDatasetRequest(BaseModel):
    """Base class for all dataset add requests with shared fields"""

    name: str = Field(
        description="The name of the dataset",
        examples=["my_dataset"],
    )
    labels: list[DatasetLabel] | None = Field(
        description="User-defined labels to add to the dataset",
        examples=[{"name": "key", "value": "value"}],
        default=None,
    )
    visualization_optimization: bool | Literal["auto"] = Field(
        description=(
            "Whether to optimize the dataset for visualization. If set to 'auto', "
            "the dataset will be optimized if it is small enough."
        ),
        examples=["auto"],
        default="auto",
    )
    pixel_info_optimizations: list[str] = Field(
        description=(
            "List of dimensions to optimize for the pixel info API. This is useful to "
            "quickly retrieve all values of a dimension for a given pixel, e.g. "
            "a time series."
        ),
        examples=[["time"]],
        default_factory=list,
    )


class AddImageDatasetRequest(BaseAddDatasetRequest):
    """Request to add an image dataset"""

    type: Literal["image"] = "image"
    urls: list[str] = Field(
        description=(
            "List of URLs or wildcards to the image files. "
            "Wildcards are supported using the * character. "
            "e.g. gs://example-bucket/image_*.tif"
        ),
        examples=["gs://example-bucket/image_*.tif"],
    )
    bands: list[str] | None = Field(
        description=(
            "List of bands to add to the dataset. If not provided, all bands will be "
            "added."
        ),
        examples=[["band1", "band2"]],
        default=None,
    )
    groupby: str | None = Field(
        description=(
            "Dimension to group the dataset by. Follows ODC's groupby convention."
        ),
        examples=["time"],
        default=None,
    )
    filename_date_pattern: str | None = Field(
        description="Pattern to extract the date from the filename.",
        examples=["%Y-%m-%d"],
        default=None,
    )
    filename_band_pattern: list[FilenameBandPattern] | None = Field(
        description="Pattern to extract the band from the filename.",
        examples=[{"pattern": "image_*.tif", "band": "band1"}],
        default=None,
    )


class AddZarrDatasetRequest(BaseAddDatasetRequest):
    """Request to add a Zarr dataset"""

    type: Literal["zarr"] = "zarr"
    urls: list[str] = Field(
        description=(
            "List of URLs to the Zarr files. Currently only supports 1 URL. "
            "Can contain a placeholder for the dimension name. If specified, this "
            "concatenates multiple Zarrs along either an existing or new dimension "
            "as named in the pattern."
        ),
        examples=["gs://example-bucket/image.zarr", "gs://example-bucket/{time}.zarr"],
    )
    rename: dict[str, str] | None = None

    @model_validator(mode="after")
    def check_only_one_url_for_now(self) -> "AddZarrDatasetRequest":
        if len(self.urls) > 1:
            raise ValueError("Only one URL is supported for now")
        return self


class AddVectorDatasetRequest(BaseAddDatasetRequest):
    """Request to add a vector dataset"""

    type: Literal["vector"] = "vector"
    url: str = Field(
        description="URL to the vector dataset.",
        examples=["https://example.com/vector.geojson"],
    )


class AddTileServerDatasetRequest(BaseAddDatasetRequest):
    type: Literal["tileserver"] = "tileserver"
    url: str = Field(
        description="URL to an XYZ tile server.",
        examples=["https://example.com/tileserver/{z}/{x}/{y}.png"],
    )


AddDatasetRequest = (
    AddImageDatasetRequest
    | AddZarrDatasetRequest
    | AddVectorDatasetRequest
    | AddTileServerDatasetRequest
)


class AddDatasetResponse(BaseModel):
    dataset_id: uuid.UUID
    """Dataset ID of the newly created dataset"""


class DatasetOverviewsStatus(BaseModel):
    status: str
    """Status of the dataset overview generation. One of:
    - "not_started": Overview generation has not started yet
    - "pending": Overview generation is pending
    - "running": Overview generation is running
    - "success": Overview generation has completed successfully
    - "error": Overview generation has failed
    """
    updated_at: datetime.datetime | None = None
    """Timestamp of the last update to the status"""


OptimizationStatus = Literal[
    "not_started",
    "pending",
    "running",
    "success",
    "error",
]


class Optimization(BaseModel):
    status: OptimizationStatus
    """Status of the optimization. One of:
    - "not_started": Optimization has not started yet
    - "pending": Optimization is pending
    - "running": Optimization is running
    - "success": Optimization has completed successfully
    - "error": Optimization has failed
    """
    updated_at: datetime.datetime | None = None
    """Timestamp of the last update to the status"""


class TileServer(BaseModel):
    tile_url: str
    """Tileserver URL to be used in an application"""
    pixel_url: str | None = None
    """Pixel info URL.

    Optional, as the dynamic tiler does not properly support this yet
    """
    min_zoom: int
    """Minimum zoom level supported by the tile server"""
    max_zoom: int
    """Maximum zoom level supported by the tile server"""


class Variable(BaseModel):
    """Estimated statistics for a variable in the dataset, useful for visualization"""

    sampled_min: float
    """Estimated minimum value in the dataset"""
    sampled_max: float
    """Estimated maximum value in the dataset"""


class DatasetResponse(BaseModel):
    dataset_id: uuid.UUID
    """Dataset ID of the dataset"""
    dataset_version_id: uuid.UUID
    """ID for the current version of the dataset"""
    name: str
    """Name of the dataset"""
    type: DatasetType
    """Type of the dataset, either `raster` or `vector`"""
    labels: list[DatasetLabel] = Field(default_factory=list)
    """User-defined labels for the dataset"""
    variables: dict[str, Variable] = Field(default_factory=dict)
    """Estimated statistics for each variable in the dataset, useful for visualization"""  # noqa: E501
    created_at: AwareDatetime
    """Timestamp of when the dataset was created"""
    visualization_optimization: Optimization
    """Status of the visualization optimization for faster visualization"""
    pixel_info_optimizations: dict[str, Optimization] = Field(default_factory=dict)
    """Status of the pixel info optimizations for faster pixel info retrieval"""

    dynamic_tile_server: TileServer
    """Dynamic tile server for fast visualization"""
    optimized_tile_server: TileServer | None
    """Optimized tile server for fast visualization"""


class ListDatasetResponse(BaseModel):
    """Single entry in the list of datasets with a subset of information"""

    dataset_id: uuid.UUID
    """Dataset ID of the dataset"""
    dataset_version_id: uuid.UUID
    """ID for the current version of the dataset"""
    name: str
    """Name of the dataset"""
    type: DatasetType
    """Type of the dataset, either `raster` or `vector`"""
    labels: list[DatasetLabel] = Field(default_factory=list)
    """User-defined labels for the dataset"""
    created_at: AwareDatetime
    """Timestamp of when the dataset was created"""


class ErrorResponse(BaseModel):
    message: str
    error_class: str


class Credentials(BaseModel):
    """Credentials model for storing authentication information."""

    user_id: str | None = None
    user_email: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    expires_in: int | None = None
    expires_at: AwareDatetime | None = None
    # For password auth
    password: str | None = None
