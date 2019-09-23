#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Author: 			Robert Wells
# Project Title: 	Smart Firefighter Support System
# FileName: 		sfss-wo_canvas.py
# Path: 			c:\Users\wells.robert\Google Drive\School\_2019 Fall\Design 2\GUI\sfss-wo_canvas.py
# Project: 			c:\Users\wells.robert\Google Drive\School\_2019 Fall\Design 2\GUI
# Created Date: 	Monday, September 16th 2019, 18:28:30 pm
# -----
# Last Modified: 	Monday, September 23rd 2019, 00:38:19 am
# Modified By: 		Robert Wells
# -----
# Copyright (c) 2019 SFSS
# 
# GNU General Public License v3.0
# https://spdx.org/licenses/LGPL-3.0-only.html
# -----
# HISTORY:
# Date      			By		Comments
# ----------			---		----------------------------------------------------------
# 2019-09-22 21:09:56	RW		redid comments to better outline code (use code folding if your IDE supports it)
# 2019-09-22 19:09:76	RW		added graph buttons, combined update functions for hr/movement, added "overview" on
#                                default tab, added frames to columns to clean up look of tab layouts, added "update
#                                all" button to dynamically refresh all tabs
# 2019-09-21 00:09:77	RW		re wrote complicated csv read/write for hr and maxhr using pandas (saved buuunches
#                                of lines)
# 2019-09-15 20:09:48	RW		updated TODO: list, added defs for raw data tables (hr/mov), loading gif, fixed
#                                default browser in usersguide and added comments
###




# ---------------------------------- imports --------------------------------- #

import csv
import os
import subprocess
import sys
import webbrowser

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import MaxNLocator

if sys.version_info[0] >= 3:
    import PySimpleGUI as sg
else:
    import PySimpleGUI27 as sg

# * DEPENDENCY: matplotlib 3.0.3
# * [env conda activate seniordesigngui]

# ? use heartpy to process the data in a loop and then plug into updating graph in new window?
# * use updating multiline to report hr and movement in text.  button to view updating graph in new window
# ?NOTE: how about running graphs in browser windows with bokeh
# // NOTE: - ***DONE***create conda environment so that matplotlib works (3.0.3)
# TODO: - add menu option to initialize connection to board
    # TODO: - write function to connect to board
    # TODO: - add updating 'gif' or progress meter for connection
    # TODO: - add indicator for connection on/off

    # ? how do i make the GUI reload the csv data at xtimes/sec
    # ? should i add a slider to increase/decrease update freq on graphs
# TODO: - add right click menus for (raw data, initialize connection, export photo?)
# // TODO: - sg.popup warnings for data above/below safe values
# // TODO: add led indicators to main page to have 'at a glance' status view
# ---------------------------------------------------------------------------- #
#                                  Definitions                                 #
# ---------------------------------------------------------------------------- #

# ----------------------------- HEART RATE TABLE ----------------------------- #

def hrtable1():
    sg.SetOptions(auto_size_buttons=True)
    filename = sg.PopupGetFile('Choose the .CSV with the data you want to see', no_window=False,
    file_types=(("CSV Files", "*.csv"),))
    # --- populate table with file contents --- #
    if filename == '':
        sys.exit(69)
    data = []
    header_list = []
    if filename is not None:
        try:
            df = pd.read_csv(filename, sep=',', engine='python', header=None)
            # Header=None means you directly pass the columns names to the dataframe
            data = df.values.tolist()
            # read everything else into a list of rows
            header_list = df.iloc[0].tolist()
            # Uses the first row (which should be column names) as columns names
            data = df[1:].values.tolist()
            # Drops the first row in the table (otherwise the header names and the first row will be the same)
        except:
            sg.PopupError('Error reading file')
            pass

    layout = [[sg.Table(values=data, headings=header_list, display_row_numbers=False,
                            auto_size_columns=True, num_rows=min(25,len(data)))]]

    hrwindow = sg.Window('Table', grab_anywhere=False)

    while True:
        event, values = hrwindow.Layout(layout).Read()
        if event in(None, 'Exit'):
            break

    pass

# ------------------------------ MOVEMENT TABLE ------------------------------ #

def movtable1():
    sg.SetOptions(auto_size_buttons=True)
    filename = sg.PopupGetFile('Choose the .CSV with the data you want to see', no_window=False,
    file_types=(("CSV Files", "*.csv"),))
    # --- populate table with file contents --- #
    if filename == '':
        sys.exit(69)
    data = []
    header_list = []
    if filename is not None:
        try:
            df = pd.read_csv(filename, sep=',', engine='python', header=None)
            data = df.values.tolist()
            header_list = df.iloc[0].tolist()
            data = df[1:].values.tolist()
        except:
            sg.PopupError('Error reading file')
            pass

    layout = [[sg.Table(values=data, headings=header_list, display_row_numbers=False,
                            auto_size_columns=True, num_rows=min(25,len(data)))]]

    movwindow = sg.Window('Table', grab_anywhere=False)
    while True:
        event, values = movwindow.Layout(layout).Read()
        if event in(None, 'Exit'):
            break
    pass

# ----------------------------------- LEDs ----------------------------------- #

def LEDIndicator(key=None, radius=40):
    return sg.Graph(canvas_size=(radius, radius),
             graph_bottom_left=(-radius, -radius),
             graph_top_right=(radius, radius),
             pad=(0, 0), key=key)

def SetLED(windowmain, key, color):
    graph = windowmain.FindElement(key)
    graph.Erase()
    graph.DrawCircle((0, 0), 20, fill_color=color, line_color=color)

# ----------------------------- HEART RATE GRAPHS ---------------------------- #

def showhr1graph():
    x=[]
    y=[]
    with open('data1.csv',  encoding = 'utf-8-sig') as csvfile:
        plots = csv.reader(csvfile)
        for data in plots:
            #get heading for x and y axes
            var1 = ('Time')
            var2 = ('Heart Rate (bpm)')
            break
        for data in plots:
            #get values - add to x list and y list
            x.append(float(data[0]))
            y.append(float(data[1]))

    ax = plt.subplot(1,1,1)
    ax.set_ylim([0, 280])
    ax.xaxis.set_major_locator(MaxNLocator(10))
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')

    plt.plot(x,y, label = 'HR')
    plt.axhline(y  = 230, color = 'red', linestyle = '--', label = 'Danger')
    plt.xlabel(var1)
    plt.ylabel(var2)
    plt.title('FireFighter1: Heart Rate')

    plt.legend()
    plt.show()

def showhr2graph():
    x=[]
    y=[]
    with open('data2.csv',  encoding = 'utf-8-sig') as csvfile:
        plots = csv.reader(csvfile)
        for data in plots:
            #get heading for x and y axes
            var1 = ('Time')
            var2 = ('Heart Rate (bpm)')
            break
        for data in plots:
            #get values - add to x list and y list
            x.append(float(data[0]))
            y.append(float(data[1]))

    ax = plt.subplot(1,1,1)
    ax.set_ylim([0, 280])
    ax.xaxis.set_major_locator(MaxNLocator(10))
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    
    plt.plot(x,y, label = 'HR')
    plt.axhline(y  = 230, color = 'red', linestyle = '--', label = 'Danger')
    plt.xlabel(var1)
    plt.ylabel(var2)
    plt.title('FireFighter 2: Heart Rate')

    plt.legend()
    plt.show()

def showhr3graph():
    x=[]
    y=[]
    with open('data3.csv',  encoding = 'utf-8-sig') as csvfile:
        plots = csv.reader(csvfile)
        for data in plots:
            #get heading for x and y axes
            var1 = ('Time')
            var2 = ('Heart Rate (bpm)')
            break
        for data in plots:
            #get values - add to x list and y list
            x.append(float(data[0]))
            y.append(float(data[1]))

    ax = plt.subplot(1,1,1)
    ax.set_ylim([0, 280])
    ax.xaxis.set_major_locator(MaxNLocator(10))
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    
    plt.plot(x,y, label = 'HR')
    plt.axhline(y  = 230, color = 'red', linestyle = '--', label = 'Danger')
    plt.xlabel(var1)
    plt.ylabel(var2)
    plt.title(' FireFighter 3: Heart Rate')
    

    plt.legend()
    plt.show()
# ---------------------------------------------------------------------------- #
#                                 PROGRAM START                                #
# ---------------------------------------------------------------------------- #

def main():

# ---------------------------- setup window "feel" --------------------------- #

    sg.ChangeLookAndFeel('Dark2')
    sg.SetOptions(font=('calibri', 12,), element_padding=(1, 1))

# ------------------------- get pathname for logo file ----------------------- #

    dirname, filename = os.path.split(os.path.abspath(__file__))
    pathname = os.path.join(dirname, 'logo.png')

# ------------------------------ Menu Definition ----------------------------- #

    menu_def = [['File', ['Initialize Connection::_INITIALIZE_', 'Terminate Connection::_TERMINATE_', 'Save', 'Exit'  ]],
                ['Edit', ['Paste', ['Special', 'Normal', ], 'Undo'], ],
                ['Help', ['Users Guide', 'About...']], ]

# ------------------------------- GUI Defintion ------------------------------ #

    # TODO: - finish linking buttons to retrieve raw data in table format in new window
    # // TODO: - show captured data in canvases

# --------------------- define columns to be used in tabs -------------------- #

    cola1_frame_layout = [
        [sg.Text("Heart Rate", font=('calibri', 12), justification='right'),
        LEDIndicator('_FF1HRLED_'), sg.Output(font=('calibri', 15, 'bold'), key='_HRTEXT1_'),
        sg.Text('Max Recorded HR:', justification='right'), sg.Output(font=('calibri', 15, 'bold'), key='_MAXHRTEXT1_'),
        sg.Button('FF1 RAW Heart Rate', key='_RAWHR1_')]
        ]

    cola1 = [[sg.Frame('Heart Rate', cola1_frame_layout)]]

    cola2_frame_layout = [
        [sg.Text('Movement', font=('calibri', 12), justification='right'),
        LEDIndicator('_FF1MOVLED_'), sg.Output(font=('calibri', 15, 'bold'), key='_MOVTEXT1_'),
        sg.Text('Movement Warnings:', justification='right'), sg.Output(font=('calibri', 15, 'bold'), key='_MOVWARN1_'),
        sg.Button('FF1 RAW Movement', key='_RAWMOV1_')]
    ]

    cola2 = [[sg.Frame('Movement', cola2_frame_layout)]]

    cola3_frame_layout = [
        [sg.Text('Temperature', font=('calibri', 12), justification='right'),
        LEDIndicator('_FF1TEMPLED_'), sg.Output(font=('calibri', 15, 'bold'), key='_TEMPTEXT1_'),
        sg.Text('Temperature Warnings:', justification='right'), sg.Output(font=('calibri', 15, 'bold'), key='_TEMPWARN1_'),
        sg.Button('FF1 RAW Temperature', key='_RAWTEMP1_')]
    ]

    cola3 = [[sg.Frame('Temperature', cola3_frame_layout)]]


    colb1_frame_layout = [
        [sg.Text("Heart Rate", font=('calibri', 12, 'bold'), justification='right'),
        LEDIndicator('_FF2HRLED_'), sg.Output(font=('calibri', 15, 'bold'), key='_HRTEXT2_'),
        sg.Text('Max Recorded HR:', justification='right'), sg.Output(font=('calibri', 15, 'bold'), key='_MAXHRTEXT2_'),
        sg.ReadButton('FF2 RAW Heart Rate', key='_RAWHR2_')]
    ]

    colb1 = [[sg.Frame('Heart Rate', colb1_frame_layout)]]

    colb2_frame_layout = [
        [sg.Text('Movement', font=('calibri', 12), justification='right'),
        LEDIndicator('_FF2MOVLED_'), sg.Output(font=('calibri', 15, 'bold'), key='_MOVTEXT2_'),
        sg.Text('Movement Warnings:', justification='right'), sg.Output(font=('calibri', 15, 'bold'), key='_MOVWARN2_'),
        sg.Button('FF2 RAW Movement', key='_RAWMOV2_')]
    ]

    colb2 = [[sg.Frame('Movement', colb2_frame_layout)]]

    colb3_frame_layout = [
        [sg.Text('Temperature', font=('calibri', 12), justification='right'),
        LEDIndicator('_FF2TEMPLED_'), sg.Output(font=('calibri', 15, 'bold'), key='_TEMPTEXT2_'),
        sg.Text('Temperature Warnings:', justification='right'), sg.Output(font=('calibri', 15, 'bold'), key='_TEMPWARN2_'),
        sg.Button('FF2 RAW Temp', key='_RAWTEMP2_')]
    ]

    colb3 = [[sg.Frame('Temperature', colb3_frame_layout)]]

    colc1_frame_layout = [
        [sg.Text("Heart Rate", font=('calibri', 12), justification='right'),
        LEDIndicator('_FF3HRLED_'), sg.Output(font=('calibri', 15, 'bold'), key='_HRTEXT3_'),
        sg.Text('Max Recorded HR:', justification='right'), sg.Output(font=('calibri', 15, 'bold'), key='_MAXHRTEXT3_'),
        sg.ReadButton('FF3 RAW Heart Rate', key='_RAWHR3_')]
    ]

    colc1 = [[sg.Frame('Heart Rate', colc1_frame_layout)]]

    colc2_frame_layout = [
        [sg.Text('Movement', font=('calibri', 12), justification='right'),
        LEDIndicator('_FF3MOVLED_'), sg.Output(font=('calibri', 15, 'bold'), key='_MOVTEXT3_'),
        sg.Text('Movement Warnings:', justification='right'), sg.Output(font=('calibri', 15, 'bold'), key='_MOVWARN3_'),
        sg.Button('FF3 RAW Movement', key='_RAWMOV3_')]
    ]

    colc3_frame_layout = [
        [sg.Text('Temperature', font=('calibri', 12), justification='right'),
        LEDIndicator('_FF3TEMPLED_'), sg.Output(font=('calibri', 15, 'bold'), key='_TEMPTEXT3_'),
        sg.Text('Temperature Warnings:', justification='right'), sg.Output(font=('calibri', 15, 'bold'), key='_TEMPWARN3_'),
        sg.Button('FF3 RAW Temp', key='_RAWTEMP3_')]
    ]

    colc3 = [[sg.Frame('Temperature', colc3_frame_layout)]]

    colc2 = [[sg.Frame('Movement', colc2_frame_layout)]]

# ---------------------------- define tab layouts ---------------------------- #
    tabdefault_frame_layout = [
                    [sg.Text('Firefighter #', justification='center'), sg.Text('Heart Rate', justification='center'),
                    sg.Text('Movement', justification='center'), sg.Text('Temperature', justification='center')],
                    [sg.Text('Firefighter 1: ', justification='left'), LEDIndicator('_TABDEFAULTFF1HRLED_'),
                    sg.Text(' '), LEDIndicator('_TABDEFAULTFF1MOVLED_'), sg.Text(' '), LEDIndicator('_TABDEFAULTFF1TEMPLED_')],
                    [sg.Text('Firefighter 2: ', justification='left'), LEDIndicator('_TABDEFAULTFF2HRLED_'),
                    sg.Text(' '), LEDIndicator('_TABDEFAULTFF2MOVLED_'), sg.Text(' '), LEDIndicator('_TABDEFAULTFF2TEMPLED_')],
                    [sg.Text('Firefighter 3: ', justification='left'), LEDIndicator('_TABDEFAULTFF3HRLED_'),
                    sg.Text(' '), LEDIndicator('_TABDEFAULTFF3MOVLED_'), sg.Text(' '), LEDIndicator('_TABDEFAULTFF3TEMPLED_')]
    ]

    tabdefault_layout =  [
                    [sg.Image(pathname, pad=(2,2))],
                    [sg.Text('Welcome to the SFSS!', size=(45, 1), justification='center',
                    font=('calibri', 25, 'bold'))],
                    [sg.Text('Use the tabs above to navigate...', size=(45, 1), justification='center',
                    font=('calibri', 15))],
                    [sg.Frame('Firefighter Status', tabdefault_frame_layout, relief=sg.RELIEF_RAISED,
                    element_justification='justified')],
                    [sg.Button('Initialize Connection', button_color=('white','green'), key='_INITIALIZE_'),
                    sg.Button('Terminate Connection', button_color=('white','firebrick'), key='_TERMINATE_')],
                    [sg.Button('Update All', key='_UPDATEALL_')]
    ]

    tab1_layout =  [
                    [sg.Text('Firefighter 1', font=('calibri', 15, 'bold'))],
                    [sg.Column(cola1)],
                    [sg.Column(cola2)],
                    [sg.Column(cola3)],
                    [sg.Button('Update', key='_UPDATETAB1_'), sg.Button('Show Graph', key='_HRGRAPH1_')]
    ]

    tab2_layout =  [
                    [sg.Text('Firefighter 2', font=('calibri', 15, 'bold'))],
                    [sg.Column(colb1)],
                    [sg.Column(colb2)],
                    [sg.Column(colb3)],
                    [sg.Button('Update', key='_UPDATETAB2_'), sg.Button('Show Graph', key='_HRGRAPH2_')]
    ]

    tab3_layout =  [
                    [sg.Text('Firefighter 3', font=('calibri', 15, 'bold'))],
                    [sg.Column(colc1)],
                    [sg.Column(colc2)],
                    [sg.Column(colc3)],
                    [sg.Button('Update', key='_UPDATETAB3_'), sg.Button('Show Graph', key='_HRGRAPH3_')]
    ]

# ------------------------------- window layout ------------------------------ #

    layout = [
        [sg.Menu(menu_def, tearoff=False)],
        [sg.TabGroup([
            [sg.Tab('Welcome', tabdefault_layout),
            sg.Tab('Firefighter 1', tab1_layout),
            sg.Tab('Firefighter 2', tab2_layout),
            sg.Tab('Firefighter 3', tab3_layout)]
            ],
            key='_TABGROUP_', title_color='Black')]
    ]


    windowmain = sg.Window("Smart Firefighter Support System", default_element_size=(20, 5), auto_size_text=False,
                            auto_size_buttons=True, element_padding=(3,3), grab_anywhere=False,
                            default_button_element_size=(5, 1), resizable=True, element_justification='center',
                            finalize=True).Layout(layout)

# -------------------- Loop & Process button menu choices -------------------- #

    while True:
        event, values = windowmain(timeout=50)
        if event == None or event == 'Exit':
            break

# -------------------------- code for showing graphs ------------------------- #
        if event == '_HRGRAPH1_':
            showhr1graph()
        if event == '_HRGRAPH2_':
            showhr2graph()
        if event == '_HRGRAPH3_':
            showhr3graph()

# ------- code for warning LEDs and outputting hr/max hr and movement ------- #

# ------------------------------- FIREFIGHTER1 ------------------------------- #

        if event == '_UPDATETAB1_' or event =='_UPDATEALL_':

    # --------------------------------- FF1heartrate -------------------------------- #

            df1 = pd.read_csv('data1.csv', names=['time', 'heartrate'], index_col=['time'])
            maxhr1 = df1['heartrate'].max()
            last_row_display1 = df1['heartrate'].iloc[-1]
            windowmain['_HRTEXT1_'].Update(last_row_display1)
            windowmain['_MAXHRTEXT1_'].Update(maxhr1)
            if last_row_display1.item() > 230:
                SetLED(windowmain, '_FF1HRLED_', 'red' if last_row_display1.all() > 230 else 'red')
                SetLED(windowmain, '_TABDEFAULTFF1HRLED_', 'red' if last_row_display1.all() > 230 else 'red')
                sg.PopupAutoClose('WARNING! HEART RATE IS HIGH!', auto_close_duration=3, non_blocking=True,
                background_color='red',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False)
            elif last_row_display1.item() <=30:
                SetLED(windowmain, '_FF1HRLED_', 'red' if last_row_display1.all() <= 30  else 'red')
                SetLED(windowmain, '_TABDEFAULTFF1HRLED_', 'red' if last_row_display1.all() <= 30 else 'red')
                sg.PopupAutoClose('WARNING! HEART RATE IS LOW!', auto_close_duration=3, non_blocking=True,
                background_color='red',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False)
            else:
                SetLED(windowmain, '_FF1HRLED_', 'green' if last_row_display1.all() < 230 else 'green')
                SetLED(windowmain, '_TABDEFAULTFF1HRLED_', 'green' if last_row_display1.all() < 230 else 'green')

    # --------------------------------- FF1movement --------------------------------- #

            df1m = pd.read_csv('data1mov.csv', names=['time', 'movement'], index_col=['time'])
            #movwarn1 = df1['movement'].max()
            last_row_display1m = df1m['movement'].iloc[-1]
            windowmain['_MOVTEXT1_'].Update(last_row_display1m)
            if last_row_display1m.item() < 1:
                windowmain['_MOVWARN1_'].Update('Low movement')
                SetLED(windowmain, '_FF1MOVLED_', 'red' if last_row_display1m.all() < 1 else 'red')
                SetLED(windowmain, '_TABDEFAULTFF1MOVLED_', 'red' if last_row_display1m.all() < 1 else 'red')
                sg.PopupAutoClose('WARNING! LOW MOVEMENT DETECTED!', auto_close_duration=3, non_blocking=True,
                background_color='red',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False)
            else:
                windowmain['_MOVWARN1_'].Update('No warnings')
                SetLED(windowmain, '_FF1MOVLED_', 'green' if last_row_display1m.all() > 1 else 'green')
                SetLED(windowmain, '_TABDEFAULTFF1MOVLED_', 'green' if last_row_display1m.all() > 1 else 'green')

    # -------------------------------- FF1temperature ------------------------------- #

            df1t = pd.read_csv('data1temp.csv', names=['time', 'temp'], index_col=['time'])
            #movwarn1 = df1['movement'].max()
            last_row_display1t = df1t['temp'].iloc[-1]
            windowmain['_TEMPTEXT1_'].Update(last_row_display1t)
            if last_row_display1t.item() > 500:
                windowmain['_TEMPWARN1_'].Update('High Temperature')
                SetLED(windowmain, '_FF1TEMPLED_', 'red' if last_row_display1t.all() > 500 else 'red')
                SetLED(windowmain, '_TABDEFAULTFF1TEMPLED_', 'red' if last_row_display1.all() > 500 else 'red')
                sg.PopupAutoClose('WARNING! HIGH TEMPERATURE DETECTED!', auto_close_duration=3, non_blocking=True,
                background_color='red',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False)
            else:
                windowmain['_TEMPWARN1_'].Update('No warnings')
                SetLED(windowmain, '_FF1TEMPLED_', 'green' if last_row_display1t.all() < 500 else 'green')
                SetLED(windowmain, '_TABDEFAULTFF1TEMPLED_', 'green' if last_row_display1t.all() < 500 else 'green')

# ------------------------------- FIREFIGHTER2 ------------------------------- #

        if event == '_UPDATETAB2_' or event =='_UPDATEALL_':

    # --------------------------------- FF2heartrate -------------------------------- #

            df2 = pd.read_csv('data2.csv', names=['time', 'heartrate'], index_col=['time'])
            maxhr2 = df2['heartrate'].max()
            last_row_display2 = df2['heartrate'].iloc[-1]
            windowmain['_HRTEXT2_'].Update(last_row_display2)
            windowmain['_MAXHRTEXT2_'].Update(maxhr2)
            if last_row_display2.item() > 230:
                SetLED(windowmain, '_FF2HRLED_', 'red' if last_row_display2.all() > 230 else 'red')
                SetLED(windowmain, '_TABDEFAULTFF2HRLED_', 'red' if last_row_display2.all() > 230 else 'red')
                sg.PopupAutoClose('WARNING! HEART RATE IS HIGH!', auto_close_duration=3, non_blocking=True,
                background_color='red',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False)
            elif last_row_display2.item() <=30:
                SetLED(windowmain, '_FF2HRLED_', 'red' if last_row_display2.all() <= 30  else 'red')
                SetLED(windowmain, '_TABDEFAULTFF2HRLED_', 'red' if last_row_display2.all() <= 30 else 'red')
                sg.PopupAutoClose('WARNING! HEART RATE IS LOW!', auto_close_duration=3, non_blocking=True,
                background_color='red',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False)
            else:
                SetLED(windowmain, '_FF2HRLED_', 'green' if last_row_display2.all() < 230 else 'green')
                SetLED(windowmain, '_TABDEFAULTFF2HRLED_', 'green' if last_row_display2.all() < 230 else 'green')

    # --------------------------------- FF2movement --------------------------------- #

            df2m = pd.read_csv('data2mov.csv', names=['time', 'movement'], index_col=['time'])
            #movwarn1 = df1['movement'].max()
            last_row_display2m = df2m['movement'].iloc[-1]
            windowmain['_MOVTEXT2_'].Update(last_row_display2m)
            if last_row_display2m.item() < 1:
                windowmain['_MOVWARN2_'].Update('Low movement')
                SetLED(windowmain, '_FF2MOVLED_', 'red' if last_row_display2m.all() < 1 else 'red')
                SetLED(windowmain, '_TABDEFAULTFF2MOVLED_', 'red' if last_row_display2.all() < 1 else 'red')
                sg.PopupAutoClose('WARNING! LOW MOVEMENT DETECTED!', auto_close_duration=3, non_blocking=True,
                background_color='red',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False)
            else:
                windowmain['_MOVWARN2_'].Update('No warnings')
                SetLED(windowmain, '_FF2MOVLED_', 'green' if last_row_display2m.all() > 1 else 'green')
                SetLED(windowmain, '_TABDEFAULTFF2MOVLED_', 'green' if last_row_display2m.all() > 1 else 'green')

    # -------------------------------- FF2temperature ------------------------------- #

            df2t = pd.read_csv('data2temp.csv', names=['time', 'temp'], index_col=['time'])
            #movwarn2 = df2['movement'].max()
            last_row_display2t = df2t['temp'].iloc[-1]
            windowmain['_TEMPTEXT2_'].Update(last_row_display2t)
            if last_row_display2t.item() > 500:
                windowmain['_TEMPWARN2_'].Update('High Temperature')
                SetLED(windowmain, '_FF2TEMPLED_', 'red' if last_row_display2t.all() > 500 else 'red')
                SetLED(windowmain, '_TABDEFAULTFF2TEMPLED_', 'red' if last_row_display2.all() > 500 else 'red')
                sg.PopupAutoClose('WARNING! HIGH TEMPERATURE DETECTED!', auto_close_duration=3, non_blocking=True,
                background_color='red',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False)
            else:
                windowmain['_TEMPWARN2_'].Update('No warnings')
                SetLED(windowmain, '_FF2TEMPLED_', 'green' if last_row_display2t.all() < 500 else 'green')
                SetLED(windowmain, '_TABDEFAULTFF2TEMPLED_', 'green' if last_row_display2t.all() < 500 else 'green')

# ------------------------------- FIREFIGHTER3 ------------------------------- #

        if event == '_UPDATETAB3_' or event =='_UPDATEALL_':

    # --------------------------------- FF3heartrate -------------------------------- #

            df3 = pd.read_csv('data3.csv', names=['time', 'heartrate'], index_col=['time'])
            maxhr3 = df3['heartrate'].max()
            last_row_display3 = df3['heartrate'].iloc[-1]
            windowmain['_HRTEXT3_'].Update(last_row_display3)
            windowmain['_MAXHRTEXT3_'].Update(maxhr3)
            if last_row_display3.item() > 230:
                SetLED(windowmain, '_FF3HRLED_', 'red' if last_row_display3.all() > 230  else 'red')
                SetLED(windowmain, '_TABDEFAULTFF3HRLED_', 'red' if last_row_display3.all() > 230 else 'red')
                sg.PopupAutoClose('WARNING! HEART RATE IS HIGH!', auto_close_duration=3, non_blocking=True,
                background_color='red',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False)
            elif last_row_display3.item() <=30:
                SetLED(windowmain, '_FF3HRLED_', 'red' if last_row_display3.all() <= 30  else 'red')
                SetLED(windowmain, '_TABDEFAULTFF3HRLED_', 'red' if last_row_display3.all() <= 30 else 'red')
                sg.PopupAutoClose('WARNING! HEART RATE IS LOW!', auto_close_duration=3, non_blocking=True,
                background_color='red',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False)
            else:
                SetLED(windowmain, '_FF3HRLED_', 'green' if last_row_display3.all() < 230 else 'green')
                SetLED(windowmain, '_TABDEFAULTFF3HRLED_', 'green' if last_row_display3.all() < 230 else 'green')

    # --------------------------------- FF3movement --------------------------------- #

            df3m = pd.read_csv('data3mov.csv', names=['time', 'movement'], index_col=['time'])
            #movwarn1 = df1['movement'].max()
            last_row_display3m = df3m['movement'].iloc[-1]
            windowmain['_MOVTEXT3_'].Update(last_row_display3m)
            if last_row_display3m.item() < 1:
                windowmain['_MOVWARN3_'].Update('Low movement')
                SetLED(windowmain, '_FF3MOVLED_', 'red' if last_row_display3m.all() < 1 else 'red')
                SetLED(windowmain, '_TABDEFAULTFF3MOVLED_', 'red' if last_row_display3.all() < 1 else 'red')
                sg.PopupAutoClose('WARNING! LOW MOVEMENT DETECTED!', auto_close_duration=3, non_blocking=True,
                background_color='red',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False)
            else:
                windowmain['_MOVWARN3_'].Update('No warnings')
                SetLED(windowmain, '_FF3MOVLED_', 'green' if last_row_display3m.all() > 1 else 'green')
                SetLED(windowmain, '_TABDEFAULTFF3MOVLED_', 'green' if last_row_display3m.all() > 1 else 'green')

    # -------------------------------- FF3temperature ------------------------------- #

            df3t = pd.read_csv('data3temp.csv', names=['time', 'temp'], index_col=['time'])
            #movwarn3 = df3['movement'].max()
            last_row_display3t = df3t['temp'].iloc[-1]
            windowmain['_TEMPTEXT3_'].Update(last_row_display3t)
            if last_row_display3t.item() > 500:
                windowmain['_TEMPWARN3_'].Update('High Temperature')
                SetLED(windowmain, '_FF3TEMPLED_', 'red' if last_row_display3t.all() > 500 else 'red')
                SetLED(windowmain, '_TABDEFAULTFF3TEMPLED_', 'red' if last_row_display3.all() > 500 else 'red')
                sg.PopupAutoClose('WARNING! HIGH TEMPERATURE DETECTED!', auto_close_duration=3, non_blocking=True,
                background_color='red',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False)
            else:
                windowmain['_TEMPWARN3_'].Update('No warnings')
                SetLED(windowmain, '_FF3TEMPLED_', 'green' if last_row_display3t.all() < 500 else 'green')
                SetLED(windowmain, '_TABDEFAULTFF3TEMPLED_', 'green' if last_row_display3t.all() < 500 else 'green')

# ----------------------------- RAW data choices ----------------------------- #

# *** add other events ***
# TODO: rewrite the xxtable() functions using pd to make it smaller

# -------------------------------- raw tables -------------------------------- #

        if event == 'FF1 RAW Heart Rate' or event == '_RAWHR1_':
            hrtable1()
        if event == 'FF1 RAW Movement' or event == '_RAWMOV1_':
            movtable1()

# --------------------------- Process menu choices --------------------------- #

#*** add calls to initialize and terminate functions and progress spinners

# --------------------------- intitialize/terminate -------------------------- #

        if event == '_INITIALIZE_':
            pathname = os.path.join(dirname, 'blue_blocks.gif')
            for i in range(500000):
                sg.PopupAnimated('blue_blocks.gif', message='Initializing Connection...', background_color='black',
                time_between_frames=75)
            sg.PopupAnimated(None)

        if event == '_TERMINATE_':
        #***terminate()  FUNCTION CALL GOES HERE
            sg.Popup('Connection Terminated','Your connection has been terminated')

# ------------------------------- menu choices ------------------------------- #

        if event == 'About...':
            sg.Popup('About this program', 'Version 0.1a', 'Smart Firefighter Support System (SFSS)', 'Robert Wells', 'Kris Perales', 'Jonathan Naranjo (PM)', 'Summer Abdullah')

        if event == 'Users Guide':

            # ----------- Subprocess to launch browser and take to SFSS github ----------- #

            CHROME = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            FIREFOX = r"C:\Program Files\Mozilla Firefox\firefox.exe"

            github = "https://github.com/sfss-rw/sfss/"

            layout = [[sg.Text('GUIDE: https://github.com/sfss-rw/sfss/', key='_TEXT_')],
                    [sg.Input('https://github.com/sfss-rw/sfss/', do_not_clear=True, key='_URL_')],
                    [sg.Button('Default', bind_return_key=True, focus=True), sg.Button('Chrome'), sg.Button('Firefox')]]

            windowguide = sg.Window("github: User's Guide", layout)

            while True:             # Event Loop
                event, values = windowguide.Read()
                print(event, values)
                if event is None or event == 'Exit':
                    break
                if event == 'Chrome':
                    sp1 = subprocess.Popen([CHROME, values['_URL_']], shell=True, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
                if event == 'Firefox':
                    sp2 = subprocess.Popen([FIREFOX, values['_URL_']], shell=True, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)

                # --------------- Use import webbrowser to open default browser --------------- #

                if event == 'Default':
                    webbrowser.open_new(github)

        elif event == 'Open':
            filename = sg.PopupGetFile('file to open', no_window=True)
            print(filename)

    #while (True):
    #    # This is the code that reads and updates your window
    #    event, values = windowmain.Read(timeout=50)
    #    print(event)
    #    if event in ('Quit', None):
    #        break

# ---------------------------------- way out --------------------------------- #

    while True:
        event, values = windowmain.Read()
        print(event, values)
        if event in(None, 'Exit'):        # always,  always give a way out!
            break

if __name__ == '__main__':
    main()
