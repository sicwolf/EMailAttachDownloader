import copy
import time
import logging


class MailQueueItem:
    def __init__(self, mail_index, mail_eml):
        self.mail_index = mail_index
        self.mail_eml = mail_eml
        self.query_times = 1
        self.query_time = time.time()

    def update_query_factor(self):
        self.query_time = time.time()
        self.query_times = self.query_times + 1

    def get_query_times(self):
        return self.query_times


class MailQueue:
    MAX_MAIL_AMOUNT = 50

    def __init__(self):
        self.mail_cache = {}
        self.minimum_query_times = 1
        self.minimum_query_times_mails_index = []

    def enqueue(self, mail_index, mail_eml):
        enqueue_flag = False

        if len(self.mail_cache) == MailQueue.MAX_MAIL_AMOUNT:
            logging.debug(
                "MailQueue.enqueue: len(self.mail_cache) = %d is equal to MailQueue.MAX_MAIL_AMOUNT = %d" %
                (len(self.mail_cache), MailQueue.MAX_MAIL_AMOUNT))

            delete_mail_index = 0

            if len(self.minimum_query_times_mails_index) == 1:
                delete_mail_index = self.minimum_query_times_mails_index[0]
                del self.mail_cache[delete_mail_index]
                del self.minimum_query_times_mails_index[0]
                enqueue_flag = True
            elif len(self.minimum_query_times_mails_index) > 1:
                temp_mails_index = copy.copy(self.minimum_query_times_mails_index)
                loop = 0
                delete_array_index = -1

                for mail_index in temp_mails_index:
                    if mail_index not in self.mail_cache:
                        logging.info("Dirty mail index in MailQueue.minimum_query_times_mails_index: %d", mail_index)
                        del self.minimum_query_times_mails_index[loop]
                    elif mail_index in self.mail_cache and \
                            delete_mail_index in self.mail_cache and \
                            self.mail_cache[mail_index].query_time < self.mail_cache[delete_mail_index].query_time:
                        delete_mail_index = mail_index
                        delete_array_index = loop
                    elif delete_array_index == -1:
                        delete_mail_index = mail_index

                    loop = loop + 1

                if delete_mail_index != 0:
                    del self.mail_cache[delete_mail_index]
                    del self.minimum_query_times_mails_index[delete_array_index]
                    enqueue_flag = True
        elif len(self.mail_cache) > MailQueue.MAX_MAIL_AMOUNT:
            logging.critical(
                "MailQueue.enqueue: len(self.mail_cache)= %d is greater than MailQueue.MAX_MAIL_AMOUNT = %d" %
                (len(self.mail_cache), MailQueue.MAX_MAIL_AMOUNT))
        elif len(self.mail_cache) < MailQueue.MAX_MAIL_AMOUNT:
            logging.debug(
                "MailQueue.enqueue: len(self.mail_cache) = %d is less than MailQueue.MAX_MAIL_AMOUNT = %d" %
                (len(self.mail_cache), MailQueue.MAX_MAIL_AMOUNT))
            enqueue_flag = True

        if enqueue_flag:
            mail_queue_item = MailQueueItem(mail_index, mail_eml)
            self.mail_cache[mail_index] = mail_queue_item

            if mail_queue_item.get_query_times() == self.minimum_query_times:
                logging.debug(
                    "MailQueue.enqueue: mail_queue_item.get_query_times() = %d is equal to self.minimum_query_times = %d" %
                    (mail_queue_item.get_query_times(), self.minimum_query_times))
                found = False

                for temp_mail_index in self.minimum_query_times_mails_index:
                    if temp_mail_index == mail_index:
                        found = True

                if not found:
                    logging.debug(
                        "MailQueue.enqueue: %s is added to minimum_query_times_mails_index" %
                        str(mail_index))
                    self.minimum_query_times_mails_index.append(mail_index)
            elif mail_queue_item.get_query_times() > self.minimum_query_times:
                logging.debug(
                    "MailQueue.enqueue: mail_queue_item.get_query_times() = %d is greater than minimum_query_times = %d" %
                    (mail_queue_item.get_query_times(), self.minimum_query_times))
            elif mail_queue_item.get_query_times() < self.minimum_query_times:
                logging.debug(
                    "MailQueue.enqueue: mail_queue_item.get_query_times() = %d is less than minimum_query_times = %d" %
                    (mail_queue_item.get_query_times(), self.minimum_query_times))

                self.minimum_query_times = mail_queue_item.get_query_times()
                self.minimum_query_times_mails_index.clear()
                self.minimum_query_times_mails_index.append(mail_index)

        return enqueue_flag

    def query(self, mail_index):
        mail_queue_item = None
        temp_mail_eml = None

        if mail_index in self.mail_cache:
            mail_queue_item = self.mail_cache[mail_index]

        if mail_queue_item is not None:
            temp_mail_eml = mail_queue_item.mail_eml
            mail_queue_item.update_query_factor()

            if mail_queue_item.get_query_times() == self.minimum_query_times:
                logging.critical(
                    "MailQueue.query: mail_queue_item.get_query_times() = %d is equal to self.minimum_query_times = %d" %
                    (mail_queue_item.get_query_times(), self.minimum_query_times))

            elif mail_queue_item.get_query_times() > self.minimum_query_times:
                logging.debug(
                    "MailQueue.query: mail_queue_item.get_query_times() = %d is greater than minimum_query_times = %d" %
                    (mail_queue_item.get_query_times(), self.minimum_query_times))

                found_index = -1
                loop = 0

                for temp_mail_index in self.minimum_query_times_mails_index:
                    if temp_mail_index == mail_index:
                        found_index = loop
                        break

                    loop = loop + 1

                if found_index != -1:
                    del self.minimum_query_times_mails_index[found_index]
            elif mail_queue_item.get_query_times() < self.minimum_query_times:
                logging.critical(
                    "MailQueue.query: mail_queue_item.get_query_times() = %d is less than minimum_query_times = %d" %
                    (mail_queue_item.get_query_times(), self.minimum_query_times))

        return temp_mail_eml
