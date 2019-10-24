#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Author: 			Robert Wells
# Project Title: 	Smart Firefighter Support System
# FileName: 		sfss with serial_NO COMMAND LINE_with frame.py
# Path: 			c:\Users\wells.robert\Google Drive\School\_2019 Fall\Design 2\GUI\SFSS with Serial\sfss with serial_NO COMMAND LINE_with frame.py
# Project: 			c:\Users\wells.robert\Google Drive\School\_2019 Fall\Design 2\GUI\SFSS with Serial
# Created Date: 	Tuesday, October 15th 2019, 15:01:41 pm
# -----
# Last Modified: 	Monday, October 21st 2019, 18:38:19 pm
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
###

# ---------------------------------- imports --------------------------------- #

import csv
import os
import subprocess
import sys
import webbrowser
import io
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import MaxNLocator
import matplotlib.animation as animation

import time

import random
from random import randrange
from random import randint

from multiprocessing import Process
from multiprocessing import Pipe
import multiprocessing

import argparse
import serial

import PySimpleGUI as sg


#print = sg.Print
#print = sg.PopupScrolled


# * DEPENDENCY: matplotlib 3.0.3
# * [env conda activate seniordesigngui]

# NOTE: p.start breaks the program

# // ? use heartpy to process the data in a loop and then plug into updating graph in new window?
# // * use updating multiline to report hr and movement in text.  button to view updating graph in new window
# // ?NOTE: how about running graphs in browser windows with bokeh
# // NOTE: - ***DONE***create conda environment so that matplotlib works (3.0.3)

# // TODO: add in setup window
    # // TODO: cmd window to print ports, accept user input of correct port, connect
# // TODO:- add menu option to initialize connection to board
    # // TODO: - write function to connect to board
    # TODO: - add updating 'gif' or progress meter for connection
    # TODO: - add indicator for connection on/off

# TODO: add hr sensor's built in graphing if possible
# // TODO: add warning gradients
    # // TODO: yellow for getting close etc

    # // ? how do i make the GUI reload the csv data at xtimes/sec
    # ? should i add a slider to increase/decrease update freq on graphs
# TODO: - add right click menus for (raw data, initialize connection, export photo?)
# // TODO: - sg.popup warnings for data above/below safe values
# // TODO: add led indicators to main page to have 'at a glance' status view


# ---------------------------------------------------------------------------- #
#                                  Definitions                                 #
# ---------------------------------------------------------------------------- #


# --------------------------- connection setup defs -------------------------- #


def porterror():
    sg.PopupError('Something went wrong', 'Make sure you have the correct port selected in the list box')
    #print('wrong port')

def ExecutePortList(command, *args):
    try:
        sp = subprocess.Popen([command, *args], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = sp.communicate()
        if out:
        #     #portlist = out.decode('utf-8')
            print(out.decode("utf-8"))
        if err:
            print(err.decode("utf-8"))
    except:
        sg.PopupError('executeportlist error')

    return (out)

# def ExecutePortConfigure(command, *args):
#     print = window.element('_SETUPOUTPUT_').Update
#     try:
#         sp = subprocess.call([command, *args], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         out, err = sp.communicate()
#         if out:
#             print('\n', out.decode("utf-8"))
#         if err:
#             print(err.decode("utf-8"))

#         return (out, err)
#     except:
#         pass

# def PowershellPortConfigure(portin, *args):
#     try:
#         sp = subprocess.call([command, *args], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         out, err = sp.communicate()
#         ExecutePortConfigure('powershell','[System.IO.Ports.SerialPort]::port= new-Object System.IO.Ports.SerialPort' ,portin)
#         ExecutePortConfigure('powershell','[System.IO.Ports.SerialPort]::port.open()')
#         pout = ExecutePortConfigure('powershell','[System.IO.Ports.SerialPort]::port.readline()')
#         # pout = ExecutePortConfigure('powershell','[System.IO.Ports.SerialPort]::port.readline()')
#         if out:
#                     print('\n', out.decode("utf-8"))
#                     print('\n PowershellPortConfigure pout= ', pout)
#                     print(portin)
#         if err:
#             print(err.decode("utf-8"))

#         return (pout,out, err)
#     except:
#         pass

# ----------------------------- file writing defs ---------------------------- #

# def FileWriter():
#     filein=open('./FF1_testwrite.csv','w')
#     i=0
#     j=0
#     while True:
#         i+=1
#         j+=1
#         t=round(random.uniform(0.7,1.5), 6)
#         #j=i
#         mov=randint(0,1)
#         f=randint(0,1)
#         h=round(random.uniform(0.0,1.0), 6)
#         mot=randrange(0,1)
#         data = filein.write(str(i)+','+'"b'+str(j)+','+str(t)+','+str(mov)+','+str(f)+','+str(h)+','+str(mot)+'"'+'\n')
#         print('wrote data')
#         time.sleep(1)
#         filein.flush()

def csvWriter(portname, filename, ffnumber):
    print('writing data for: ', ffnumber)
    with serial.Serial(portname, 115200, timeout=2) as ser, open(filename, 'w+b') as csv_file:
        # if not ser.is_open:
        #     # ser.open()
        #i=0
        while True:
            #i+=1
            x=ser.readline()
            #print(i, x)
            #data = [i,x]
            data = x
            csv_file.write(data)
            csv_file.flush()
            time.sleep(1)

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

    hr_table_layout = [[sg.Table(values=data, headings=header_list, display_row_numbers=False, auto_size_columns=True, num_rows=min(25,len(data)))]]
    hrwindow = sg.Window('FF1 HR Table', grab_anywhere=False)
    while True:
        event, values = hrwindow.Layout(hr_table_layout).Read()
        if event in(None, 'Exit'):
            break
    pass
    # def hrtable1():
    #     print('hrtable1')
    #     sg.SetOptions(auto_size_buttons=True)
    #     df = pd.read_csv('data1.csv', names = ['time', 'heartrate'], index_col=['time'])
    #     print('file read')
    #     data = df.values.tolist()
    #     header_list = df.iloc[0].tolist()
    #     data = df[1:].values.tolist()


    #     hr_table_layout = [[sg.Table(values=data, headings = header_list, display_row_numbers=False, auto_size_columns=True, num_rows=min(25,len(data)))]]

    #     hrtable = sg.Window('FF1 HR Table', grab_anywhere=False)
    
    #     while True:
    #         event, values = hrtable.Layout(hr_table_layout).Read()
    #         if event in(None, 'Exit'):
    #             break
        #pass
    
    
    # def hrtable1():
    #     hr=pd.read_csv('data1.csv', names=['Time', 'HR'])
    #     if hr == None:
    #         print('error reading file')
    #         sys.exit('Error Reading File')
    #     data = []
    #     header_list = hr.iloc[0].tolist()
    #     if hr is not None:
    #         try:
    #             data = hr.values.tolist()
    #         except:
    #             sg.PopupError('Error Reading File')
    #             pass

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

    mov_table_layout = [[sg.Table(values=data, headings=header_list, display_row_numbers=False,
                            auto_size_columns=True, num_rows=min(25,len(data)))]]

    movwindow = sg.Window('Table', grab_anywhere=False)
    while True:
        event, values = movwindow.Layout(mov_table_layout).Read()
        if event in(None, 'Exit'):
            break
    pass

# ------------------------------- Warning LEDs ------------------------------- #

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

# def animate1(i):
    # fig = plt.figure()
    # ax1 = fig.add_subplot(1,1,1)
    # pullData = open("data1.csv","r").read()
    # dataArray = pullData.split('\n')
    # xar = []
    # yar = []
    # for eachLine in dataArray:
    #     if len(eachLine)>1:
    #         x,y = eachLine.split(',')
    #         xar.append(int(x))
    #         yar.append(int(y))
    # ax1.clear()
    # ax1.plot(xar,yar)
    # ani = animation.FuncAnimation(fig, animate, interval=1000)
    # plt.show()

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

    # P = multiprocessing.Process(target=csvWriter, args=(portToConfig, 'ff1.csv', 'ff1'))
    # P.start()

    # ser = serial.Serial()
    # ser.baudrate=115200
    # ser.timeout=2

# ---------------------------- setup window "feel" --------------------------- #

    sg.ChangeLookAndFeel('Dark2')
    sg.SetOptions(font=('calibri', 12,), element_padding=(1, 1))

# ------------------------- get pathname for logo file ----------------------- #

    dirname, filename = os.path.split(os.path.abspath(__file__))
    pathname = os.path.join(dirname, 'logo.png')

# ------------------------------ Menu Definition ----------------------------- #

    menu_def = [['File', ['Setup Connection::_SETUP_', 'Terminate Connection::_TERMINATE_', 'Save', 'Exit'  ]],
                ['Edit', ['Paste', ['Special', 'Normal', ], 'Undo'], ],
                ['Help', ['Users Guide', 'About...']], ]

# ---------------------------------------------------------------------------- #
#                                 GUI Defintion                                #
# ---------------------------------------------------------------------------- #

# --------------------- define columns to be used in tabs -------------------- #

    comlist = ['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8',
                'COM9', 'COM10', 'COM11', 'COM12', 'COM13', 'COM14', 'COM15']

    cold1_frame_layout = [
        [sg.Output(size=(65, 30), key='_SETUPOUTPUT_',font='Courier 8')],
         #sg.DropDown(comlist, default_value='COM7',enable_events=True, key='_LISTBOX_')],
        [sg.Button('Check COM Ports', pad=(5,2), bind_return_key=False),
         sg.Button('Configure COM Port', pad=(5,2), bind_return_key=False, button_color=('white', 'green')),
         sg.DropDown(comlist, size=(10,1), enable_events=True, readonly=True, key='_LISTBOX_')]
    ]

    cold1 = [[sg.Frame('Setup', layout = cold1_frame_layout, relief=sg.RELIEF_RAISED, element_justification='justified')]]

    cold2_frame_layout = [
        [sg.Text('Firefighter #', justification='center'), sg.Text('Heart Rate', justification='center'),
        sg.Text('Movement', justification='center'), sg.Text('Temperature', justification='center')],
        [sg.Text('Firefighter 1: ', justification='left'), LEDIndicator('_TABDEFAULTFF1HRLED_'),
        sg.Text(' '), LEDIndicator('_TABDEFAULTFF1MOVLED_'), sg.Text(' '), LEDIndicator('_TABDEFAULTFF1TEMPLED_')],
        [sg.Text('Firefighter 2: ', justification='left'), LEDIndicator('_TABDEFAULTFF2HRLED_'),
        sg.Text(' '), LEDIndicator('_TABDEFAULTFF2MOVLED_'), sg.Text(' '), LEDIndicator('_TABDEFAULTFF2TEMPLED_')],
        [sg.Text('Firefighter 3: ', justification='left'), LEDIndicator('_TABDEFAULTFF3HRLED_'),
        sg.Text(' '), LEDIndicator('_TABDEFAULTFF3MOVLED_'), sg.Text(' '), LEDIndicator('_TABDEFAULTFF3TEMPLED_')],
        [sg.Button('Update All', pad=(5,2), key='_UPDATEALL_'), sg.Button('Stop Updates', pad=(5,2), key='_TABDEFAULTSTOPUP_')]
        ]

    cold2 = [[sg.Frame('Firefighter Status', cold2_frame_layout, relief=sg.RELIEF_RAISED, element_justification='justified')]]

    cola1_frame_layout = [
        [sg.Text("Heart Rate", font=('calibri', 12), justification='right'),
        LEDIndicator('_FF1HRLED_'), sg.Output(font=('calibri', 15, 'bold'), key='_HRTEXT1_'),
        sg.Text('Max Recorded HR:', justification='right'), sg.Output(font=('calibri', 15, 'bold'), key='_MAXHRTEXT1_'),
        sg.Button('FF1 RAW Heart Rate', key='_RAWHR1_')]
        ]

    cola1 = [[sg.Frame('Heart Rate', cola1_frame_layout, element_justification='center')]]

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

    colc2 = [[sg.Frame('Movement', colc2_frame_layout)]]

    colc3_frame_layout = [
        [sg.Text('Temperature', font=('calibri', 12), justification='right'),
        LEDIndicator('_FF3TEMPLED_'), sg.Output(font=('calibri', 15, 'bold'), key='_TEMPTEXT3_'),
        sg.Text('Temperature Warnings:', justification='right'), sg.Output(font=('calibri', 15, 'bold'), key='_TEMPWARN3_'),
        sg.Button('FF3 RAW Temp', key='_RAWTEMP3_')]
    ]

    colc3 = [[sg.Frame('Temperature', colc3_frame_layout)]]

# ---------------------------- define tab layouts ---------------------------- #

    tabdefault_layout = [
                    [sg.Text('Welcome to the SFSS!', size=(45, 1), justification='center', font=('calibri', 25, 'bold'))],
                    [sg.Text('Use the tabs above to navigate...', size=(45, 1), justification='center', font=('calibri', 15))],
                    [sg.Column(cold1), sg.Column(cold2)]
    ]

    tab1_layout =  [
                    [sg.Text('Firefighter 1', font=('calibri', 15, 'bold'))],
                    [sg.Column(cola1)],
                    [sg.Column(cola2)],
                    [sg.Column(cola3)],
                    [sg.Button('Update', key='_UPDATETAB1_'), sg.Button('Stop Updates', key='_STOPUPTAB1_'),
                    sg.Button('Show Graph', key='_HRGRAPH1_')]
    ]

    tab2_layout =  [
                    [sg.Text('Firefighter 2', font=('calibri', 15, 'bold'))],
                    [sg.Column(colb1)],
                    [sg.Column(colb2)],
                    [sg.Column(colb3)],
                    [sg.Button('Update', key='_UPDATETAB2_'), sg.Button('Stop Updates', key='_STOPUPTAB2_'),
                    sg.Button('Show Graph', key='_HRGRAPH2_')]
    ]

    tab3_layout =  [
                    [sg.Text('Firefighter 3', font=('calibri', 15, 'bold'))],
                    [sg.Column(colc1)],
                    [sg.Column(colc2)],
                    [sg.Column(colc3)],
                    [sg.Button('Update', key='_UPDATETAB3_'), sg.Button('Stop Updates', key='_STOPUPTAB12'),
                    sg.Button('Show Graph', key='_HRGRAPH3_')]
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
                            auto_size_buttons=True, element_padding=(2,2), grab_anywhere=False,
                            default_button_element_size=(5, 1), resizable=True, element_justification='center',
                            finalize=True).Layout(layout)

# ------------------------------- EXAMPLE DATA ------------------------------- #
    print = windowmain.element('_SETUPOUTPUT_').Update

    while True:
        event, values = windowmain.Read(timeout=100)

        if event == None or event == 'Exit' or event == '_TABDEFAULTSTOPUP_':
            P.terminate()
            Pff1.terminate()
            break

# ------------------------------ showing graphs ------------------------------ #

        if event == '_HRGRAPH1_':
            plt.ion()
            plt.show()
            fig = plt.figure()
            ax1 = fig.add_subplot(1,1,1)
            def animate(i):
                pullData = open("data1.csv","rb").read()
                dataArray = pullData.split('\n')
                xar = []
                yar = []
                for eachLine in dataArray:
                    if len(eachLine)>1:
                        x,y = eachLine.split(',')
                        xar.append(int(x))
                        yar.append(int(y))
                ax1.clear()
                ax1.plot(xar,yar)
            ani = animation.FuncAnimation(fig, animate, interval=1000)
            # plt.ion()
            # plt.show()
            plt.draw()
            plt.pause(.1)
        if event == '_HRGRAPH2_':
            showhr2graph()
        if event == '_HRGRAPH3_':
            showhr3graph()

# ---------------------------------------------------------------------------- #
#                      warning LEDs and outputting status                      #
# ---------------------------------------------------------------------------- #

# ------------------------------- FIREFIGHTER1 ------------------------------- #

    # ------------------------------- updating FF1 ------------------------------- #

        if event == '_UPDATETAB1_' or event =='_UPDATEALL_':

            file_update_ff1 = 1
            ser.open()
            while True:
                event, values = windowmain.Read(timeout=2000)
                if event is None:
                    ser.close()
                    P.terminate()
                    break
                elif event == '_STOPUPTAB1_' or event=='_TABDEFAULTSTOPUP_':
                    file_update_ff1 = not file_update_ff1
                    ser.close()
                    break
                elif file_update_ff1:

                    #P.start()
                    # Pff1 = multiprocessing.Process(target=ff1dataframe)
                    # Pff1.start()
                        # -------- this line opens the csv file and defines the column headers ------- #

                    try:
                        P = multiprocessing.Process(target=csvWriter, args=(ser.name, 'ff1_test_writingfunctions_SFSS.csv', 'ff1'))
                        P.start()

                        df1 = pd.read_csv(r'C:\Users\wells.robert\Google Drive\School\_2019 Fall\Design 2\GUI\ff1_test_writingfunctions.csv', 'r', engine='python', names=['pycntr','microcntr', 'temp', 'movement', 'fall', 'heartrate', 'motor'], index_col=['pycntr'])

                        # ------------ strip the csv of quotes & parse the it into columns ----------- #

                        #df1.iloc[:, [0,-1]] = df1.iloc[:, [0,-1]].apply(lambda x: x.str.strip('"'))
                        maxhr1 = df1['heartrate'].max()
                        last_row_display_HR1 = df1['heartrate'].iloc[-1]
                        #prevhr1 = df1['heartrate'].iloc[-2]
                        windowmain['_HRTEXT1_'].Update(last_row_display_HR1)
                        windowmain['_MAXHRTEXT1_'].Update(maxhr1)

    # --------------    ------------------- FF1heartrate -------------------------------- #

                        if last_row_display_HR1.item() >= 230:
                            SetLED(windowmain, '_FF1HRLED_', 'red' if last_row_display_HR1.all() > 230 else 'red')
                            SetLED(windowmain, '_TABDEFAULTFF1HRLED_', 'red' if last_row_display_HR1.all() > 230 else 'red')
                            sg.PopupAutoClose('WARNING! FF1 High Heart Rate!', auto_close_duration=2, non_blocking=True,
                            background_color='firebrick',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False, location=(600,150))
                        elif last_row_display_HR1.item() <=50:
                            SetLED(windowmain, '_FF1HRLED_', 'red' if last_row_display_HR1.all() <= 50  else 'red')
                            SetLED(windowmain, '_TABDEFAULTFF1HRLED_', 'red' if last_row_display_HR1.all() <= 50 else 'red')
                            sg.PopupAutoClose('WARNING! FF1 Low Heart Rate!', auto_close_duration=2, non_blocking=True,
                            background_color='light blue',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False, location=(600,150))
                        elif last_row_display_HR1.item() > 200 and last_row_display_HR1.item() < 230:
                            SetLED(windowmain, '_FF1HRLED_', 'orange' if last_row_display_HR1.all()  > 200 and last_row_display_HR1.all() <230  else 'orange')
                            SetLED(windowmain, '_TABDEFAULTFF1HRLED_', 'orange' if last_row_display_HR1.all()  > 200 and last_row_display_HR1.all() <230  else 'orange')
                        else:
                            SetLED(windowmain, '_FF1HRLED_', 'green' if last_row_display_HR1.all() < 230 else 'green')
                            SetLED(windowmain, '_TABDEFAULTFF1HRLED_', 'green' if last_row_display_HR1.all() < 230 else 'green')

    # --------------    ------------------- FF1movement --------------------------------- #

                        #df1m = pd.read_csv('data1mov.csv', names=['time', 'movement'], index_col=['time'])
                        #movwarn1 = df1['movement'].max()
                        last_row_display1m = df1['movement'].iloc[-1]
                        windowmain['_MOVTEXT1_'].Update(last_row_display1m)
                        if last_row_display1m.item() < 1:
                            windowmain['_MOVWARN1_'].Update('Low movement')
                            SetLED(windowmain, '_FF1MOVLED_', 'red' if last_row_display1m.all() < 1 else 'red')
                            SetLED(windowmain, '_TABDEFAULTFF1MOVLED_', 'red' if last_row_display1m.all() < 1 else 'red')
                            sg.PopupAutoClose('WARNING! FF1 Low Movement!', auto_close_duration=2, non_blocking=True,
                            background_color='darkorange',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False, location=(750, 150))
                        else:
                            windowmain['_MOVWARN1_'].Update('No warnings')
                            SetLED(windowmain, '_FF1MOVLED_', 'green' if last_row_display1m.all() > 1 else 'green')
                            SetLED(windowmain, '_TABDEFAULTFF1MOVLED_', 'green' if last_row_display1m.all() > 1 else 'green')
    
    # --------------    ------------------ FF1temperature ------------------------------- #

                        last_row_display1t = df1['temp'].iloc[-1]
                        windowmain['_TEMPTEXT1_'].Update(last_row_display1t)
                        if last_row_display1t.item() >= 500:
                            windowmain['_TEMPWARN1_'].Update('High Temperature')
                            SetLED(windowmain, '_FF1TEMPLED_', 'darkorange' if last_row_display1t.all() > 500 else 'red')
                            SetLED(windowmain, '_TABDEFAULTFF1TEMPLED_', 'red' if last_row_display1t.all() > 500 else 'red')
                            sg.PopupAutoClose('WARNING! FF1 High Temperature!', auto_close_duration=2, non_blocking=True,
                            background_color='orangered',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False, location=(450,150))
                        elif last_row_display1t.item() > 400 and last_row_display1t.item() < 500:
                            windowmain['_TEMPWARN1_'].Update('Moderate Temperature')
                            SetLED(windowmain, '_FF1TEMPLED_', 'orange' if last_row_display1t.all()  > 400 and last_row_display1t.all() < 500  else 'orange')
                            SetLED(windowmain, '_TABDEFAULTFF1TEMPLED_', 'orange' if last_row_display1t.all()  > 400 and last_row_display1t.all() < 500  else 'orange')
                        else:
                            windowmain['_TEMPWARN1_'].Update('No warnings')
                            SetLED(windowmain, '_FF1TEMPLED_', 'green' if last_row_display1t.all() < 500 else 'green')
                            SetLED(windowmain, '_TABDEFAULTFF1TEMPLED_', 'green' if last_row_display1t.all() < 500 else 'green')
                    except:
                        sg.PopupError('Something Went Wrong. [ff1 data]')
                #hr_warning(hrwarn)

# ------------------------------- FIREFIGHTER2 ------------------------------- #

    # ------------------------------- updating FF2 ------------------------------- #

        if event == '_UPDATETAB2_' or event =='_UPDATEALL_':
            file_update_ff2 = 1

            while True:
                event, values = windowmain.Read(timeout=500)
                if event is None:
                    break
                elif event == '_STOPUPTAB2_' or event=='_TABDEFAULTSTOPUP_':
                    file_update_ff2 = not file_update_ff2
                    break
                elif file_update_ff2:
                    df2 = pd.read_csv('data2.csv', names=['time', 'heartrate'], index_col=['time'])
                    maxhr2 = df2['heartrate'].max()
                    last_row_display2 = df2['heartrate'].iloc[-1]
                    windowmain['_HRTEXT2_'].Update(last_row_display2)
                    windowmain['_MAXHRTEXT2_'].Update(maxhr2)

    # --------------------------------- FF2heartrate -------------------------------- #


                    if last_row_display2.item() >= 230:
                        SetLED(windowmain, '_FF2HRLED_', 'red' if last_row_display2.all() > 230 else 'red')
                        SetLED(windowmain, '_TABDEFAULTFF2HRLED_', 'red' if last_row_display2.all() > 230 else 'red')
                        sg.PopupAutoClose('WARNING! HEART RATE IS HIGH!', auto_close_duration=3, non_blocking=True,
                        background_color='firebrick',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False, location=(600,150))
                    elif last_row_display2.item() <=50:
                        SetLED(windowmain, '_FF2HRLED_', 'red' if last_row_display2.all() <= 50  else 'red')
                        SetLED(windowmain, '_TABDEFAULTFF2HRLED_', 'red' if last_row_display2.all() <= 50 else 'red')
                        sg.PopupAutoClose('WARNING! HEART RATE IS LOW!', auto_close_duration=3, non_blocking=True,
                        background_color='lightblue',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False, location=(600,150))
                    elif last_row_display2.item() > 200 and last_row_display2.item() < 230:
                        SetLED(windowmain, '_FF2HRLED_', 'orange' if last_row_display2.all()  > 200 and last_row_display2.all() <230  else 'orange')
                        SetLED(windowmain, '_TABDEFAULTFF2HRLED_', 'orange' if last_row_display2.all()  > 200 and last_row_display2.all() <230  else 'orange')
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
                        background_color='darkorange',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False, location=(750,150))
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
                        background_color='orangered',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False, location=(450,150))
                    elif last_row_display2t.item() > 400 and last_row_display2t.item() < 500:
                        windowmain['_TEMPWARN2_'].Update('Moderate Temperature')
                        SetLED(windowmain, '_FF2TEMPLED_', 'orange' if last_row_display2t.all()  > 400 and last_row_display2t.all() < 500  else 'orange')
                        SetLED(windowmain, '_TABDEFAULTFF2TEMPLED_', 'orange' if last_row_display2t.all()  > 400 and last_row_display2t.all() < 500  else 'orange')
                    else:
                        windowmain['_TEMPWARN2_'].Update('No warnings')
                        SetLED(windowmain, '_FF2TEMPLED_', 'green' if last_row_display2t.all() < 500 else 'green')
                        SetLED(windowmain, '_TABDEFAULTFF2TEMPLED_', 'green' if last_row_display2t.all() < 500 else 'green')

# ------------------------------- FIREFIGHTER3 ------------------------------- #

    # ------------------------------- updating FF3 ------------------------------- #

        if event == '_UPDATETAB3_' or event =='_UPDATEALL_':

            file_update_ff3 = 1

            while True:
                event, values = windowmain.Read(timeout=500)
                if event is None:
                    break
                elif event == '_STOPUPTAB2_' or event=='_TABDEFAULTSTOPUP_':
                    file_update_ff3 = not file_update_ff3
                    break
                elif file_update_ff3:
                    df3 = pd.read_csv('data3.csv', names=['time', 'heartrate'], index_col=['time'])
                    maxhr3 = df3['heartrate'].max()
                    last_row_display3 = df3['heartrate'].iloc[-1]
                    windowmain['_HRTEXT3_'].Update(last_row_display3)
                    windowmain['_MAXHRTEXT3_'].Update(maxhr3)

    # ------------------------------- FF3heartrate ------------------------------- #

                    if last_row_display3.item() >= 230:
                        SetLED(windowmain, '_FF3HRLED_', 'red' if last_row_display3.all() > 230  else 'red')
                        SetLED(windowmain, '_TABDEFAULTFF3HRLED_', 'red' if last_row_display3.all() > 230 else 'red')
                        sg.PopupAutoClose('WARNING! HEART RATE IS HIGH!', auto_close_duration=3, non_blocking=True,
                        background_color='firebrick',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False, location=(600,150))
                    elif last_row_display3.item() <=50:
                        SetLED(windowmain, '_FF3HRLED_', 'red' if last_row_display3.all() <= 50  else 'red')
                        SetLED(windowmain, '_TABDEFAULTFF3HRLED_', 'red' if last_row_display3.all() <= 50 else 'red')
                        sg.PopupAutoClose('WARNING! HEART RATE IS LOW!', auto_close_duration=3, non_blocking=True,
                        background_color='lightblue',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False, location=(600,150))
                    elif last_row_display3.item() > 200 and last_row_display3.item() < 230:
                        SetLED(windowmain, '_FF3HRLED_', 'orange' if last_row_display3.all()  > 200 and last_row_display3.all() <230  else 'orange')
                        SetLED(windowmain, '_TABDEFAULTFF3HRLED_', 'orange' if last_row_display3.all()  > 200 and last_row_display3.all() <230  else 'orange')
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
                        background_color='darkorange',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False, location=(750,150))
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
                        background_color='orangered',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False, location=(450,150))
                    elif last_row_display3t.item() > 400 and last_row_display3t.item() < 500:
                        windowmain['_TEMPWARN3_'].Update('Moderate Temperature')
                        SetLED(windowmain, '_FF3TEMPLED_', 'orange' if last_row_display3t.all()  > 400 and last_row_display3t.all() < 500  else 'orange')
                        SetLED(windowmain, '_TABDEFAULTFF3TEMPLED_', 'orange' if last_row_display3t.all()  > 400 and last_row_display3t.all() < 500  else 'orange')
                    else:
                        windowmain['_TEMPWARN3_'].Update('No warnings')
                        SetLED(windowmain, '_FF3TEMPLED_', 'green' if last_row_display3t.all() < 500 else 'green')
                        SetLED(windowmain, '_TABDEFAULTFF3TEMPLED_', 'green' if last_row_display3t.all() < 500 else 'green')

# ----------------------------------- setup ---------------------------------- #

        if event == 'Check COM Ports':
            foo = ExecutePortList('powershell', '[System.IO.Ports.SerialPort]::getportnames()')
            print("Searching... \n ... \n >>> Your COM port is: {} \n >>> Select it from the ComboBox below,\n >>> then click 'Configure COM Port'".format(foo.decode("utf-8")))
            windowmain.Refresh()

        if event == 'Configure COM Port':
            ser = serial.Serial()
            ser.baudrate=115200
            ser.timeout=2
            try:
                portToConfig = values['_LISTBOX_']
                print('The port you have selected is: ', portToConfig)
                ser.port = portToConfig
        # ------------------------------ print port info ----------------------------- #
                ser.open()
                print('The port opened is: {} \n The Baudrate is: {} \n The Bytesize is: {} \n The Parity is: {} \n Is it readable?: {} \n Is the port really open??: {} \n SUCESS!! \n You have been configured to work with the SFSS!'.format(ser.name,ser.baudrate,ser.bytesize,ser.parity,ser.readable(),ser.is_open))
                ser.close()
            except:
                porterror()


        # print('\t >>> Configuring', ser.name, '\n')
        # print('\t >>> The port opened is:\t\t\t\t ', ser.name)
        # print('\t >>> The baudrate is:\t\t\t\t ', ser.baudrate)
        # print('\t >>> The bytesize is:\t\t\t\t ', ser.bytesize)
        # print('\t >>> The parity is:\t\t\t\t ', ser.parity)
        # print('\t >>> Is it readable?:\t\t\t\t ', ser.readable())
        # print('\t >>> Is it writable?:\t\t\t\t ', ser.writable())
        # print('\t >>> Is the port really open?:\t\t ', ser.is_open, '\n')
        # print('\n\t >>> SUCESS!')
        # print('\t >>> Your COM Port has been configured to work with the SFSS!')




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


# ---------------------------------- way out --------------------------------- #

    # while True:
    #     event, values = windowmain.Read()
    #     print(event, values)
    #     if event in(None, 'Exit'):        # always,  always give a way out!
    #         break

if __name__ == '__main__':
    main()
