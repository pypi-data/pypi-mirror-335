import os
import sys
import argparse
from .check import CHECKER
from musa_develop.install import PACKAGE_MANAGER
from .report import report
from .utils import parse_args, demo_parse_args, FontBlue, get_os_name
from .download import DOWNLOADER
from musa_develop.demo import DEMO
from musa_develop.demo.demo import DemoTask

CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
OPTIONAL_LENGTH = 11


class CustomHelpFormatter(argparse.HelpFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._indent_increment = 8  # 增加缩进层级
        self._max_help_position = 30  # 控制 `help` 对齐位置
        self._width = 100  # 设定更宽的列宽，避免换行问题


def main():
    parser = argparse.ArgumentParser(
        prog="musa-develop",
        add_help=False,
        formatter_class=argparse.RawTextHelpFormatter,
        description="A tool for deploying and checking the musa environment.",
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        help=f"{' '*OPTIONAL_LENGTH}Show this help message and exit.",
    )
    report_parser = parser.add_argument_group(FontBlue("Report"))
    report_parser.add_argument(
        "-r",
        "--report",
        dest="report",
        action="store_true",
        default=False,
        help=f"{' '*OPTIONAL_LENGTH}Display the software stack and hardware information of the current environment.",
    )

    check_parser = parser.add_argument_group(FontBlue("Check"))
    check_parser.add_argument(
        "-c",
        "--check",
        nargs="?",
        dest="check",
        metavar="PACKAGE_NAME",
        const="driver",
        default="",
        choices=[
            "host",
            "driver",
            "mtlink",
            "ib",
            "smartio",
            "container_toolkit",
            "torch_musa",
            "musa",
            "vllm",
            None,
        ],
        help=f"""{" "*OPTIONAL_LENGTH}Check musa-related develop environment. Default value is 'driver' if only '-c' or '--check' is set.
{" "*OPTIONAL_LENGTH}PACKAGE_NAME choices = [
                "host",
                "driver",
                "mtlink",
                "ib",
                "smartio",
                "container_toolkit",
                "musa",
                "torch_musa",
                "vllm"
            ]""",
    )
    check_parser.add_argument(
        "--container",
        dest="container",
        metavar="CONTAINER_NAME",
        type=str,
        default=None,
        help="(optional) Check the musa environment in the container while musa-develop tool is executing in the host.",
    )

    download_parser = parser.add_argument_group(FontBlue("Download"))
    download_parser.add_argument(
        "-d",
        "--download",
        dest="download",
        metavar="PACKAGE_NAME",
        type=parse_args,
        help=f"""{" "*OPTIONAL_LENGTH}Only download MUSA software stack offline packages; users need to install them manually.
           PACKAGE_NAME choices = [
                "kuae/kuae=1.3.0/kuae==1.3.0",
                "sdk/sdk=3.1.0/sdk==3.1.0",
                "musa"
                "mudnn",
                "mccl",
                "driver",
                "smartio",
                "container_toolkit",
                "torch_musa"
            ]
        """,
    )
    download_parser.add_argument(
        "--dir",
        type=str,
        help="""(optional) Specified software package download link. Need use it with --d""",
    )

    install_parser = parser.add_argument_group(FontBlue("Install"))
    install_parser.add_argument(
        "-i",
        "--install",
        dest="install",
        metavar="PACKAGE_NAME",
        type=parse_args,
        # TODO(@wangkang): 是否需要kuae参数?, 如何处理?
        help=f"""{" "*OPTIONAL_LENGTH}Install the specified software based on the package name.
           PACKAGE_NAME choices = [
                "kuae/kuae==1.3.0/kuae=1.3.0/kuae--1.3.0/kuae-1.3.0",
                "sdk/sdk==3.1.0/sdk=3.1.0/sdk--3.1.0/sdk-3.1.0",
                "mudnn",
                "mccl",
                "driver",
                "musa"
                "container_toolkit",
                "torch_musa",
            ]
        """,
        # "smartio",
    )
    install_parser.add_argument(
        "-u",
        "--uninstall",
        metavar="PACKAGE_NAME",
        dest="uninstall",
        type=parse_args,
        help=f"""{" "*OPTIONAL_LENGTH}Uninstall the specified software based on the package name.
           PACKAGE_NAME choices = [
                "musa",
                "sdk",
                "mudnn",
                "mccl",
                "driver",
                "smartio",
                "container_toolkit",
                "torch_musa",
                "vllm"
            ]
        """,
    )
    # install_parser.add_argument(
    #     "--update",
    #     dest="update",
    #     metavar="PACKAGE_NAME",
    #     type=parse_args,
    #     # TODO(@wangkang): 是否需要kuae参数?, 如何处理?
    #     help=f"""{" "*OPTIONAL_LENGTH}Update the specified software to lasted version based on the package name.
    #        PACKAGE_NAME choices = [
    #             "kuae/kuae==1.3.0/kuae=1.3.0/kuae--1.3.0/kuae-1.3.0",
    #             "sdk/sdk==3.1.0/sdk=3.1.0/sdk--3.1.0/sdk-3.1.0",
    #             "mudnn",
    #             "mccl",
    #             "driver",
    #             "musa/musa_toolkits"
    #             "smartio",
    #             "container_toolkit",
    #             "torch_musa",
    #         ]
    #     """,
    # )
    install_parser.add_argument(
        "-p",
        "--path",
        type=str,
        help="""(optional) Install the specified offline package based on the path. Need use it with --i""",
    )

    # =====================demo=====================
    demo_parser = parser.add_argument_group(FontBlue("Demo"))
    demo_parser.add_argument(
        "--demo",
        dest="demo",
        type=demo_parse_args,
        help=f"""{" "*OPTIONAL_LENGTH}Run the built-in AI demo, specifying the product name, product version, and whether to run it inside a Docker container.
           DEMO choices = [
                "torch_musa==1.3.0/torch_musa--1.3.0",
                "torch_musa=1.3.0/torch_musa-1.3.0",
                "torch_musa==1.3.0==docker/torch_musa=1.3.0=docker",
                "torch_musa--1.3.0--docker/torch_musa-1.3.0-docker",
                "vllm==0.2.1/vllm--0.2.1",
                "vllm=0.2.1/vllm-0.2.1",
                "vllm==0.2.1==docker/vllm=0.2.1=docker",
                "vllm--0.2.1--docker/vllm-0.2.1-docker",
                "kuae==1.3.0/kuae--1.3.0",
                "kuae=1.3.0/kuae-1.3.0",
                "kuae==1.3.0==docker/kuea=1.3.0=docker",
                "kuae--1.3.0--docker/kuea-1.3.0-docker",
                "ollama==1.3.0/ollam=1.3.0",
                "ollama--1.3.0/ollam-1.3.0",
                "ollama==1.3.0==docker/ollam=1.3.0=docker",
                "ollama--1.3.0--docker/ollam-1.3.0-docker",
            ]
        """,
        # "torch_musa",
        # "torch_musa==docker/torch_musa--docker",
        # "torch_musa=docker/torch_musa-docker",
        # "vllm",
        # "vllm==docker/vllm=docker",
        # "vllm--docker/vllm-docker",
        # "kuae",
    )
    # Task Options
    task_options = DemoTask()
    demo_parser.add_argument(
        "-t",
        "--task",
        dest="task",
        type=str,
        default="base",
        # choices=task_options.get_all_task(),
        help=f"""(optional) Run a specified task.
{" "*OPTIONAL_LENGTH}TASK choices:
{" "*OPTIONAL_LENGTH}    {task_options.get_all_task()}""",
    )

    # TODO(@gl): v0.3.0：need test
    demo_parser.add_argument(
        "--ctnr-name",
        dest="ctnr_name",
        type=str,
        default=False,
        help="(optional) specify a container name whose status is 'running'.",
    )

    demo_parser.add_argument(
        "--host-dir",
        dest="host_dir",
        type=str,
        default=False,
        help="(optional) specify a host directory mapping to the container.",
    )

    demo_parser.add_argument(
        "--ctnr-dir",
        dest="ctnr_dir",
        type=str,
        default=False,
        help="(optional) specify a container directory mapping from host.",
    )

    # ===========================================

    # default with no args will print help
    if len(sys.argv) == 1:
        report()
        return

    args = parser.parse_args()

    # ====================check===================
    if args.container and not args.check:
        parser.error("--container can only be used with -c/--check")
        return

    if args.check:
        checker = CHECKER[args.check](container_name=args.container)
        checker.check()
        checker.report()
        return

    # ====================report===================
    if args.report:
        report()
        return

    # ====================download===================
    if args.download:
        download_name, download_version = args.download
        DOWNLOADER().download(download_name, download_version, args.dir)
        return

    # ====================install===================
    if args.install:
        install_name, install_version = args.install
        if get_os_name == "Kylin":
            PACKAGE_MANAGER["kylin"].install(install_name, install_version)
        else:
            PACKAGE_MANAGER[install_name].install(install_version, args.path)
        return

    # =====================uninstall=====================
    if args.uninstall:
        uninstall_name, uninstall_version = args.uninstall
        if get_os_name == "Kylin":
            PACKAGE_MANAGER["kylin"].uninstall(uninstall_name)
        else:
            PACKAGE_MANAGER[uninstall_name].uninstall()
        return

    # ====================update===================
    # if args.update:
    #     install_name, install_version = args.update
    #     PACKAGE_MANAGER[install_name].update(install_version, args.path)
    #     return

    # =====================demo=====================
    if not args.demo:
        if args.task or args.ctnr_name or args.host_dir or args.ctnr_dir:
            parser.error(
                "The --demo option is required when using --task, --host-dir, or --ctnr-name."
            )
            return 1
    else:
        if args.ctnr_dir:
            if not args.host_dir:
                parser.error("'--host-dir' must be specified when using '--ctnr-dir'")

        if args.ctnr_name:
            print(f"Container name: {args.ctnr_name}")

        if args.host_dir:
            if not args.ctnr_dir:
                args.ctnr_dir = "/workspace"
                print(f"Directory on host: {args.host_dir}.")
                print("The Directory will mapping to the container: /workspace .")
            else:
                print(f"Directory on host: {args.host_dir}.")
                print(f"The Directory will mapping to the container: {args.ctnr_dir}.")
        # task args check
        if not args.task:
            args.task = "base"
            print("Without specifying a task, start a container runs on MT-GPU. ")
        if args.task not in task_options.get_all_task():
            parser.error(
                f"task '{args.task}' is invalid, choose from {task_options.get_all_task()}"
            )
        demo, version, _ = args.demo
        use_docker = True
        demo_class = DEMO.get(demo, None)
        if demo_class:
            demo_class.start(version, args.task, use_docker=use_docker, demo=demo)
        else:
            parser.error(f"demo '{demo}' is invalid, choose from {DEMO.keys()}")
    # ============================================


if __name__ == "__main__":
    main()
