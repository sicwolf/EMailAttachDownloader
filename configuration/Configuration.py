import os
import time


def get_default_download_path():
    """Returns the default downloads path for linux or windows"""
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        return os.path.join(os.path.expanduser('~'), 'downloads')


class Configuration:
    def __init__(self):
        self.app_name = "电子邮件附件下载器"
        self.app_version = "V1.0.6"
        self.display_flag_mail_with_attach = True
        self.app_icon_file = 'resource\\app2.ico'
        self.attach_icon_file = 'resource\\paperclipreal.gif'
        self.download_flag_time = False
        self.download_flag_last_mails = True
        self.download_since_time = time.localtime(time.time() - 10000)
        self.download_till_time = time.localtime(time.time())
        self.mail_header_amount = 80
        self.worker_queue_size = 30
        self.download_mail_number = 20
        self.download_default_folder = get_default_download_path()
        self.download_folder = get_default_download_path()
        self.download_in_same_folder = False
        self.download_folder_time_prefix = False
        self.feedback_link_github = "https://github.com/sicwolf/EMailAttachDownloader/issues"
        self.feedback_link_gitee = "https://gitee.com/deepwater/EMailAttachDownloader/issues"
        self.auth_code_links = {
            "imap.qq.com": "https://service.mail.qq.com/cgi-bin/help?subtype=1&&no=1001607&&id=28",
            "imap.163.com": "https://note.youdao.com/ynoteshare/index.html?id=f9fef46114fb922b45460f4f55d96853",
            "imap.gmail.com": "https://support.google.com/accounts/answer/185833",
            "imap.sohu.com": "https://blog.csdn.net/sicwolf/article/details/121050352"}
        self.status_recall = None

    def set_status_recall(self, status_recall):
        self.status_recall = status_recall
