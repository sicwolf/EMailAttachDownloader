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
        self.__has_attach = False
        self.mail_index = mail_index

        self.__parse_mail()
        self.log_mail()

    def set_mail(self, mail):
        self.mail = mail

    def log_mail(self):
        """
        Do not filter the special character in subject, log it faithfully
        """
        logging.info(str(self.mail_index) + str(self.sender_name) + " " + str(self.receiver_name) + " " +
                     str(self.receive_time) + " " + str(self.subject))

    def __parse_mail(self):
        to_be_parsed = None

        if self.header is not None:
            to_be_parsed = self.header
        elif self.mail is not None:
            to_be_parsed = self.mail

        # parse receive time
        self.receive_time_raw, self.receive_time = self.__parse_receive_time(to_be_parsed)
        # parse sender
        sender, self.sender_addr, self.sender_name = self.__parse_participant(to_be_parsed, "from")
        # parse receiver
        receiver, self.receiver_addr, self.receiver_name = self.__parse_participant(to_be_parsed, "to")
        # parse subject
        self.subject = self.__parse_subject(to_be_parsed, receiver)

    def __parse_receive_time(self, to_be_parsed):
        receive_time_raw = email.utils.parsedate(to_be_parsed['Date'])
        receive_time = None

        if isinstance(to_be_parsed, str) is False and \
                receive_time_raw is not None:
            receive_time = Utils.time_tuple_to_number(receive_time_raw, False)

        return receive_time_raw, receive_time

    def __parse_participant(self, to_be_parsed, participant_type):
        participant = to_be_parsed.get(participant_type)
        participant_name = email.utils.parseaddr(to_be_parsed.get(participant_type))[0]
        participant_addr = email.utils.parseaddr(to_be_parsed.get(participant_type))[1]
        participant_name = email.header.decode_header(participant_name)

        if participant_name[0][1] is not None:
            participant_name = participant_name[0][0].decode(participant_name[0][1])
        else:
            participant_name = participant_name[0][0]

        return participant, participant_addr, participant_name

    def __parse_subject(self, to_be_parsed, receiver):
        subject_raw = to_be_parsed.get("Subject")
        subject = email.header.decode_header(subject_raw)

        if subject[0][1] is not None and receiver is not None:
            # If encoding type is 'unknown-8bit', decode it as 'GB2312' by default. This is a bug of QQ mail service.
            # TODO: Check the encoding type in other fields of the mail, which country the mail service provider of
            #  sender is , so that the language can be guessed, use the majority encoding type of that language.
            if subject[0][1] == 'unknown-8bit' and 'qq.com' in receiver:
                logging.debug("unknown-8bit error: mail from " + str(self.sender_addr) + "at " + str(self.receive_time))
                subject_str = subject[0][0].decode('GB2312')
            elif subject[0][1] == 'unknown-8bit' and 'westone.com.cn' in receiver:
                logging.debug("unknown-8bit error: mail from " + str(self.sender_addr) + "at " + str(self.receive_time))
                subject_str = subject[0][0].decode('utf-8')
            elif subject[0][1] == 'unknown-8bit':
                logging.debug("unknown-8bit error: mail from " + str(self.sender_addr) + "at " + str(self.receive_time))
                subject_str = subject[0][0].decode('utf-8')
            else:
                subject_str = subject[0][0].decode(subject[0][1])
        elif receiver is None and '10000@qq.com' in self.sender_addr:
            # If sender is 10000@qq.com and encoding type is 'unknown-8bit', decode it as 'GB2312' by default.
            # This is a bug of QQ mail service.
            logging.debug("unknown-8bit error: mail from " + str(self.sender_addr) + "at " + str(self.receive_time))
            subject_str = subject[0][0].decode('GB2312')
        else:
            subject_str = subject[0][0]

        return subject_str

    def check_attachment_existence(self):
        has_attach = False

        if self.mail is not None:
            for part in self.mail.walk():
                temp_content_disposition = part.get('Content-Disposition')

                if temp_content_disposition is not None and 'attachment' in temp_content_disposition.lower():
                    has_attach = True
                    break

        return has_attach
