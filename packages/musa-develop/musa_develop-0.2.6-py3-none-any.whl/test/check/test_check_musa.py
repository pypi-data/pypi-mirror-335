import sys
import os
from musa_develop.check.utils import CheckModuleNames
from musa_develop.utils import FontRed, FontGreen

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from test.utils import TestChecker, set_env


@set_env({"EXECUTED_ON_HOST_FLAG": "False"})
def test_check_musa_installed_inside_container():
    """
    check musa installed, whether it works or not

    Simulation Log Details:
        - `simulation_log["MUSAToolkits"]`: A tuple where the second element
          (`True` or `False`) signifies the installation status.
        - other log do not impact the installation check
    """
    tester = TestChecker(CheckModuleNames.musa.name)
    simulation_log = {
        "MUSAToolkits": [("", "", 0), True],
        "musa_version": (
            """\
musa_toolkits:
{
        "version":      "3.0.0",
        "git branch":   "dev3.0.0",
        "git tag":      "No tag",
        "commit id":    "f50264844211b581e1d9b0dab2447243c8d4cfb0",
        "commit date":  "2024-06-21 15:20:10 +0800
}""",
            "",
            0,
        ),
        "test_musa": ("", "", 0),
    }
    musa_ground_truth = "MUSAToolkits                Version: 3.0.0+f502648"
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(musa_ground_truth)
    tester.test_single_module()


@set_env({"EXECUTED_ON_HOST_FLAG": "False"})
def test_check_musa_uninstalled_inside_container():
    """
    check musa uninstalled, whether it works or not
    see more in function above: test_check_musa_installed_inside_container
    """
    tester = TestChecker(CheckModuleNames.musa.name)
    simulation_log = {
        "MUSAToolkits": [("", "", 0), False],
        "musa_version": (
            """\
musa_toolkits:
{
        "version":      "3.0.0",
        "git branch":   "dev3.0.0",
        "git tag":      "No tag",
        "commit id":    "f50264844211b581e1d9b0dab2447243c8d4cfb0",
        "commit date":  "2024-06-21 15:20:10 +0800
}""",
            "",
            0,
        ),
        "test_musa": ("", "", 0),
    }
    musa_ground_truth = f"""\
MUSAToolkits
    - status: {FontRed('UNINSTALLED')}
    - {FontGreen("Recommendation")}: Unable to find /usr/local/musa directory, please check if musa_toolkits is installed."""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(musa_ground_truth)
    tester.test_single_module()


@set_env({"EXECUTED_ON_HOST_FLAG": "False"})
def test_check_musa_failed_version_match_unrecorded():
    """
    ground:
    1. check musa failed for its version not matched with the driver
    2. cur musa version in log not recorded
    """
    tester = TestChecker(CheckModuleNames.musa.name)
    simulation_log = {
        "MUSAToolkits": [
            (
                """\
\ncompiler: mcc
error: 'system has unsupported display driver / musa driver combination'(803) at /home/jenkins/agent/workspace/compute_musa_pkg_gitlab/musa_toolkit/MUSA-Runtime/src/tools/musaInfo.cpp:155
error: API returned error code.
error: TEST FAILED""",
                "",
                1,
            ),
            True,
        ],
        "musa_version": (
            """\
musa_toolkits:
{
        "version":      "3.0.0",
        "git branch":   "dev3.0.0",
        "git tag":      "No tag",
        "commit id":    "f50264844211b581e1d9b0dab2447243c8d4cfb0",
        "commit date":  "2024-06-21 15:20:10 +0800
}""",
            "",
            0,
        ),
        "test_musa": (
            [
                "MUSA Error:",
                "Error code: 803",
                "Error text: system has unsupported display driver / musa driver combination",
            ],
            "",
            1,
        ),
    }
    musa_ground_truth = f"""\
MUSAToolkits                Version: 3.0.0+f502648
    - status: {FontRed('FAILED')}
    - Info: "
compiler: mcc
error: 'system has unsupported display driver / musa driver combination'(803) at /home/jenkins/agent/workspace/compute_musa_pkg_gitlab/musa_toolkit/MUSA-Runtime/src/tools/musaInfo.cpp:155
error: API returned error code.
error: TEST FAILED\"
    - {FontGreen('Recommendation')}: The execution result of `musaInfo` is abnormal, please check if musa_toolkits version matches the driver, or if the kernel version supports it.
                      The current MUSAToolkits version may not be an official release version. The version compatibility check has been skipped. If necessary, please manually check the version compatibility."""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(musa_ground_truth)
    tester.test_single_module()


if __name__ == "__main__":
    test_check_musa_installed_inside_container()
