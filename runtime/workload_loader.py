import json
from typing import List, Tuple, Dict, Any
from runtime.request import Request

def load_workload(file_path: str) -> Tuple[List[Request], Dict[str, Any]]:
    with open(file_path, "r") as file:
        data = json.load(file)

    # extract model config
    model_cfg = data.get("model_config", {})
    num_layers = model_cfg.get("num_layers", 32)
    num_heads_kv = model_cfg.get("num_heads_kv", 8)
    head_dim = model_cfg.get("head_dim", 128)
    dtype_bytes = model_cfg.get("dtype_bytes", 2)
    block_size = model_cfg.get("block_size_tokens", 16)

    # Total KV Cache per token across all layers (2 for K and V)
    bytes_per_token = 2 * num_layers * num_heads_kv * head_dim * dtype_bytes
    block_size_bytes = block_size * bytes_per_token

    model_metadata = {
        "name": model_cfg.get("name", "custom"),
        "bytes_per_token": bytes_per_token,
        "block_size_bytes": block_size_bytes,
        "block_size_tokens": block_size
    }

    # extract requests and compute required KV blocks
    requests: List[Request] = []
    for item in data.get("requests", []):
        total_tokens = item["prompt_tokens"] + item["output_tokens"]
        calculated_kv_blocks = (total_tokens + block_size - 1) // block_size

        req = Request(
            request_id=item["request_id"],
            arrival_time=item["arrival_time"],
            prompt_tokens=item["prompt_tokens"],
            output_tokens=item["output_tokens"],
            slo_deadline=item["slo_deadline"],
            kv_blocks=calculated_kv_blocks
        )
        requests.append(req)

    return requests, model_metadata