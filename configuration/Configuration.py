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
        self.app_version = "V1.0.1"
        self.display_flag_mail_with_attach = True
        self.app_icon_file = 'resource\\app2.ico'
        self.download_flag_time = False
        self.download_flag_last_mails = True
        self.download_since_time = time.localtime(time.time() - 10000)
        self.download_till_time = time.localtime(time.time())
        self.download_mail_number = 20
        self.download_default_folder = get_default_download_path()
        self.download_folder = get_default_download_path()
        self.download_in_different_folder = True
        self.status_recall = None

    def set_status_recall(self, status_recall):
        self.status_recall = status_recall
