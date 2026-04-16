# -*- coding: utf-8 -*-
import os
import pytest
import subprocess
import time
import sys


def kill_port_5000():
    """强杀 Mock Server 占用的 5000 端口"""
    if sys.platform == 'win32':
        # 增加 /T 确保杀掉整个进程树
        os.system(
            'FOR /F "tokens=5" %P IN (\'netstat -ano ^| findstr :5000 ^| findstr LISTENING\') DO taskkill /F /T /PID %P >nul 2>&1')


def run_all_tests():
    # --- 1. 基础配置 ---
    results_dir = "reports/allure-results"
    mock_script = "mock_server.py"
    python_exe = sys.executable
    is_jenkins = os.getenv('JENKINS_URL') is not None

    # --- 2. 环境初始化 (仅本地) ---
    if not is_jenkins:
        print(" 正在清理旧的进程与缓存...")
        kill_port_5000()

        print(" 正在异步启动 Mock Server...")
        try:
            # 使用 DETACHED_PROCESS 标志，让 Mock 完全脱离 run.py 独立运行
            # 这样即便点击 PyCharm 的停止按钮，也不会因为子进程未关闭而卡死
            subprocess.Popen(
                [python_exe, mock_script],
                creationflags=0x00000008 if sys.platform == 'win32' else 0,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(2)
            print(" Mock Server 已启动 (Port: 5000)")
        except Exception as e:
            print(f" 启动 Mock Server 失败: {e}")

    # --- 3. 执行测试 ---
    print(" 开始执行自动化测试用例...")
    # 增加 --clean-alluredir 确保每次报告都是最新的
    pytest.main(['-s', '-v', f'--alluredir={results_dir}', '--clean-alluredir'])

    # --- 4. 清理与报告 (仅本地) ---
    if not is_jenkins:
        print(" 测试结束，正在关闭本地 Mock Server...")
        kill_port_5000()

        print(" 正在启动 Allure 报告服务...")
        print(" 提示：报告服务在独立进程运行，你可以点击 PyCharm 的停止按钮关闭本次运行。")

        # 【关键修改】使用 Popen 异步启动 allure，不阻塞主进程
        # 这样 run.py 就能正常结束，PyCharm 按钮会变绿
        try:
            subprocess.Popen(
                ['allure', 'serve', results_dir],
                shell=True,
                creationflags=0x00000008 if sys.platform == 'win32' else 0
            )
        except Exception as e:
            print(f" 无法启动 Allure 报告: {e}")
    else:
        print(" CI 环境：已完成测试数据收集，请在 Jenkins 插件中查看报告。")


if __name__ == "__main__":
    run_all_tests()