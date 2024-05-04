import smtplib
import sys
from email.mime.text import MIMEText
from email.header import Header


# 第三方 SMTP 服务
mail_host="smtp.qq.com"  #设置服务器
mail_user="158354902@qq.com"    #用户名
mail_pass="nlmiihmokwqvcada"   #口令
sender = "158354902@qq.com"

receivers = ['fan_jia_chen@163.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

# 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码


def send_mail(error_msg):
    message = MIMEText('错误信息为%s' % error_msg, 'plain', 'utf-8')
    message['From'] = Header("自动更新系统", 'utf-8')  # 发送者
    message['To'] = Header("测试", 'utf-8')  # 接收者

    subject = '更新系统警告信息'
    message['Subject'] = Header(subject, 'utf-8')
    try:
        smtpObj = smtplib.SMTP_SSL()
        smtpObj.connect(mail_host, 465)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException as e:
        print(e)
        print("Error: 无法发送邮件")

# def send_email(msg):
# send_mail("市场数据更新错误")
