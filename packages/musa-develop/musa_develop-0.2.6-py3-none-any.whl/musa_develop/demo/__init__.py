from .demo import (
    TorchMusaDeployer,
    vLLMDeployer,
    KuaeDeployer,
    OllamaDeployer,
)

from musa_develop.check.utils import CheckModuleNames

DEMO = dict()
DEMO[CheckModuleNames.torch_musa.name] = TorchMusaDeployer()
DEMO[CheckModuleNames.vllm.name] = vLLMDeployer()
DEMO["kuae"] = KuaeDeployer()
DEMO["ollama"] = OllamaDeployer()
