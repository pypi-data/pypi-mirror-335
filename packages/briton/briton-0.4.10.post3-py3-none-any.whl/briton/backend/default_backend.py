import logging
import time
from pathlib import Path
from typing import Any, AsyncGenerator, Awaitable, Callable, Dict, Optional, Union

from openai.types.chat import ChatCompletion
from openai.types.completion import Completion

from briton.backend.backend_types import (
    InferBackend,
    LazyLoadParams,
    LoadParams,
    RequestDetails,
)
from briton.backend.briton_request import (
    model_input_to_briton_request,
    openai_spec_response,
)
from briton.data_structures import or_default, or_false
from briton.proto import InferenceRequest
from briton.proto import InferenceAnswerPart, InferenceRequest
from briton.schema import ModelInput

logger = logging.getLogger(__name__)


class DefaultBackend(InferBackend):
    """Regular OpenAI spec support backend."""

    def __init__(self):
        self._tokenizer = None
        self._briton_stub = None
        self._generate_request_id = None
        self._config = None

    def load(self, load_params: LoadParams) -> None:
        self._tokenizer = load_params.tokenizer
        self._generate_request_id = load_params.generate_request_id
        self._config = load_params.config

    async def lazy_load(self, lazy_load_params: LazyLoadParams) -> None:
        self._briton_stub = lazy_load_params.briton_stub

    async def accepts_request(self, model_input: ModelInput) -> Optional[RequestDetails]:
        if self._config is None or self._tokenizer is None:
            return None

        if not self._config.is_openai_compatible:
            return None

        input_ids = model_input.input_ids(self._tokenizer)
        return RequestDetails(input_ids=input_ids)

    async def _generate(
        self,
        request: InferenceRequest,
        model_input: ModelInput,
        is_cancelled: Callable[[], Awaitable[bool]],
    ) -> AsyncGenerator[InferenceAnswerPart, None]:
        if self._config is None or self._briton_stub is None:
            raise ValueError("Model is not loaded.")

        settings = self._config.chunked_generation_settings

        if (
            settings is not None
            and request.request_output_len >= settings.single_request_max_tokens
            and len(request.input_ids) >= settings.input_length_cutoff
        ):
            return self._generate_chunked(request, model_input, is_cancelled)
        else:
            return self._briton_stub.Infer(request)

    async def _generate_chunked(
        self,
        request: InferenceRequest,
        model_input: ModelInput,
        is_cancelled: Callable[[], Awaitable[bool]],
    ) -> AsyncGenerator[InferenceAnswerPart, None]:
        if self._config is None or self._briton_stub is None:
            raise ValueError("Model is not loaded.")

        logger.info("Starting chunked generation for request %d.", request.request_id)
        settings = self._config.chunked_generation_settings
        assert settings is not None

        start = time.time()
        tokens_to_generate = request.request_output_len
        if request.output_schema_hash is not None:
            request.write_output_states = True

        generated_tokens = 0
        while True:
            output_text = ""
            output_ids = []
            output_states = []

            logger.info(
                "%d tokens remaining for request %d.", tokens_to_generate, request.request_id
            )
            request.request_output_len = min(settings.single_request_max_tokens, tokens_to_generate)

            async for part in self._briton_stub.Infer(request):
                yield part
                output_text += part.output_text
                output_ids.extend(part.output_ids)
                output_states.extend(part.output_states)

            tokens_to_generate -= len(output_ids)
            generated_tokens += len(output_ids)
            request.input_ids.extend(output_ids)
            if len(output_states) > 0:
                request.fsm_state = output_states[-1]

            if len(output_ids) < settings.single_request_max_tokens:
                logger.info(
                    "Generated less than single_request_max_tokens. Stopping request %d.",
                    request.request_id,
                )
                break
            if tokens_to_generate < 1:
                break
            if output_ids[-1] == request.end_id:
                logger.info("Found eos. Stopping request %d.", request.request_id)
                break
            if output_text.endswith(tuple(request.stop_words)):
                logger.info("Found stop words. Stopping request %d.", request.request_id)
                break
            if await is_cancelled():
                logger.info(
                    "Request cancelled. Stopping request %d. Generated %d tokens,",
                    request.request_id,
                    generated_tokens,
                )
                input_str = model_input.model_dump_json()
                dir = Path("/app/timeouts")
                dir.mkdir(parents=True, exist_ok=True)
                file_path = dir / f"{request.request_id}.json"
                file_path.write_text(input_str)
                break
            if time.time() - start > settings.timeout_secs:
                logger.warning("Request stopped after %d seconds", int(time.time() - start))
                break

    async def infer(
        self,
        model_input: ModelInput,
        is_cancelled: Callable[[], Awaitable[bool]],  # TODO(pankaj) Wire up request cancellation
        add_schema_to_cache: Callable[[Dict[str, Any]], Awaitable[str]],
        resolve_lora: Optional[Callable[[str], Optional[int]]],
        request_details: RequestDetails,
    ) -> Union[AsyncGenerator[str, None], ChatCompletion, Completion]:
        if (
            self._config is None
            or self._tokenizer is None
            or self._briton_stub is None
            or self._generate_request_id is None
        ):
            raise ValueError("Model is not loaded.")

        input_ids = request_details.input_ids
        if input_ids is None:
            raise ValueError("Input ids are None.")

        request_id = self._generate_request_id()
        briton_request = await model_input_to_briton_request(
            request_id=request_id,
            model_input=model_input,
            input_ids=input_ids,
            tokenizer_eos_token_id=self._tokenizer.eos_token_id,
            tokenizer_pad_token_id=self._tokenizer.pad_token_id,
            add_schema_to_cache=add_schema_to_cache,
            resolve_lora=resolve_lora,
            default_max_tokens=self._config.default_max_tokens,
            max_seq_len=self._config.max_seq_len,
        )

        # TODO(@bdubayah): replace with num_return_sequences in Briton
        # This is a workaround to send n requests, which would be equivalent to
        # sampling n return sequences in the same request
        response_streams = [await self._generate(briton_request, model_input, is_cancelled)]
        if model_input.n is not None and model_input.n > 1:
            for _ in range(1, model_input.n):
                new_request = InferenceRequest()
                new_request.CopyFrom(briton_request)
                new_request.request_id = self._generate_request_id()
                new_request.random_seed = new_request.random_seed + 1
                response_streams.append(
                    await self._generate(new_request, model_input, is_cancelled)
                )

        return await openai_spec_response(
            response_streams=response_streams,
            request_id=str(request_id),
            num_input_ids=len(input_ids),
            streaming=or_false(model_input.stream),
            eos_token=self._tokenizer.eos_token,
            tool_call_token=self._config.tool_call_token,
            tool_call_id_fn=self._config.tool_call_id_fn,
            model_name=or_default(model_input.model, ""),
            include_stream_usage=model_input.include_stream_usage,
            stop_words=model_input.stop,
            skip_special_tokens=model_input.skip_special_tokens,
            tokenizer=self._tokenizer,
            top_logprobs=model_input.top_logprobs,
            is_chat_completion=model_input._is_chat_completion,
        )
