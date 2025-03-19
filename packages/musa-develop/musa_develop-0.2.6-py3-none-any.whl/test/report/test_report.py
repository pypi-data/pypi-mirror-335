import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from test.utils import ReportTest


# 1. PyTorch OK
# 2. torch_musa Failed, but version from `pip list` is OK
# 3. TorchVision Failed, but version from `pip list` is OK
# 4. TorchAudio Failed, but version from `pip list` is OK
def test_torch_musa_report_simulation():
    simulation_log = {
        "PyTorch_version": [
            (["name: torch", "Version: 2.4.1"], "", 0),
            ("38b96d3399a695e704ed39b60dac733c3fbf20e2", "", 0),
        ],
        "PyTorch": ("", "", 0),
        "Torch_musa_version": [
            (["name: torch_musa", "Version: 1.3.0"], "", 0),
            (
                "",
                '/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py:28: UserWarning: torch version should be v2.0.0 when using torch_musa, but now torch version is 2.4.1+cu121\n  warnings.warn(\nTraceback (most recent call last):\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py", line 39, in <module>\n    import torch_musa._MUSAC\nImportError: /opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/lib/libmusa_kernels.so: undefined symbol: _ZNK2at10TensorBase14const_data_ptrIN3c107complexIfEEEEPKT_v\n\nThe above exception was the direct cause of the following exception:\n\nTraceback (most recent call last):\n  File "<string>", line 1, in <module>\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py", line 41, in <module>\n    raise ImportError("Please try running Python from a different directory!") from err\nImportError: Please try running Python from a different directory!\n',
                1,
            ),
        ],
        "Torch_musa": (
            "",
            '/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py:28: UserWarning: torch version should be v2.0.0 when using torch_musa, but now torch version is 2.4.1+cu121\n  warnings.warn(\nTraceback (most recent call last):\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py", line 39, in <module>\n    import torch_musa._MUSAC\nImportError: /opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/lib/libmusa_kernels.so: undefined symbol: _ZNK2at10TensorBase14const_data_ptrIN3c107complexIfEEEEPKT_v\n\nThe above exception was the direct cause of the following exception:\n\nTraceback (most recent call last):\n  File "/home/mccxadmin/caizhi/musa_develop/musa_develop/check/test/torch_musa_demo.py", line 1, in <module>\n    import torch, torch_musa  # noqa\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py", line 41, in <module>\n    raise ImportError("Please try running Python from a different directory!") from err\nImportError: Please try running Python from a different directory!\n',
            1,
        ),
        "TorchVision_version": [
            (["name: torchvision", "Version: 0.19.1"], "", 0),
            ("61943691d3390bd3148a7003b4a501f0e2b7ac6e", "", 0),
        ],
        "TorchVision": (
            "",
            '/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py:28: UserWarning: torch version should be v2.0.0 when using torch_musa, but now torch version is 2.4.1+cu121\n  warnings.warn(\nTraceback (most recent call last):\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py", line 39, in <module>\n    import torch_musa._MUSAC\nImportError: /opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/lib/libmusa_kernels.so: undefined symbol: _ZNK2at10TensorBase14const_data_ptrIN3c107complexIfEEEEPKT_v\n\nThe above exception was the direct cause of the following exception:\n\nTraceback (most recent call last):\n  File "/home/mccxadmin/caizhi/musa_develop/musa_develop/check/test/torchvision_demo.py", line 1, in <module>\n    import torch, torch_musa  # noqa\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py", line 41, in <module>\n    raise ImportError("Please try running Python from a different directory!") from err\nImportError: Please try running Python from a different directory!\n',
            1,
        ),
        "TorchAudio_version": [
            (["name: torchaudio", "Version: 2.2.2+cefdb36"], "", 0),
            (
                "",
                'Traceback (most recent call last):\n  File "<string>", line 1, in <module>\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torchaudio-2.2.2+cefdb36-py3.8-linux-x86_64.egg/torchaudio/__init__.py", line 2, in <module>\n    from . import _extension  # noqa  # usort: skip\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torchaudio-2.2.2+cefdb36-py3.8-linux-x86_64.egg/torchaudio/_extension/__init__.py", line 38, in <module>\n    _load_lib("libtorchaudio")\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torchaudio-2.2.2+cefdb36-py3.8-linux-x86_64.egg/torchaudio/_extension/utils.py", line 60, in _load_lib\n    torch.ops.load_library(path)\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch/_ops.py", line 1295, in load_library\n    ctypes.CDLL(path)\n  File "/opt/conda/envs/py38/lib/python3.8/ctypes/__init__.py", line 373, in __init__\n    self._handle = _dlopen(self._name, mode)\nOSError: /opt/conda/envs/py38/lib/python3.8/site-packages/torchaudio-2.2.2+cefdb36-py3.8-linux-x86_64.egg/torchaudio/lib/libtorchaudio.so: undefined symbol: _ZNK5torch8autograd4Node4nameB5cxx11Ev\n',
                1,
            ),
        ],
        "TorchAudio": (
            "",
            "/opt/conda/envs/py38/bin/python: can't open file '/home/mccxadmin/caizhi/musa_develop/musa_develop/check/test/torchaudio_demo.py': [Errno 2] No such file or directory\n",
            2,
        ),
    }
    ground_truth = """\
Torch_musa                                      Version: 1.3.0
TorchVision                                     Version: 0.19.1+6194369
TorchAudio                                      Version: 2.2.2+cefdb36"""
    ReportTest(simulation_log, ground_truth)


# 1. PyTorch OK
# 2. torch_musa Failed, but version from `pip list` is OK
# 3. TorchVision Failed, but version from `pip list` is OK
# 4. TorchAudio Failed, but version from `pip list` is OK
def test_torch_musa_report_git_version_simulation():
    simulation_log = {
        "PyTorch_version": [
            (["name: torch", "Version: 2.4.1"], "", 0),
            ("38b96d3399a695e704ed39b60dac733c3fbf20e2", "", 0),
        ],
        "PyTorch": ("", "", 0),
        "Torch_musa_version": [
            (["name: torch_musa", "Version: 1.3.0"], "", 0),
            (
                "",
                '/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py:28: UserWarning: torch version should be v2.0.0 when using torch_musa, but now torch version is 2.4.1+cu121\n  warnings.warn(\nTraceback (most recent call last):\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py", line 39, in <module>\n    import torch_musa._MUSAC\nImportError: /opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/lib/libmusa_kernels.so: undefined symbol: _ZNK2at10TensorBase14const_data_ptrIN3c107complexIfEEEEPKT_v\n\nThe above exception was the direct cause of the following exception:\n\nTraceback (most recent call last):\n  File "<string>", line 1, in <module>\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py", line 41, in <module>\n    raise ImportError("Please try running Python from a different directory!") from err\nImportError: Please try running Python from a different directory!\n',
                1,
            ),
        ],
        "Torch_musa": (
            "",
            '/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py:28: UserWarning: torch version should be v2.0.0 when using torch_musa, but now torch version is 2.4.1+cu121\n  warnings.warn(\nTraceback (most recent call last):\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py", line 39, in <module>\n    import torch_musa._MUSAC\nImportError: /opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/lib/libmusa_kernels.so: undefined symbol: _ZNK2at10TensorBase14const_data_ptrIN3c107complexIfEEEEPKT_v\n\nThe above exception was the direct cause of the following exception:\n\nTraceback (most recent call last):\n  File "/home/mccxadmin/caizhi/musa_develop/musa_develop/check/test/torch_musa_demo.py", line 1, in <module>\n    import torch, torch_musa  # noqa\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py", line 41, in <module>\n    raise ImportError("Please try running Python from a different directory!") from err\nImportError: Please try running Python from a different directory!\n',
            1,
        ),
        "TorchVision_version": [
            (["name: torchvision", "Version: 0.19.1+git6194369"], "", 0),
            ("61943691d3390bd3148a7003b4a501f0e2b7ac6e", "", 0),
        ],
        "TorchVision": (
            "",
            '/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py:28: UserWarning: torch version should be v2.0.0 when using torch_musa, but now torch version is 2.4.1+cu121\n  warnings.warn(\nTraceback (most recent call last):\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py", line 39, in <module>\n    import torch_musa._MUSAC\nImportError: /opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/lib/libmusa_kernels.so: undefined symbol: _ZNK2at10TensorBase14const_data_ptrIN3c107complexIfEEEEPKT_v\n\nThe above exception was the direct cause of the following exception:\n\nTraceback (most recent call last):\n  File "/home/mccxadmin/caizhi/musa_develop/musa_develop/check/test/torchvision_demo.py", line 1, in <module>\n    import torch, torch_musa  # noqa\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch_musa/__init__.py", line 41, in <module>\n    raise ImportError("Please try running Python from a different directory!") from err\nImportError: Please try running Python from a different directory!\n',
            1,
        ),
        "TorchAudio_version": [
            (["name: torchaudio", "Version: 2.2.2+cefdb36"], "", 0),
            (
                "",
                'Traceback (most recent call last):\n  File "<string>", line 1, in <module>\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torchaudio-2.2.2+cefdb36-py3.8-linux-x86_64.egg/torchaudio/__init__.py", line 2, in <module>\n    from . import _extension  # noqa  # usort: skip\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torchaudio-2.2.2+cefdb36-py3.8-linux-x86_64.egg/torchaudio/_extension/__init__.py", line 38, in <module>\n    _load_lib("libtorchaudio")\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torchaudio-2.2.2+cefdb36-py3.8-linux-x86_64.egg/torchaudio/_extension/utils.py", line 60, in _load_lib\n    torch.ops.load_library(path)\n  File "/opt/conda/envs/py38/lib/python3.8/site-packages/torch/_ops.py", line 1295, in load_library\n    ctypes.CDLL(path)\n  File "/opt/conda/envs/py38/lib/python3.8/ctypes/__init__.py", line 373, in __init__\n    self._handle = _dlopen(self._name, mode)\nOSError: /opt/conda/envs/py38/lib/python3.8/site-packages/torchaudio-2.2.2+cefdb36-py3.8-linux-x86_64.egg/torchaudio/lib/libtorchaudio.so: undefined symbol: _ZNK5torch8autograd4Node4nameB5cxx11Ev\n',
                1,
            ),
        ],
        "TorchAudio": (
            "",
            "/opt/conda/envs/py38/bin/python: can't open file '/home/mccxadmin/caizhi/musa_develop/musa_develop/check/test/torchaudio_demo.py': [Errno 2] No such file or directory\n",
            2,
        ),
    }
    ground_truth = """\
Torch_musa                                      Version: 1.3.0
TorchVision                                     Version: 0.19.1+6194369
TorchAudio                                      Version: 2.2.2+cefdb36"""
    ReportTest(simulation_log, ground_truth)


if __name__ == "__main__":
    test_torch_musa_report_simulation()
