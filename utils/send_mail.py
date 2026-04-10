import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime


class EmailSender:
    """邮件发送器"""

    def __init__(self, smtp_server, port, sender, password, receivers):
        self.smtp_server = smtp_server
        self.port = port
        self.sender = sender
        self.password = password
        self.receivers = receivers

    def send_report(self, subject, content, report_path=None, use_ssl=True):
        """
        发送测试报告邮件
        :param subject: 邮件主题
        :param content: 邮件正文（支持HTML）
        :param report_path: 附件路径（可选）
        :param use_ssl: 是否使用SSL连接
        """
        # 创建邮件对象
        msg = MIMEMultipart()
        msg["From"] = Header(f"自动化测试<{self.sender}>", "utf-8")
        msg["To"] = Header(",".join(self.receivers), "utf-8")
        msg["Subject"] = Header(subject, "utf-8")

        # 添加正文
        msg.attach(MIMEText(content, "html", "utf-8"))

        # 添加附件（压缩后的Allure报告）
        if report_path and os.path.exists(report_path):
            with open(report_path, "rb") as f:
                attachment = MIMEText(f.read(), "base64", "utf-8")
                attachment["Content-Type"] = "application/octet-stream"
                attachment["Content-Disposition"] = f'attachment; filename="{os.path.basename(report_path)}"'
                msg.attach(attachment)

        # 发送邮件
        try:
            if use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.port)

            server.login(self.sender, self.password)
            server.sendmail(self.sender, self.receivers, msg.as_string())
            server.quit()
            print(f"邮件发送成功: {subject}")
            return True
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False


def send_test_report():
    """发送测试报告邮件（供Jenkins调用）"""
    import json
    import zipfile
    from datetime import datetime

    # 读取测试结果统计
    summary_path = "./reports/allure-report/widgets/summary.json"
    if os.path.exists(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)
        total = summary.get("statistic", {}).get("total", 0)
        passed = summary.get("statistic", {}).get("passed", 0)
        failed = summary.get("statistic", {}).get("failed", 0)
        skipped = summary.get("statistic", {}).get("skipped", 0)
    else:
        total = passed = failed = skipped = 0

    # 打包Allure报告
    zip_path = "./reports/allure-report.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk("./reports/allure-report"):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, "./reports/allure-report")
                z.write(file_path, arc_name)

    # 邮件配置（建议从环境变量读取）
    sender = EmailSender(
        smtp_server=os.getenv("SMTP_SERVER", "smtp.qq.com"),
        port=int(os.getenv("SMTP_PORT", "465")),
        sender=os.getenv("SENDER_EMAIL", "3117252107@qq.com"),
        password=os.getenv("SENDER_PASSWORD", "ietxukegggzjdedd"),  # QQ邮箱需使用授权码
        receivers=os.getenv("RECEIVER_EMAILS", "1020828245@qq.com").split(",")
    )

    # 构建邮件内容
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = f"接口自动化测试报告 - {now}"

    content = f"""
    <h2>接口自动化测试报告</h2>
    <p><strong>执行时间：</strong>{now}</p>
    <h3>测试结果统计</h3>
    <table border="1" cellpadding="8" style="border-collapse: collapse;">
        <tr><th>总用例数</th><th>通过</th><th>失败</th><th>跳过</th><th>通过率</th></tr>
        <tr>
            <td>{total}</td>
            <td style="color: green;">{passed}</td>
            <td style="color: red;">{failed}</td>
            <td>{skipped}</td>
            <td>{passed / total * 100:.1f}%</td>
        </tr>
    </table>
    <p>详细报告请查看附件。</p>
    <p><em>本邮件由自动化测试系统自动发送，请勿回复。</em></p>
    """

    sender.send_report(subject, content, zip_path)


if __name__ == "__main__":
    send_test_report()