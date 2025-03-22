"""
Client for the Earthscale API.

This client can be used to register, query, and list datasets.

"""

import logging
import uuid
from typing import Any, Literal

import requests
from pydantic import TypeAdapter

from earthscale.v1._http_client import _EarthscaleHttpClient
from earthscale.v1.exceptions import (
    VersionIncompatibleError,
)
from earthscale.v1.models import (
    AddDatasetRequest,
    AddDatasetResponse,
    AddImageDatasetRequest,
    AddTileServerDatasetRequest,
    AddVectorDatasetRequest,
    AddZarrDatasetRequest,
    DatasetLabel,
    DatasetResponse,
    FilenameBandPattern,
    ListDatasetResponse,
    VersionCheckResponse,
)
from earthscale.v1.settings import EarthscaleSettings

logger = logging.getLogger(__name__)


class EarthscaleClient:
    """Client for the Earthscale API.

    This client can be used as a context manager to ensure proper session handling:

    ```python
    with EarthscaleClient() as client:
        response = client.list_datasets()
    ```

    If not used as a context manager, the client will create a new HTTP session for
    each request.

    Authentication can be handled through two methods:
    - Environment variables:
        - EARTHSCALE_EMAIL: Email for authentication
        - EARTHSCALE_PASSWORD: Password for authentication
    - OAuth:
        - If no environment variables are set, the client will use OAuth
          to authenticate, opening a browser window.

    The client uses built-in retry logic with exponential backoff for token refresh.

    Examples:
        Basic usage with environment variables:
        ```python
        # Set environment variables
        os.environ["EARTHSCALE_EMAIL"] = "service@example.com"
        os.environ["EARTHSCALE_PASSWORD"] = "service_password"

        # Create client
        client = EarthscaleClient()
        ```

        Using as a context manager:
        ```python
        # Set environment variables
        os.environ["EARTHSCALE_EMAIL"] = "service@example.com"
        os.environ["EARTHSCALE_PASSWORD"] = "service_password"

        with EarthscaleClient() as client:
            # Token will be automatically obtained and refreshed as needed
            datasets = client.list_datasets()
        ```

        Using custom URLs:
        ```python
        client = EarthscaleClient(
            api_url="https://custom-api.example.com",
            auth_url="https://custom-auth.example.com"
        )
        ```
    """

    API_VERSION = "v1"

    def __init__(
        self,
        api_url: str | None = None,
        auth_url: str | None = None,
        anon_key: str | None = None,
        skip_version_check: bool = False,
        session: requests.Session | None = None,
        use_proxy: bool = False,
    ):
        """Initialize the Earthscale client.

        Args:
            api_url: The URL of the Earthscale API.
                Defaults to https://api.earthscale.ai.
            auth_url: URL for authentication service.
                Defaults to https://supabase.earthscale.ai.
            anon_key: The anon key for the Earthscale API.
                Defaults to the authentication anon key from EarthscaleSettings.
            skip_version_check: Whether to skip version compatibility check.
                Defaults to False.
            session: Optional custom requests session to use.
            use_proxy: Whether to use the proxy server for authentication
                Defaults to False.
        """
        settings = EarthscaleSettings()
        self.api_url = api_url or settings.api_url
        if use_proxy:
            self.auth_url = settings.auth_proxy_url
        else:
            self.auth_url = auth_url or settings.auth_url
        self.anon_key = anon_key or settings.auth_anon_key
        self.skip_version_check = skip_version_check

        # Create the HTTP client
        self._http_client = _EarthscaleHttpClient(
            api_url=self.api_url,
            auth_url=self.auth_url,
            anon_key=self.anon_key,
            email=settings.email,
            password=settings.password,
            credentials_file=settings.credentials_file,
            session=session,
        )

    def __enter__(self) -> "EarthscaleClient":
        # Initialize the HTTP client session
        self._http_client.initialize_session()

        # Check version compatibility
        if not self.skip_version_check:
            self.check_api_support()

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        # Close the HTTP client session
        self._http_client.close_session()

    def login(self) -> None:
        """Login using service account credentials from environment variables,
        or OAuth authentication if no environment variables are set.

        Raises:
            AuthenticationError: If authentication fails.
        """
        self._http_client.login()

    def _add_dataset(self, request: AddDatasetRequest) -> AddDatasetResponse:
        """Internal method to add a dataset using a request model.

        Args:
            request: The dataset request model.

        Returns:
            The dataset response.
        """
        raw_response = self._http_client.request(
            method="POST",
            endpoint="datasets",
            data=request,
            api_version=self.API_VERSION,
        )
        return AddDatasetResponse.model_validate_json(raw_response)

    def add_image_dataset(
        self,
        name: str,
        url: str | list[str],
        labels: list[DatasetLabel] | None = None,
        bands: list[str] | None = None,
        groupby: str | None = None,
        filename_date_pattern: str | None = None,
        filename_band_pattern: list[dict[str, str]] | None = None,
        visualization_optimization: bool | Literal["auto"] = "auto",
        pixel_info_optimizations: list[str] | None = None,
    ) -> AddDatasetResponse:
        """Add an image dataset. Images must be in a format that can be
        read by `rasterio`, e.g. GeoTIFFs.

        This function supports creating a time dimension through the
        `filename_date_pattern` argument. This pattern uses strftime-style format
        codes to extract date information from the filenames.

        Example:

        ```python
        # For filenames like "brasil_coverage_2011.tif"
        client.add_image_dataset(
            name="my_dataset",
            url="gs://mybucket/my_dataset/brasil_coverage_*.tif",
            filename_date_pattern="%Y",
        )
        ```

        Args:
            name: The name of the dataset. Creates a new version of an existing dataset
                  if the latest version of a dataset has the same name.
            url: The URL or list of URLs of the dataset.
            labels: Optional attributes as key-value pairs.
            bands: Optional list of bands to include.
            groupby: Optional groupby parameter. Follows ODC's groupby convention.
                Use "time" to create a time dimension for images grouped by datetime.
                See ODC's groupby documentation for details on other options.
            filename_date_pattern: Optional date pattern for filenames.
            filename_band_pattern: Optional band patterns for filenames.
                E.g. {"*_B[0-9]": "band_1"} would map all bands starting with "B" and
                ending with a number to "band_1". Uses Unix filename pattern rules.
            visualization_optimization: Whether to optimize for visualization.
                Use 'auto' for automatic optimization based on size, True to force,
                or False to disable. Defaults to 'auto'.
            pixel_info_optimizations: List of dimensions to optimize for pixel info API.
                Defaults to None.

        Returns:
            The dataset response.
        """
        # Convert filename_band_pattern to the expected format
        formatted_band_patterns = None
        if filename_band_pattern:
            formatted_band_patterns = [
                FilenameBandPattern(pattern=p["pattern"], band=p["band"])
                for p in filename_band_pattern
            ]

        urls = url if isinstance(url, list) else [url]
        request = AddImageDatasetRequest(
            name=name,
            urls=urls,
            labels=labels,
            bands=bands,
            groupby=groupby,
            filename_date_pattern=filename_date_pattern,
            filename_band_pattern=formatted_band_patterns,
            visualization_optimization=visualization_optimization,
            pixel_info_optimizations=pixel_info_optimizations or [],
        )
        return self._add_dataset(request)

    def add_zarr_dataset(
        self,
        name: str,
        url: str,
        labels: list[DatasetLabel] | None = None,
        rename: dict[str, str] | None = None,
        visualization_optimization: bool | Literal["auto"] = "auto",
        pixel_info_optimizations: list[str] | None = None,
    ) -> AddDatasetResponse:
        """Add a Zarr dataset.

        When loading into xarray, this dataset type will automatically standardize the
        dimensions of the dataset to 'y', 'x' and 'time' if present. It will infer
        spatial dimensions, so if 'lon' or 'longitude' is present, it will be renamed
        to 'x'.

        This supports arbitrary multi-dimensional datasets, for example a dataset with
        'time' or 'level' dimensions in addition to 'y', 'x'.

        Args:
            name: The name of the dataset. Creates a new version of an existing dataset
                  if the latest version of a dataset has the same name.
            url: The URL of the dataset. Can optionally contain a placeholder for the
                dimension name. If specified, this concatenates multiple Zarrs along
                either an existing or new dimension as named in the pattern. Example:
                "gs://mybucket/my_dataset/{time}.zarr"
            labels: Optional. User-defined labels as key-value pairs.
            rename: Optional. Dictionary to rename dimensions.
            visualization_optimization: Whether to optimize for visualization.
                Use 'auto' for automatic optimization based on size, True to force,
                or False to disable. Defaults to 'auto'.
            pixel_info_optimizations: List of dimensions to optimize for pixel info API.
                Defaults to None.

        Returns:
            The dataset response.
        """
        request = AddZarrDatasetRequest(
            name=name,
            urls=[url] if isinstance(url, str) else url,
            labels=labels,
            rename=rename,
            visualization_optimization=visualization_optimization,
            pixel_info_optimizations=pixel_info_optimizations or [],
        )
        return self._add_dataset(request)

    def add_vector_dataset(
        self,
        name: str,
        url: str,
        labels: list[DatasetLabel] | None = None,
    ) -> AddDatasetResponse:
        """Add a vector dataset.

        This function supports adding vector datasets from a variety of sources,
        including GeoJSON, GeoParquet, FlatGeobuf, and more.

        Args:
            name: The name of the dataset. Creates a new version of an existing dataset
                  if the latest version of a dataset has the same name.
            url: The URL of the dataset.
            labels: Optional attributes as key-value pairs.

        Returns:
            The dataset response.
        """
        request = AddVectorDatasetRequest(
            name=name,
            url=url,
            labels=labels,
        )
        return self._add_dataset(request)

    def add_tile_server_dataset(
        self,
        name: str,
        url: str,
        labels: list[DatasetLabel] | None = None,
    ) -> AddDatasetResponse:
        """Add a tile server dataset.

        The URL must be a template string with placeholders for the x, y, and z
        coordinates, e.g. `https://server.com/tiles/{z}/{x}/{y}.png`.

        Args:
            name: The name of the dataset.
            url: The URL of the dataset.
            labels: Optional attributes as key-value pairs.

        Returns:
            The dataset response.
        """
        request = AddTileServerDatasetRequest(
            name=name,
            url=url,
            labels=labels,
        )
        return self._add_dataset(request)

    def list_datasets(self) -> list[ListDatasetResponse]:
        """List all datasets.

        Returns:
            The dataset list response. Each element in the list
            contains basic metadata such as the ID, name, and labels.
        """
        raw_response = self._http_client.request(
            method="GET",
            endpoint="datasets",
            api_version=self.API_VERSION,
        )
        return TypeAdapter(list[ListDatasetResponse]).validate_json(raw_response)

    def get_dataset(self, dataset_id: str | uuid.UUID) -> DatasetResponse:
        """Get the latest version of a dataset by dataset ID.

        Args:
            dataset_id: The dataset ID.

        Returns:
            The dataset response.
        """
        raw_response = self._http_client.request(
            method="GET",
            endpoint=f"datasets/{dataset_id}/latest",
            api_version=self.API_VERSION,
        )
        return DatasetResponse.model_validate_json(raw_response)

    def get_dataset_version_by_id(self, version_id: str | uuid.UUID) -> DatasetResponse:
        """Get a dataset version by version ID.

        Args:
            version_id: The version ID.

        Returns:
            The dataset response.
        """
        if not isinstance(version_id, uuid.UUID):
            version_id = uuid.UUID(version_id)

        raw_response = self._http_client.request(
            method="GET",
            endpoint=f"dataset-versions/{version_id}",
            api_version=self.API_VERSION,
        )
        return DatasetResponse.model_validate_json(raw_response)

    def check_api_support(self) -> VersionCheckResponse:
        """Check if the client's API version is compatible with the server.

        This method contacts the server to verify that the API version used by the
        client is supported by the server. It also provides information about the
        supported API versions and whether the current version is deprecated.

        Returns:
            The version check response from the server.

        Raises:
            VersionIncompatibleError: If the API version is not supported by the server.
        """
        raw_response = self._http_client.request(
            method="GET",
            endpoint=f"api-versions/{self.API_VERSION}",
            api_version="",
        )
        response = VersionCheckResponse.model_validate_json(raw_response)

        if not response.is_supported:
            raise VersionIncompatibleError(
                f"API version {self.API_VERSION} is not supported. "
                f"Please upgrade to version {response.newest_supported_version}."
            )

        # Log a warning if the API version is deprecated
        if response.is_deprecated:
            removal_info = ""
            if response.will_be_removed_after:
                removal_info = (
                    f" It will be removed after {response.will_be_removed_after}."
                )

            logger.warning(
                f"API version {self.API_VERSION} is deprecated.{removal_info} "
                f"Please upgrade to version {response.newest_supported_version}."
            )

        return response
