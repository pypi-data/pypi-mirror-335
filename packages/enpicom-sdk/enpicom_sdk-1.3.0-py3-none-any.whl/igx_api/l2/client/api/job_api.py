import time

from loguru import logger
from typing_extensions import assert_never

from igx_api.l1 import openapi_client
from igx_api.l2.types.api_error import ApiErrorContext
from igx_api.l2.types.collection import CollectionId
from igx_api.l2.types.job import Job, JobId, JobState
from igx_api.l2.types.log import LogLevel
from igx_api.l2.types.tag import TagId


class JobFailed(Exception):
    """Indicates that the job has failed."""

    def __init__(self, job_id: JobId):
        """@private"""
        super().__init__(f"Job with ID `{job_id}` failed")


class JobCancelled(Exception):
    """Indicates that the job has been cancelled."""

    def __init__(self, job_id: JobId):
        """@private"""
        super().__init__(f"Job with ID `{job_id}` was cancelled")


class JobTimedOut(Exception):
    """Indicates that the job has timed out."""

    def __init__(self, job_id: JobId):
        """@private"""
        super().__init__(f"Job with ID `{job_id}` timed out")


class JobApi:
    _inner_api_client: openapi_client.ApiClient
    _log_level: LogLevel

    def __init__(self, inner_api_client: openapi_client.ApiClient, log_level: LogLevel):
        """@private"""
        self._inner_api_client = inner_api_client
        self._log_level = log_level

    def get_job(self, job_id: JobId) -> Job:
        """
        .. danger::
            **Beta version of API functionality.**

            This functionality is considered **unstable** and may be changed in the future without it
            being considered a breaking change.

        Get a single job by its ID.

        Args:
            job_id (igx_api.l2.types.job.JobId): The ID of the job to get.

        Returns:
            igx_api.l2.types.job.Job: Job ID and it's state. This job may or may not be completed, and may or may not have
              failed. If you want to automatically wait for the job to be completed, use `wait_for_job_to_be_completed`.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:

            ```python
            with IgxApiClient() as igx_client:
                job: Job = igx_client.job_api.get_job(job_id=JobId(1234))
            ```
        """

        logger.info(f"Getting job with ID `{job_id}`")

        job_api_instance = openapi_client.JobApi(self._inner_api_client)

        with ApiErrorContext():
            get_job_response = job_api_instance.get_job(job_id)

        job = Job.from_raw(get_job_response.job)

        return job

    def get_collection_id_for_import_job(self, job_id: JobId) -> CollectionId:
        """
        .. danger::
            **Beta version of API functionality.**

            This functionality is considered **unstable** and may be changed in the future without it
            being considered a breaking change.

        Get a collection ID for a single import job by its ID.

        Args:
            job_id (igx_api.l2.types.job.JobId): The ID of the import job.

        Returns:
            igx_api.l2.types.collection.CollectionId: The collection ID for the import job.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            with IgxApiClient() as igx_client:
                collection_id: CollectionId = igx_client.job_api.get_collection_id_for_import(job_id=JobId(1234))
            ```
        """
        logger.info(f"Getting collection ID for import job with id `{job_id}`")

        job_api_instance = openapi_client.JobApi(self._inner_api_client)

        with ApiErrorContext():
            get_collection_id_response = job_api_instance.get_collection_id_for_import_job(job_id)

        return CollectionId(get_collection_id_response.collection_id)

    def get_tag_id_for_create_tag_job(self, job_id: JobId) -> TagId:
        """
        .. danger::
            **Beta version of API functionality.**

            This functionality is considered **unstable** and may be changed in the future without it
            being considered a breaking change.

        Get a tag ID for a single create tag job by its ID.

        Args:
            job_id (igx_api.l2.types.job.JobId): The ID of the create tag job.

        Returns:
            igx_api.l2.types.tag.TagId: The ID of the tag that was created.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            with IgxApiClient() as igx_client:
            tag_id: TagId = job_api.get_tag_id_for_create_tag_job(JobId(1234))
            ```
        """

        logger.info(f"Getting tag ID for create tag job with ID `{job_id}`")

        job_api_instance = openapi_client.JobApi(self._inner_api_client)

        with ApiErrorContext():
            get_tag_id_response = job_api_instance.get_tag_id_for_create_tag_job(job_id)

        return TagId(get_tag_id_response.tag_id)

    def wait_for_job_to_be_completed(self, job_id: JobId) -> Job:
        """
        .. danger::
            **Beta version of API functionality.**

            This functionality is considered **unstable** and may be changed in the future without it
            being considered a breaking change.

        Wait for a job to be completed. If the job fails an exception will be raised.

        Args:
            job_id (igx_api.l2.types.job.JobId): The ID of the job to wait for.

        Returns:
            igx_api.l2.types.job.Job: The job that was waited for. If this returns, it means the job has succeeded.

        Raises:
            igx_api.l2.client.api.job_api.JobFailed: If the job failed.
            igx_api.l2.client.api.job_api.JobCancelled: If the job was cancelled.
            igx_api.l2.client.api.job_api.JobTimedOut: If the job timed out.
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:

            ```python
            with IgxApiClient() as igx_client:
                job: Job = igx_client.job_api.wait_for_job_to_be_completed(job_id=JobId(1234))
            ```
        """

        logger.info(f"Waiting for job with ID `{job_id}` to be completed")

        poll_interval_seconds = 10

        # We do not limit this loop at the top level, we do not know how long it takes for a job to be picked up.
        while True:
            with ApiErrorContext():
                job = self.get_job(job_id)

            match job.state:
                case JobState.QUEUED:
                    logger.debug(f"Job with ID `{job_id}` is still in state `{job.state.value}`. Waiting for {poll_interval_seconds} seconds")
                    time.sleep(poll_interval_seconds)
                case JobState.RUNNING:
                    logger.debug(f"Job with ID `{job_id}` is still in state `{job.state.value}`. Waiting for {poll_interval_seconds} seconds")
                    time.sleep(poll_interval_seconds)
                case JobState.SUCCEEDED:
                    logger.success(f"Job with ID `{job_id}` succeeded")
                    return job
                case JobState.CANCELLED:
                    raise JobCancelled(job_id)
                case JobState.FAILED:
                    raise JobFailed(job_id)
                case JobState.TIMED_OUT:
                    raise JobTimedOut(job_id)
                case _:
                    assert_never(job.state)
