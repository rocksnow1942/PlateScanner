import tkinter as tk
from threading import Thread
from . import BaseViewPage


class NumberInputPage(BaseViewPage):
    resultType = int

    def __init__(self, parent, master) -> None:

        super().__init__(parent, master)
        self.createDefaultWidgets()
        self.placeDefaultWidgets()

    @property
    def inputValue(self):
        row = self.rowVar.get()
        col = self.colVar.get()
        return (col-1)*8 + ord(row)-64

    def placeDefaultWidgets(self):
        self._msg.place(x=20, y=430, width=740)
        self._prevBtn.place(x=340, y=300,  height=90, width=130,)
        self._nextBtn.place(x=650, y=300, height=90, width=130)
        self._title.place(x=0, y=20, width=800, height=30)

        self.rowVar = tk.StringVar()
        self.rowVar.set('D')
        self.colVar = tk.IntVar()
        self.colVar.set(4)

        tk.Label(self, textvariable=self.colVar, font=(
            'Arial', 65)).place(x=400, y=130, width=100)
        tk.Button(self, text='-', font=('Arial', 45), command=lambda: self.colVar.set(max(1, self.colVar.get()-1)))\
            .place(x=550, y=100, width=150, height=60)
        tk.Button(self, text='+', font=('Arial', 45), command=lambda: self.colVar.set(min(12, self.colVar.get()+1)))\
            .place(x=550, y=200, width=150, height=60)

        tk.Label(self, textvariable=self.rowVar, font=(
            'Arial', 65)).place(x=300, y=130, width=100)
        tk.Button(self, text='-', font=('Arial', 45), command=lambda: self.rowVar.set(self.getNextChar(self.rowVar.get(), -1)))\
            .place(x=100, y=100, width=150, height=60)
        tk.Button(self, text='+', font=('Arial', 45), command=lambda: self.rowVar.set(self.getNextChar(self.rowVar.get(), 1)))\
            .place(x=100, y=200, width=150, height=60)

    def getNextChar(self, current, step):
        new = ord(current) + step
        new = min(max(new, 65), 72)
        return chr(new)

    def showPage(self, title='Number input page', msg='Enter a number', color='green'):
        self.setTitle(title, color)
        self.tkraise()
        self.focus_set()
        self.displaymsg(msg, color)

    def closePage(self):
        pass

    def resetState(self):
        pass
