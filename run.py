# -*- coding: utf-8 -*-
import os
import pytest
import subprocess
import time
import sys
import signal


def run_all_tests():
    # 1. 环境变量与路径准备
    results_dir = "reports/allure-results"
    mock_script = "mock_server.py"
    python_exe = sys.executable  # 获取当前使用的 Python 解释器路径

    # 强制设置输出编码为 UTF-8，解决控制台乱码
    if sys.platform.startswith('win'):
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # 2. 自动判断环境并启动 Mock Server
    # 在本地运行时自动启动，Jenkins 运行则跳过（因为 Jenkins Pipeline 里已经写了启动逻辑）
    is_jenkins = os.getenv('JENKINS_URL') is not None
    mock_process = None

    if not is_jenkins:
        print(" 检测到本地运行，正在启动 Mock Server...")
        # 使用 CREATE_NEW_PROCESS_GROUP 标志，方便后续彻底杀掉进程树
        try:
            mock_process = subprocess.Popen(
                [python_exe, mock_script],
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(2)  # 等待 Flask 启动
            print("Mock Server 已在后台运行 (Port: 5000)")
        except Exception as e:
            print(f" 启动 Mock Server 失败: {e}")

    # 3. 执行测试
    print(" 开始执行自动化测试用例...")
    pytest.main(['-s', '-v', f'--alluredir={results_dir}', '--clean-alluredir'])

    # 4. 清理工作
    if not is_jenkins and mock_process:
        print(" 正在清理本地 Mock Server 进程...")
        try:
            # 暴力清理 5000 端口，确保不会残留
            if sys.platform == 'win32':
                os.system(
                    'FOR /F "tokens=5" %P IN (\'netstat -ano ^| findstr :5000 ^| findstr LISTENING\') DO taskkill /F /PID %P >nul 2>&1')
            else:
                mock_process.terminate()
            print(" 清理完毕。")
        except Exception as e:
            print(f" 清理进程时出错: {e}")

    # 5. 生成报告
    if is_jenkins:
        print("CI 环境：跳过 Allure serve，请在 Jenkins 页面查看报告。")
    else:
        print("本地环境：准备生成并打开 Allure 报告...")
        os.system(f'allure serve {results_dir}')


if __name__ == "__main__":
    run_all_tests()