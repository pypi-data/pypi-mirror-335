from loguru import logger

from igx_api.l1 import openapi_client
from igx_api.l2.client.api.job_api import JobApi
from igx_api.l2.types.api_error import ApiError
from igx_api.l2.types.clone import CloneId
from igx_api.l2.types.execution import Execution
from igx_api.l2.types.job import JobId
from igx_api.l2.types.log import LogLevel
from igx_api.l2.types.sequence import SequenceId


class LiabilitiesApi:
    _inner_api_client: openapi_client.ApiClient
    _log_level: LogLevel

    def __init__(self, inner_api_client: openapi_client.ApiClient, log_level: LogLevel):
        """@private"""
        self._inner_api_client = inner_api_client
        self._log_level = log_level

    def start(
        self,
        clone_ids: list[CloneId] | None = None,
        sequence_ids: list[SequenceId] | None = None,
    ) -> Execution[None]:
        """Run liabilities computation on a set of target clones.

        This will compute liabilities for clones matched with clone and sequence IDs passed
        to the function and will add new tags to those clones if computations are successful.

        > This functionality uses clone resolving.\n
        > Clone resolving uses passed clone and sequence IDs in order to resolve clones.
        > For each clone, a maximum of one *big* chain and one *small* chain sequence will be picked, resulting in a
        maximum of two sequences per clone.
        > Sequences matched with passed sequence IDs have priority over internally resolved sequences, meaning that if
        possible, they will be picked as sequences for the resolved clones.

        Args:
            clone_ids (list[igx_api.l2.types.clone.CloneId]): IDs of clones based on which clones will be
                resolved and passed for liabilities computation.
            sequence_ids (list[igx_api.l2.types.sequence.SequenceId]): IDs of sequences based on which clones will be
                resolved and passed for liabilities computation. If clone resolving based on clone IDs and sequence IDs results in the same,
                "overlapping" clones (with the same clone IDs) but potentially different sequences within, clones resolved with use of sequence IDs
                will be picked over the ones resolved with clone IDs.

        Returns:
            igx_api.l2.types.execution.Execution[None]: An awaitable.

        Raises:
            ValueError: If clone and/or sequence IDs passed to this function are empty or invalid.
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:

            ```
            collection_id = CollectionId(1234)

            # Get all clones belonging to a collection
            collection_filter = client.filter_api.create_filter(name="test_collection", condition=MatchId(target=MatchIdTarget.COLLECTION, id=collection_id))
            clones_df = client.collection_api.get_as_df(
                collection_ids=[collection_id],
                filter=collection_filter,
                tag_ids=[],
            ).wait()

            # Extract clone ids from the dataframe
            clone_ids = [CloneId(id) for id in clones_df.index.tolist()]

            # Run liabilities computation
            client.liabilities_api.start(clone_ids=clone_ids).wait()

            # Get clones updated with new tags, result of liabilities computation
            updated_clones_df = client.collection_api.get_as_df(
                collection_ids=[collection_id],
                filter=collection_filter,
                tag_ids=[
                    CloneTags.TapScore # Tag added during liabilities run
                ],
            ).wait()
            ```
        """
        liabilities_api_instance = openapi_client.LiabilitiesApi(self._inner_api_client)

        # Check if we got any ids to work with
        if (clone_ids is None or len(clone_ids) == 0) and (sequence_ids is None or len(sequence_ids) == 0):
            raise ValueError("Both clone and sequence IDs arrays are null, at least one of them needs to contain proper values.")

        # Validate if ID types are right
        if clone_ids is not None and not all([isinstance(id, str) for id in clone_ids]):
            raise ValueError("Some of the passed clone IDs are not strings.")
        elif sequence_ids is not None and not all([isinstance(id, int) for id in sequence_ids]):
            raise ValueError("Some of the passed sequence IDs are not integers.")

        try:
            liabilities_work = openapi_client.LiabilitiesWork(
                clone_ids=None if clone_ids is None else [str(id) for id in clone_ids],
                sequence_ids=None if sequence_ids is None else [int(id) for id in sequence_ids],
            )
            logger.info("Making a request for liabilities computation run start...")
            liabilities_job = liabilities_api_instance.start_liabilities(liabilities_work=liabilities_work)
        except openapi_client.ApiException as e:
            raise ApiError(e)

        job_id = JobId(liabilities_job.job_id)
        job_api = JobApi(self._inner_api_client, self._log_level)

        def wait() -> None:
            job = job_api.wait_for_job_to_be_completed(job_id)

            logger.success(f"Liabilities computation run with ID {job} was finished successfully.")

        return Execution(wait=wait)
