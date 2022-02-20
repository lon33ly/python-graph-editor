import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
from constants import *


class CustomDialog(simpledialog.Dialog):

    def __init__(self, title, prompt,
                 initialvalue=None,
                 minvalue=None, maxvalue=None,
                 parent=None):

        self.prompt = prompt
        self.minvalue = minvalue
        self.maxvalue = maxvalue
        self.answer_type = ''

        self.initialvalue = initialvalue

        simpledialog.Dialog.__init__(self, parent, title)

    def body(self, master):
        self.geometry("400x120")

        w = tk.Label(master, text="Вес грани:", justify=tk.LEFT)
        w.grid(row=0, padx=5, sticky=tk.W)

        self.entry = tk.Entry(master, name="entry")
        self.entry.grid(row=1, padx=5, sticky=tk.W + tk.E)

        if self.initialvalue is not None:
            self.entry.insert(0, self.initialvalue)
            self.entry.select_range(0, tk.END)

        return self.entry

    def destroy(self):
        self.entry = None
        simpledialog.Dialog.destroy(self)

    def buttonbox(self):
        box = tk.Frame(self)
        w = tk.Button(box, text=DIRECTED, width=14, command=lambda x=DIRECTED: self.button_down(x), default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text=UNDIRECTED, width=14, command=lambda x=UNDIRECTED: self.button_down(x))
        w.pack(side=tk.LEFT, padx=5, pady=5)

        # self.bind("<Return>", self.ok)
        # self.bind("<Escape>", self.cancel)

        box.pack()

    def button_down(self, x):
        self.answer_type = x
        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        try:
            self.apply()
        finally:
            self.cancel()

    def validate(self):
        try:
            result = self.getresult()
        except ValueError:
            messagebox.showwarning(
                "Illegal value",
                self.errormessage + "\nPlease try again",
                parent=self
            )
            return 0

        if self.minvalue is not None and result < self.minvalue:
            messagebox.showwarning(
                "Too small",
                "The allowed minimum value is %s. "
                "Please try again." % self.minvalue,
                parent=self
            )
            return 0

        if self.maxvalue is not None and result > self.maxvalue:
            messagebox.showwarning(
                "Too large",
                "The allowed maximum value is %s. "
                "Please try again." % self.maxvalue,
                parent=self
            )
            return 0

        self.result = result

        return 1


class _QueryString(CustomDialog):
    def __init__(self, *args, **kw):
        if "show" in kw:
            self.__show = kw["show"]
            del kw["show"]
        else:
            self.__show = None
        CustomDialog.__init__(self, *args, **kw)

    def body(self, master):
        entry = CustomDialog.body(self, master)
        if self.__show is not None:
            entry.configure(show=self.__show)
        return entry

    def getresult(self):
        return self.entry.get(), self.answer_type


def askstring(title, prompt, **kw):
    d = _QueryString(title, prompt, **kw)
    return d.result
