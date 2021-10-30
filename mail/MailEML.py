import email
import logging

from mail import Utils


class MailEML:
    def __init__(self, header=None, mail=None, mail_index=None):
        self.header = header
        self.mail = mail
        self.sender_name = None
        self.receiver_name = None
        self.sender_addr = None
        self.receiver_addr = None
        self.subject = None
        self.sent_time = None
        self.receive_time = None
        self.receive_time_raw = None
        self.has_attach = False
        self.mail_index = mail_index

        self.parse_mail()
        self.log_mail()

    def set_mail(self, mail):
        self.mail = mail

    def log_mail(self):
        """
        Do not filter the special character in subject, log it faithfully
        """
        logging.info(str(self.mail_index) + str(self.sender_name) + " " + str(self.receiver_name) + " " +
                     str(self.receive_time) + " " + str(self.subject))

    def parse_mail(self):
        to_be_parsed = None

        if self.header is not None:
            to_be_parsed = self.header
        elif self.mail is not None:
            to_be_parsed = self.mail

        self.receive_time_raw = email.utils.parsedate(to_be_parsed['Date'])

        if isinstance(to_be_parsed, str) is False and \
                self.receive_time_raw is not None:
            self.receive_time = Utils.time_tuple_to_number(self.receive_time_raw, False)

        sender = to_be_parsed.get("from")
        receiver = to_be_parsed.get("to")

        sender_name = email.utils.parseaddr(to_be_parsed.get("from"))[0]
        self.sender_addr = email.utils.parseaddr(to_be_parsed.get("from"))[1]
        receiver_name = email.utils.parseaddr(to_be_parsed.get("to"))[0]
        self.receiver_addr = email.utils.parseaddr(to_be_parsed.get("to"))[1]
        self.sender_name = email.header.decode_header(sender_name)
        self.receiver_name = email.header.decode_header(receiver_name)

        if self.sender_name[0][1] is not None:
            self.sender_name = self.sender_name[0][0].decode(self.sender_name[0][1])
        else:
            self.sender_name = self.sender_name[0][0]

        if self.receiver_name[0][1] is not None:
            self.receiver_name = self.receiver_name[0][0].decode(self.receiver_name[0][1])
        else:
            self.receiver_name = self.receiver_name[0][0]

        subject_raw = to_be_parsed.get("Subject")
        subject = email.header.decode_header(subject_raw)

        if subject[0][1] is not None:
            # If encoding type is 'unknown-8bit', decode it as 'GB2312' by default. This is a bug of QQ mail service.
            # TODO: Check the encoding type in other fields of the mail, which country the mail service provider of
            #  sender is , so that the language can be guessed, use the majority encoding type of that language.
            if subject[0][1] == 'unknown-8bit' and 'qq.com' in receiver:
                logging.debug("unknown-8bit error: mail from " + str(self.sender_addr) + "at " + str(self.receive_time))
                self.subject = subject[0][0].decode('GB2312')
            elif subject[0][1] == 'unknown-8bit' and 'westone.com.cn' in receiver:
                logging.debug("unknown-8bit error: mail from " + str(self.sender_addr) + "at " + str(self.receive_time))
                self.subject = subject[0][0].decode('utf-8')
            elif subject[0][1] == 'unknown-8bit':
                logging.debug("unknown-8bit error: mail from " + str(self.sender_addr) + "at " + str(self.receive_time))
                self.subject = subject[0][0].decode('utf-8')
            else:
                self.subject = subject[0][0].decode(subject[0][1])
        else:
            self.subject = subject[0][0]
