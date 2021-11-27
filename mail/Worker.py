import logging
import imaplib
import os
import socket
import threading
import queue

from mail.MailSession import MailSession
from message.message import CommonMSG


class Worker(threading.Thread):

    def __init__(self, configuration):
        threading.Thread.__init__(self)
        self.thread_stop = False
        self.mail_session = None
        self.configuration = configuration
        self.queue = queue.Queue(configuration.worker_queue_size)

    def run(self):
        while not self.thread_stop:
            logging.debug("Work.run: thread %d %s waiting for message" % (self.ident, self.name))
            try:
                message = self.queue.get(block=True)  # 接收消息
            except queue.Empty as e:
                logging.error("Work.run: " + str(e))
                break

            if message.message_type == CommonMSG.MSG_TYPE_THREAD_STOP:
                logging.info("Worker.run: MSG_TYPE_THREAD_STOP received.")
                message.set_status(CommonMSG.MSG_STATUS_HANDLING)
                self.stop()
            elif message.message_type == CommonMSG.MSG_TYPE_MAIL_LOGIN:
                logging.info("Worker.run: MSG_TYPE_MAIL_LOGIN received")
                mails_eml = None
                message.set_status(CommonMSG.MSG_STATUS_HANDLING)
                (handle_result, mails_index) = self.login(message.mail_server, message.mail_address, message.password)

                if handle_result == CommonMSG.ERR_CODE_SUCCESSFUL:
                    mails_eml = self.mail_session.load_header(mails_index[-1], message.load_header_amount)

                message.recall(handle_result, mails_index, mails_eml)
                logging.debug("Worker.run: " + str(mails_index))
                message.set_status(CommonMSG.MSG_STATUS_COMPLETED)
            elif message.message_type == CommonMSG.MSG_TYPE_MAIL_DOWNLOAD:
                logging.info("Worker.run: MSG_TYPE_MAIL_DOWNLOAD received")
                message.set_status(CommonMSG.MSG_STATUS_HANDLING)
                self.download(message)
                message.set_status(CommonMSG.MSG_STATUS_COMPLETED)
            elif message.message_type == CommonMSG.MSG_TYPE_CONFIG_UPDATE:
                logging.info("Worker.run: MSG_TYPE_CONFIG_UPDATE received")
                message.set_status(CommonMSG.MSG_STATUS_HANDLING)
                self.configuration = message.configuration
                self.mail_session.set_configuration(self.configuration)
                message.set_status(CommonMSG.MSG_STATUS_COMPLETED)
            elif message.message_type == CommonMSG.MSG_TYPE_MAIL_LOAD:
                logging.info("Worker.run: MSG_TYPE_MAIL_LOAD received")
                message.set_status(CommonMSG.MSG_STATUS_HANDLING)
                mails = self.mail_session.load_mail(message.start_mail_index, message.load_mail_amount)
                message.recall(mails)
                message.set_status(CommonMSG.MSG_STATUS_COMPLETED)
            elif message.message_type == CommonMSG.MSG_TYPE_MAIL_LOAD_FULL:
                logging.info("Worker.run: MSG_TYPE_MAIL_LOAD_FULL received")
                message.set_status(CommonMSG.MSG_STATUS_HANDLING)
                mails = self.mail_session.load_mail(message.mail_index, 1)
                temp_mail_element = mails[message.mail_index]

                # if temp_mail_element is not None:
                has_attach = temp_mail_element.check_attachment_existence()
                message.recall(message.mail_index_gui, has_attach)
                message.set_status(CommonMSG.MSG_STATUS_COMPLETED)

    def put_message(self, message, block=False, timeout=None):
        logging.debug("Worker.put_message calling")
        return_status = CommonMSG.ERR_CODE_SUCCESSFUL

        if self.queue.qsize() == self.configuration.worker_queue_size:
            return_status = CommonMSG.ERR_CODE_QUEUE_FULL
        else:
            self.queue.put(message, block, timeout)
            message.set_status(CommonMSG.MSG_STATUS_SENT)

        logging.debug("Worker.put_message called")
        return return_status

    def login(self, server_name, user_name, password):
        logging.debug("Worker.login calling")
        return_status = CommonMSG.ERR_CODE_SUCCESSFUL
        mails_index = None

        try:
            self.mail_session = MailSession(server_name,
                                            user_name,
                                            password,
                                            configuration=self.configuration)
            # mails_index = self.mail_session.fetch_all_mail_index()
        except imaplib.IMAP4.error as e:
            logging.error(e)
            self.mail_session = None
            return_status = CommonMSG.ERR_CODE_WRONG_USER_NAME_OR_PASSWORD
        except socket.gaierror as e:
            logging.error(e)
            self.mail_session = None
            return_status = CommonMSG.ERR_CODE_WRONG_SERVER_NAME
        except os.error as e:
            logging.error(e)
            self.mail_session = None
            return_status = CommonMSG.ERR_CODE_CONNECTION_TIMEOUT
        except BaseException as e:
            logging.error(e)
            self.mail_session = None
            return_status = CommonMSG.ERR_CODE_UNKNOWN_ERROR

        if return_status == CommonMSG.ERR_CODE_SUCCESSFUL:
            try:
                mails_index = self.mail_session.fetch_all_mail_index()
            except imaplib.IMAP4.error as e:
                logging.error(e)
                self.mail_session = None
                return_status = CommonMSG.ERR_CODE_WRONG_USER_NAME_OR_PASSWORD
            except BaseException as e:
                logging.error(e)
                self.mail_session = None
                return_status = CommonMSG.ERR_CODE_UNKNOWN_ERROR

        logging.debug("Worker.login called")
        return return_status, mails_index

    def download(self, message):
        logging.debug("Worker.download calling")

        if message.download_mails_index is not None:
            self.mail_session.save_mails_attachment(message.download_mails_index, message.download_mail_number)

        logging.debug("Worker.download called")

    def stop(self):
        logging.debug("Worker.stop calling")
        self.thread_stop = True
        logging.debug("Worker.stop called")
