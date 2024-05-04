import smtplib
from email.mime.text import MIMEText
from email.header import Header


# 第三方 SMTP 服务
mail_host = "smtp.exmail.qq.com"  #设置服务器
mail_user = "fanjiachen@rongdaitong.cn"    #用户名
mail_pass = "7xQieS29e2Ftex84"   #口令
sender = "fanjiachen@rongdaitong.cn"

receivers = ['fan_jia_chen@163.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

# 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码


def send_mail(error_msg):
    message = MIMEText(error_msg, 'plain', 'utf-8')
    message['From'] = Header("估值数据", 'utf-8')  # 发送者
    message['To'] = Header("测试", 'utf-8')  # 接收者

    subject = '估值信息'
    message['Subject'] = Header(subject, 'utf-8')
    try:
        smtpObj = smtplib.SMTP_SSL(host=mail_host)
        smtpObj.connect(mail_host, 465)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException as e:
        print(e)
        print("Error: 无法发送邮件")
