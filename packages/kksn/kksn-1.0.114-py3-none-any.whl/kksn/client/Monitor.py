# -*- coding: utf-8 -*-
import os
import threading
import time
from tkinter import *
from tkinter import messagebox, filedialog
from .utils import get_random_string, check_type
import shutil
import types
from .auth import get_license_txt, auth_license, get_hard_info


class Monitor:
    def __init__(self, target=None, pwd=None, title='kksn', icon_path=None, *args, **kwargs):
        if target is None:
            raise ValueError('target can not be None')
        if pwd is None:
            raise ValueError('pwd can not be None')

        if not isinstance(target, (types.FunctionType, types.MethodType)):
            raise TypeError('target must be function or method')

        self.target = target
        self.pwd = pwd
        self.check_thread = None
        self.event = threading.Event()

        self.disk_number, self.cpu_number, self.bios_number = get_hard_info()

        self.title = title
        self.icon_path = icon_path
        self.root = None
        self.serial_code = get_license_txt(self.disk_number, self.cpu_number, self.bios_number)

        self.copy_message = kwargs.get('copy_message', '序列号已复制，请将序列号发送给管理员')
        self.powered_by = kwargs.get('powered_by', '微信公众号：Python卡皮巴拉')
        self.delay = kwargs.get('delay', 10 * 60)
        self.ntp = kwargs.get('ntp', None)

        self.key_error_message = kwargs.get('key_error_message', '授权文件错误')
        self.key_expired_message = kwargs.get('key_expired_message', '授权文件过期')
        self.ntp_error_message = kwargs.get('ntp_error_message', '无法离线运行，请连接网络')

        check_type('title', title, str)
        check_type('icon_path', icon_path, str)
        check_type('copy_message', self.copy_message, str)
        check_type('powered_by', self.powered_by, str)
        check_type('delay', self.delay, int)
        check_type('ntp', self.ntp, str)

        check_type('key_error_message', self.key_error_message, str)
        check_type('key_expired_message', self.key_expired_message, str)
        check_type('ntp_error_message', self.ntp_error_message, str)

        key_path = self._get_key_path()

        is_pass = False
        message = None
        if key_path is not None:
            is_pass, message = self._auth_license(key_path)

        if not is_pass:
            self.setup(message)
        else:
            self.start()

    def _get_key_path(self):
        file_list = os.listdir(os.getcwd())

        key_files = [file for file in file_list if file.endswith('.key')]
        key_path = None

        if len(key_files) == 1:
            key_path = os.path.join(os.getcwd(), key_files[0])

        return key_path

    def _auth_license(self, key_path):
        is_pass, message = auth_license(
            key_path,
            self.pwd,
            self.disk_number,
            self.cpu_number,
            self.bios_number,
            self.ntp,
            self.key_error_message,
            self.key_expired_message,
            self.ntp_error_message
        )
        return is_pass, message

    def _center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2 - 140

        window.geometry(f'{width}x{height}+{x}+{y}')

    def copy_to_clipboard(self):
        # 复制序列号到剪贴板
        self.root.clipboard_clear()  # 清空剪贴板
        self.root.clipboard_append(self.serial_code)  # 添加序列号到剪贴板
        self.root.update()  # 更新剪贴板
        messagebox.showinfo('提示', self.copy_message)

    def import_file(self):
        # 打开文件选择对话框，选择 .key 文件
        file_path = filedialog.askopenfilename(
            title='选择 .key 文件',
            filetypes=[('Key Files', '*.key')]
        )
        if file_path:
            is_pass, message = self._auth_license(file_path)

            if is_pass:
                file_list = os.listdir(os.getcwd())
                key_files = [file for file in file_list if file.endswith('.key')]

                file_name = file_path.replace('\\', '/').split('/')[-1][:-4]
                file_name = f'{file_name}_{get_random_string(4)}.key'
                current_key_path = os.path.join(os.getcwd(), file_name)
                shutil.copy(file_path, current_key_path)

                for file in key_files:
                    os.remove(os.path.join(os.getcwd(), file))

                self.root.destroy()
                self.start()
            else:
                messagebox.showerror('抱歉', message)

    def setup(self, message=None):
        self.root = Tk(screenName=self.title)
        self.root.title(self.title)
        self.root.withdraw()

        if self.icon_path is not None:
            if not os.path.exists(self.icon_path):
                raise Exception('no ico file')
            if not isinstance(self.icon_path, str) or not self.icon_path.endswith('.ico'):
                raise Exception('not an ico file type')

            self.root.iconbitmap(self.icon_path)

        self._center_window(self.root, 820, 120)
        self.root.resizable(False, False)
        self.root.configure(bg='white')

        self.root.grid_columnconfigure(0, weight=1)  # 列 0 权重为 1

        # 创建一个带边框的 Frame 容器
        border_frame = Frame(self.root, bd=2, bg='white', relief='groove')
        border_frame.grid(row=0, column=0, padx=20, pady=20, sticky='nsew')

        # 在 border_frame 中添加序列号标签
        serial_label = Label(border_frame, text=f'序列号：{self.serial_code}', bg='white', font=('Arial', 10))
        serial_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        # 在 border_frame 中添加复制按钮
        copy_button = Button(border_frame, text='复制', command=self.copy_to_clipboard, font=('Arial', 9))
        copy_button.grid(row=0, column=1, padx=10, pady=10, sticky='e')

        import_button = Button(border_frame, text='导入授权文件', command=self.import_file, font=('Arial', 9))
        import_button.grid(row=0, column=2, padx=10, pady=10, sticky='e')

        # 在右下角添加 'Powered by' 标签
        powered_by_label = Label(self.root, text=self.powered_by, bg='white', font=('Arial', 8))
        powered_by_label.grid(row=1, column=0, padx=10, pady=0, sticky='se')

        if message is not None:
            messagebox.showerror('抱歉', message)

        self.root.update_idletasks()
        self.root.deiconify()
        mainloop()

    def check_handle(self):
        key_path = self._get_key_path()

        if key_path is not None:
            last_timestamp = int(time.time())
            while not self.event.is_set():
                time.sleep(1)

                now_timestamp = int(time.time())

                if now_timestamp - last_timestamp >= self.delay:
                    print('进来判断了')
                    is_pass, message = self._auth_license(key_path)

                    if not is_pass:
                        break

                    last_timestamp = now_timestamp

        os._exit(0)

    def start(self):
        if self.target is not None:
            if self.check_thread is None:
                self.check_thread = threading.Thread(target=self.check_handle, args=())
                self.check_thread.start()

            self.target()
            self.event.set()
