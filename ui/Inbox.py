import tkinter as tk
from tkinter import messagebox as mb
from ui.GUI import GUI


class Inbox(GUI):
    def __init__(self, worker):
        GUI.__init__(self, worker, 500, 400)

        self.menuBar = tk.Menu(self.window)
        self.window.config(menu=self.menuBar)

        # Add menu items
        self.helpMenu = tk.Menu(self.menuBar, tearoff=0)
        self.helpMenu.add_command(label="帮助", command=self.help_clicked)
        self.helpMenu.add_separator()
        self.helpMenu.add_command(label="关于", command=self.about_clicked)
        self.menuBar.add_cascade(label="帮助", menu=self.helpMenu)

        self.fullscreen()

    def about_clicked(self):
        mb.showinfo("关于", "电子邮件附件下载器V1.0.1")

    def help_clicked(self):
        mb.showinfo("帮助", "电子邮件附件下载器的帮助")
