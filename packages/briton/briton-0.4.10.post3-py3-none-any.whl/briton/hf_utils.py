import logging
import os
import time
from pathlib import Path

from huggingface_hub import snapshot_download
from huggingface_hub.utils import RepositoryNotFoundError, RevisionNotFoundError

logger = logging.getLogger(__name__)


def download_and_link_snapshot(
    hf_repo_id: str, hf_token: str, local_dir: Path, max_retries: int, retry_delay: int
):
    """Download a snapshot using the local HF cache and symlink it to local dir"""
    logger.info("Downloading model snapshot...")

    for attempt in range(max_retries):
        try:
            snapshot_path = snapshot_download(
                hf_repo_id,
                token=hf_token,
                etag_timeout=60 * 10,
                resume_download=True,
            )
            logger.info(f"Model snapshot downloaded successfully to {snapshot_path}.")

            for item in Path(snapshot_path).iterdir():
                d = local_dir / item.name
                if d.is_symlink():
                    d.unlink()
                elif d.is_dir():
                    d.rmdir()
                elif d.exists():
                    d.unlink()

                if item.is_dir():
                    os.symlink(item, d, target_is_directory=True)
                else:
                    os.symlink(item, d)
            break
        except (ConnectionError, TimeoutError) as e:
            if attempt < max_retries - 1:
                logger.warning(f"Connection error: {e}. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2  # exponential backoff
            else:
                print(
                    f"Failed to download after {max_retries} attempts. Please check your internet connection."
                )
                raise
        except (RepositoryNotFoundError, RevisionNotFoundError) as e:
            logger.error(
                "Please check the repository ID and ensure you have the correct permissions."
            )
            raise
        except Exception as e:
            logger.error("An unexpected error occurred.")
            raise
