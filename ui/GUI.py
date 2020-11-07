import tkinter as tk

from message.message import StopMSG
from ui.UIUtils import center_window


class GUI(object):
    DISPLAY_LOGIN = 0
    DISPLAY_INBOX = 1

    def __init__(self, worker, width, height):
        self.worker = worker
        self.width = width
        self.height = height
        self.window = tk.Tk()
        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()
        self.window.title('电子邮件附件下载器')
        self.window.geometry('%dx%d' % (self.width, self.height))

        self.message_number = 0

        center_window(self.window, self.width, self.height)

        self.window.protocol('WM_DELETE_WINDOW', self.quit_clicked)

    def mainloop(self):
        self.window.mainloop()

    def get_new_msg_number(self):
        """
        TODO: Add thread lock to protect message_number.
        :return new message number:
        """
        self.message_number = self.message_number + 1
        return self.message_number

    def fullscreen(self):
        self.window.state('zoomed')

    def half_screen(self):
        center_window(self.window, self.screen_width/2, self.screen_height/2)
        self.window.resizable(self.screen_width/2, self.screen_height/2)
        self.window.update()

    def quit_clicked(self):
        self.window.destroy()
        stop_message = StopMSG(self.get_new_msg_number())
        self.worker.put_message(stop_message)

    def quit(self):
        self.window.destroy()
