import datetime
import logging
import re
import time
import tkinter as tk
import webbrowser
from tkinter import messagebox as mb, ttk
from tkinter import Text as tx
from tkinter.filedialog import askdirectory
from tkinter.ttk import Progressbar

import mail.Utils as Utils
import ui.UIUtils as UIUtils
from message.message import LoginMSG, CommonMSG, DownloadMSG, UpdateConfigMSG, LoadMailMSG
from ui.GUI import GUI


class Login(GUI):

    def __init__(self, worker, configuration):
        GUI.__init__(self, worker, 375, 140)
        self.configuration = configuration
        self.window.iconbitmap(self.configuration.app_icon_file)

        self.mail_amount_one_page = self.configuration.mail_header_amount

        self.label_addr_width = 60
        self.label_addr_height = 25
        self.entry_addr_width = 260
        self.entry_addr_height = 25
        self.label_entry_spacing = 10
        self.label_password_width = 60
        self.label_password_height = 25
        self.entry_password_width = 260
        self.entry_password_height = 25
        self.button_login_width = 100
        self.button_login_height = 25
        self.button_quit_width = 100
        self.button_quit_height = 25
        self.login_quit_spacing = 10
        self.progress_login_width = self.button_login_width
        self.progress_login_height = self.button_login_height
        self.login_vertical_spacing = 15

        self.button_save_folder_width = 90
        self.button_save_folder_height = 25
        self.entry_save_folder_width = 340
        self.entry_save_folder_height = 25
        self.button_save_folder_place_x = 5
        self.button_save_folder_place_y = 5
        self.button_entry_save_folder_spacing = 10

        self.label_percent_width = 40
        self.label_percent_height = 15
        self.progress_download_height = 15
        self.label_status_height = 15
        self.label_percent_place_x = 20
        self.progress_download_place_x = 20
        self.label_status_place_x = 1
        self.label_percent_status_spacing = 5
        self.progress_download_percent_spacing = 5
        self.label_status_window_spacing = 1

        self.frame_inbox_spacing = 5
        self.frame_inbox_width = self.window.winfo_width() - 2 * self.frame_inbox_spacing
        self.frame_inbox_height = self.window.winfo_height() - \
                                  2 * self.frame_inbox_spacing - \
                                  self.button_save_folder_place_y - self.button_save_folder_height - \
                                  self.label_percent_height - self.label_percent_status_spacing - \
                                  self.label_status_height - self.label_status_window_spacing
        self.tree_inbox_spacing = 0
        self.scrollBar_inbox_width = 15
        self.tree_inbox_scrollbar_spacing = 5
        self.tree_inbox_attach_width = 40
        self.tree_inbox_sender_width = 130
        self.tree_inbox_receiver_width = 130
        self.tree_inbox_receive_time_width = 130

        self.window.resizable(0, 0)

        self.label_addr = tk.Label(self.window, text="邮箱地址")
        self.label_password = tk.Label(self.window, text="邮箱密码")

        self.entry_addr = tk.Entry(self.window, text="邮箱地址", show=None, font=('Arial', 12))
        self.entry_password = tk.Entry(self.window, text="密码", show='*', font=('Arial', 12))

        self.button_login = tk.Button(self.window, text="登录", command=self.login_clicked)
        self.button_quit = tk.Button(self.window, text="退出", command=self.quit_clicked)

        self.progress_login = ttk.Progressbar(self.window,
                                              length=200,
                                              mode="indeterminate",
                                              orient=tk.HORIZONTAL)

        self.__layout_login()

        self.progress_frame = None
        self.progress_bar = None

        self.frame_inbox = tk.Frame(self.window)
        self.scrollBar_inbox = tk.Scrollbar(self.frame_inbox)
        self.tree_inbox = ttk.Treeview(
            self.frame_inbox,
            columns=('attachment', 'sender', 'receiver', 'receive_time', 'subject'),
            show="headings",
            yscrollcommand=self.scrollBar_inbox.set)
        self.tree_inbox.column('attachment', minwidth=self.tree_inbox_attach_width, width=self.tree_inbox_attach_width, anchor='center', stretch=tk.NO)
        self.tree_inbox.column('sender', minwidth=self.tree_inbox_sender_width, width=self.tree_inbox_sender_width, anchor='w', stretch=tk.NO)
        self.tree_inbox.column('receiver', minwidth=self.tree_inbox_receiver_width, width=self.tree_inbox_receiver_width, anchor='w', stretch=tk.NO)
        self.tree_inbox.column('receive_time', minwidth=self.tree_inbox_receive_time_width, width=self.tree_inbox_receive_time_width, anchor='center', stretch=tk.NO)
        self.tree_inbox.column('subject', minwidth=175, width=175, anchor='w')
        self.tree_inbox.heading('attachment', text='附件')
        self.tree_inbox.heading('sender', text='发件人')
        self.tree_inbox.heading('receiver', text='收件人')
        self.tree_inbox.heading('receive_time', text='收件时间')
        self.tree_inbox.heading('subject', text='邮件主题')
        self.scrollBar_inbox.config(command=self.tree_inbox.yview)

        self.label_percent = tk.Label(self.window, text="0%")
        self.progress_download = Progressbar(self.window, length=500, mode='determinate')
        self.label_status = tk.Label(self.window,
                                     # text='点击"操作->下载附件"开始下载附件文件...',
                                     text='',
                                     justify=tk.LEFT,
                                     relief=tk.SUNKEN,
                                     anchor=tk.W,
                                     borderwidth=1)

        self.menuBar = tk.Menu(self.window)
        self.window.config(menu=self.menuBar)

        # Add menu items
        self.operationMenu = tk.Menu(self.menuBar, tearoff=0)
        # self.operationMenu.add_command(label="收取新邮件", command=self.refresh_clicked)
        self.operationMenu.add_command(label="下载选中邮件附件", command=self.download_selected_clicked)
        self.operationMenu.add_command(label="下载所有邮件附件", command=self.download_clicked)
        self.operationMenu.add_separator()
        # self.operationMenu.add_command(label="更换邮箱", command=self.switch_clicked)
        self.operationMenu.add_command(label="退出", command=self.quit_clicked)
        self.menuBar.add_cascade(label="操作", menu=self.operationMenu)

        self.configMenu = tk.Menu(self.menuBar, tearoff=0)
        # self.configMenu.add_command(label="显示设置", command=self.display_config_clicked)
        # self.configMenu.add_command(label="下载设置", command=self.download_config_clicked)
        self.config_download_in_same_folder = tk.BooleanVar()
        self.config_download_in_same_folder.set(self.configuration.download_in_same_folder)
        self.configMenu.add_checkbutton(label="附件下载到相同路径下",
                                        onvalue=True,
                                        offvalue=False,
                                        variable=self.config_download_in_same_folder,
                                        command=self.download_folder_config_clicked)
        self.config_time_prefix_folder = tk.BooleanVar()
        self.config_time_prefix_folder.set(self.configuration.download_folder_time_prefix)
        self.configMenu.add_checkbutton(label="下载子路径带时间戳",
                                        onvalue=True,
                                        offvalue=False,
                                        variable=self.config_time_prefix_folder,
                                        command=self.time_prefix_folder_clicked)

        self.menuBar.add_cascade(label="设置", menu=self.configMenu)

        self.helpMenu = tk.Menu(self.menuBar, tearoff=0)
        # self.helpMenu.add_command(label="帮助", command=self.help_clicked)
        # self.helpMenu.add_separator()
        submenu_feedback = tk.Menu(self.helpMenu, tearoff=0)
        # self.helpMenu.add_command(label="反馈", command=self.feedback_clicked)
        submenu_feedback.add_command(label="通过gitee反馈问题", command=self.feedback_clicked_gitee)
        submenu_feedback.add_command(label="通过github反馈问题", command=self.feedback_clicked_github)
        self.helpMenu.add_cascade(label="反馈", menu=submenu_feedback)
        self.helpMenu.add_command(label="关于", command=self.about_clicked)
        self.menuBar.add_cascade(label="帮助", menu=self.helpMenu)

        # self.donateMenu = tk.Menu(self.menuBar, tearoff=0)
        # self.donateMenu.add_command(label="捐赠二维码", command=self.donate_clicked)
        # self.menuBar.add_cascade(label="捐赠", menu=self.donateMenu)

        self.button_save_folder = tk.Button(self.window, text="附件下载文件夹", command=self.select_path_clicked)
        self.current_save_folder = tk.StringVar(self.window, value=self.configuration.download_folder)
        self.entry_save_folder = tk.Entry(self.window, textvariable=self.current_save_folder, state='disabled')

        self.str_addr = None
        self.str_password = None
        self.str_server = None

        self.minimum_display_mail_index = -1
        self.maximum_display_mail_index = -1
        self.mails_index = []
        self.current_display_mails = {}
        self.received_mails = {}

        self.clean_inbox_control()

        self.display_status = GUI.DISPLAY_LOGIN

    def __layout_login(self):
        self.window.update()
        logging.debug("__layout_login: window.winfo_width()=%d window.winfo_height()=%d" %
                      (self.window.winfo_width(), self.window.winfo_height()))

        label_addr_place_x = self.window.winfo_width() / 2 - \
                             (self.label_addr_width + self.label_entry_spacing + self.entry_addr_width) / 2
        label_addr_place_y = self.window.winfo_height() / 2 - \
                             (self.label_addr_height + self.login_vertical_spacing + self.label_password_height +
                              self.login_vertical_spacing + self.button_login_height) / 2
        entry_addr_place_x = label_addr_place_x + self.label_addr_width + self.label_entry_spacing
        entry_addr_place_y = label_addr_place_y

        label_password_place_x = self.window.winfo_width() / 2 - \
                                 (self.label_password_width + self.label_entry_spacing + self.entry_password_width) / 2
        label_password_place_y = label_addr_place_y + self.label_addr_height + self.login_vertical_spacing
        entry_password_place_x = label_password_place_x + self.label_password_width + self.label_entry_spacing
        entry_password_place_y = label_password_place_y

        button_login_place_x = self.window.winfo_width() / 2 - \
                               (self.button_login_width + self.label_entry_spacing + self.button_quit_width) / 2
        button_login_place_y = label_password_place_y + self.label_password_height + self.label_entry_spacing
        button_quit_place_x = button_login_place_x + self.button_login_width + self.label_entry_spacing
        button_quit_place_y = button_login_place_y

        self.label_addr.place(x=label_addr_place_x, y=label_addr_place_y,
                              width=self.label_addr_width, height=self.label_addr_height)
        self.entry_addr.place(x=entry_addr_place_x, y=entry_addr_place_y,
                              width=self.entry_addr_width, height=self.entry_addr_height)
        self.label_password.place(x=label_password_place_x, y=label_password_place_y,
                                  width=self.label_password_width, height=self.label_password_height)
        self.entry_password.place(x=entry_password_place_x, y=entry_password_place_y,
                                  width=self.entry_password_width, height=self.entry_password_height)
        self.button_login.place(x=button_login_place_x, y=button_login_place_y,
                                width=self.button_login_width, height=self.button_login_height)
        self.button_quit.place(x=button_quit_place_x, y=button_quit_place_y,
                               width=self.button_quit_width, height=self.button_quit_height)

    def __layout_inbox(self):
        self.window.update()
        entry_save_folder_place_x = self.button_save_folder_place_x + \
                                    self.button_save_folder_width + \
                                    self.button_entry_save_folder_spacing
        entry_save_folder_place_y = self.button_save_folder_place_y
        entry_save_folder_width = self.window.winfo_width() - \
                                  self.button_save_folder_place_x - \
                                  self.button_save_folder_place_x - \
                                  self.button_save_folder_width - \
                                  self.button_entry_save_folder_spacing

        label_status_place_x = self.label_status_place_x
        label_status_place_y = self.window.winfo_height() - self.label_status_height - self.label_status_window_spacing
        label_status_width = self.window.winfo_width() - self.label_status_place_x * 2
        label_status_height = self.label_status_height

        progress_download_place_x = self.progress_download_place_x
        progress_download_place_y = label_status_place_y - \
                                    self.label_percent_status_spacing - \
                                    self.progress_download_height
        progress_download_width = self.window.winfo_width() - \
                                  progress_download_place_x * 2 - \
                                  self.progress_download_percent_spacing - \
                                  self.label_percent_width
        progress_download_height = self.progress_download_height

        label_percent_place_x = progress_download_place_x + \
                                progress_download_width + \
                                self.progress_download_percent_spacing
        label_percent_place_y = progress_download_place_y
        label_percent_width = self.label_percent_width
        label_percent_height = self.label_percent_height

        frame_inbox_place_x = self.frame_inbox_spacing
        frame_inbox_place_y = self.button_save_folder_place_y + self.button_save_folder_height + \
                              self.frame_inbox_spacing
        frame_inbox_width = self.window.winfo_width() - 2 * self.frame_inbox_spacing
        frame_inbox_height = self.window.winfo_height() - \
                             2 * self.frame_inbox_spacing - \
                             self.button_save_folder_place_y - self.button_save_folder_height - \
                             self.label_percent_height - self.label_percent_status_spacing - \
                             self.label_status_height - self.label_status_window_spacing
        tree_inbox_place_x = self.tree_inbox_spacing
        tree_inbox_place_y = self.tree_inbox_spacing
        tree_inbox_width = frame_inbox_width - self.scrollBar_inbox_width - self.tree_inbox_scrollbar_spacing
        tree_inbox_height = frame_inbox_height
        scrollbar_inbox_place_x = frame_inbox_width - self.scrollBar_inbox_width
        scrollbar_inbox_place_y = self.tree_inbox_spacing
        scrollbar_inbox_width = self.scrollBar_inbox_width
        scrollbar_inbox_height = frame_inbox_height
        tree_inbox_subject_width = frame_inbox_width - \
                                   self.tree_inbox_receive_time_width - \
                                   self.tree_inbox_attach_width - \
                                   self.tree_inbox_receiver_width - \
                                   self.tree_inbox_sender_width

        self.button_save_folder.place(x=self.button_save_folder_place_x, y=self.button_save_folder_place_y,
                                      width=self.button_save_folder_width, height=self.button_save_folder_height)
        self.entry_save_folder.place(x=entry_save_folder_place_x, y=entry_save_folder_place_y,
                                     width=entry_save_folder_width, height=self.entry_save_folder_height)

        self.frame_inbox.place(x=frame_inbox_place_x, y=frame_inbox_place_y,
                               width=frame_inbox_width, height=frame_inbox_height)
        self.tree_inbox.place(x=tree_inbox_place_x, y=tree_inbox_place_y,
                              width=tree_inbox_width, height=tree_inbox_height)
        self.scrollBar_inbox.place(x=scrollbar_inbox_place_x, y=scrollbar_inbox_place_y,
                                   width=scrollbar_inbox_width, height=scrollbar_inbox_height)

        self.label_status.place(x=label_status_place_x, y=label_status_place_y,
                                width=label_status_width, height=label_status_height)
        self.progress_download.place(x=progress_download_place_x, y=progress_download_place_y,
                                     width=progress_download_width, height=progress_download_height)
        self.label_percent.place(x=label_percent_place_x, y=label_percent_place_y,
                                 width=label_percent_width, height=label_percent_height)

    def ctl_sft_a_clicked(self, ke):
        # mb.showinfo("提示", ke.keysym + " " + ke.char + " " + str(ke.keycode))
        logger = logging.getLogger()

        if logger.getEffectiveLevel() == logging.INFO:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

    def ctl_sft_y_clicked(self, ke):
        self.configuration.download_mail_number = self.mail_amount_one_page
        self.__notify_configuration()

    def login_clicked(self):
        self.str_addr = self.entry_addr.get()
        self.str_password = self.entry_password.get()

        self.str_server = Utils.get_server_from_email_address(self.str_addr)

        if self.str_addr is None or self.str_addr == '':
            mb.showerror("错误", "请输入邮箱地址！")
        elif self.str_password is None or self.str_password == '':
            mb.showerror("错误", "请输入邮箱密码！")
        elif self.str_server is None or self.str_server == '':
            mb.showerror("错误", "请输入有效邮箱地址！")
        else:
            # mb.showinfo("", '"' + self.str_addr + '"' + ' input.\n Mail server is ' + self.str_server)

            login_message = LoginMSG(self.get_new_msg_number(),
                                     self.str_server,
                                     self.str_addr,
                                     self.str_password,
                                     self.mail_amount_one_page,
                                     recall=self.login_recall)

            if self.worker.put_message(login_message) == CommonMSG.ERR_CODE_QUEUE_FULL:
                mb.showinfo("提示", "系统繁忙，请稍后重试。")
            else:
                self.start_login_progress()

    def donate_clicked(self):
        mb.showinfo("捐赠", "感谢认可，捐赠金额随意！")

    def select_path_clicked(self):
        tmp_download_folder = askdirectory().replace("/", "\\")

        if tmp_download_folder is not None and \
                tmp_download_folder != '' and \
                self.configuration.download_folder != tmp_download_folder:
            self.configuration.download_folder = tmp_download_folder
            self.__notify_configuration()
            self.current_save_folder.set(tmp_download_folder)

    def feedback_clicked_github(self):
        webbrowser.open(self.configuration.feedback_link_github)

    def feedback_clicked_gitee(self):
        webbrowser.open(self.configuration.feedback_link_gitee)

    def about_clicked(self):
        mb.showinfo("关于", self.configuration.app_name + ' ' + self.configuration.app_version)

    def help_clicked(self):
        mb.showinfo("帮助", "电子邮件附件下载器的帮助\n即将呈现！")

    def display_config_clicked(self):
        mb.showinfo("显示设置", "电子邮件附件下载器显示设置\n即将呈现！")

    def download_folder_config_clicked(self):
        self.configuration.download_in_same_folder = self.config_download_in_same_folder.get()
        self.__notify_configuration()

    def time_prefix_folder_clicked(self):
        self.configuration.download_folder_time_prefix = self.config_time_prefix_folder.get()
        self.__notify_configuration()

    def switch_clicked(self):
        mb.showinfo("更换邮箱", "电子邮件附件下载器更换邮箱操作\n即将呈现！")

    def download_selected_clicked(self):
        download_flag = CommonMSG.DOWNLOAD_FLAG_LAST_NUMBER
        selected_items = self.tree_inbox.selection()

        if len(selected_items) > self.configuration.download_mail_number:
            mb.showinfo("提示",
                        "一次最多下载" + str(self.configuration.download_mail_number) + "封邮件的附件，请减少选中邮件数量。")
        else:
            selected_mails_index = []
            current_display_mails_keys = list(self.current_display_mails.keys())

            for selected_item in selected_items:
                selected_item_index_str = selected_item.split('I')[1]
                selected_item_index = int(selected_item_index_str, 16) - 1
                selected_mail_index = current_display_mails_keys[selected_item_index]
                selected_mails_index.append(selected_mail_index)

            download_message = DownloadMSG(self.get_new_msg_number(),
                                           download_flag,
                                           session_index=-1,
                                           download_mail_number=self.configuration.download_mail_number,
                                           download_since_time=None,
                                           download_till_time=None,
                                           download_mails_index=selected_mails_index,
                                           recall=None)

            if self.worker.put_message(download_message) == CommonMSG.ERR_CODE_QUEUE_FULL:
                mb.showinfo("提示", "系统繁忙，请稍后重试。")

    def download_clicked(self):
        # mb.showinfo("下载附件", "电子邮件附件下载器下载附件操作\n即将呈现！")
        download_flag = CommonMSG.DOWNLOAD_FLAG_LAST_NUMBER
        download_message = DownloadMSG(self.get_new_msg_number(),
                                       download_flag,
                                       session_index=-1,
                                       download_mail_number=self.configuration.download_mail_number,
                                       download_since_time=None,
                                       download_till_time=None,
                                       download_mails_index=self.current_display_mails.keys(),
                                       recall=None)

        if self.worker.put_message(download_message) == CommonMSG.ERR_CODE_QUEUE_FULL:
            mb.showinfo("提示", "系统繁忙，请稍后重试。")

    def refresh_clicked(self):
        mb.showinfo("更新邮件", "电子邮件附件下载器更新邮件操作\n即将呈现！")

    def resize_occurred(self, event):
        self.__layout_inbox()

    def update_status_recall(self, status=None, percent=None):
        self.progress_download['value'] = percent
        self.label_percent['text'] = "{}%".format(int(percent))

        if status is not None:
            self.label_status['text'] = "{}".format(status)

    def login_recall(self, handle_result, mails_index, mails_eml):

        self.stop_login_progress()

        if handle_result == CommonMSG.ERR_CODE_SUCCESSFUL:
            self.clean_login_control()
            self.half_screen()
            self.display_inbox_control()
            self.configuration.set_status_recall(self.update_status_recall)
            self.__notify_configuration()
            self.mails_index = mails_index
            self.received_mails = mails_eml

            # Reorder mails by received time.
            # It is a bug in QQ mail service, the mail index order does not whole match the received time order.
            # TODO: mail index calculation need to be optimized.
            temp_current_display_mails = {}
            for mail_item in self.received_mails.items():
                if mail_item[1].receive_time is not None:
                    temp_time_stamp_array = time.strptime(mail_item[1].receive_time, '%Y/%m/%d %H:%M:%S')
                    temp_time_stamp = time.mktime(temp_time_stamp_array)
                    temp_current_display_mails[temp_time_stamp] = mail_item[1]
                else:
                    temp_mail_index_bytes = mail_item[0]
                    temp_mail_index_int = int.from_bytes(temp_mail_index_bytes, 'big')
                    first_mail_index_int = int.from_bytes(list(self.received_mails.keys())[0], 'big')

                    if temp_mail_index_int == first_mail_index_int:
                        temp_time_stamp = int(time.time())
                        mail_item[1].receive_time = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(temp_time_stamp))
                        temp_current_display_mails[temp_time_stamp] = mail_item[1]
                    elif temp_mail_index_int > 0:
                        next_elder_mail_index_int = temp_mail_index_int + 1
                        next_elder_mail_index_int_bytes = int.to_bytes(next_elder_mail_index_int,
                                                                       len(temp_mail_index_bytes),
                                                                       'big')
                        temp_receive_time = self.received_mails[next_elder_mail_index_int_bytes].receive_time
                        temp_time_stamp_array = time.strptime(temp_receive_time, '%Y/%m/%d %H:%M:%S')
                        temp_time_stamp = time.mktime(temp_time_stamp_array) - 1
                        mail_item[1].receive_time = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(temp_time_stamp))
                        temp_current_display_mails[temp_time_stamp] = mail_item[1]

            sorted_keys = sorted(temp_current_display_mails.keys(), reverse=True)

            for temp_key in sorted_keys:
                temp_index = temp_current_display_mails[temp_key].mail_index
                self.current_display_mails[temp_index] = temp_current_display_mails[temp_key]

            self.__display_inbox()
            self.window.bind("<Configure>", self.resize_occurred)
            self.window.bind(sequence="<Control-A>", func=self.ctl_sft_a_clicked)
            self.window.bind(sequence="<Control-Y>", func=self.ctl_sft_y_clicked)
        elif handle_result == CommonMSG.ERR_CODE_WRONG_SERVER_NAME:
            mb.showerror("错误的邮箱域名", "请输入正确的邮箱地址。")
        elif handle_result == CommonMSG.ERR_CODE_WRONG_USER_NAME_OR_PASSWORD:
            if self.str_server in self.configuration.auth_code_links:
                link = self.configuration.auth_code_links[self.str_server]
                result = mb.askquestion("请使用正确邮箱地址和授权码登录", "打开授权码获取方法帮助网页？\n" + link)
                if result == "yes":
                    webbrowser.open(link)
            else:
                mb.showerror("请使用正确邮箱地址和授权码登录", "请访问邮箱官网查找授权码获取方法")
        elif handle_result == CommonMSG.ERR_CODE_CONNECTION_TIMEOUT:
            mb.showerror("邮件服务器连接超时", "请检查计算机网络连接是否正常。")
        elif handle_result == CommonMSG.ERR_CODE_UNKNOWN_ERROR:
            mb.showerror("错误", "系统未知错误。")

    def load_mail_recall(self, mails):
        logging.debug(self.__class__.__name__ + '.load_mail_recall calling')
        self.current_display_mails = mails
        self.__display_inbox()

    def __display_inbox(self):
        logging.debug(self.__class__.__name__ + '.__display_inbox calling')

        loop = 0

        for mail_item in self.current_display_mails.items():
            # logging.debug(mail_item)
            mail_eml = mail_item[1]
            tmp_subject = UIUtils.correct_subject(mail_eml.subject)

            self.tree_inbox.insert(
                '',
                loop,
                values=('', mail_eml.sender_name, mail_eml.receiver_addr, mail_eml.receive_time, tmp_subject))
            loop = loop + 1

    def __notify_configuration(self):
        # Update configuration
        update_config_message = UpdateConfigMSG(self.get_new_msg_number(), self.configuration)

        if self.worker.put_message(update_config_message) == CommonMSG.ERR_CODE_QUEUE_FULL:
            mb.showinfo("提示", "系统繁忙，请稍后重试。")

    def __load_mail(self, start_message_index, load_mail_amount, ascending=False):
        load_mail_message = LoadMailMSG(
            self.get_new_msg_number(),
            start_message_index,
            load_mail_amount,
            ascending=ascending,
            recall=self.load_mail_recall)

        if self.worker.put_message(load_mail_message) == CommonMSG.ERR_CODE_QUEUE_FULL:
            mb.showinfo("提示", "系统繁忙，请稍后重试。")

    def start_login_progress(self):
        self.disable_input()

        label_addr_place_y = self.window.winfo_height() / 2 - \
                             (self.label_addr_height + self.login_vertical_spacing + self.label_password_height +
                              self.login_vertical_spacing + self.button_login_height) / 2
        label_password_place_y = label_addr_place_y + self.label_addr_height + self.login_vertical_spacing

        button_login_place_x = self.window.winfo_width() / 2 - \
                               (self.button_login_width + self.label_entry_spacing + self.button_quit_width) / 2
        button_login_place_y = label_password_place_y + self.label_password_height + self.label_entry_spacing

        self.button_login.place_forget()
        self.progress_login.place(x=button_login_place_x, y=button_login_place_y,
                                  width=self.button_login_width, height=self.button_login_height)

        self.progress_login.start(10)

    def stop_login_progress(self):
        self.enable_input()
        label_addr_place_y = self.window.winfo_height() / 2 - \
                             (self.label_addr_height + self.login_vertical_spacing + self.label_password_height +
                              self.login_vertical_spacing + self.button_login_height) / 2
        label_password_place_y = label_addr_place_y + self.label_addr_height + self.login_vertical_spacing

        button_login_place_x = self.window.winfo_width() / 2 - \
                               (self.button_login_width + self.label_entry_spacing + self.button_quit_width) / 2
        button_login_place_y = label_password_place_y + self.label_password_height + self.label_entry_spacing

        self.progress_login.place_forget()
        self.button_login.place(x=button_login_place_x, y=button_login_place_y,
                                  width=self.button_login_width, height=self.button_login_height)

    def disable_input(self):
        self.entry_addr.config(state='disabled')
        self.entry_password.config(state='disabled')
        self.button_login.config(state='disabled')

    def enable_input(self):
        self.entry_addr.config(state='normal')
        self.entry_password.config(state='normal')
        self.button_login.config(state='normal')

    def clean_login_control(self):
        self.label_addr.place_forget()
        self.label_password.place_forget()
        self.entry_addr.place_forget()
        self.entry_password.place_forget()
        self.button_login.place_forget()
        self.button_quit.place_forget()

    def clean_inbox_control(self):
        empty_menu = tk.Menu(self.window)
        self.window.config(menu=empty_menu)

    def display_inbox_control(self):
        self.window.minsize(int(self.screen_width / 3), int(self.screen_height / 3))
        self.window.config(menu=self.menuBar)
        self.__layout_inbox()
        self.display_status = GUI.DISPLAY_INBOX
