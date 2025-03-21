import json
import logging
import time
import zipfile
from logging import Logger
from pathlib import Path
from typing import Optional

import pandas as pd
import py7zr
from pandas import DataFrame
from tqdm.auto import tqdm
import webbrowser
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_fixed


@retry(
    retry=retry_if_exception(Exception),
    stop=stop_after_attempt(3),  # stop after 3 attempts
    wait=wait_fixed(5),  # wait 5 seconds between attempts
    reraise=True,
)
def download_dataset(
    competition_id: str,
    download_dir: Path,
    quiet: bool = False,
    force: bool = False,
) -> Path:
    """Downloads the competition data as a zip file using the Kaggle API and returns the path to the zip file."""


    if not download_dir.exists():
        download_dir.mkdir(parents=True)

    api = authenticate_kaggle_api()
    logger.info(f"Authenticated with Kaggle API")

    try:
        api.competition_download_files(
            competition=competition_id,
            path=download_dir,
            quiet=quiet,
            force=force,
        )
        logger.info(f"Downloaded the dataset for `{competition_id}` to `{download_dir}`")
    except Exception as e:
        if _need_to_accept_rules(str(e)):
            logger.warning("You must accept the competition rules before downloading the dataset.")
            _prompt_user_to_accept_rules(competition_id)
            download_dataset(competition_id, download_dir, quiet, force)
        else:
            raise e

    zip_files = list(download_dir.glob("*.zip"))

    assert (
        len(zip_files) == 1
    ), f"Expected to download a single zip file, but found {len(zip_files)} zip files."

    zip_file = zip_files[0]

    return zip_file


def _need_to_accept_rules(error_msg: str) -> bool:
    return "You must accept this competition" in error_msg


def _prompt_user_to_accept_rules(competition_id: str) -> None:
    response = input("Would you like to open the competition page in your browser now? (y/n): ")

    if response.lower() != "y":
        raise RuntimeError("You must accept the competition rules before downloading the dataset.")

    webbrowser.open(f"https://www.kaggle.com/c/{competition_id}/rules")
    input("Press Enter to continue after you have accepted the rules...")



def authenticate_kaggle_api():
    """Authenticates the Kaggle API and returns an authenticated API object, or raises an error if authentication fails."""
    try:
        # only import when necessary; otherwise kaggle asks for API key on import
        from kaggle.api.kaggle_api_extended import KaggleApi

        api = KaggleApi()
        api.authenticate()
        api.competitions_list()  # a cheap op that requires authentication
        return api
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise PermissionError(
            "Kaggle authentication failed! Please ensure you have valid Kaggle API credentials "
            "configured. Refer to the Kaggle API documentation for guidance on setting up "
            "your API token."
        ) from e


def read_jsonl(file_path: str, skip_commented_out_lines: bool = False) -> list[dict]:
    """
    Read a JSONL file and return a list of dictionaries of its content.

    Args:
        file_path (str): Path to the JSONL file.
        skip_commented_out_lines (bool): If True, skip commented out lines.

    Returns:
        list[dict]: List of dictionaries parsed from the JSONL file.
    """
    result = []
    with open(file_path, "r") as f:
        if skip_commented_out_lines:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("//"):
                    continue
                result.append(json.loads(line))
        else:
            return [json.loads(line) for line in f]
    return result



def is_compressed(fpath: Path) -> bool:
    """Checks if the file is compressed."""

    return fpath.suffix in [".zip", ".tar", ".gz", ".tgz", ".tar.gz", ".rar", ".7z"]


def compress(src: Path, compressed: Path, exist_ok: bool = False) -> None:
    """Compresses the contents of a source directory to a compressed file."""
    assert src.exists(), f"Source directory `{src}` does not exist."
    assert src.is_dir(), f"Expected a directory, but got `{src}`."
    if not exist_ok:
        assert not compressed.exists(), f"Compressed file `{compressed}` already exists."

    tqdm_desc = f"Compressing {src.name} to {compressed.name}"
    file_paths = [path for path in src.rglob("*") if path.is_file()]
    total_files = len(file_paths)

    def zip_compress(src: Path, compressed: Path):
        with zipfile.ZipFile(compressed, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in tqdm(file_paths, desc=tqdm_desc, unit="file", total=total_files):
                zipf.write(file_path, arcname=file_path.relative_to(src))

    def sevenz_compress(src: Path, compressed: Path):
        with py7zr.SevenZipFile(compressed, "w") as archive:
            for file_path in tqdm(file_paths, desc=tqdm_desc, unit="file", total=total_files):
                archive.write(file_path, arcname=file_path.relative_to(src))

    # Determine the compression format from the destination file suffix
    if compressed.suffix == ".zip":
        zip_compress(src, compressed)
    elif compressed.suffix == ".7z":
        sevenz_compress(src, compressed)
    else:
        raise NotImplementedError(f"Unsupported compression format: `{compressed.suffix}`.")


def extract(
    compressed: Path, dst: Path, recursive: bool = False, already_extracted: set = set()
) -> None:
    """Extracts the contents of a compressed file to a destination directory."""

    # pre-conditions
    assert compressed.exists(), f"File `{compressed}` does not exist."
    assert compressed.is_file(), f"Path `{compressed}` is not a file."
    assert is_compressed(compressed), f"File `{compressed}` is not compressed."

    if compressed.suffix == ".7z":
        with py7zr.SevenZipFile(compressed, mode="r") as ref:
            ref.extractall(dst)
    elif compressed.suffix == ".zip":
        with zipfile.ZipFile(compressed, "r") as ref:
            ref.extractall(dst)
    else:
        raise NotImplementedError(f"Unsupported compression format: `{compressed.suffix}`.")

    already_extracted.add(compressed)
    if recursive:
        to_extract = {
            fpath for fpath in set(dst.iterdir()) - already_extracted if is_compressed(fpath)
        }
        already_extracted.update(to_extract)

        for fpath in to_extract:
            extract(fpath, fpath.parent, recursive=True, already_extracted=already_extracted)



def get_logger(name: str, level: int = logging.INFO, filename: Optional[Path] = None) -> Logger:
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] [%(filename)s:%(lineno)d] %(message)s",
        filename=filename,
    )
    return logging.getLogger(name)




def read_csv(*args, **kwargs) -> DataFrame:
    """Reads a CSV file and returns a DataFrame with custom default kwargs."""

    try:
        new_default_kwargs = {"float_precision": "round_trip"}
        new_kwargs = {**new_default_kwargs, **kwargs}
        return pd.read_csv(*args, **new_kwargs)
    except pd.errors.EmptyDataError:
        logger.warning(f"CSV file empty! {args[0]}")
        return pd.DataFrame()


def get_timestamp() -> str:
    """Returns the current timestamp in the format `YYYY-MM-DDTHH-MM-SS-Z`."""

    return time.strftime("%Y-%m-%dT%H-%M-%S-%Z", time.gmtime())


logger = get_logger(__name__)
