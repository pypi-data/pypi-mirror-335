import sys
import os
import io
import re
import pytest
import subprocess
from unittest.mock import patch
from io import StringIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from test.utils import (
    LOCAL_IP,
    S80_REBOOT_IP,
    capture_print,
    is_package_installed,
    is_container_up,
    set_env,
    TestInstall,
)
from musa_develop.install import PACKAGE_MANAGER, DriverPkgMgr
from musa_develop.demo import DEMO


def extract_container_name(input_str):
    pattern = r"`docker attach ([^`]+)`"
    match = re.search(pattern, input_str)
    if match:
        return match.group(1)
    else:
        return None


# ====================stage 0: machine with Dirver/ContainerToolkit fully installed====================


@pytest.mark.skipif(LOCAL_IP != S80_REBOOT_IP, reason="machine may be restarted")
@pytest.mark.order(1)
def test_uninstall_container_toolkit():
    # Ensure that it has already been installed.
    package = "mt-container-toolkit"
    installed, info = is_package_installed(package)
    assert installed
    package = "mtml"
    installed, info = is_package_installed(package)
    assert installed
    package = "sgpu-dkms"
    installed, info = is_package_installed(package)
    assert installed

    name = "container_toolkit"
    func = PACKAGE_MANAGER[name].uninstall
    result_string = capture_print(func)

    # assert log
    log1 = "Uninstalling \x1b[91mmt-container-toolkit\x1b[0m ..."
    log2 = "Uninstalling dependencies \x1b[91mmtml\x1b[0m ..."
    log3 = "Uninstalling dependencies \x1b[91msgpu-dkms\x1b[0m ..."
    log4 = "Successfully uninstall \x1b[91mcontainer-toolkit\x1b[0m."
    log5 = "Successfully uninstall \x1b[91mmtml\x1b[0m."
    log6 = "Successfully uninstall \x1b[91msgpu-dkms\x1b[0m."
    assert log1 in result_string
    assert log2 in result_string
    assert log3 in result_string
    assert log4 in result_string
    assert log5 in result_string
    assert log6 in result_string

    # assert status
    package = "mt-container-toolkit"
    installed, info = is_package_installed(package)
    assert not installed
    package = "mtml"
    installed, info = is_package_installed(package)
    assert not installed
    package = "sgpu-dkms"
    installed, info = is_package_installed(package)
    assert not installed

    name = "container_toolkit"
    func = PACKAGE_MANAGER[name].install
    result_string = capture_print(func)

    package = "mt-container-toolkit"
    installed, info = is_package_installed(package)
    assert installed
    package = "mtml"
    installed, info = is_package_installed(package)
    assert installed
    package = "sgpu-dkms"
    installed, info = is_package_installed(package)
    assert installed


@pytest.mark.skipif(LOCAL_IP != S80_REBOOT_IP, reason="machine may be restarted")
@pytest.mark.order(2)
def test_uninstall_driver():
    # Ensure that it has already been installed.
    package = "musa"
    installed, info = is_package_installed(package)
    assert installed

    name = "driver"
    func = PACKAGE_MANAGER[name].uninstall
    result_string = capture_print(func)

    # assert log
    log1 = "Uninstalling \x1b[91mdriver\x1b[0m ..."
    log2 = "Successfully uninstall \x1b[91mdriver\x1b[0m."
    assert log1 in result_string
    assert log2 in result_string

    # assert status
    package = "musa"
    installed, info = is_package_installed(package)
    assert not installed

    name = "driver"
    func = PACKAGE_MANAGER[name].install
    result_string = capture_print(func)

    package = "musa"
    installed, info = is_package_installed(package)
    assert installed


@pytest.mark.skipif(LOCAL_IP != S80_REBOOT_IP, reason="machine may be restarted")
@pytest.mark.order(2)
def test_demo():
    name = "container_toolkit"
    func = PACKAGE_MANAGER[name].uninstall
    result_string = capture_print(func)

    package = "mt-container-toolkit"
    installed, info = is_package_installed(package)
    assert not installed
    package = "mtml"
    installed, info = is_package_installed(package)
    assert not installed
    package = "sgpu-dkms"
    installed, info = is_package_installed(package)
    assert not installed

    # ------------------
    name = "driver"
    func = PACKAGE_MANAGER[name].uninstall
    result_string = capture_print(func)

    package = "musa"
    installed, info = is_package_installed(package)
    assert not installed

    # ------------------
    name = "host"
    func = PACKAGE_MANAGER[name].uninstall
    result_string = capture_print(func)

    package = "dkms"
    installed, info = is_package_installed(package)
    assert not installed
    package = "lightdm"
    installed, info = is_package_installed(package)
    assert not installed

    demo = "torch_musa"
    version = None
    task = "base"
    use_docker = True
    DEMO[demo].start(version, task, use_docker)

    package = "dkms"
    installed, info = is_package_installed(package)
    assert installed
    package = "lightdm"
    installed, info = is_package_installed(package)
    assert installed
    package = "musa"
    installed, info = is_package_installed(package)
    assert installed

    # reboot after install driver, and continue task
    func = DEMO[demo].start
    result_string = capture_print(
        func, version=version, task=task, use_docker=use_docker
    )

    package = "mt-container-toolkit"
    installed, info = is_package_installed(package)
    assert installed
    package = "mtml"
    installed, info = is_package_installed(package)
    assert installed
    package = "sgpu-dkms"
    installed, info = is_package_installed(package)
    assert installed

    assert (
        "Please execute \x1b[32m`docker attach musa_develop_torch_musa_base"
        in result_string
    )
    container_name = extract_container_name(result_string)
    assert is_container_up(container_name)
    gmi_cmd0 = f"docker exec -it {container_name} /usr/bin/mthreads-gmi"
    gmi_cmd1 = f"docker exec -it {container_name} /usr/local/bin/mthreads-gmi"
    result0 = subprocess.run(
        gmi_cmd0,
        shell=True,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    result1 = subprocess.run(
        gmi_cmd1,
        shell=True,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert "Driver Version" in result0.stdout or "Driver Version" in result1.stdout

    os.system(f"docker stop {container_name}")
    os.system(f"docker rm {container_name}")


# @pytest.mark.skipif(LOCAL_IP != S80_REBOOT_IP, reason="machine may be restarted")
@pytest.mark.order(2)
def test_reinstall():
    name = "driver"

    # First to ensure that driver = 3.1.0 has already been installed.
    PACKAGE_MANAGER[name].install("3.1.0")

    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        PACKAGE_MANAGER[name].install("3.1.0")
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout  # 恢复 stdout

    log1 = "has already been installed successfully!"

    assert log1 in output


@set_env({"DOWNLOAD_IN_HOST_TEST": "True"})
def test_install_unnecessary_uninstall_log():
    test_install = TestInstall(DriverPkgMgr)
    test_install.uninstall()  # make sure container_toolkit has been installed
    mock_input = StringIO("n\n")
    with patch.object(sys, "stdin", mock_input):
        test_install.install()  # check log
    test_install.check_report_excludes(truth_log="Uninstalling driver ...")


def test_driver_install_with_input():
    test_install = TestInstall(DriverPkgMgr)
    test_install.uninstall()
    mock_input = StringIO("n\n")
    with patch.object(sys, "stdin", mock_input):
        test_install.install()
    test_install.check_report_includes(
        "System needs to be restarted to load the driver. Restart now?"
    )
