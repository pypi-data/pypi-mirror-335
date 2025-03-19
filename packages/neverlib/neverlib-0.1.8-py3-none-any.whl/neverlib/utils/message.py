# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/2/1
"""
通过邮件发送通知
"""
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr
import numpy as np

np.set_printoptions(precision=1)  # 设置numpy的打印精度


def send_QQEmail(title, content, from_email, from_password, to_email):
    """
    Args:
        title: 邮件标题
        content: 邮件内容
        from_email: 设置发件人邮箱地址 "xxxx@qq.com"
        from_password: SMTP 授权码
        to_email: 设置收件人邮箱地址 "xxxx@qq.com"
    """
    # 设置邮箱的域名
    HOST = "smtp.qq.com"

    # 设置邮件正文
    message = MIMEText(content, "plain", "utf-8")
    message["Subject"] = Header(title, charset="utf-8")
    message["From"] = formataddr(("never", from_email))
    message["From"] = Header(from_email)
    message["To"] = Header(to_email)

    try:
        # 使用SSL连接
        server = smtplib.SMTP_SSL(HOST)
        server.connect(HOST, 465)
        server.login(from_email, from_password)  # 登录邮箱
        server.sendmail(from_email, to_email, message.as_string())  # 发送邮件
        server.quit()  # 关闭SMTP服务器
        print("邮件发送成功")
    except Exception as e:
        print(f"邮件发送失败：{e}")



if __name__ == "__main__":
    send_QQEmail("实验跑完", "实验跑完了，快去看看吧！",
                 from_email="1786088386@qq.com", from_password="xxxx",
                 to_email="1786088386@qq.com")
    pass
