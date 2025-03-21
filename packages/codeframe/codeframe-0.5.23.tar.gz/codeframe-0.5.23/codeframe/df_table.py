#!/usr/bin/env python3

# to override print <= can be a big problem with exceptions
# from __future__ import print_function # must be 1st
# import builtins

# import sys

from fire import Fire

# from codeframe.version import __version__
# from codeframe import unitname
from codeframe import config
# from codeframe import libs_one
# from codeframe import libs_two

# import time
# import datetime as dt
from console import fg, bg
import time
# import os

import pandas as pd
import numpy as np
from terminaltables import SingleTable
import datetime as dt
from dateutil import parser
#import dateutil
# =============================================================
#
#--------------------------------------------------------------

def decode_datetime(date_string):
    return parser.parse(date_string, dayfirst=True)

def crtable():
    """
    create table every loop or @  1/N loops .....
    """
    # call some libraries....
    df = pd.DataFrame(  columns=['cron', 'screen',  'elapsed', 'comment', 'DT'])
    #print(df)

    return df

# =============================================================
#
#--------------------------------------------------------------

def create_dummy_df():
    """
    create dummy dataframe from scratch.... test purposes
    """
    columns = ["a", "b", "c", "_fg", "_bg"]
    # columns1=[x for x in columns if x[0]!="_"]
    df = pd.DataFrame(np.random.randint(0, 9, size=(11, len(columns))),
                      columns=columns)
    df["_fg"] = fg.lightgray  # fg.default
    df["_bg"] = bg.default

    # --------------------------- default pattern ------------
    for i, row in df.iterrows():
        if i % 3 == 0:
            df.loc[i, ["_bg"]] = bg.darkslategray  # bg.dimgray#bg.darkslategray
        else:
            df.loc[i, ["_bg"]] = bg.default  # bg.black

        #if i % 5 == 0:
        #    df.loc[i, ["_fg"]] = fg.lightgreen  # lightyellow

    return df


def inc_dummy_df(df):
    """
    increase df cells by unit for the demo dummy table
    """
    for i, row in df.iterrows():
        df.iloc[i, :-2] = df.iloc[i, :-2] + 1  # loc doesnt work, iloc is ok
    return df



def enhance_df(df):
    """
    With a read dataframe, you need to enhance with _bg and _fg to be displayable
    """
    #columns = ["a", "b", "c", "_fg", "_bg"]
    # columns1=[x for x in columns if x[0]!="_"]
    #df = pd.DataFrame(np.random.randint(0, 9, size=(11, len(columns))),
    #                  columns=columns)
    df["_fg"] = fg.lightgray  # fg.default
    df["_bg"] = bg.default

    # --------------------------- default pattern ------------
    for i, row in df.iterrows():
        if i % 3 == 0:
            df.loc[i, ["_bg"]] = bg.darkslategray  # bg.dimgray#bg.darkslategray
        else:
            df.loc[i, ["_bg"]] = bg.default  # bg.black
        #
        #if i % 5 == 0:
        #    df.loc[i, ["_fg"]] = fg.lightgreen  # lightyellow
    return df




# ======================================================
def show_table(df, selection="3", return_subdf=False):
    """
    enhance the df and display fancy. Also return df when selection
    """

    row_n = [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
    ]
    #---------------

    if return_subdf:
        # Convert selection to a list of integers (0-based index)
        # selected_indices = [ord(char) - 1 for char in str(selection) ]
        selected_indices = [row_n.index(char) for char in selection]
        selected_indices = [i for i in selected_indices if i < len(df)] # avoid crasjh
        return  df.iloc[selected_indices]

    dfenha = df.copy()
    dfenha = enhance_df(dfenha)
    #-
    dfpure = df.copy()
    # dfpure.drop(columns=["_fg", "_bg"], inplace=True) # oooo

    rows = dfpure.values.tolist() #-------------------->>>>>
    rows = [[str(el) for el in row] for row in rows] #->>>>>
    # columns = df.columns.tolist()
    #
    columns2 = [x for x in list(dfenha.columns) if x[0] != "_"]
    #
    tab_header = [["n"] + columns2]  #----------
    #
    # tab_header = [  f"{fg.white}{x}{fg.default}" for x in tab_header] # NOTW
    # data = [['a','b'], ['ca','cb']]
    #========================= start to construct the table ============
    tab_src = tab_header.copy()

    # nn=0  #I use index
    padding = "  "  # nicer bars
    for index, row in dfenha.iterrows():
        # i take row from pure
        row = list(dfpure.loc[index, :])
        fgcol = fg.white
        fgcol = dfenha.loc[index, ["_fg"]].iloc[0]
        bgcol = dfenha.loc[index, ["_bg"]].iloc[0]
        if selection is not None and row_n[index] in list(selection):
            # print(index, selection)
            bgcol = bg.yellow4  # df.loc[index,['_fg']][0]

        # print(bgcol)
        # print(index, row ) # list of pure df cols for row
        row = [row_n[index]] + row

        for j in range(len(row)):  # change color for all columns
            row[j] = (
                fgcol
                + bgcol
                + padding
                + str(row[j])
                + padding
                + bg.default
                + fg.default
            )



        tab_src.append(row)  # prepend to list /THE TABLE TO DISPLAY/
        # nn+=1

    # ==================== HERE IS THE OBJECT=========
    table = SingleTable(tab_src)
    table.padding_left = 0
    table.padding_right = 0
    # blessings terminal() t.clear()

    # --------- if too wide - i think
    if not table.ok:
        table.padding_left = 0
    if not table.ok:
        table.padding_right = 0
    while not table.ok:
        # if bad size
        # remove columns here
        j = 0
        for k in tab_src:
            tab_src[j] = k[:-1]
            j+=1
        table = SingleTable(tab_src)
        table.padding_left = 0
        table.padding_right = 0

    print(table.table)





def main():
    """
    Show table
    """
    df = create_dummy_df()
    df = inc_dummy_df(df)
    move_cursor(15, 4)
    show_table(df)


if __name__ == "__main__":
    Fire(main)
