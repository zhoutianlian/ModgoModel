import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage


__all__ = ['Mail']


class Mail:
    host = 'smtp.exmail.qq.com'
    port = 465
    user = 'modgo@rongdaitong.cn'
    password = 'Qwer101213'
    mailfrom = '摩估智能数字投行'
    mailto = '尊敬的用户'

    def __init__(self, title: str, text: str, fromfile: bool = False):
        """
        发送邮件+附件
        :param title: 邮件标题
        :param text: 文件正文
        :param fromfile: True:将text作为路径读取文件内容作为邮件正文,仅限txt文件;False:将text
        """
        self.mail = MIMEMultipart()
        if fromfile:
            with open(text) as file:
                content = ''
                for row in file:
                    content += row
        else:
            content = text
        self.mail.attach(MIMEText(content, 'plain', 'utf-8'))
        self.mail['Subject'] = title
        self.mail['From'] = formataddr([self.mailfrom, self.user])
        self.mail['To'] = formataddr([self.mailto, ''])

    def __enter__(self):
        self.server = smtplib.SMTP_SSL(self.host, port=self.port)
        self.server.login(self.user, self.password)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.server.quit()

    def sendto(self, *args):
        """
        发送的收件人
       :param args: 字符串表示收件人邮箱，如果没有加@xxxx.xxx后缀，则自动添加“@rongdaitong.cn”后缀
        """
        self.server.sendmail(self.user, args, self.mail.as_string())

    def attach(self, path, rename: str = None):
        """
        目前支持pdf，zip文件,其他自己尝试
        :param path:文件完整路径
        :param rename: 重命名，否则将path最后一个斜杠之后的内容作为文件名
        """
        filename = path.replace('\\', '/')
        filename = filename.split('/')[-1] if rename is None else rename
        pdf = MIMEApplication(open(path, 'rb').read())
        pdf.add_header('Content-Disposition', 'attachment', filename=filename)
        self.mail.attach(pdf)

    def image(self, path: str):
        """
        以阅览图的形式添加图片附件
        :param path: 图片完整路径
        """
        with open(path, 'rb') as f:
            image = MIMEImage(f.read())
            image.add_header('Content-Disposition', 'attachment', filename='test.png')
            self.mail.attach(image)


if __name__ == '__main__':
    with Mail('分享一个用python发送融贷通内部邮件的package', '见附件') as m:
        m.attach('所发附件所在完整路径')
        m.image('所发图片附件所在完整路径')
        m.sendto('收件人1', '收件人2', '收件人n+')

