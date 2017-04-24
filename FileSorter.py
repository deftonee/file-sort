
import locale
import json
import os
import threading

from gettext import gettext as _
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Combobox, Notebook, Progressbar

from main import sort, validate, FORMAT_HELP, SortMethodEnum

# locale_var = 'ru_RU'
# locale.setlocale(locale.LC_TIME, locale_var)

LABEL_WIDTH = 20
FIELD_WIDTH = 20
BUTTON_WIDTH = 5
PROGRESSBAR_LENGTH = 200
SETTINGS_FILENAME = 'settings.json'
SRC_SETTINGS_KEY = 'src'
DST_SETTINGS_KEY = 'dst'
FMT_SETTINGS_KEY = 'fmt'

format_help_window = None
result_window = None

# load settings, savings
settings_path = os.path.join(os.path.dirname(__file__), SETTINGS_FILENAME)
try:
    settings_file = open(settings_path, 'r')
    settings = json.load(settings_file)
    settings_file.close()
except FileNotFoundError:
    settings = {}


def save_settings():
    settings_file = open(settings_path, 'w')
    json.dump(settings, settings_file)
    settings_file.close()


def open_folder_dialog(entry, title):
    def _internal(event):
        path = filedialog.askdirectory(title=title)

        entry.delete(0, END)
        entry.insert(0, path)
    return _internal


def show_format_help(event):

    def _close_format_help_window():
        global format_help_window
        format_help_window.destroy()
        del format_help_window
        format_help_window = None

    global format_help_window

    if format_help_window is not None:
        return

    format_help_window = Toplevel()
    format_help_window.title(_('Format help'))
    format_help_window.wm_geometry("")
    format_help_window.wm_resizable(width=False, height=False)
    format_help_window.protocol("WM_DELETE_WINDOW", _close_format_help_window)

    msg = Message(
        format_help_window,
        text=FORMAT_HELP)
    msg.pack()

    button = Button(format_help_window,
                    text=_('Understood'), command=_close_format_help_window)
    button.pack()


def sort_button_pressed(event):

    def _close_result_window():
        global result_window
        result_window.destroy()
        del result_window
        result_window = None

    def _sorting_thread_body():
        for is_done, file_name in sort(
                src_path, dst_path, fmt, method_var.get()):
            try:
                result_pgb.step(1)
                if is_done:
                    done_lst.insert(END, '%s\n' % file_name)
                else:
                    failed_lst.insert(END, '%s\n' % file_name)
            except TclError:
                messagebox.showinfo(
                    title=_('Information'),
                    message=_('The sorting process is interrupted'),
                )
                return

        result_pgb.config(value=total)
        messagebox.showinfo(
            title=_('Success'),
            message=_('Sort process completed'),
        )

    global result_window

    if result_window is not None:
        return

    src_path = src_fld.get()
    dst_path = dst_fld.get()
    fmt = fmt_fld.get()
    is_valid, msg = validate(src_path, dst_path, fmt, method_var.get())
    if not is_valid:
        messagebox.showerror(
            title=_('Validation error'),
            message=msg,
        )
    else:

        total = 0
        for x in os.walk(src_path):
            total += len(x[2])

        result_window = Toplevel()
        result_window.title(_('Sorting process'))
        result_window.wm_geometry("")
        result_window.protocol("WM_DELETE_WINDOW", _close_result_window)

        result_pgb = Progressbar(
            result_window, orient="horizontal",
            length=PROGRESSBAR_LENGTH, mode="determinate")
        result_pgb.config(maximum=total)
        result_pgb.config(value=0)

        tabs = Notebook(result_window)
        done_frame = Frame(tabs)
        fails_frame = Frame(tabs)
        tabs.add(done_frame, text=_('Done'))
        tabs.add(fails_frame, text=_('Fails'))
        done_lst = ScrolledText(done_frame)
        failed_lst = ScrolledText(fails_frame)

        result_pgb.pack(fill=X)
        tabs.pack(fill=BOTH)
        done_lst.pack(fill=BOTH)
        failed_lst.pack(fill=BOTH)

        # start sorting
        sorting_thread = threading.Thread(target=_sorting_thread_body)
        sorting_thread.start()

        # update settings
        if src_path not in settings[SRC_SETTINGS_KEY]:
            settings[SRC_SETTINGS_KEY].append(src_path)
            src_fld.config(values=get_src_choices())

        if dst_path not in settings[DST_SETTINGS_KEY]:
            settings[DST_SETTINGS_KEY].append(dst_path)
            dst_fld.config(values=get_dst_choices())

        if fmt not in settings[FMT_SETTINGS_KEY]:
            settings[FMT_SETTINGS_KEY].append(fmt)
            fmt_fld.config(values=get_fmt_choices())

        save_settings()


def get_src_choices():
    return settings.setdefault(SRC_SETTINGS_KEY, [])


def get_dst_choices():
    return settings.setdefault(DST_SETTINGS_KEY, [])


def get_fmt_choices():
    return settings.setdefault(FMT_SETTINGS_KEY, [])


def close_main_window():
    save_settings()
    sys.exit()


main_window = Tk()
main_window.title(_('File Sorter'))
main_window.wm_geometry("")
main_window.wm_resizable(width=False, height=False)
main_window.protocol("WM_DELETE_WINDOW", close_main_window)


src_lbl = Label(main_window, text=_('Source folder'),
                width=LABEL_WIDTH, anchor=E, justify=RIGHT)
src_fld = Combobox(main_window, values=get_src_choices(), width=FIELD_WIDTH)
src_btn = Button(main_window, text=_('View'), width=BUTTON_WIDTH)

dst_lbl = Label(main_window, text=_('Destination folder'),
                width=LABEL_WIDTH, anchor=E, justify=RIGHT)
dst_fld = Combobox(main_window, values=get_dst_choices(), width=FIELD_WIDTH)
dst_btn = Button(main_window, text=_('View'), width=BUTTON_WIDTH)

fmt_lbl = Label(main_window, text=_('Folder structure format'),
                width=LABEL_WIDTH, anchor=E, justify=RIGHT)
fmt_fld = Combobox(main_window, values=get_fmt_choices(), width=FIELD_WIDTH)
fmt_btn = Button(main_window, text=_('?'), width=BUTTON_WIDTH)

method_lbl = Label(main_window, text=_('Sorting method'),
                   width=LABEL_WIDTH, anchor=E, justify=RIGHT)
method_var = StringVar(main_window, SortMethodEnum.values[SortMethodEnum.COPY])
method_fld = OptionMenu(main_window, method_var,
                        *SortMethodEnum.values.values())

# TODO поле выбора языка

main_btn = Button(main_window, text=_('Sort'))

src_lbl.grid(row=0, column=0)
src_fld.grid(row=0, column=1, sticky=W)
src_btn.grid(row=0, column=2)

dst_lbl.grid(row=1, column=0)
dst_fld.grid(row=1, column=1, sticky=W)
dst_btn.grid(row=1, column=2)

fmt_lbl.grid(row=2, column=0)
fmt_fld.grid(row=2, column=1, sticky=W)
fmt_btn.grid(row=2, column=2)

method_lbl.grid(row=3, column=0)
method_fld.grid(row=3, column=1)

main_btn.grid(row=4, column=1)

src_btn.bind(
    '<Button-1>',
    open_folder_dialog(src_fld, _('Select source folder of your files'))
)
dst_btn.bind(
    '<Button-1>',
    open_folder_dialog(dst_fld, _('Select destination folder of your files'))
)
fmt_btn.bind(
    '<Button-1>',
    show_format_help
)
main_btn.bind(
    '<Button-1>',
    sort_button_pressed
)

mainloop()

