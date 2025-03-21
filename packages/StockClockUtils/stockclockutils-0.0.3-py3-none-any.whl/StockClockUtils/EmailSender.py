#%%
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
#%%
# ====== 邮件内容类 ======
class MailContext:
    def __init__(self,
                title:str='这是一封测试用的邮件',
                conten_path:str='/www/files/Stock/Utils/EmailUtils/content/body.html',
                attachments_path_list:list[str]=None,
                image_attachments_path_list:list[str]=None):
        """
        用于定义邮件的内容 
        可以传入的参数有：  \\
        :param title: 邮件标题 \\
        :param content: 邮件正文的html文件路径 \\
        :param attachments: 附件路径列表 \\
        :param image_attachments: 图片附件路径列表 
        """

        # 邮件标题
        self.title = title # 邮件标题

        # 邮件正文-html文件路径
        self.content_path = conten_path # 邮件正文的html文件路径

        # 附件名称 
        self.attachments_name_list = []
        for path in attachments_path_list:
            if isinstance(path, str):
                filename = path.split('/')[-1]
                self.attachments_name_list.append(filename)
            else:
                print(f"警告: {path} 不是有效的文件路径字符串，将被忽略。")

        # 图片附件名称
        self.image_attachments_name_list = []
        for path in attachments_path_list:
            if isinstance(path, str):
                imgname = path.split('/')[-1]
                self.image_attachments_name_list.append(imgname)
            else:
                print(f"警告: {path} 不是有效的文件路径字符串，将被忽略。")
        
        # 附件路径
        self.attachments_path_list = attachments_path_list
        # 图片附件路径
        self.image_attachments_path_list = image_attachments_path_list

# 邮寄类
class MailSender:
    def __init__(self,
                mail_host:str,
                mail_user:str,
                mail_pass:str,
                sender:str,
                receivers:list[str]):
        """
        用于发送邮件的类 \\
        :param mail_host: 邮件服务器地址,如smtp.qq.com \\
        :param mail_user: 邮件发送者账号 \\
        :param mail_pass: 邮件发送者密码or授权码 \\
        :param sender: 邮件发送者 \\
        :param receivers: 邮件接收者列表 \\
        """
        self.mail_host = mail_host # 邮件服务器地址
        self.mail_user = mail_user # 邮件发送者账号
        self.mail_pass = mail_pass # 邮件发送者密码
        self.sender = sender # 邮件发送者
        self.receivers = receivers # 邮件接收者列表
        
    def send_mail(self,
                context:MailContext):
        """
        发送邮件的方法 \\
        :param context: 邮件内容类"
        """
        # 邮件信息
        message = MIMEMultipart()
        message['From'] = self.sender
        message['To'] = ', '.join(receivers)
        message['Subject'] = context.title

        # 邮件正文
        try:
            with open(context.content_path,'r',encoding='utf-8') as f:
                body = MIMEText(f.read(),'html','utf-8')
                message.attach(body)
        except Exception as e:
            print(f'没找到文件{context.content_path}')

        # 添加附件
        for att_path,att_name in zip(context.attachments_path_list,context.attachments_name_list):
            with open(att_path,'r') as f:
                attachment = MIMEApplication(f.read()) # 添加内容
                attachment['Content-Type'] = 'application/octet-stream' # 类型：二进制流
                attachment['Content-Disposition'] = 'attachment; filename="%s"' % att_name # 附件头
                message.attach(attachment) # 添加附件
        
        # 添加图片附件
        for img_path,img_name in zip(context.image_attachments_path_list,context.image_attachments_name_list):
            with open(img_path,'rb') as fp:
                image = MIMEImage(fp.read()) # 添加内容
                image['Content-Type'] = 'image/png' # 类型：二进制流
                image['Content-Disposition'] = 'attachment; filename="%s"' % img_name # 附件头
                message.attach(image) # 添加附件
        
        # 发送邮件
        try:
            smtpObj = smtplib.SMTP_SSL(self.mail_host,465)
            smtpObj.login(self.mail_user,self.mail_pass)
            smtpObj.sendmail(
                self.sender,self.receivers,message.as_string())
            print('success')
            smtpObj.quit()
        except smtplib.SMTPException as e:
            print('error',e)
        
# %%
