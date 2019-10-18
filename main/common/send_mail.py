#!/usr/bin/python
# -*- coding: UTF-8 -*-
import smtplib
import email.mime.multipart
import email.mime.text
from email.mime.application import MIMEApplication
def send_email(smtp_host, smtp_port, sendAddr, password, recipientAddrs, subject='', content=''):
    '''
    :param smtp_host: 域名
    :param smtp_port: 端口
    :param sendAddr: 发送邮箱
    :param password: 邮箱密码
    :param recipientAddrs: 发送地址
    :param subject: 标题
    :param content: 内容
    :return: 无
    '''
    msg = email.mime.multipart.MIMEMultipart()
    msg['from'] = sendAddr
    msg['to'] = recipientAddrs
    msg['subject'] = subject
    content = content
    txt = email.mime.text.MIMEText(content, 'plain', 'utf-8')
    msg.attach(txt)

    # 添加附件地址
    part = MIMEApplication(open(r'D:\project\autoInterface\report\result.html', 'rb').read())
    part.add_header('Content-Disposition', 'attachment', filename="result.html")  # 发送文件名称
    msg.attach(part)

    try:
        smtpSSLClient = smtplib.SMTP_SSL(smtp_host, smtp_port)  # 实例化一个SMTP_SSL对象
        loginRes = smtpSSLClient.login(sendAddr, password)  # 登录smtp服务器
        print(u"登录结果：loginRes = {loginRes}")  # loginRes = (235, b'Authentication successful')
        if loginRes and loginRes[0] == 235:
            print(u"登录成功，code = {loginRes[0]}")
            smtpSSLClient.sendmail(sendAddr, recipientAddrs, str(msg))
            print(u"mail has been send successfully. message:{str(msg)}")
            smtpSSLClient.quit()
        else:
            print(u"登陆失败，code = {loginRes[0]}")
    except Exception as e:
        print(u"发送失败，Exception: e={e}")
try:
    subject = 'Python 测试邮件'
    content = '这是一封来自 Python 编写的测试邮件。'
    send_email('smtp.163.com', 465, '18740394057@163.com', 'weinan394057', 'nan.wei@yff.com', subject, content)
except Exception as err:
    print(err)
