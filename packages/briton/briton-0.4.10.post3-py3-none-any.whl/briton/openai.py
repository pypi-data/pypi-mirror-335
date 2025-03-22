import json
import logging
import time
from json import JSONDecodeError
from typing import Any, AsyncGenerator, Callable, List, Literal, Optional, Tuple

import openai.types.chat.chat_completion as chat_completion
import openai.types.chat.chat_completion_chunk as chat_completion_chunk
from fastapi import HTTPException
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)
from openai.types.chat.chat_completion_token_logprob import (
    ChatCompletionTokenLogprob,
    TopLogprob,
)
from openai.types.completion import Completion
from openai.types.completion_choice import CompletionChoice
from openai.types.completion_usage import CompletionUsage
from transformers import PreTrainedTokenizerFast

from briton.async_util import interleave_generators
from briton.proto import FinishReason, InferenceAnswerPart

logger = logging.getLogger(__name__)


def _load_content_json(content: str) -> Any:
    """Safely load the content json from the input text."""
    try:
        return json.loads(content)
    except JSONDecodeError:
        raise HTTPException(status_code=400, detail="Tool call was cut off by max_tokens.")


def _create_tool_calls(
    content: str,
    tool_call_id_fn: Callable[[], str],
) -> List[ChatCompletionMessageToolCall]:
    content_json = _load_content_json(content)
    tool_calls = []
    for briton_fn in content_json:
        fn = Function(name=briton_fn["name"], arguments=json.dumps(briton_fn["parameters"]))
        tool_call = ChatCompletionMessageToolCall(
            id=tool_call_id_fn(), function=fn, type="function"
        )
        tool_calls.append(tool_call)
    return tool_calls


def _finish_reason_from_text(
    text: str, eos_token: Optional[str] = None, stop_words: Optional[List[str]] = None
) -> Literal["stop", "length"]:
    if eos_token and text.endswith(eos_token):
        return "stop"
    if stop_words and text.endswith(tuple(stop_words)):
        return "stop"
    return "length"


def _finish_reason_from_inference_answer_part(
    inference_answer_part: InferenceAnswerPart,
    eos_token: Optional[str] = None,
    stop_words: Optional[List[str]] = None,
) -> Literal["stop", "length"]:
    if inference_answer_part.finish_reason != FinishReason.NOT_FINISHED:
        return "length" if inference_answer_part.finish_reason == FinishReason.LENGTH else "stop"
    else:
        return _finish_reason_from_text(inference_answer_part.output_text, eos_token, stop_words)


def remove_suffix_from_text(
    text: str,
    eos_token: Optional[str] = None,
    stop_words: Optional[List[str]] = None,
    skip_special_tokens: Optional[List[str]] = None,
) -> str:
    if eos_token is not None and text.endswith(eos_token):
        return text.removesuffix(eos_token)
    if stop_words is not None:
        for stop_word in stop_words:
            if text.endswith(stop_word):
                return text.removesuffix(stop_word)
    # HACK (bdubayah): this could end up being very expensive.
    if skip_special_tokens is not None:
        for special_token in skip_special_tokens:
            text = text.replace(special_token, "")
    return text


def _create_choice(
    index: int,
    inference_answer: InferenceAnswerPart,
    tokenizer: PreTrainedTokenizerFast,
    eos_token: Optional[str],
    tool_token: Optional[str],
    tool_call_id_fn: Optional[Callable[[], str]],
    stop_words: Optional[List[str]],
    skip_special_tokens: Optional[List[str]],
    top_logprobs: Optional[int],
    is_chat_completion: bool,
) -> chat_completion.Choice:
    finish_reason = _finish_reason_from_inference_answer_part(
        inference_answer, eos_token, stop_words
    )
    content = remove_suffix_from_text(
        inference_answer.output_text, eos_token, stop_words, skip_special_tokens
    )
    if is_chat_completion:
        tool_calls = None
        if (
            tool_token is not None
            and tool_call_id_fn is not None
            and content.startswith(tool_token)
        ):
            finish_reason = "tool_calls"
            content = content.removeprefix(tool_token)
            tool_calls = _create_tool_calls(content, tool_call_id_fn)
            content = None
        message = ChatCompletionMessage(content=content, role="assistant", tool_calls=tool_calls)
        logprobs_content = _create_choice_log_probs(inference_answer, top_logprobs, tokenizer)
        logprobs = (
            chat_completion.ChoiceLogprobs(content=logprobs_content)
            if logprobs_content is not None
            else None
        )
        return chat_completion.Choice(
            finish_reason=finish_reason, index=index, message=message, logprobs=logprobs
        )
    else:
        if content is None:
            content = ""
        # TODO(@bdubayah): add logprobs to completions
        return CompletionChoice(finish_reason=finish_reason, index=index, text=content)


def create_completion(
    req_id: str,
    model: str,
    inference_answers: List[InferenceAnswerPart],
    tokenizer: PreTrainedTokenizerFast,
    eos_token: Optional[str] = None,
    tool_token: Optional[str] = None,
    tool_call_id_fn: Optional[Callable[[], str]] = None,
    prompt_tokens: Optional[int] = None,
    completion_tokens: Optional[int] = None,
    stop_words: Optional[List[str]] = None,
    skip_special_tokens: Optional[List[str]] = None,
    top_logprobs: Optional[int] = None,
    is_chat_completion: bool = False,
) -> ChatCompletion:
    created = int(time.time())
    choices = []
    for i, inference_answer in enumerate(inference_answers):
        choice = _create_choice(
            index=i,
            inference_answer=inference_answer,
            tokenizer=tokenizer,
            eos_token=eos_token,
            tool_token=tool_token,
            tool_call_id_fn=tool_call_id_fn,
            stop_words=stop_words,
            skip_special_tokens=skip_special_tokens,
            top_logprobs=top_logprobs,
            is_chat_completion=is_chat_completion,
        )
        choices.append(choice)
    usage = None
    if prompt_tokens is not None and completion_tokens is not None:
        usage = CompletionUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )
    if is_chat_completion:
        return ChatCompletion(
            id=req_id,
            choices=choices,
            created=created,
            model=model,
            object="chat.completion",
            usage=usage,
        )
    else:
        return Completion(
            id=req_id,
            choices=choices,
            created=created,
            model=model,
            object="text_completion",
            usage=usage,
        )


def _make_sse_chunk(chunk: ChatCompletionChunk | Completion) -> str:
    return f"data: {chunk.model_dump_json()}\n\n"


async def _chunk_args(args_str: str) -> AsyncGenerator[str, None]:
    chunk = ""
    for char in args_str:
        chunk += char
        if char == " ":
            yield chunk
            chunk = ""
    if chunk:
        yield chunk


async def _create_tool_call_deltas(
    content: str,
    tool_call_id_fn: Callable[[], str],
) -> AsyncGenerator[chat_completion_chunk.ChoiceDeltaToolCall, None]:
    content_json = _load_content_json(content)
    for i, briton_fn in enumerate(content_json):
        if not (isinstance(briton_fn, dict) and "name" in briton_fn and "parameters" in briton_fn):
            logger.error(f"Generated tool calls {content_json} are not valid")
            continue

        name_delta = chat_completion_chunk.ChoiceDeltaToolCall(
            index=i,
            id=tool_call_id_fn(),
            function=chat_completion_chunk.ChoiceDeltaToolCallFunction(name=briton_fn["name"]),
            type="function",
        )
        yield name_delta

        args_str = json.dumps(briton_fn["parameters"])
        async for chunk in _chunk_args(args_str):
            args_delta = chat_completion_chunk.ChoiceDeltaToolCall(
                index=i,
                function=chat_completion_chunk.ChoiceDeltaToolCallFunction(arguments=chunk),
                type="function",
            )
            yield args_delta


def _get_token_and_bytes(
    token_id: int, tokenizer: PreTrainedTokenizerFast
) -> Tuple[str, List[int]]:
    token = tokenizer.convert_ids_to_tokens(token_id)
    assert isinstance(token, str)
    token_bytes = list(token.encode("utf-8"))
    return token, token_bytes


def _create_choice_log_probs(
    inference_answer_part: InferenceAnswerPart,
    top_logprobs: Optional[int],
    tokenizer: PreTrainedTokenizerFast,
) -> Optional[List[ChatCompletionTokenLogprob]]:
    num_top_logprobs = len(inference_answer_part.top_logprobs)
    num_output_ids = len(inference_answer_part.output_ids)
    if num_top_logprobs == 0 or num_output_ids != num_top_logprobs:
        return None
    content: List[ChatCompletionTokenLogprob] = []
    for token_id, top_logprobs_proto in zip(
        inference_answer_part.output_ids, inference_answer_part.top_logprobs
    ):
        top_logprobs_list = []
        if top_logprobs is not None and top_logprobs > 0:
            for child_token_id, child_logprob in top_logprobs_proto.logprobs.items():
                child_token, child_token_bytes = _get_token_and_bytes(child_token_id, tokenizer)
                top_logprob = TopLogprob(
                    token=child_token, bytes=child_token_bytes, logprob=child_logprob
                )
                top_logprobs_list.append(top_logprob)
        token, token_bytes = _get_token_and_bytes(token_id, tokenizer)
        token_logprob = ChatCompletionTokenLogprob(
            token=token,
            logprob=top_logprobs_proto.logprob,
            bytes=token_bytes,
            top_logprobs=top_logprobs_list,
        )
        content.append(token_logprob)
    return content


def _create_completion_chunk(
    id: str,
    created: int,
    index: int,
    model: str,
    is_chat_completion: bool,
    content: Optional[str] = None,
    role: Optional[Literal["system", "user", "assistant", "tool"]] = None,
    finish_reason: Optional[
        Literal["stop", "length", "tool_calls", "content_filter", "function_call"]
    ] = None,
    tool_calls: Optional[List[chat_completion_chunk.ChoiceDeltaToolCall]] = None,
    logprobs: Optional[chat_completion_chunk.ChoiceLogprobs] = None,
) -> ChatCompletionChunk | Completion:
    if is_chat_completion:
        delta = chat_completion_chunk.ChoiceDelta(content=content, role=role, tool_calls=tool_calls)
        choice = chat_completion_chunk.Choice(
            index=index, delta=delta, finish_reason=finish_reason, logprobs=logprobs
        )
        return ChatCompletionChunk(
            id=id,
            choices=[choice],
            created=created,
            model=model,
            object="chat.completion.chunk",
        )
    else:
        if content is None:
            content = ""
        if finish_reason is None:
            finish_reason = "length"
        choice = CompletionChoice(index=index, text=content, finish_reason=finish_reason)
        return Completion(
            id=id,
            choices=[choice],
            created=created,
            model=model,
            object="text_completion",
        )


async def _create_completion_chunks(
    created: int,
    req_id: str,
    index: int,
    model: str,
    response_stream: AsyncGenerator[InferenceAnswerPart, None],
    tokenizer: PreTrainedTokenizerFast,
    eos_token: Optional[str],
    tool_token: Optional[str],
    tool_call_id_fn: Optional[Callable[[], str]],
    stop_words: Optional[List[str]],
    skip_special_tokens: Optional[List[str]],
    top_logprobs: Optional[int],
    is_chat_completion: bool,
) -> AsyncGenerator[ChatCompletionChunk | Completion, None]:
    start_chunk = _create_completion_chunk(
        id=req_id,
        created=created,
        index=index,
        model=model,
        content="",
        role="assistant",
        is_chat_completion=is_chat_completion,
    )
    is_first_iter = True
    inference_answer_part = None
    async for inference_answer_part in response_stream:
        if is_first_iter:
            if tool_token is not None and inference_answer_part.output_text.startswith(tool_token):
                break
            is_first_iter = False
            yield start_chunk

        content = remove_suffix_from_text(
            text=inference_answer_part.output_text,
            eos_token=eos_token,
            stop_words=stop_words,
            skip_special_tokens=skip_special_tokens,
        )
        if len(content) == 0:
            continue  # Don't send empty chunks
        logprobs_content = _create_choice_log_probs(inference_answer_part, top_logprobs, tokenizer)
        logprobs = (
            chat_completion_chunk.ChoiceLogprobs(content=logprobs_content)
            if logprobs_content is not None
            else None
        )
        yield _create_completion_chunk(
            id=req_id,
            created=created,
            index=index,
            model=model,
            content=content,
            logprobs=logprobs,
            is_chat_completion=is_chat_completion,
        )

    if (
        is_first_iter
        and inference_answer_part is not None
        and tool_token is not None
        and tool_call_id_fn is not None
        and inference_answer_part.output_text.startswith(tool_token)
    ):
        full_text = inference_answer_part.output_text.removeprefix(tool_token)
        async for inference_answer_part in response_stream:
            full_text += inference_answer_part.output_text

        tool_calls = _create_tool_call_deltas(
            remove_suffix_from_text(
                text=full_text,
                eos_token=eos_token,
                stop_words=stop_words,
                skip_special_tokens=skip_special_tokens,
            ),
            tool_call_id_fn,
        )
        yield start_chunk
        async for tool_call_chunk in tool_calls:
            # TODO(@bdubayah): logprobs to streamed tool calls
            yield _create_completion_chunk(
                id=req_id,
                created=created,
                index=index,
                model=model,
                tool_calls=[tool_call_chunk],
                is_chat_completion=is_chat_completion,
            )
        finish_reason = "tool_calls"
    else:
        if inference_answer_part is None:
            finish_reason = "length"
        else:
            finish_reason = _finish_reason_from_inference_answer_part(
                inference_answer_part, eos_token, stop_words
            )

    yield _create_completion_chunk(
        id=req_id,
        created=created,
        index=index,
        model=model,
        finish_reason=finish_reason,
        is_chat_completion=is_chat_completion,
    )


async def create_completion_chunks(
    req_id: str,
    model: str,
    response_streams: List[AsyncGenerator[InferenceAnswerPart, None]],
    tokenizer: PreTrainedTokenizerFast,
    eos_token: Optional[str] = None,
    tool_token: Optional[str] = None,
    tool_call_id_fn: Optional[Callable[[], str]] = None,
    prompt_tokens: Optional[int] = None,
    completion_tokens_fn: Optional[Callable[[], int]] = None,
    stop_words: Optional[List[str]] = None,
    skip_special_tokens: Optional[List[str]] = None,
    top_logprobs: Optional[int] = None,
    is_chat_completion: bool = False,
) -> AsyncGenerator[str, None]:
    created = int(time.time())

    chunk_generators = [
        _create_completion_chunks(
            created=created,
            req_id=req_id,
            index=i,
            model=model,
            response_stream=response_stream,
            tokenizer=tokenizer,
            eos_token=eos_token,
            tool_token=tool_token,
            tool_call_id_fn=tool_call_id_fn,
            stop_words=stop_words,
            skip_special_tokens=skip_special_tokens,
            top_logprobs=top_logprobs,
            is_chat_completion=is_chat_completion,
        )
        for i, response_stream in enumerate(response_streams)
    ]
    async for chunk in interleave_generators(*chunk_generators):
        yield _make_sse_chunk(chunk)

    if prompt_tokens is not None and completion_tokens_fn is not None:
        completion_tokens = completion_tokens_fn()
        usage = CompletionUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )
        if is_chat_completion:
            usage_chunk = ChatCompletionChunk(
                id=req_id,
                choices=[],
                created=created,
                model=model,
                object="chat.completion.chunk",
                usage=usage,
            )
        else:
            usage_chunk = Completion(
                id=req_id,
                choices=[],
                created=created,
                model=model,
                object="text_completion",
                usage=usage,
            )
        yield _make_sse_chunk(usage_chunk)

    yield "data: [DONE]\n\n"
