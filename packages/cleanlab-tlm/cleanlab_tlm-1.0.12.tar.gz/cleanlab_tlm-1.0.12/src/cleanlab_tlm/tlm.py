"""
Cleanlab's Trustworthy Language Model (TLM) is a large language model that gives more reliable answers and quantifies its uncertainty in these answers.

Learn how to use TLM via the [quickstart tutorial](/tlm/tutorials/tlm).
"""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine, Sequence
from typing import (
    # lazydocs: ignore
    TYPE_CHECKING,
    Any,
    Optional,
    Union,
    cast,
)

import aiohttp
from tqdm.asyncio import tqdm_asyncio
from typing_extensions import (  # for Python <3.11 with (Not)Required
    NotRequired,
    TypedDict,
)

from cleanlab_tlm.errors import ValidationError
from cleanlab_tlm.internal.api import api
from cleanlab_tlm.internal.base import BaseTLM
from cleanlab_tlm.internal.constants import (
    _DEFAULT_TLM_QUALITY_PRESET,
    _TLM_CONSTRAIN_OUTPUTS_KEY,
    _TLM_MAX_RETRIES,
    _VALID_TLM_QUALITY_PRESETS,
    _VALID_TLM_TASKS,
)
from cleanlab_tlm.internal.exception_handling import handle_tlm_exceptions
from cleanlab_tlm.internal.types import Task
from cleanlab_tlm.internal.validation import (
    tlm_prompt_process_and_validate_kwargs,
    tlm_score_process_response_and_kwargs,
    validate_tlm_prompt,
    validate_tlm_prompt_response,
    validate_tlm_try_prompt,
    validate_try_tlm_prompt_response,
)

if TYPE_CHECKING:
    from cleanlab_tlm.internal.types import TLMQualityPreset


class TLM(BaseTLM):
    """
    Represents a Trustworthy Language Model (TLM) instance, which is bound to a Cleanlab TLM account.

    The TLM object can be used as a drop-in replacement for an LLM, or for scoring the trustworthiness of arbitrary text prompt/response pairs.

    Advanced users can optionally specify TLM configuration options. The documentation below summarizes these options, more details are explained in the [Advanced TLM tutorial](/tlm/tutorials/tlm_advanced/).

    Args:
        quality_preset ({"base", "low", "medium", "high", "best"}, default = "medium"): an optional preset configuration to control
            the quality of TLM responses and trustworthiness scores vs. latency/costs.

            The "best" and "high" presets auto-improve LLM responses,
            with "best" also returning more reliable trustworthiness scores than "high".
            The "medium" and "low" presets return standard LLM responses along with associated trustworthiness scores,
            with "medium" producing more reliable trustworthiness scores than "low".
            The "base" preset provides a standard LLM response and a trustworthiness score in the lowest possible latency/cost.

            Higher presets have increased runtime and cost (and may internally consume more tokens).
            Reduce your preset if you see token-limit errors.
            Details about each present are documented in [TLMOptions](#class-tlmoptions).
            Avoid "best" or "high" presets if you just want trustworthiness scores (i.e. are using `tlm.get_trustworthiness_score()` rather than `tlm.prompt()`).
            These "best" or "high" presets can additionally improve the LLM response itself, but do not return more reliable trustworthiness scores than "medium" or "low" presets.

        task ({"default", "classification", "code_generation"}, default = "default"): determines which scoring flow/methodology to use for evaluating the trustworthiness of the response.
            - "default": use for general tasks such as QA, summarization, etc.
            - "classification": use for classification tasks, where the response is a categorical prediction. \
                When using this task type, `constrain_outputs` must be provided in the `prompt()` and `get_trustworthiness_score()` methods.
            - "code_generation": use for code generation tasks.

        options (TLMOptions, optional): a typed dict of advanced configurations you can optionally specify.
        Available options (keys in this dict) include "model", "max_tokens", "num_candidate_responses", "num_consistency_samples", "use_self_reflection",
        "similarity_measure", "reasoning_effort", "log", "custom_eval_criteria".
        See detailed documentation under [TLMOptions](#class-tlmoptions).
        If specified, these override any settings from the choice of `quality_preset`
        (each `quality_preset` is just a certain TLMOptions configuration).

        timeout (float, optional): timeout (in seconds) to apply to each TLM prompt.
        If a batch of data is passed in, the timeout will be applied to each individual item in the batch.
        If a result is not produced within the timeout, a TimeoutError will be raised. Defaults to None, which does not apply a timeout.

        verbose (bool, optional): whether to print outputs during execution, i.e. show a progress bar when running TLM over a batch of data.
        If None, this will be determined automatically based on whether the code is running in an interactive environment such as a Jupyter notebook.
    """

    def __init__(
        self,
        quality_preset: TLMQualityPreset = _DEFAULT_TLM_QUALITY_PRESET,
        *,
        task: str = "default",
        api_key: Optional[str] = None,
        options: Optional[TLMOptions] = None,
        timeout: Optional[float] = None,
        verbose: Optional[bool] = None,
    ) -> None:
        """
        lazydocs: ignore
        """
        # Initialize base class
        super().__init__(
            quality_preset=quality_preset,
            valid_quality_presets=_VALID_TLM_QUALITY_PRESETS,
            support_custom_eval_criteria=True,
            api_key=api_key,
            options=options,
            timeout=timeout,
            verbose=verbose,
        )

        # TLM-specific initialization
        if task not in _VALID_TLM_TASKS:
            raise ValidationError(f"Invalid task {task} -- must be one of {_VALID_TLM_TASKS}")

        self._task = Task(task)

    async def _batch_prompt(
        self,
        prompts: Sequence[str],
        capture_exceptions: bool = False,
        constrain_outputs: Optional[Sequence[Optional[list[str]]]] = None,
    ) -> list[TLMResponse]:
        """Run a batch of prompts through TLM and get responses/scores for each prompt in the batch. The list returned will have the same length as the input list.

        Args:
            prompts (list[str]): list of prompts to run
            capture_exceptions (bool): if ``True``, the returned list will contain [TLMResponse](#class-tlmresponse) objects with error messages and retryability information in place of the response for any errors or timeout when processing a particular prompt from the batch.
                If ``False``, this entire method will raise an exception if TLM fails to produce a result for any prompt in the batch.

        Returns:
            list[TLMResponse]: TLM responses/scores for each prompt (in supplied order)
        """
        if capture_exceptions:
            per_query_timeout, per_batch_timeout = self._timeout, None
        else:
            per_query_timeout, per_batch_timeout = None, self._timeout

        # run batch of TLM
        tlm_responses = await self._batch_async(
            [
                self._prompt_async(
                    prompt,
                    timeout=per_query_timeout,
                    capture_exceptions=capture_exceptions,
                    batch_index=batch_index,
                    constrain_outputs=constrain_output,
                )
                for batch_index, (prompt, constrain_output) in enumerate(
                    zip(
                        prompts,
                        constrain_outputs if constrain_outputs else [None] * len(prompts),
                    )
                )
            ],
            per_batch_timeout,
        )

        if capture_exceptions:
            return cast(list[TLMResponse], tlm_responses)

        return cast(list[TLMResponse], tlm_responses)

    async def _batch_get_trustworthiness_score(
        self,
        prompts: Sequence[str],
        responses: Sequence[dict[str, Any]],
        capture_exceptions: bool = False,
    ) -> list[TLMScore]:
        """Run batch of TLM get trustworthiness score.

        capture_exceptions behavior:
        - If true, the list will contain None in place of the response for any errors or timeout processing some inputs.
        - Otherwise, the method will raise an exception for any errors or timeout processing some inputs.

        capture_exceptions interaction with timeout:
        - If true, timeouts are applied on a per-query basis (i.e. some queries may succeed while others fail)
        - If false, a single timeout is applied to the entire batch (i.e. all queries will fail if the timeout is reached)

        Args:
            prompts (Sequence[str]): list of prompts to run get trustworthiness score for
            responses (Sequence[str]): list of responses to run get trustworthiness score for
            capture_exceptions (bool): if True, the returned list will contain [TLMScore](#class-tlmscore) objects with error messages and retryability information in place of the score for any errors or timeout when processing a particular prompt from the batch.

        Returns:
            list[TLMScore]: TLM trustworthiness score for each prompt (in supplied order).
        """
        if capture_exceptions:
            per_query_timeout, per_batch_timeout = self._timeout, None
        else:
            per_query_timeout, per_batch_timeout = None, self._timeout

        # run batch of TLM get trustworthiness score
        tlm_responses = await self._batch_async(
            [
                self._get_trustworthiness_score_async(
                    prompt,
                    response,
                    timeout=per_query_timeout,
                    capture_exceptions=capture_exceptions,
                    batch_index=batch_index,
                )
                for batch_index, (prompt, response) in enumerate(zip(prompts, responses))
            ],
            per_batch_timeout,
        )

        if capture_exceptions:
            return cast(list[TLMScore], tlm_responses)

        return cast(list[TLMScore], tlm_responses)

    async def _batch_async(
        self,
        tlm_coroutines: Sequence[Coroutine[None, None, Union[TLMResponse, TLMScore]]],
        batch_timeout: Optional[float] = None,
    ) -> Sequence[Union[TLMResponse, TLMScore]]:
        """Runs batch of TLM queries.

        Args:
            tlm_coroutines (list[Coroutine[None, None, Union[TLMResponse, TLMScore]]]): list of query coroutines to run, returning [TLMResponse](#class-tlmresponse) or [TLMScore](#class-tlmscore)
            batch_timeout (Optional[float], optional): timeout (in seconds) to run all queries, defaults to None (no timeout)

        Returns:
            Sequence[Union[TLMResponse, TLMScore]]: list of coroutine results, with preserved order
        """
        tlm_query_tasks = [asyncio.create_task(tlm_coro) for tlm_coro in tlm_coroutines]

        if self._verbose:
            gather_task = tqdm_asyncio.gather(
                *tlm_query_tasks,
                total=len(tlm_query_tasks),
                desc="Querying TLM...",
                bar_format="{desc} {percentage:3.0f}%|{bar}|",
            )
        else:
            gather_task = asyncio.gather(*tlm_query_tasks)  # type: ignore[assignment]

        wait_task = asyncio.wait_for(gather_task, timeout=batch_timeout)
        try:
            return cast(
                Sequence[Union[TLMResponse, TLMScore]],
                await wait_task,
            )
        except Exception:
            # if exception occurs while awaiting batch results, cancel remaining tasks
            for query_task in tlm_query_tasks:
                query_task.cancel()

            # await remaining tasks to ensure they are cancelled
            await asyncio.gather(*tlm_query_tasks, return_exceptions=True)

            raise

    def prompt(
        self,
        prompt: Union[str, Sequence[str]],
        /,
        **kwargs: Any,
    ) -> Union[TLMResponse, list[TLMResponse]]:
        """
        Gets response and trustworthiness score for any text input.

        This method prompts the TLM with the given prompt(s), producing completions (like a standard LLM)
        but also provides trustworthiness scores quantifying the quality of the output.

        Args:
            prompt (str | Sequence[str]): prompt (or list of multiple prompts) for the language model.
                Providing a batch of many prompts here will be faster than calling this method on each prompt separately.
            kwargs: Optional keyword arguments for TLM. When using TLM for multi-class classification, specify `constrain_outputs` as a keyword argument to ensure returned responses are one of the valid classes/categories.
                `constrain_outputs` is a list of strings (or a list of lists of strings), used to denote the valid classes/categories of interest.
                We recommend also listing and defining the valid outputs in your prompt as well.
                If `constrain_outputs` is a list of strings, the response returned for every prompt will be constrained to match one of these values. The last entry in this list is additionally treated as the output to fall back to if the raw LLM output does not resemble any of the categories (for instance, this could be an Other category, or it could be the category you'd prefer to return whenever the LLM is unsure).
                If you run a list of multiple prompts simultaneously and want to differently constrain each of their outputs, then specify `constrain_outputs` as a list of lists of strings (one list for each prompt).
        Returns:
            TLMResponse | list[TLMResponse]: [TLMResponse](#class-tlmresponse) object containing the response and trustworthiness score.
                If multiple prompts were provided in a list, then a list of such objects is returned, one for each prompt.
                This method will raise an exception if any errors occur or if you hit a timeout (given a timeout is specified).
                Use it if you want strict error handling and immediate notification of any exceptions/timeouts.

                If running this method on a big batch of prompts, you might lose partially completed results if TLM fails on any one of them.
                Use the [`try_prompt()`](#method-try_prompt) method instead and run it on multiple smaller batches.
        """
        validate_tlm_prompt(prompt)
        tlm_prompt_process_and_validate_kwargs(prompt, self._task, kwargs)
        if isinstance(prompt, str):
            return cast(
                TLMResponse,
                self._event_loop.run_until_complete(
                    self._prompt_async(
                        prompt,
                        timeout=self._timeout,
                        capture_exceptions=False,
                        constrain_outputs=kwargs.get(_TLM_CONSTRAIN_OUTPUTS_KEY),
                    ),
                ),
            )

        return self._event_loop.run_until_complete(
            self._batch_prompt(
                prompt,
                capture_exceptions=False,
                constrain_outputs=cast(
                    Optional[list[Optional[list[str]]]],
                    kwargs.get(_TLM_CONSTRAIN_OUTPUTS_KEY),
                ),
            ),
        )

    def try_prompt(
        self,
        prompt: Sequence[str],
        /,
        **kwargs: Any,
    ) -> list[TLMResponse]:
        """
        Gets response and trustworthiness score for any batch of prompts, handling any failures (errors or timeouts).

        The list returned will have the same length as the input list. If there are any
        failures (errors or timeouts) processing some inputs, the [TLMResponse](#class-tlmresponse) objects in the returned list will contain error messages and retryability information instead of the usual response.

        This is the recommended way to run TLM over large datasets with many prompts.
        It ensures partial results are preserved, even if some individual TLM calls over the dataset fail.

        Args:
            prompt (Sequence[str]): list of multiple prompts for the TLM
            kwargs: Optional keyword arguments, the same as for the [`prompt()`](#method-prompt) method.
        Returns:
            list[TLMResponse]: list of [TLMResponse](#class-tlmresponse) objects containing the response and trustworthiness score.
                The returned list will always have the same length as the input list.
                In case of TLM failure on any prompt (due to timeouts or other errors),
                the return list will include a [TLMResponse](#class-tlmresponse) with an error message and retryability information instead of the usual TLMResponse for that failed prompt.
                Use this method to obtain TLM results for as many prompts as possible, while handling errors/timeouts manually.
                For immediate notification about any errors or timeouts when processing multiple prompts,
                use [`prompt()`](#method-prompt) instead.
        """
        validate_tlm_try_prompt(prompt)
        tlm_prompt_process_and_validate_kwargs(prompt, self._task, kwargs)

        return self._event_loop.run_until_complete(
            self._batch_prompt(
                prompt,
                capture_exceptions=True,
                constrain_outputs=cast(
                    Optional[list[Optional[list[str]]]],
                    kwargs.get(_TLM_CONSTRAIN_OUTPUTS_KEY),
                ),
            ),
        )

    async def prompt_async(
        self,
        prompt: Union[str, Sequence[str]],
        /,
        **kwargs: Any,
    ) -> Union[TLMResponse, list[TLMResponse]]:
        """
        Asynchronously get response and trustworthiness score for any text input from TLM.
        This method is similar to the [`prompt()`](#method-prompt) method but operates asynchronously,
        allowing for non-blocking concurrent operations.

        Use this method if prompts are streaming in one at a time, and you want to return results
        for each one as quickly as possible, without the TLM execution of one prompt blocking the execution of the others.
        Asynchronous methods do not block until completion, so you need to fetch the results yourself.

        Args:
            prompt (str | Sequence[str]): prompt (or list of multiple prompts) for the TLM
            kwargs: Optional keyword arguments, the same as for the [`prompt()`](#method-prompt) method.
        Returns:
            TLMResponse | list[TLMResponse]: [TLMResponse](#class-tlmresponse) object containing the response and trustworthiness score.
                If multiple prompts were provided in a list, then a list of such objects is returned, one for each prompt.
                This method will raise an exception if any errors occur or if you hit a timeout (given a timeout is specified).
        """
        validate_tlm_prompt(prompt)
        tlm_prompt_process_and_validate_kwargs(prompt, self._task, kwargs)

        async with aiohttp.ClientSession() as session:
            if isinstance(prompt, str):
                tlm_response = await self._prompt_async(
                    prompt,
                    session,
                    timeout=self._timeout,
                    capture_exceptions=False,
                    constrain_outputs=kwargs.get(_TLM_CONSTRAIN_OUTPUTS_KEY),
                )
                return cast(TLMResponse, tlm_response)

            return await self._batch_prompt(
                prompt,
                capture_exceptions=False,
                constrain_outputs=cast(
                    Optional[list[Optional[list[str]]]],
                    kwargs.get(_TLM_CONSTRAIN_OUTPUTS_KEY),
                ),
            )

    @handle_tlm_exceptions("TLMResponse")
    async def _prompt_async(
        self,
        prompt: str,
        client_session: Optional[aiohttp.ClientSession] = None,
        timeout: Optional[float] = None,
        capture_exceptions: bool = False,  # noqa: ARG002
        batch_index: Optional[int] = None,
        constrain_outputs: Optional[list[str]] = None,
    ) -> TLMResponse:
        """
        Private asynchronous method to get response and trustworthiness score from TLM.

        Args:
            prompt (str): prompt for the TLM
            client_session (aiohttp.ClientSession, optional): async HTTP session to use for TLM query. Defaults to None (creates a new session).
            timeout: timeout (in seconds) to run the prompt, defaults to None (no timeout)
            capture_exceptions (bool): if True, the returned [TLMResponse](#class-tlmresponse) object will include error details and retry information if any errors or timeouts occur during processing.
            batch_index: index of the prompt in the batch, used for error messages
            constrain_outputs: list of strings to constrain the output of the TLM to
        Returns:
            TLMResponse: [TLMResponse](#class-tlmresponse) object containing the response and trustworthiness score.
        """
        response_json = await asyncio.wait_for(
            api.tlm_prompt(
                self._api_key,
                prompt,
                self._quality_preset,
                self._task.value,
                self._options,
                self._rate_handler,
                client_session,
                batch_index=batch_index,
                retries=_TLM_MAX_RETRIES,
                constrain_outputs=constrain_outputs,
            ),
            timeout=timeout,
        )

        tlm_response = {
            "response": response_json["response"],
            "trustworthiness_score": response_json["confidence_score"],
        }

        if self._return_log:
            tlm_response["log"] = response_json["log"]

        return cast(TLMResponse, tlm_response)

    def get_trustworthiness_score(
        self,
        prompt: Union[str, Sequence[str]],
        response: Union[str, Sequence[str]],
        **kwargs: Any,
    ) -> Union[TLMScore, list[TLMScore]]:
        """Computes trustworthiness score for arbitrary given prompt-response pairs.

        Args:
            prompt (str | Sequence[str]): prompt (or list of prompts) for the TLM to evaluate
            response (str | Sequence[str]): existing response (or list of responses) associated with the input prompts.
                These can be from any LLM or human-written responses.
            kwargs: Optional keyword arguments, it supports the same arguments as the [`prompt()`](#method-prompt) method such as `constrain_outputs`.
        Returns:
            TLMScore | list[TLMScore]: If a single prompt/response pair was passed in, method returns a [TLMScore](#class-tlmscore) object containing the trustworthiness score and optional log dictionary keys.

                If a list of prompt/responses was passed in, method returns a list of [TLMScore](#class-tlmscore) objects each containing the trustworthiness score and optional log dictionary keys for each prompt-response pair passed in.

                The score quantifies how confident TLM is that the given response is good for the given prompt.
                If running on many prompt-response pairs simultaneously:
                this method will raise an exception if any TLM errors or timeouts occur.
                Use it if immediate notification of any exceptions/timeouts is preferred.
                You will lose any partial results if an exception is raised.
                For big datasets, we recommend using [`try_get_trustworthiness_score()`](#method-try_get_trustworthiness_score) instead, and running it in multiple batches.
        """
        validate_tlm_prompt_response(prompt, response)
        processed_response = tlm_score_process_response_and_kwargs(prompt, response, self._task, kwargs)

        if isinstance(prompt, str) and isinstance(processed_response, dict):
            return cast(
                TLMScore,
                self._event_loop.run_until_complete(
                    self._get_trustworthiness_score_async(
                        prompt,
                        processed_response,
                        timeout=self._timeout,
                        capture_exceptions=False,
                    )
                ),
            )

        assert isinstance(prompt, Sequence)
        assert isinstance(processed_response, Sequence)

        return self._event_loop.run_until_complete(
            self._batch_get_trustworthiness_score(prompt, processed_response, capture_exceptions=False)
        )

    def try_get_trustworthiness_score(
        self,
        prompt: Sequence[str],
        response: Sequence[str],
        **kwargs: Any,
    ) -> list[TLMScore]:
        """Gets trustworthiness score for batches of many prompt-response pairs.

        The list returned will have the same length as the input list, if TLM hits any
        errors or timeout processing certain inputs, the list will contain [TLMScore](#class-tlmscore) objects with error messages and retryability information
        in place of the TLM score for this failed input.

        This is the recommended way to get TLM trustworthiness scores for big datasets.
        It ensures partial results are not lost if some individual TLM calls within the dataset fail.

        Args:
            prompt (Sequence[str]): list of prompts for the TLM to evaluate
            response (Sequence[str]): list of existing responses corresponding to the input prompts (from any LLM or human-written)
            kwargs: Optional keyword arguments, it supports the same arguments as the [`prompt()`](#method-prompt) method such as `constrain_outputs`.
        Returns:
            list[TLMScore]: If a list of prompt/responses was passed in, method returns a list of [TLMScore](#class-tlmscore) objects each containing the trustworthiness score and the optional log dictionary keys for each prompt-response pair passed in. For all TLM calls that failed, the returned list will contain [TLMScore](#class-tlmscore) objects with error messages and retryability information instead.

                The score quantifies how confident TLM is that the given response is good for the given prompt.
                The returned list will always have the same length as the input list.
                In case of TLM error or timeout on any prompt-response pair,
                the returned list will contain [TLMScore](#class-tlmscore) objects with error messages and retryability information in place of the trustworthiness score.
                Use this method if you prioritize obtaining results for as many inputs as possible.
                To be notified immediately about any errors or timeouts when running many inputs,
                use the [`get_trustworthiness_score()`](#method-get_trustworthiness_score) method instead.
        """
        validate_try_tlm_prompt_response(prompt, response)
        processed_response = tlm_score_process_response_and_kwargs(prompt, response, self._task, kwargs)

        assert isinstance(processed_response, list)

        return self._event_loop.run_until_complete(
            self._batch_get_trustworthiness_score(
                prompt,
                processed_response,
                capture_exceptions=True,
            )
        )

    async def get_trustworthiness_score_async(
        self,
        prompt: Union[str, Sequence[str]],
        response: Union[str, Sequence[str]],
        **kwargs: Any,
    ) -> Union[TLMScore, list[TLMScore]]:
        """Asynchronously gets trustworthiness score for prompt-response pairs.
        This method is similar to the [`get_trustworthiness_score()`](#method-get_trustworthiness_score) method but operates asynchronously,
        allowing for non-blocking concurrent operations.

        Use this method if prompt-response pairs are streaming in, and you want to return TLM scores
        for each pair as quickly as possible, without the TLM scoring of any one pair blocking the scoring of the others.
        Asynchronous methods do not block until completion, so you will need to fetch the results yourself.

        Args:
            prompt (str | Sequence[str]): prompt (or list of prompts) for the TLM to evaluate
            response (str | Sequence[str]): response (or list of responses) corresponding to the input prompts
            kwargs: Optional keyword arguments, it supports the same arguments as the [`prompt()`](#method-prompt) method such as `constrain_outputs`.
        Returns:
            TLMScore | list[TLMScore]: If a single prompt/response pair was passed in, method returns either a float (representing the output trustworthiness score) or a [TLMScore](#class-tlmscore) object containing both the trustworthiness score and log dictionary keys.

                If a list of prompt/responses was passed in, method returns a list of floats representing the trustworthiness score or a list of [TLMScore](#class-tlmscore) objects each containing both the trustworthiness score and log dictionary keys for each prompt-response pair passed in.
                The score quantifies how confident TLM is that the given response is good for the given prompt.
                This method will raise an exception if any errors occur or if you hit a timeout (given a timeout is specified).
        """
        validate_tlm_prompt_response(prompt, response)
        processed_response = tlm_score_process_response_and_kwargs(prompt, response, self._task, kwargs)

        async with aiohttp.ClientSession() as session:
            if isinstance(prompt, str) and isinstance(processed_response, dict):
                trustworthiness_score = await self._get_trustworthiness_score_async(
                    prompt,
                    processed_response,
                    session,
                    timeout=self._timeout,
                    capture_exceptions=False,
                )
                return cast(TLMScore, trustworthiness_score)

            assert isinstance(prompt, Sequence)
            assert isinstance(processed_response, Sequence)

            return await self._batch_get_trustworthiness_score(prompt, processed_response, capture_exceptions=False)

    @handle_tlm_exceptions("TLMScore")
    async def _get_trustworthiness_score_async(
        self,
        prompt: str,
        response: dict[str, Any],
        client_session: Optional[aiohttp.ClientSession] = None,
        timeout: Optional[float] = None,
        capture_exceptions: bool = False,  # noqa: ARG002
        batch_index: Optional[int] = None,
    ) -> TLMScore:
        """Private asynchronous method to get trustworthiness score for prompt-response pairs.

        Args:
            prompt: prompt for the TLM to evaluate
            response: response corresponding to the input prompt
            client_session: async HTTP session to use for TLM query. Defaults to None.
            timeout: timeout (in seconds) to run the prompt, defaults to None (no timeout)
            capture_exceptions (bool): if True, the returned [TLMScore](#class-tlmscore) object will include error details and retry information if any errors or timeouts occur during processing.
            batch_index: index of the prompt in the batch, used for error messages
        Returns:
            [TLMScore](#class-tlmscore) objects with error messages and retryability information in place of the trustworthiness score
        """
        response_json = await asyncio.wait_for(
            api.tlm_get_confidence_score(
                self._api_key,
                prompt,
                response,
                self._quality_preset,
                self._task.value,
                self._options,
                self._rate_handler,
                client_session,
                batch_index=batch_index,
                retries=_TLM_MAX_RETRIES,
            ),
            timeout=timeout,
        )

        if self._return_log:
            return {
                "trustworthiness_score": response_json["confidence_score"],
                "log": response_json["log"],
            }

        return {"trustworthiness_score": response_json["confidence_score"]}

    def get_model_name(self) -> str:
        """Returns the underlying LLM used to generate responses and score their trustworthiness."""
        return cast(str, self._options["model"])


class TLMResponse(TypedDict):
    """A typed dict containing the response, trustworthiness score, and additional logs output by the Trustworthy Language Model.

    Attributes:
        response (str): text response from the Trustworthy Language Model.

        trustworthiness_score (float, optional): score between 0-1 corresponding to the trustworthiness of the response.
        A higher score indicates a higher confidence that the response is correct/good.

        log (dict, optional): additional logs and metadata returned from the LLM call, only if the `log` key was specified in TLMOptions.
    """

    response: Optional[str]
    trustworthiness_score: Optional[float]
    log: NotRequired[dict[str, Any]]


class TLMScore(TypedDict):
    """A typed dict containing the trustworthiness score and additional logs output by the Trustworthy Language Model.

    Attributes:
        trustworthiness_score (float, optional): score between 0-1 corresponding to the trustworthiness of the response.
        A higher score indicates a higher confidence that the response is correct/good.

        log (dict, optional): additional logs and metadata returned from the LLM call, only if the `log` key was specified in TLMOptions.
    """

    trustworthiness_score: Optional[float]
    log: NotRequired[dict[str, Any]]


class TLMOptions(TypedDict):
    """Typed dict of advanced configuration options for the Trustworthy Language Model.
    Many of these configurations are determined by the quality preset selected
    (learn about quality presets in the TLM [initialization method](./#class-tlm)).
    Specifying TLMOptions values directly overrides any default values set from the quality preset.

    For all options described below, higher settings will lead to longer runtimes and may consume more tokens internally.
    You may not be able to run long prompts (or prompts with long responses) in your account,
    unless your token/rate limits are increased. If you hit token limit issues, try lower/less expensive TLMOptions
    to be able to run longer prompts/responses, or contact Cleanlab to increase your limits.

    The default values corresponding to each quality preset are:
    - **best:** `num_candidate_responses` = 6, `num_consistency_samples` = 8, `use_self_reflection` = True. This preset improves LLM responses.
    - **high:** `num_candidate_responses` = 4, `num_consistency_samples` = 8, `use_self_reflection` = True. This preset improves LLM responses.
    - **medium:** `num_candidate_responses` = 1, `num_consistency_samples` = 8, `use_self_reflection` = True.
    - **low:** `num_candidate_responses` = 1, `num_consistency_samples` = 4, `use_self_reflection` = True.
    - **base:** `num_candidate_responses` = 1, `num_consistency_samples` = 0, `use_self_reflection` = False.
        When using `get_trustworthiness_score()` on "base" preset, a cheaper self-reflection will be used to compute the trustworthiness score.

    By default, the TLM uses the "medium" quality preset. The default base LLM `model` used is "gpt-4o-mini", and `max_tokens` is 512 for all quality presets.
    You can set custom values for these arguments regardless of the quality preset specified.

    Args:
        model ({"gpt-4o-mini", "gpt-4o", "o3-mini", "o1", "o1-mini", "o1-preview", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4.5-preview", "claude-3.7-sonnet", \
        "claude-3.5-sonnet-v2", "claude-3.5-sonnet", "claude-3.5-haiku", "claude-3-haiku", "nova-micro", "nova-lite", "nova-pro"}, default = "gpt-4o-mini"): \
        Underlying base LLM to use (better models yield better results, faster models yield faster/cheaper results).
        - Models still in beta: "o1", "o3-mini", "o1-mini", "gpt-4.5-preview", "claude-3.7-sonnet", "claude-3.5-sonnet-v2", "claude-3.5-haiku", "nova-micro", "nova-lite", "nova-pro".
        - Recommended models for accuracy: "gpt-4o", "o3-mini", "o1", "claude-3.7-sonnet".
        - Recommended models for low latency/costs: "nova-micro", "gpt-4o-mini".

        max_tokens (int, default = 512): the maximum number of tokens that can be generated in the TLM response (and in internal trustworthiness scoring).
        Higher values here may produce better (more reliable) TLM responses and trustworthiness scores, but at higher costs/runtimes.
        If you experience token/rate limit errors while using TLM, try lowering this number.
        For OpenAI models, this parameter must be between 64 and 4096. For Claude models, this parameter must be between 64 and 512.

        num_candidate_responses (int, default = 1): how many alternative candidate responses are internally generated by TLM.
        TLM scores the trustworthiness of each candidate response, and then returns the most trustworthy one.
        Higher values here can produce better (more accurate) responses from the TLM, but at higher costs/runtimes (and internally consumes more tokens).
        This parameter must be between 1 and 20.
        When it is 1, TLM simply returns a standard LLM response and does not attempt to auto-improve it.

        num_consistency_samples (int, default = 8): the amount of internal sampling to evaluate LLM response consistency.
        Must be between 0 and 20. Higher values produce more reliable TLM trustworthiness scores, but at higher costs/runtimes.
        This consistency helps quantify the epistemic uncertainty associated with
        strange prompts or prompts that are too vague/open-ended to receive a clearly defined 'good' response.
        TLM internally measures consistency via the degree of contradiction between sampled responses that the model considers equally plausible.

        use_self_reflection (bool, default = `True`): whether the LLM is asked to self-reflect upon the response it
        generated and self-evaluate this response.
        Setting this False disables self-reflection and may worsen trustworthiness scores, but will reduce costs/runtimes.
        Self-reflection helps quantify aleatoric uncertainty associated with challenging prompts
        and catches answers that are obviously incorrect/bad.

        similarity_measure ({"semantic", "string", "embedding", "embedding_large"}, default = "semantic"): how the trustworthiness scoring algorithm measures
        similarity between sampled responses considered by the model in the consistency assessment.
        Supported similarity measures include "semantic" (based on natural language inference), "string" (based on character/word overlap),
        "embedding" (based on embedding similarity), and "embedding_large" (based on embedding similarity with a larger embedding model).
        Set this to "string" to improve latency/costs.

        reasoning_effort ({"none", "low", "medium", "high"}, default = "high"): how much the LLM can reason (number of thinking tokens)
        when considering alternative possible responses and double-checking responses.
        Higher efforts here may produce better TLM trustworthiness scores and LLM responses. Reduce this value to improve latency/costs.

        log (list[str], default = []): optionally specify additional logs or metadata that TLM should return.
        For instance, include "explanation" here to get explanations of why a response is scored with low trustworthiness.

        custom_eval_criteria (list[dict[str, Any]], default = []): optionally specify custom evalution criteria.
        The expected input format is a list of dictionaries, where each dictionary has the following keys:
        - name: Name of the evaluation criteria.
        - criteria: Instructions specifying the evaluation criteria.
    """

    model: NotRequired[str]
    max_tokens: NotRequired[int]
    num_candidate_responses: NotRequired[int]
    num_consistency_samples: NotRequired[int]
    use_self_reflection: NotRequired[bool]
    similarity_measure: NotRequired[str]
    reasoning_effort: NotRequired[str]
    log: NotRequired[list[str]]
    custom_eval_criteria: NotRequired[list[dict[str, Any]]]
