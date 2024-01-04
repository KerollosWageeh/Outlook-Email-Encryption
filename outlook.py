import win32com.client
import datetime

class OutlookHandler:
    @staticmethod
    def get_current_user():
        outlook_app = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook_app.GetNamespace("MAPI")
        current_user = namespace.CurrentUser.AddressEntry.GetExchangeUser().PrimarySmtpAddress
        return current_user
    
    @staticmethod
    def send_email(to, message):
        sender = OutlookHandler.get_current_user()
        outlook_app = win32com.client.Dispatch("Outlook.Application")
        mail_item = outlook_app.CreateItem(0)
        mail_item.Subject = "Secure Email Through Team 7"
        mail_item.Body = message
        mail_item.To = to
        mail_item.Send()

    @staticmethod
    def get_inbox():
        outlook_app = win32com.client.Dispatch("Outlook.Application")
        mapi = outlook_app.GetNamespace("MAPI")
        inbox = mapi.GetDefaultFolder(6)
        messages = inbox.Items
        messages = messages.Restrict("[Subject] = 'Secure Email Through Team 7'")
        messages.Sort("[ReceivedTime]", True)
        return messages