import os
import pytest


def run_all_tests():
    print("🚀 开始执行自动化测试用例...")

    # 1. 相当于在命令行输入 pytest -vs --alluredir=./reports/allure-results --clean-alluredir
    # 注意：这里的列表参数就是命令行的参数
    pytest.main([
        "-vs",
        "testcases/",  # 指明运行哪个文件夹下的用例
        "--alluredir=./reports/allure-results",
        "--clean-alluredir"  # 每次运行前清空旧数据
    ])

    print("✅ 测试执行完毕，正在启动 Allure 报告服务...")

    # 2. 相当于在命令行输入 allure serve ...
    # 这句话会自动帮你把 json 数据转成 html，并自动在浏览器打开
    os.system("allure serve ./reports/allure-results")


if __name__ == "__main__":
    run_all_tests()