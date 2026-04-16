import os
import pytest


def run_all_tests():
    # 1. 定义报告路径
    results_dir = "reports/allure-results"
    print(" 开始执行自动化测试用例...")

    # 2. 运行 pytest
    # -s: 打印输出, -v: 详细模式, --alluredir: 指定结果存放目录
    pytest.main(['-s', '-v', f'--alluredir={results_dir}', '--clean-alluredir'])

    # 3. 智能判断运行环境
    # Jenkins 运行时会自动设置环境变量 'JENKINS_URL' 或 'BUILD_NUMBER'
    is_jenkins = os.getenv('JENKINS_URL') is not None

    if is_jenkins:
        print(" 检测到 CI 环境运行，跳过本地生成报告步骤。")
        print(" 请直接在 Jenkins 项目页面查看 Allure Report 图标。")
    else:
        print(" 检测到本地环境运行，准备生成并打开 Allure 报告...")
        # 只有在本地才执行生成和打开报告的操作
        os.system(f'allure serve {results_dir}')


if __name__ == "__main__":
    run_all_tests()