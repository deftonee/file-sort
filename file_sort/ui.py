import locale
import os
import threading
from gettext import gettext as _
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText  # type: ignore
from tkinter.ttk import Combobox, Notebook, Progressbar

from file_sort.utils.enums import (
    ConflictResolveMethodEnum,
    FolderCleanupOptionsEnum,
    LangEnum,
    SortMethodEnum
)
from file_sort.utils.helpers import (
    load_var_from_enum_to_settings,
    save_var_from_enum_to_settings,
    set_locale
)
from file_sort.utils.main import Sorter
from file_sort.utils.settings import SettingEnum, Settings
from file_sort.utils.tag_classes import get_tag_help

LABEL_WIDTH = 25
FIELD_WIDTH = 25
BUTTON_WIDTH = 5
PROGRESSBAR_LENGTH = 200


settings = Settings()

# set language
lang = settings.get(SettingEnum.LNG)
if lang:
    lang = LangEnum(lang)
set_locale(lang)


class MyWindow:
    name: str = ''

    def launch(self):
        if self.is_launched:
            return
        self._window = Toplevel(self.master)
        self._window.title(self.name)
        self._window.wm_geometry("")
        self._window.protocol("WM_DELETE_WINDOW", self._close_handler)
        self._after_launch()

    @property
    def is_launched(self) -> bool:
        return bool(self._window)

    def close(self):
        self._close_handler()

    def __init__(self, master):
        self._window = None
        self.master = master

    def _after_launch(self):
        pass

    def _close_handler(self):
        if self._window:
            self._window.destroy()
            self._window = None


class FormatHelpWindow(MyWindow):
    name = _('Path format help')

    def _after_launch(self):
        msg = Message(self._window, text=get_tag_help())
        msg.pack()
        button = Button(self._window, text=_('Understood'), command=self._close_handler)
        button.pack()


class ResultWindow(MyWindow):
    name = _('Sorting process')

    def __init__(self, master):
        super().__init__(master)
        self.total = 0
        self.result_pgb = None
        self.done_lst = None
        self.failed_lst = None

    def _after_launch(self):
        self.result_pgb = Progressbar(
            self._window, orient="horizontal",
            length=PROGRESSBAR_LENGTH, mode="determinate")
        self.result_pgb.config(maximum=self.total)
        self.result_pgb.config(value=0)

        tabs = Notebook(self._window)
        done_frame = Frame(tabs)
        fails_frame = Frame(tabs)
        tabs.add(done_frame, text=_('Done'))
        tabs.add(fails_frame, text=_('Fails'))
        self.done_lst = ScrolledText(done_frame)
        self.failed_lst = ScrolledText(fails_frame)

        self.result_pgb.pack(fill=X)
        tabs.pack(fill=BOTH)
        self.done_lst.pack(fill=BOTH)
        self.failed_lst.pack(fill=BOTH)


class MyUI:
    def __init__(self):
        self.main_window = Tk()
        self.main_window.wm_geometry("")
        self.main_window.wm_resizable(width=False, height=False)
        self.main_window.protocol("WM_DELETE_WINDOW", self._close_main_window)
        self._create_variables()
        self._assign_a_value_to_variables()
        self._load_settings()
        self._initialize()

    def run(self):
        mainloop()

    def _initialize(self):
        for cmp in tuple(self.main_window.children.values()):
            cmp.destroy()

        self._create_widgets()

        # additional windows
        self.format_help_window = FormatHelpWindow(self.main_window)
        self.result_window = ResultWindow(self.main_window)

        self._place_widgets()
        self._bind_handlers()
        self._toggle_widgets_visibility()

    def _create_variables(self):
        self.method_var = StringVar(self.main_window)
        self.conflict_var = StringVar(self.main_window)
        self.cleanup_var = IntVar(self.main_window)
        self.lang_var = StringVar(self.main_window)
        self.options_var = IntVar(self.main_window)

    def _create_widgets(self):
        self.main_window.title(_('File Sorter'))

        self.src_lbl = Label(self.main_window, text=_('Source folder'),
                             width=LABEL_WIDTH, anchor=E, justify=RIGHT)
        self.src_fld = Combobox(self.main_window,
                                values=settings.get(SettingEnum.SRC, ()),
                                width=FIELD_WIDTH)
        self.src_btn = Button(self.main_window,
                              text=_('View'), width=BUTTON_WIDTH)

        self.dst_lbl = Label(self.main_window, text=_('Destination folder'),
                             width=LABEL_WIDTH, anchor=E, justify=RIGHT)
        self.dst_fld = Combobox(self.main_window,
                                values=settings.get(SettingEnum.DST, ()),
                                width=FIELD_WIDTH)
        self.dst_btn = Button(self.main_window,
                              text=_('View'), width=BUTTON_WIDTH)

        self.fmt_lbl = Label(self.main_window, text=_('Folder structure format'),
                             width=LABEL_WIDTH, anchor=E, justify=RIGHT)
        self.fmt_fld = Combobox(self.main_window,
                                values=settings.get(SettingEnum.FMT, ()),
                                width=FIELD_WIDTH)
        self.fmt_btn = Button(self.main_window,
                              text=_('?'), width=BUTTON_WIDTH)

        self.options_btn = Button(self.main_window, text=_('Options'))

        self.method_lbl = Label(self.main_window, text=_('Sorting method'),
                                width=LABEL_WIDTH, anchor=E, justify=RIGHT)
        self.method_fld = OptionMenu(self.main_window,
                                     self.method_var,
                                     *SortMethodEnum.values().values())

        self.conflict_lbl = Label(self.main_window,
                                  text=_('Conflict resolving method'),
                                  width=LABEL_WIDTH, anchor=E, justify=RIGHT)
        self.conflict_fld = OptionMenu(
            self.main_window,
            self.conflict_var,
            *ConflictResolveMethodEnum.values().values())

        self.cleanup_lbl = Label(self.main_window,
                                 text=_('Remove empty folders from source'),
                                 width=LABEL_WIDTH, anchor=E, justify=RIGHT)
        self.cleanup_fld = Checkbutton(
            self.main_window, variable=self.cleanup_var,
            offvalue=FolderCleanupOptionsEnum.LEAVE.value,
            onvalue=FolderCleanupOptionsEnum.REMOVE.value)

        self.lang_lbl = Label(self.main_window, text=_('Language'),
                              width=LABEL_WIDTH, anchor=E, justify=RIGHT)
        self.lang_fld = OptionMenu(self.main_window,
                                   self.lang_var,
                                   *LangEnum.values().values())

        self.main_btn = Button(self.main_window, text=_('Sort'))

    def _place_widgets(self):
        self.src_lbl.grid(row=0, column=0)
        self.src_fld.grid(row=0, column=1, sticky=E + W)
        self.src_btn.grid(row=0, column=2)

        self.dst_lbl.grid(row=1, column=0)
        self.dst_fld.grid(row=1, column=1, sticky=E + W)
        self.dst_btn.grid(row=1, column=2)

        self.fmt_lbl.grid(row=2, column=0)
        self.fmt_fld.grid(row=2, column=1, sticky=E + W)
        self.fmt_btn.grid(row=2, column=2)

        self.options_btn.grid(row=3, column=2)

        self.method_lbl.grid(row=4, column=0)
        self.method_fld.grid(row=4, column=1, sticky=E + W)

        self.conflict_lbl.grid(row=5, column=0)
        self.conflict_fld.grid(row=5, column=1, sticky=E + W)

        self.cleanup_lbl.grid(row=6, column=0)
        self.cleanup_fld.grid(row=6, column=1, sticky=E + W)

        self.lang_lbl.grid(row=7, column=0)
        self.lang_fld.grid(row=7, column=1, sticky=E + W)

        self.main_btn.grid(row=8, column=1)

    def _bind_handlers(self):
        self.src_btn.bind(
            '<Button-1>',
            self._open_folder_dialog(self.src_fld, _('Select source folder of your files')),
        )
        self.dst_btn.bind(
            '<Button-1>',
            self._open_folder_dialog(self.dst_fld, _('Select destination folder of your files')),
        )
        self.fmt_btn.bind(
            '<Button-1>',
            self._launch_something,
        )
        self.main_btn.bind(
            '<Button-1>',
            self._sort_button_pressed,
        )
        self.options_btn.bind(
            '<Button-1>',
            self._options_button_pressed,
        )
        self.lang_var.trace("w", self._language_changed)

    def _launch_something(self, event):
        self.format_help_window.launch()

    def _assign_a_value_to_variables(self):
        self.method_var.set(
            SortMethodEnum.to_text(SortMethodEnum.get_default()))

        self.conflict_var.set(
            ConflictResolveMethodEnum.to_text(
                ConflictResolveMethodEnum.get_default()))

        self.cleanup_var.set(FolderCleanupOptionsEnum.get_default().value)

        locale_code, encoding = locale.getlocale()
        try:
            lang = LangEnum(locale_code)
        except ValueError:
            pass
        else:
            self.lang_var.set(LangEnum.to_text(lang))

    def _load_settings(self):
        self.options_var.set(int(settings.get(
            SettingEnum.OPTIONS,
            -1,
        )))

        load_var_from_enum_to_settings(
            SortMethodEnum, SettingEnum.METHOD, self.method_var,
        )
        load_var_from_enum_to_settings(
            ConflictResolveMethodEnum, SettingEnum.CONFLICT, self.conflict_var,
        )

        value = settings.get(SettingEnum.CLEANUP)
        if value:
            self.cleanup_var.set(value)

    def _save_settings(self):
        src_path = self.src_fld.get()
        if src_path:
            settings.set(SettingEnum.SRC, src_path)
        dst_path = self.dst_fld.get()
        if dst_path:
            settings.set(SettingEnum.DST, dst_path)
        fmt = self.fmt_fld.get()
        if fmt:
            settings.set(SettingEnum.FMT, fmt)

        settings.set(SettingEnum.OPTIONS, str(self.options_var.get()))
        save_var_from_enum_to_settings(
            SortMethodEnum, SettingEnum.METHOD, self.method_var,
        )
        save_var_from_enum_to_settings(
            ConflictResolveMethodEnum, SettingEnum.CONFLICT, self.conflict_var,
        )
        settings.set(SettingEnum.CLEANUP, str(self.cleanup_var.get()))

        settings.save()

    def _open_folder_dialog(self, entry, title):
        def _internal(event):
            path = filedialog.askdirectory(title=title)
            entry.delete(0, END)
            entry.insert(0, path)

        return _internal

    def _language_changed(self, *args, **kwargs):

        save_var_from_enum_to_settings(LangEnum, SettingEnum.LNG, self.lang_var)
        self._save_settings()

        # changing language
        language = LangEnum.to_value(self.lang_var.get())
        set_locale(language)

        self._load_settings()

        # rebuilding interface
        self._initialize()

    def _sort_button_pressed(self, event):

        sm = SortMethodEnum.to_value(self.method_var.get())
        crm = ConflictResolveMethodEnum.to_value(self.conflict_var.get())
        co = FolderCleanupOptionsEnum(self.cleanup_var.get())

        def _sorting_thread_body(sorter):
            for is_done, file_name in sorter.sort():
                try:
                    self.result_window.result_pgb.step(1)
                    if is_done:
                        self.result_window.done_lst.insert(END, '%s\n' % file_name)
                    else:
                        self.result_window.failed_lst.insert(END, '%s\n' % file_name)
                except TclError:
                    messagebox.showinfo(
                        title=_('Information'),
                        message=_('The sorting process is interrupted'),
                    )
                    return

            self.result_window.result_pgb.config(value=total)
            messagebox.showinfo(
                title=_('Success'),
                message=_('Sort process completed'),
            )

        if self.result_window.is_launched:
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
            # FIXME in some cases counts incorrectly
            total = 0
            for top, dirs, non_dirs in os.walk(src_path):
                total += len(non_dirs)

            self.result_window.total = total
            self.result_window.launch()
            # start sorting
            sorting_thread = threading.Thread(
                target=lambda: _sorting_thread_body(sorter))
            sorting_thread.start()

        # update settings and widget values
        self._save_settings()
        self.src_fld.config(values=settings.get(SettingEnum.SRC, ()))
        self.dst_fld.config(values=settings.get(SettingEnum.DST, ()))
        self.fmt_fld.config(values=settings.get(SettingEnum.FMT, ()))

    def _options_button_pressed(self, event):
        self.options_var.set(-self.options_var.get())
        self._toggle_widgets_visibility()

    def _toggle_widgets_visibility(self):
        visible = self.options_var.get() > 0
        options_widgets = (
            self.method_lbl, self.method_fld,
            self.conflict_lbl, self.conflict_fld,
            self.cleanup_lbl, self.cleanup_fld,
            self.lang_lbl, self.lang_fld,
        )
        for widget in options_widgets:
            if visible:
                widget.grid()
            else:
                widget.grid_remove()

    def _close_main_window(self):
        self._save_settings()
        self.result_window.close()
        self.format_help_window.close()
        self.main_window.destroy()
        sys.exit()


if __name__ == '__main__':
    ui = MyUI()
    ui.run()
