#coding:utf-8
from exchangelib import DELEGATE, Account, Credentials,Configuration,NTLM

from exchangelib import HTMLBody,Message,Mailbox,FileAttachment
import sys,os
reload(sys)
sys.setdefaultencoding('utf8')

class MailSender:
    sendername="MHS\\automator"
    password="arr78612#"
    mailserver="owasz.yff.com"
    sendermail="Automator@yff.com"

    def sendMail(self,recipients,subject,content,isHtml,attatchment,successNum,faileNum,errorNum,importance='Normal'):
        """
        发送邮件
        :param recipients:  收件人列表
        :param subject: 邮件标题
        :param attatchment: 附件
        :param importance: 重要级别，默认中等
        :return:
        """
        config = Configuration(
            server=self.mailserver,
            credentials=Credentials(username=self.sendername, password=self.password),
            auth_type=NTLM
            )

        account = Account(primary_smtp_address=self.sendermail,
                          config =config,
                          access_type=DELEGATE,
                          locale="CN"
                          )

        if isHtml:
            try:
                content=HTMLBody(content)
            except:
                content="%s is not html content" % content
        mailto= []
        for recipient in recipients :
            mailto.append(Mailbox(email_address=recipient))

        choice = "Normal"
        if importance in ['High', 'high', 'HIGH', 'H', 'h']:
            choice = 'High'
        if importance in ['Low', 'low', 'LOW', 'L', 'l']:
            choice = 'Low'
        if importance in ['Normal', 'normal', 'NORMAl', 'N', 'n']:
            choice = 'Normal'


    #发送附件
        if os.path.isfile(attatchment):
            file_obj=open(attatchment,"r")
            try:
                attatchcontent=file_obj.read()
            finally:
                file_obj.close()
            binary_file_content = attatchcontent.encode('utf-8')
            attatchmentName="接口运行详情报告.html"
            my_file = FileAttachment(name=attatchmentName, content=binary_file_content)
        else:
            binary_file_content ="<p>报告获取失败</p>"
            my_file = ""
        allcasenum=successNum+faileNum+errorNum
        if my_file=="":
            body_content = '<html><body style="text-align:center"></h4>' \
                           '<table border="1" style="width:700px;text-align:center">' \
                           '<caption>接口运行情况</caption><tr><th>总用例数</th><th>通过用例总数</th><th>失败用例总数</th><th>错误用例总数</th>' \
                           '</tr><tr><td>%d</td><td style="color:green">%d </td><td style="color:orange">%d </td><td style="color:red">%d </td>' \
                           '</tr></table></body></html>'%(allcasenum,successNum,faileNum,errorNum)
        else:
            body_content = '<html><body style="text-align:center"></h4>' \
                           '<table border="1" style="width:700px;text-align:center">' \
                           '<caption>接口运行情况</caption><tr><th>总用例数</th><th>通过用例总数</th><th>失败用例总数</th><th>错误用例总数</th>' \
                           '</tr><tr><td>%d</td><td style="color:green">%d </td><td style="color:orange">%d </td><td style="color:red">%d </td>' \
                           '</tr></table><p>接口详情信息请下载附件查看</p></body></html>' % (allcasenum, successNum, faileNum, errorNum)

        item = Message(
            account=account,
            subject=subject,
            body=HTMLBody(body_content),
            to_recipients=mailto,
            importance=choice
        )
        if my_file!="":
            item.attach(my_file)
        item.send()

if __name__ == '__main__':
    mailsender=MailSender()
    mailsender.sendMail(['nan.wei@yff.com'],'Test','weinannantest',True,r'D:\project\auto_interface\antoInterfacePlatform\main\report\2019-10-27-15_00_06_result.html','normal')