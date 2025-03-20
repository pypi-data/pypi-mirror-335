#!/usr/bin/env python
"""
Text widget for manipulation of DataFrame

This text widget allows putting in code to manipulate the current data frame.

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

:copyright: Copyright 2023- Matthias Cuntz - mc (at) macu (dot) de
:license: MIT License, see LICENSE for details.

.. moduleauthor:: Matthias Cuntz

The following classes are provided:

.. autosummary::
   dfvTransform

History
   * Written Oct 2024 by Matthias Cuntz (mc (at) macu (dot) de)

"""
try:
    from customtkinter import CTkToplevel as Toplevel
    from customtkinter import CTkFrame as Frame
    from customtkinter import CTkButton as Button
    from customtkinter import CTkTextbox as Text
    from customtkinter import CTkScrollbar as Scrollbar
    ihavectk = True
except ModuleNotFoundError:
    from tkinter import Toplevel
    from tkinter.ttk import Frame
    from tkinter.ttk import Button
    from tkinter import Text
    from tkinter.ttk import Scrollbar
    ihavectk = False
from .ncvwidgets import add_tooltip


__all__ = ['dfvTransform']


class dfvTransform(Toplevel):
    """
    Window for reading Python code to change DataFrame.

    """

    #
    # Setup panel
    #

    def __init__(self, top, callback=None, **kwargs):
        super().__init__(top, **kwargs)

        self.top = top  # top window
        self.callback = callback

        self.name = 'dfvTransform'
        self.title("Manipulate DataFrame")
        if ihavectk:
            self.geometry('1000x540+100+10')
        else:
            self.geometry('1000x490+100+10')

        # copy for ease of use
        self.csvfile = self.top.csvfile
        self.newcsvfile = self.top.newcsvfile
        self.df = self.top.df
        self.sep = self.top.sep
        self.index_col = self.top.index_col
        self.skiprows = self.top.skiprows
        self.parse_dates = self.top.parse_dates
        self.date_format = self.top.date_format
        self.missing_value = self.top.missing_value
        self.cols = self.top.cols

        # 1. row - treeview current DataFrame
        self.rowtext = Frame(self)
        self.rowtext.pack(side='top', fill='x')
        if ihavectk:
            # px
            self.text = Text(self.rowtext, height=500, width=985,
                             font=("Helvetica", 18), wrap='none')
        else:
            # characters
            self.text = Text(self.rowtext, height=22, width=88,
                             font=("Helvetica", 18), wrap='none')
        # self.text = Text(self.rowtext, height=24, width=88,
        #                  font=("Helvetica", 18), wrap='none')
        self.vscroll = Scrollbar(self.rowtext, command=self.text.yview)
        self.hscroll = Scrollbar(self.rowtext, command=self.text.xview)
        self.text.configure(yscrollcommand=self.vscroll.set,
                            xscrollcommand=self.hscroll.set)
        self.text.insert('1.0', '# Example daily mean if datetime index\n')
        self.text.insert('2.0',
                         "self.df = self.df.resample('1D').mean().squeeze()")
        self.text.pack(side='left')
        self.vscroll.pack(side='right', fill='y')
        self.hscroll.pack(side='bottom', fill='x')

        # add cancel and read buttons to last row
        self.rowdone = Frame(self)
        self.rowdone.pack(side='top', fill='x')
        self.done = Button(self.rowdone, text="Transform",
                           command=self.exec_text)
        self.donetip = add_tooltip(self.done,
                                   'Execute DataFrame manipulations')
        self.done.pack(side='right', padx=10, pady=5)
        self.cancel = Button(self.rowdone, text="Cancel",
                             command=self.cancel)
        self.canceltip = add_tooltip(self.cancel,
                                     'Cancel DataFrame manipulation')
        self.cancel.pack(side='right', pady=5)

        self.focus_force()

    #
    # Event bindings
    #

    def cancel(self, event=None):
        if self.callback is not None:
            self.callback()
        # do not self.destroy() with ctk.CTkButton, leading to
        # 'invalid command name
        #     ".!dfvreadcsv.!ctkframe3.!ctkbutton2.!ctkcanvas"'
        # self.destroy() works with ttk.Button
        self.withdraw()

    def exec_text(self, event=None):
        tt = self.text.get('1.0', 'end')
        _ = exec(tt)
        self.top.df = self.df
        if self.callback is not None:
            self.callback()
        # do not self.destroy() with ctk.CTkButton, leading to
        # 'invalid command name
        #     ".!dfvreadcsv.!ctkframe3.!ctkbutton2.!ctkcanvas"'
        # self.destroy() works with ttk.Button
        self.withdraw()
