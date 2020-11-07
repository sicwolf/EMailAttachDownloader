import email

from mail import Utils


class MailEML:
    def __init__(self, header=None, mail=None):
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

        self.parse_mail()

    def set_mail(self, mail):
        self.mail = mail

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
            self.subject = subject[0][0].decode(subject[0][1])
        else:
            self.subject = subject[0][0]
