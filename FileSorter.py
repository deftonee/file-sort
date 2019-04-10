import json
import os
import threading

from gettext import gettext as _
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Combobox, Notebook, Progressbar

from enums import (
    ConflictResolveMethodEnum, FolderCleanupOptionsEnum, SortMethodEnum)
from main import Sorter
from tag_classes import TAG_HELP


LABEL_WIDTH = 25
FIELD_WIDTH = 25
BUTTON_WIDTH = 5
PROGRESSBAR_LENGTH = 200
SETTINGS_FILENAME = 'settings.json'
SRC_SETTINGS_KEY = 'src'
DST_SETTINGS_KEY = 'dst'
FMT_SETTINGS_KEY = 'fmt'


class UI:
    def __init__(self):

        # load settings, savings
        self.settings_path = os.path.join(os.path.dirname(__file__),
                                          SETTINGS_FILENAME)
        try:
            settings_file = open(self.settings_path, 'r')
            self.settings = json.load(settings_file)
            settings_file.close()
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self.settings = {}

        main_window = Tk()
        main_window.title(_('File Sorter'))
        main_window.wm_geometry("")
        main_window.wm_resizable(width=False, height=False)
        main_window.protocol("WM_DELETE_WINDOW", self._close_main_window)

        src_lbl = Label(main_window, text=_('Source folder'),
                        width=LABEL_WIDTH, anchor=E, justify=RIGHT)
        self.src_fld = Combobox(main_window, values=self._get_src_choices(),
                                width=FIELD_WIDTH)
        self.src_btn = Button(main_window, text=_('View'), width=BUTTON_WIDTH)

        dst_lbl = Label(main_window, text=_('Destination folder'),
                        width=LABEL_WIDTH, anchor=E, justify=RIGHT)
        self.dst_fld = Combobox(main_window, values=self._get_dst_choices(),
                                width=FIELD_WIDTH)
        self.dst_btn = Button(main_window, text=_('View'), width=BUTTON_WIDTH)

        fmt_lbl = Label(main_window, text=_('Folder structure format'),
                        width=LABEL_WIDTH, anchor=E, justify=RIGHT)
        self.fmt_fld = Combobox(main_window, values=self._get_fmt_choices(),
                                width=FIELD_WIDTH)
        self.fmt_btn = Button(main_window, text=_('?'), width=BUTTON_WIDTH)

        method_lbl = Label(main_window, text=_('Sorting method'),
                           width=LABEL_WIDTH, anchor=E, justify=RIGHT)
        self.method_var = StringVar(
            main_window,
            SortMethodEnum.to_text(SortMethodEnum.get_default()))
        self.method_fld = OptionMenu(main_window,
                                     self.method_var,
                                     *SortMethodEnum.values().values())

        conflict_lbl = Label(main_window, text=_('Conflict resolving method'),
                             width=LABEL_WIDTH, anchor=E, justify=RIGHT)
        self.conflict_var = StringVar(
            main_window,
            ConflictResolveMethodEnum.to_text(
                ConflictResolveMethodEnum.get_default()))
        self.conflict_fld = OptionMenu(
            main_window,
            self.conflict_var,
            *ConflictResolveMethodEnum.values().values())

        cleanup_lbl = Label(main_window,
                            text=_('Remove empty folders from source'),
                            width=LABEL_WIDTH, anchor=E, justify=RIGHT)
        self.cleanup_var = IntVar(main_window,
                                  FolderCleanupOptionsEnum.get_default().value)
        self.cleanup_fld = Checkbutton(
            main_window, variable=self.cleanup_var,
            offvalue=FolderCleanupOptionsEnum.LEAVE.value,
            onvalue=FolderCleanupOptionsEnum.REMOVE.value)

        self.main_btn = Button(main_window, text=_('Sort'))

        src_lbl.grid(row=0, column=0)
        self.src_fld.grid(row=0, column=1, sticky=E + W)
        self.src_btn.grid(row=0, column=2)

        dst_lbl.grid(row=1, column=0)
        self.dst_fld.grid(row=1, column=1, sticky=E + W)
        self.dst_btn.grid(row=1, column=2)

        fmt_lbl.grid(row=2, column=0)
        self.fmt_fld.grid(row=2, column=1, sticky=E + W)
        self.fmt_btn.grid(row=2, column=2)

        method_lbl.grid(row=3, column=0)
        self.method_fld.grid(row=3, column=1, sticky=E + W)

        conflict_lbl.grid(row=4, column=0)
        self.conflict_fld.grid(row=4, column=1, sticky=E + W)

        cleanup_lbl.grid(row=5, column=0)
        self.cleanup_fld.grid(row=5, column=1, sticky=E + W)

        self.main_btn.grid(row=6, column=1)

        self.src_btn.bind(
            '<Button-1>',
            self._open_folder_dialog(
                self.src_fld, _('Select source folder of your files'))
        )
        self.dst_btn.bind(
            '<Button-1>',
            self._open_folder_dialog(
                self.dst_fld, _('Select destination folder of your files'))
        )
        self.fmt_btn.bind(
            '<Button-1>',
            self._show_format_help
        )
        self.main_btn.bind(
            '<Button-1>',
            self._sort_button_pressed
        )

        # links to additional windows
        self.format_help_window = None
        self.result_window = None

    def run(self):
        mainloop()

    def _open_folder_dialog(self, entry, title):
        def _internal(event):
            path = filedialog.askdirectory(title=title)
            entry.delete(0, END)
            entry.insert(0, path)

        return _internal

    def _close_format_help_window(self):
        self.format_help_window.destroy()
        self.format_help_window = None

    def _show_format_help(self, event):

        if self.format_help_window is not None:
            return

        self.format_help_window = Toplevel()
        self.format_help_window.title(_('Format help'))
        self.format_help_window.wm_geometry("")
        self.format_help_window.wm_resizable(width=False, height=False)
        self.format_help_window.protocol("WM_DELETE_WINDOW",
                                         self._close_format_help_window)

        msg = Message(
            self.format_help_window,
            text=TAG_HELP)
        msg.pack()

        button = Button(self.format_help_window,
                        text=_('Understood'),
                        command=self._close_format_help_window)
        button.pack()

    def _close_result_window(self):
        self.result_window.destroy()
        self.result_window = None

    def _sort_button_pressed(self, event):

        sm = SortMethodEnum.to_value(self.method_var.get())
        crm = ConflictResolveMethodEnum.to_value(self.conflict_var.get())
        co = FolderCleanupOptionsEnum(self.cleanup_var.get())

        def _sorting_thread_body(sorter):
            for is_done, file_name in sorter.sort():
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

        if self.result_window is not None:
            return

        src_path = self.src_fld.get()
        dst_path = self.dst_fld.get()
        fmt = self.fmt_fld.get()
        sorter = Sorter(src_path=src_path, dst_path=dst_path, path_format=fmt,
                        method=sm, conflict_resolve_method=crm,
                        cleanup_option=co)
        is_valid, msg = sorter.validate_paths()
        if not is_valid:
            messagebox.showerror(
                title=_('Validation error'),
                message=msg,
            )
        else:
            # FIXME in some cases counts in wrong way
            total = 0
            for x in os.walk(src_path):
                total += len(x[2])

            self.result_window = Toplevel()
            self.result_window.title(_('Sorting process'))
            self.result_window.wm_geometry("")
            self.result_window.protocol("WM_DELETE_WINDOW",
                                        self._close_result_window)

            result_pgb = Progressbar(
                self.result_window, orient="horizontal",
                length=PROGRESSBAR_LENGTH, mode="determinate")
            result_pgb.config(maximum=total)
            result_pgb.config(value=0)

            tabs = Notebook(self.result_window)
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
            sorting_thread = threading.Thread(
                target=lambda: _sorting_thread_body(sorter))
            sorting_thread.start()

            # update settings
            if src_path not in self.settings[SRC_SETTINGS_KEY]:
                self.settings[SRC_SETTINGS_KEY].insert(0, src_path)
                self.src_fld.config(values=self._get_src_choices())

            if dst_path not in self.settings[DST_SETTINGS_KEY]:
                self.settings[DST_SETTINGS_KEY].insert(0, dst_path)
                self.dst_fld.config(values=self._get_dst_choices())

            if fmt not in self.settings[FMT_SETTINGS_KEY]:
                self.settings[FMT_SETTINGS_KEY].insert(0, fmt)
                self.fmt_fld.config(values=self._get_fmt_choices())

            self._save_settings()

    def _save_settings(self):
        settings_file = open(self.settings_path, 'w')
        json.dump(self.settings, settings_file)
        settings_file.close()

    def _get_src_choices(self):
        return self.settings.setdefault(SRC_SETTINGS_KEY, [])

    def _get_dst_choices(self):
        return self.settings.setdefault(DST_SETTINGS_KEY, [])

    def _get_fmt_choices(self):
        return self.settings.setdefault(FMT_SETTINGS_KEY, [])

    def _close_main_window(self):
        self._save_settings()
        sys.exit()


ui = UI()
ui.run()
