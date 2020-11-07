import copy


class CommonMSG:
    """
    Thread message format: [message number, message status, message[message type, field 1, ..., field n]
    """
    MSG_STATUS_CREATED = 0
    MSG_STATUS_SENT = 1
    MSG_STATUS_HANDLING = 2
    MSG_STATUS_RESPONDED = 3
    MSG_STATUS_COMPLETED = 4

    # Common message
    MSG_TYPE_COMMON = 0x000001

    # Thread related message
    MSG_TYPE_THREAD_STOP = 0x010001

    # User related message
    MSG_TYPE_MAIL_LOGIN = 0x020001

    # Mail related message
    MSG_TYPE_MAIL_DOWNLOAD = 0x030001
    MSG_TYPE_MAIL_LOAD = 0x030002

    # Configuration related message
    MSG_TYPE_CONFIG_UPDATE = 0x040001

    #
    ERR_CODE_SUCCESSFUL = 0x800000

    # Mail error code
    ERR_CODE_WRONG_SERVER_NAME = 0x810001
    ERR_CODE_WRONG_USER_NAME_OR_PASSWORD = 0x810002

    # Worker error code
    ERR_CODE_QUEUE_FULL = 0x820001

    DOWNLOAD_FLAG_LAST_NUMBER = 1
    DOWNLOAD_FLAG_PERIOD = 2

    def __init__(self, message_number, recall=None):
        self.message_number = message_number
        self.message_type = CommonMSG.MSG_TYPE_COMMON
        self.message_status = CommonMSG.MSG_STATUS_CREATED
        self.error_code = CommonMSG.ERR_CODE_SUCCESSFUL
        self.recall = recall

    def set_status(self, status):
        self.message_status = status

    def get_status(self):
        return self.message_status


class LoginMSG(CommonMSG):
    need_response = True

    def __init__(self, message_number, mail_server, mail_address, password, load_header_amount, recall=None):
        CommonMSG.__init__(self, message_number, recall=recall)
        self.message_type = CommonMSG.MSG_TYPE_MAIL_LOGIN
        self.mail_server = mail_server
        self.mail_address = mail_address
        self.password = password
        self.load_header_amount = load_header_amount


class UpdateConfigMSG(CommonMSG):

    def __init__(self, message_number, configuration, recall=None):
        CommonMSG.__init__(self, message_number, recall=recall)
        self.message_type = CommonMSG.MSG_TYPE_CONFIG_UPDATE
        self.configuration = copy.copy(configuration)


class DownloadMSG(CommonMSG):

    def __init__(self,
                 message_number,
                 download_flag,
                 session_index=-1,
                 download_folder='tmp',
                 download_mail_number=50,
                 download_mails_index=None,
                 download_since_time=None,
                 download_till_time=None,
                 recall=None):
        CommonMSG.__init__(self, message_number, recall=recall)
        self.message_type = CommonMSG.MSG_TYPE_MAIL_DOWNLOAD
        self.download_flag = download_flag
        self.session_index = session_index
        self.download_folder = download_folder
        self.download_mail_number = download_mail_number
        self.download_mails_index = download_mails_index
        self.download_since_time = download_since_time
        self.download_till_time = download_till_time
        self.error_code = CommonMSG.ERR_CODE_SUCCESSFUL


class LoadMailMSG(CommonMSG):

    def __init__(self, message_number, start_mail_index, load_mail_amount, ascending=False, recall=None):
        CommonMSG.__init__(self, message_number)
        self.message_type = CommonMSG.MSG_TYPE_MAIL_LOAD
        self.start_mail_index = start_mail_index
        self.load_mail_amount = load_mail_amount
        self.ascending = ascending
        self.need_response = True
        self.recall = recall


class StopMSG(CommonMSG):

    def __init__(self, message_number):
        CommonMSG.__init__(self, message_number)
        self.message_type = CommonMSG.MSG_TYPE_THREAD_STOP
        self.need_response = False
