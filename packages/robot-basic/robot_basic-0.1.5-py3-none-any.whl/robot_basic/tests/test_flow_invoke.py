import sys

from robot_base import log_util

from ..__init__ import invoke_flow


def setup_function():
    log_util.Logger("", "DEBUG")
    sys.path.insert(
        0, r"D:\ProgramData\data\project\be6def2d-813e-4091-9844-b03a88327734\gobot"
    )


def test_invoke_flow():
    test = invoke_flow(
        flow_name="vgqigxmq",
        return_value=["输出参数1"],
        输入参数1="99999999999999999",
        输入参数2="88888888888",
        local_data=locals(),
        code_block_extra_data={
            "code_map_id": "OKmmU2NdJSqHj0kO",
            "code_block_name": "调用流程",
        },
    )
    print(test)
