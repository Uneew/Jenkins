import pytest
import sys
import os


def run_tests():
    """执行测试并生成Allure报告"""
    # 默认参数
    args = [
        "-v",
        "-s",
        "--alluredir=./reports/allure-results",
        "--clean-alluredir",
        "testcases/"
    ]

    # 支持命令行传入额外参数
    args.extend(sys.argv[1:])

    exit_code = pytest.main(args)

    # 生成Allure HTML报告
    os.system("allure generate ./reports/allure-results -o ./reports/allure-report --clean")

    return exit_code


if __name__ == "__main__":
    sys.exit(run_tests())