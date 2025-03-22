import logging
import time
from pathlib import Path
from typing import Dict, Optional

import grpc
import numpy as np

from briton.constants import DEFAULT_BRITON_PORT
from briton.fs import list_dirs, safe_mkdir
from briton.proto import BritonStub, DataType, InferenceRequest, Tensor

LORA_CONFIG_FILENAME = "model.lora_config.npy"
LORA_WEIGHTS_FILENAME = "model.lora_weights.npy"

NP_TO_BRITON_DTYPE = {
    np.int8: DataType.DT_INT8,
    np.uint8: DataType.DT_UINT8,
    np.int32: DataType.DT_INT32,
    np.int64: DataType.DT_INT64,
    np.float16: DataType.DT_FLOAT16,
    np.float32: DataType.DT_FLOAT32,
    np.bool_: DataType.DT_BOOL,
}

logger = logging.getLogger(__name__)


class LoraNotFoundException(Exception):
    pass


class LoraInvalidException(Exception):
    pass


class LoraCache:
    def __init__(self, base_model_name: str, loras_dir: Path):
        logger.info("Lora is enabled.")

        self._base_model_name = base_model_name
        self._loras_dir = loras_dir
        safe_mkdir(self._loras_dir)
        self._loaded_loras: Dict[str, int] = {}

        channel = grpc.insecure_channel(f"localhost:{DEFAULT_BRITON_PORT}")
        stub = BritonStub(channel)
        for i, lora_name in enumerate(list_dirs(self._loras_dir)):
            lora_task_id = i + 1
            self._load_lora(lora_name=lora_name, lora_task_id=lora_task_id, stub=stub)
        channel.close()

    def resolve_lora(self, lora_name: str) -> Optional[int]:
        if lora_name == self._base_model_name:
            return None
        if lora_name not in self._loaded_loras:
            raise LoraNotFoundException
        return self._loaded_loras[lora_name]

    def _load_lora(self, lora_name: str, lora_task_id: int, stub: BritonStub) -> None:
        logger.info(f"Loading LoRA {lora_name}...")
        start = time.time()

        if lora_name == self._base_model_name:
            raise LoraInvalidException

        lora_config = self._load_tensor(self._loras_dir / lora_name / LORA_CONFIG_FILENAME)
        lora_weights = self._load_tensor(self._loras_dir / lora_name / LORA_WEIGHTS_FILENAME)

        request = InferenceRequest(
            request_id=1,
            input_text=" ",
            request_output_len=1,
        )
        request.lora_task_id = lora_task_id
        request.lora_config.CopyFrom(lora_config)
        request.lora_weights.CopyFrom(lora_weights)

        for _ in stub.Infer(request):
            pass

        self._loaded_loras[lora_name] = lora_task_id

        stop = time.time()
        logger.info(f"Loaded LoRA {lora_name} in {stop - start}s!")

    @staticmethod
    def _load_tensor(np_tensor_path: Path) -> Tensor:
        if not np_tensor_path.exists():
            raise LoraInvalidException
        data = np.load(np_tensor_path, allow_pickle=True)
        tensor = Tensor()
        tensor.shape.dim.extend(data.shape)
        tensor.data = data.tobytes()
        tensor.dtype = NP_TO_BRITON_DTYPE[data.dtype.type]
        return tensor
