# coding: utf-8

import locale

# import tkFileDialog
from gettext import gettext as _
from Tkinter import *
import tkFileDialog
import tkMessageBox
from ttk import *
from main import sort, validate

# locale_var = 'ru_RU'
# locale.setlocale(locale.LC_TIME, locale_var)


def open_dialog(entry, title):
    def _internal(event):
        path = tkFileDialog.askdirectory(title=title)

        entry.delete(0, END)
        entry.insert(0, path)
    return _internal


def sort_button_pressed(event):

    src_path = src_fld.get()
    dst_path = dst_fld.get()
    fmt = fmt_fld.get()
    is_valid, msg = validate(src_path, dst_path, fmt)
    if not is_valid:
        tkMessageBox.showerror(
            title=_(u'Validation error'),
            message=msg,
        )
    else:
        sort(src_path, dst_path, fmt)


root = Tk()
root.title(_(u'File Sorter'))
root.geometry(u'500x150')

src_lbl = Label(root, text=_(u'Source folder'))
src_fld = Entry(root)
src_btn = Button(root, text=_(u'View'))


dst_lbl = Label(root, text=_(u'Destination folder'))
dst_fld = Entry(root)
dst_btn = Button(root, text=_(u'View'))


fmt_lbl = Label(root, text=_(u'Destination folder structure format'))
fmt_fld = Combobox(
    root,
    # TODO выводить сохранённые старые варики
    values=('3dfgdfsgdsg', 'fdsddsga', 'dsgads')
)
fmt_btn = Button(root, text=_(u'?'))

# TODO поле выбора языка

main_btn = Button(root, text=_(u'Make me a Sandwich'))

src_lbl.grid(row=0, column=0, columnspan=1)
src_fld.grid(row=0, column=1, columnspan=2)
src_btn.grid(row=0, column=3, columnspan=1)

dst_lbl.grid(row=1, column=0, columnspan=1)
dst_fld.grid(row=1, column=1, columnspan=2)
dst_btn.grid(row=1, column=3, columnspan=1)

fmt_lbl.grid(row=2, column=0, columnspan=2)
fmt_fld.grid(row=2, column=2, columnspan=1)
fmt_btn.grid(row=2, column=3, columnspan=1)

main_btn.grid(row=3, column=0, columnspan=1)

src_btn.bind(
    '<Button-1>',
    open_dialog(src_fld, _(u'Select source folder of your files'))
)
dst_btn.bind(
    '<Button-1>',
    open_dialog(dst_fld, _(u'Select destination folder of your files'))
)
main_btn.bind(
    '<Button-1>',
    sort_button_pressed
)

mainloop()

