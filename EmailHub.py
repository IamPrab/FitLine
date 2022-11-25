import win32com.client as win32
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('message', help="Message To Sender")
parser.add_argument('emailsList',help="emails")


args = parser.parse_args()

def EmailsToStr (emailList):

        defaultEmails = "axel_adtl_team@intel.com" + ";"
        additionalEmails = emailList.split(",")

        for emails in additionalEmails:
                defaultEmails = defaultEmails +str(emails) + ";"

        print(defaultEmails)
        return defaultEmails

def send_mail(message, emailList):
        EmailsToStr(emailList)
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)

        emailStrList = EmailsToStr(emailList)
        mail.To = emailStrList

        #mail.Cc = 'dummy@intel.com'
        mail.Subject = "  Axel Notification "
        mail.HtmlBody = (message)
        mail.Send()


if args.message != '' and args.emailsList != '':
        send_mail(args.message, args.emailsList)
