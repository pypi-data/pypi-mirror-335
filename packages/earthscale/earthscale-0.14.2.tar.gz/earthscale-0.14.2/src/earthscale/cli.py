from collections.abc import Callable

import click

from earthscale import EarthscaleClient
from earthscale.v1.models import AddDatasetResponse


@click.group()
def cli() -> None:
    """Earthscale command line tool."""
    pass


@cli.command(help="Add a dataset to Earthscale using only a name and a URL.")
@click.argument("url")
@click.option(
    "-n",
    "--name",
    required=True,
    help="Name of the dataset as it will appear in Earthscale.",
)
@click.option(
    "-t",
    "--type",
    type=click.Choice(["vector", "image", "zarr", "tile_server"]),
    default="vector",
    help="Type of dataset to add. Defaults to vector.",
)
@click.option(
    "-p",
    "--proxy",
    is_flag=True,
    help="Use the proxy server for authentication.",
)
def add(
    url: str,
    name: str,
    type: str,
    proxy: bool,
) -> None:
    with EarthscaleClient(use_proxy=proxy) as client:
        try:
            # Map dataset types to their corresponding client methods
            add_methods: dict[str, Callable[[str, str], AddDatasetResponse]] = {
                "vector": client.add_vector_dataset,
                "image": client.add_image_dataset,
                "zarr": client.add_zarr_dataset,
                "tile_server": client.add_tile_server_dataset,
            }

            add_method = add_methods[type]

            # Call the appropriate method based on type
            response = add_method(
                name=name,
                url=url,
            )  # type: ignore

            click.secho(
                f"Successfully added {type} dataset '{name}' with ID:"
                f" {response.dataset_id}",
                fg="green",
            )
        except Exception as e:
            click.secho(f"Failed to add dataset: {e!s}", err=True, fg="red")
            raise click.Abort() from None


@cli.command(help="Authenticate with Earthscale.")
@click.option(
    "-p",
    "--proxy",
    is_flag=True,
    help="Use the proxy server for authentication.",
)
def authenticate(proxy: bool) -> None:
    client = EarthscaleClient(use_proxy=proxy)
    # This automatically saves credentials after login
    try:
        client.login()
        click.secho("Successfully authenticated with Earthscale.", fg="green")
    except Exception as e:
        click.secho(
            f"Failed to authenticate with Earthscale: {e!s}", err=True, fg="red"
        )
        raise click.Abort() from None


if __name__ == "__main__":
    cli()
