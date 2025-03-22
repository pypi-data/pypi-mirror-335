from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Awaitable, Callable, Dict, List, Optional

from pydantic import BaseModel
from transformers import PreTrainedTokenizerFast

from briton.proto import BritonStub
from briton.schema import ModelInput


class BatchSchedulerPolicy(IntEnum):
    MAX_UTILIZATION = 0
    GUARANTEED_NO_EVICT = 1


class ChunkedGenerationSettings(BaseModel):
    timeout_secs: int  # Number of seconds to let the request running before stopping
    single_request_max_tokens: int  # Maximum number of tokens generated in single Briton request
    input_length_cutoff: int  # Input length below which to disable chunked generation


class BackendConfig(BaseModel):
    model_metadata: dict
    base_model: str
    tp: int = 1
    tokenizer_repo: str
    kv_cache_gpu_mem_fraction: float
    kv_cache_host_memory_bytes: Optional[int]
    enable_kv_cache_reuse: bool
    enable_chunked_context: bool
    max_num_tokens: Optional[int]
    max_seq_len: int

    batch_scheduler_policy: BatchSchedulerPolicy = BatchSchedulerPolicy.GUARANTEED_NO_EVICT
    default_max_tokens: Optional[int]
    tool_call_token: Optional[str]
    tool_call_token_id: Optional[int]
    tool_call_id_fn: Optional[Callable[[], str]]

    is_openai_compatible: bool = True

    chunked_generation_settings: Optional[ChunkedGenerationSettings]


@dataclass
class LoadParams:
    generate_request_id: Callable[[], int]
    tokenizer: PreTrainedTokenizerFast
    config: BackendConfig


@dataclass
class LazyLoadParams:
    briton_stub: BritonStub


class RequestDetails(BaseModel):
    input_ids: Optional[List[int]] = None
    num_input_ids: Optional[int] = None


class InferBackend(ABC):

    @abstractmethod
    def load(self, load_params: LoadParams):
        pass

    @abstractmethod
    async def lazy_load(self, lazy_load_params: LazyLoadParams):
        pass

    @abstractmethod
    async def accepts_request(self, model_input: ModelInput) -> Optional[RequestDetails]:
        """
        Whether this backend supports given request.

        :param model_input: model input
        :return: None if backend does not support the request,
            ParseRequestParams otherwise.
        """
        pass

    @abstractmethod
    async def infer(
        self,
        model_input: ModelInput,
        is_cancelled: Callable[[], Awaitable[bool]],
        add_schema_to_cache: Callable[[Dict[str, Any]], Awaitable[str]],
        resolve_lora: Optional[Callable[[str], Optional[int]]],
        request_details: RequestDetails,
    ) -> Any:
        """
        Similar to Truss's async predict function, this should return either a
        response(batch) or an async iterator(streaming). It should itself not be
        an async iterator.
        """
        pass
