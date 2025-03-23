import requests
import tenacity
from loguru import logger


def _log_after_attempt(retry_state):
    """Log after each attempt."""
    if retry_state.outcome.failed:
        logger.warning(
            f"Attempt {retry_state.attempt_number} for method {retry_state.fn.__name__} failed with: " f"{retry_state.outcome.exception()}"
        )


@tenacity.retry(
    wait=tenacity.wait_fixed(5),
    stop=tenacity.stop_after_attempt(3),
    after=_log_after_attempt,
)
def download_from_s3(presigned_url, f):
    response = requests.get(presigned_url)
    response.raise_for_status()

    logger.debug("Downloaded object from S3")
    f.write(response.content)
    f.seek(0)


def delete_s3_obj(presigned_delete_url, raises=True):
    r = requests.delete(presigned_delete_url)
    if raises:
        r.raise_for_status()
    logger.debug("Deleted object from S3")
