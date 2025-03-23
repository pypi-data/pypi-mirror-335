import os
from typing import Dict, Any

from ray.serve import Application
from vllm.model_executor.model_loader.tensorizer import TensorizerConfig

from vllm_model import VLLMModel


def deploy_model(args: Dict[str, Any]) -> Application:
    assert args
    deployment_name = args.pop("deployment", None)
    assert deployment_name

    model: str = args.pop("model", "")
    assert model
    served_model_name = args.pop("served_model_name", os.path.basename(model))
    assert served_model_name
    if not isinstance(served_model_name, list):
        served_model_name = [served_model_name]

    multimodal = args.pop("multimodal", False)
    load_format = args.pop("load_format", "")
    model_tensors_uri = args.pop("model_tensors_uri", "")
    tensorizer_num_readers = args.pop("tensorizer_num_readers", 3)
    trust_remote_code = args.pop("trust_remote_code", False)
    enforce_eager = args.pop("enforce_eager", True)
    tensor_parallel_size = args.pop("tensor_parallel_size", 1)
    max_model_len = args.pop("max_model_len", 4096)
    gpu_memory_utilization = args.pop("gpu_memory_utilization", 0.9)
    swap_space = args.pop("swap_space", 2)
    enable_chunked_prefill = args.pop("enable_chunked_prefill", False)
    limit_mm_per_prompt = args.pop("limit_mm_per_prompt", {})
    assert isinstance(limit_mm_per_prompt, dict)

    engine_args = dict(model=model,
                       served_model_name=served_model_name,
                       trust_remote_code=trust_remote_code,
                       enforce_eager=enforce_eager,
                       tensor_parallel_size=tensor_parallel_size,
                       max_model_len=max_model_len,
                       gpu_memory_utilization=gpu_memory_utilization,
                       swap_space=swap_space,
                       enable_chunked_prefill=enable_chunked_prefill
                       )

    if multimodal:
        if not limit_mm_per_prompt:
            limit_mm_per_prompt = {'image': 1, 'video': 0}
        engine_args["limit_mm_per_prompt"] = limit_mm_per_prompt

    if load_format == "tensorizer":
        # Config for CoreWeave's tensorizer tool
        assert model_tensors_uri
        tensorizer_config = TensorizerConfig(tensorizer_uri=model_tensors_uri, num_readers=tensorizer_num_readers)
        engine_args["load_format"] = load_format
        engine_args["model_loader_extra_config"] = tensorizer_config

    if args:
        # If there are any leftover args, copy them over
        engine_args.update(args)

    deployment = VLLMModel.options(name=deployment_name).bind(engine_args)
    return deployment
