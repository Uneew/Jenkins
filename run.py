# -*- coding: utf-8 -*-
import os, pytest, subprocess, time, sys


# 1. 强杀 5000 端口 (Windows 专用极简指令)
def clean_port():
    os.system(
        'FOR /F "tokens=5" %P IN (\'netstat -ano ^| findstr :5000 ^| findstr LISTENING\') DO taskkill /F /T /PID %P >nul 2>&1')


def run():
    is_ci = os.getenv('JENKINS_URL')

    # 2. 本地环境：启动前清理并异步开启 Mock
    if not is_ci:
        clean_port()
        subprocess.Popen([sys.executable, "mock_server.py"], creationflags=0x08)  # 0x08 = DETACHED_PROCESS
        time.sleep(2)

    # 3. 执行测试
    pytest.main(['-s', '-v', '--alluredir=reports/allure-results', '--clean-alluredir'])

    # 4. 本地环境：结束后清理 Mock 并异步开启报告
    if not is_ci:
        clean_port()
        subprocess.Popen('allure serve reports/allure-results', shell=True, creationflags=0x08)


if __name__ == "__main__":
    run()