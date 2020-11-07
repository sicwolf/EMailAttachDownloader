import logging

from configuration.Configuration import Configuration
from mail.Worker import Worker
from ui.Login import Login


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.DEBUG)
    fileHandler = logging.FileHandler('log.log', mode='w', encoding='UTF-8')
    fileHandler.setLevel(logging.NOTSET)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    consoleHandler.setFormatter(formatter)
    fileHandler.setFormatter(formatter)

    logger.addHandler(consoleHandler)
    logger.addHandler(fileHandler)

    fetch_mail = None
    mails = None

    configuration = Configuration()
    logging.info(configuration.app_name + ' ' + configuration.app_version)

    worker = Worker()
    worker.start()

    login_window = Login(worker, configuration)
    login_window.mainloop()

    worker.join()
