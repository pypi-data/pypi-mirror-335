# TODO(pankaj) Pick this from truss constants, once a small lib is extracted out of truss.
import random
import os
import string

OPENAI_NON_COMPATIBLE_TAG = "force-legacy-api-non-openai-compatible"
OPENAI_COMPATIBLE_TAG = "openai-compatible"
DEFAULT_BRITON_PORT = 50051
DEFAULT_TP_COUNT = 1

# Use a directory that can be picked up by baseten-fs, if enabled
FSM_CACHE_DIR = "/cache/model/fsm_cache"
FSM_CREATION_TIMEOUT = 90

# Directory where huggingface config.json files are uploaded by engine-builder.
# identical to engine-builder config.json
TOKENIZATION_DIR = "tokenization"


TOOL_CALL_IDS = {
    "llama": 128010,
    "mistral": 5,
    "palmyra": 151657,
    "qwen": 151657,
}

TOOL_CALL_TOKENS = {
    "llama": "<|python_tag|>",
    "mistral": "[TOOL_CALLS]",
    "palmyra": "<tool_call>",
    "qwen": "<tool_call>",
}

ALPHANUMERIC_CHARS = string.ascii_letters + string.digits

# vLLM uses the format `chatcmpl-tool-` followed by a length 32
# alphanumeric string: chatcmpl-tool-ace101101c7149f2b0ef11d5ef6bf694
#
# Note that Llama and its variants don't internally use the tool call id,
# so this id could be anything.
#
# Mistral's chat template expects a length 9 alphanumeric string, so we can't
# use the vLLM tool call id style.
MISTRAL_TOOL_CALL_ID_FN = lambda: "".join(random.choices(ALPHANUMERIC_CHARS, k=9))
VLLM_TOOL_CALL_ID_FN = lambda: "chatcmpl-tool-" + "".join(random.choices(ALPHANUMERIC_CHARS, k=32))
TOOL_CALL_ID_FNS = {
    "llama": VLLM_TOOL_CALL_ID_FN,
    "mistral": MISTRAL_TOOL_CALL_ID_FN,
    "palmyra": VLLM_TOOL_CALL_ID_FN,
    "qwen": VLLM_TOOL_CALL_ID_FN,
}

MODEL_INPUT_TO_BRITON_FIELD = {
    "max_tokens": "request_output_len",
    "beam_width": "beam_width",
    "repetition_penalty": "repetition_penalty",
    "presence_penalty": "presence_penalty",
    "temperature": "temperature",
    "length_penalty": "len_penalty",
    "end_id": "end_id",
    "pad_id": "pad_id",
    "runtime_top_k": "runtime_top_k",
    "runtime_top_p": "runtime_top_p",
    "random_seed": "random_seed",
    "stop_words": "stop_words",
    "bad_words": "bad_words",
}

# TODO(bdubayah): Don't hardcode this
LOCAL_PREDICT_ENDPOINT = "http://localhost:8080/v1/models/model:predict"

UINT32_MAX = 2**32 - 1

BRITON_DEFAULT_MAX_TOKENS = 50

TRT_CONFIG_FILENAME = "config.json"

ENABLE_EXECUTOR_API = "ENABLE_EXECUTOR_API"
EXECUTOR_API_ENABLED = (
    os.environ.get(ENABLE_EXECUTOR_API, "false").lower() == "true"
    or os.environ.get(ENABLE_EXECUTOR_API, "false").lower() == "1"
    or os.environ.get(ENABLE_EXECUTOR_API, "false").lower() == "yes"
)
