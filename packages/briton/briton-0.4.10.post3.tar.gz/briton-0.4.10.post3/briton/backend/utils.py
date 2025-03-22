from typing import AsyncGenerator

from briton.proto import InferenceAnswerPart


async def collate_inference_answer_parts(
    response_stream: AsyncGenerator[InferenceAnswerPart, None]
) -> InferenceAnswerPart:
    """Creates a complete inference answer from a stream of partial answers."""
    inference_answer = InferenceAnswerPart()
    inference_answer_part = None
    async for inference_answer_part in response_stream:
        inference_answer.output_text += inference_answer_part.output_text
        inference_answer.output_ids.extend(inference_answer_part.output_ids)
        inference_answer.top_logprobs.extend(inference_answer_part.top_logprobs)
    if inference_answer_part is not None:
        inference_answer.finish_reason = inference_answer_part.finish_reason
    return inference_answer
