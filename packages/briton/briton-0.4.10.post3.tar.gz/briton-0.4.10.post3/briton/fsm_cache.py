import asyncio
import hashlib
import json
import logging
import multiprocessing
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Dict, Optional, cast

from fastapi import HTTPException
from outlines.fsm.guide import RegexGuide
from outlines.models.transformers import TransformerTokenizer
from outlines.processors.structured import JSONLogitsProcessor
from transformers import PreTrainedTokenizerFast

from briton.fs import list_files, safe_mkdir
from briton.proto import StatesToTokens, TokenToNextState

logger = logging.getLogger(__name__)

# This must be defined globally to be used in the forked processes
outlines_tokenizer = None


def _create_states_to_tokens_pb(
    vocab_size: int, end_id: int, tools_id: Optional[int], schema: Dict[str, Any], output_path: Path
):
    """
    Create FSM and serialize to protobuf string.

    Args:
        vocab_size (int): The size of the vocabulary.
        end_id (int): The end-of-sequence token ID.
        schema (Dict[str, Any]): The schema used by the JSONLogitsProcessor.
        output_path (Path): The path to write to.
    """
    try:
        assert outlines_tokenizer is not None
        logits_processor = JSONLogitsProcessor(schema, outlines_tokenizer)
        guide = cast(RegexGuide, logits_processor.guide)
        states_to_tokens = {}
        for state, token_to_next_state in guide.get_index_dict().items():
            states_to_tokens[state] = TokenToNextState(token_to_next_state=token_to_next_state)
        states_to_tokens_pb = StatesToTokens(
            states_to_tokens=states_to_tokens,
            vocab_size=vocab_size,
            eos_token_id=end_id,
            tools_id=tools_id,
        )
        output_path.write_bytes(states_to_tokens_pb.SerializeToString())
    except Exception as e:
        logger.error(f"An error occurred generating the fsm: {str(e)}")
        raise


def create_states_to_tokens_pb(
    vocab_size: int,
    end_id: int,
    tools_id: Optional[int],
    schema: Dict[str, Any],
    output_path: Path,
    timeout: Optional[float],
):
    p = multiprocessing.Process(
        target=_create_states_to_tokens_pb, args=(vocab_size, end_id, tools_id, schema, output_path)
    )
    p.start()
    p.join(timeout=timeout)

    if p.is_alive():
        p.kill()
        p.join()
        raise FsmTimeoutError()

    if p.exitcode != 0:
        raise FsmCreationError()


class FsmCreationError(Exception):
    pass


class FsmTimeoutError(Exception):
    pass


def dummy_task():
    pass


class FsmCache:
    def __init__(
        self,
        cache_dir: Path,
        tokenizer: PreTrainedTokenizerFast,
        tools_id: Optional[int],
    ):
        self._cache_dir = cache_dir
        safe_mkdir(self._cache_dir)
        self._tmp_dir = Path("/cache/model/tmp")
        safe_mkdir(self._tmp_dir)
        self._cache = set(list_files(self._cache_dir))
        self._tokenizer = tokenizer
        self._vocab_size = len(getattr(self._tokenizer, "vocab"))
        self._eos_token_id = getattr(self._tokenizer, "eos_token_id")
        self._tools_id = tools_id

        global outlines_tokenizer
        outlines_tokenizer = TransformerTokenizer(tokenizer)  # type: ignore
        _ = JSONLogitsProcessor({"properties": {}}, outlines_tokenizer)
        self._executor = ProcessPoolExecutor(max_workers=32)
        # We must create all processes BEFORE the GRPC python client is started to avoid errors
        # forking from the process GRPC is running in
        for _ in range(32):
            self._executor.submit(dummy_task)

    @property
    def cache_dir(self) -> str:
        return str(self._cache_dir)

    async def add_schema(self, schema: Dict[str, Any], timeout: Optional[float] = None) -> str:
        schema_str = json.dumps(schema)
        schema_hash = hashlib.sha256(schema_str.encode()).hexdigest()
        if schema_hash not in self._cache:
            schema_path = self._cache_dir / schema_hash
            if not schema_path.exists():
                with tempfile.NamedTemporaryFile(dir=self._tmp_dir, delete=False) as f:
                    loop = asyncio.get_running_loop()
                    tmp_path = Path(f.name)
                    try:
                        await loop.run_in_executor(
                            self._executor,
                            create_states_to_tokens_pb,
                            self._vocab_size,
                            self._eos_token_id,
                            self._tools_id,
                            schema,
                            tmp_path,
                            timeout,
                        )
                    except (FsmCreationError, FsmTimeoutError):
                        tmp_path.unlink(missing_ok=True)
                        raise
                    await asyncio.to_thread(tmp_path.replace, schema_path)
            self._cache.add(schema_hash)
        return schema_hash


async def add_schema_to_cache(fsm_cache: FsmCache, schema: Dict[str, Any], timeout: float) -> str:
    try:
        schema_hash = await fsm_cache.add_schema(schema=schema, timeout=timeout)
    except FsmCreationError:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process schema. Please ensure the schema is valid.",
        )
    except FsmTimeoutError:
        logger.error(f"FSM generation timed out for schema {json.dumps(schema)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process schema. Generation timed out. Please ensure the schema is valid and avoid maxItems/minItems.",
        )
    return schema_hash
