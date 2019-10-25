

# // NOTE: trying multilines in tabs instead of output
# // NOTE: for this to work, need to change 'reroutestdout' property of the output element
# // NOTE: also change the "print=update..."

# NOTE: motor status is True all the time? check into the df

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
import serial.tools.list_ports

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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
#                                    GLOBALS                                   #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

# serial globals
BAUDRATE=115200
TIMEOUT=2
ser=serial.Serial()



# ---------------------------------------------------------------------------- #
#                                  Definitions                                 #
# ---------------------------------------------------------------------------- #


# --------------------------- connection setup defs -------------------------- #

def statusWarningPopup(ffnum, status, color):
    # sg.PopupAutoClose('{} Warning for {}'.format(status,ffnum), auto_close_duration=2, non_blocking=True,
    # background_color= color, grab_anywhere=True, keep_on_top=False, location=(-1,-1))
    sg.popup_no_wait('{} Warning for {}'.format(status,ffnum), auto_close=True, auto_close_duration=1, non_blocking=True,
    background_color= color, grab_anywhere=True, keep_on_top=False, location=(-1,-1))


def dataError(ffnum):
    sg.PopupAutoClose('Something went wrong', "There was an error with {}'s data".format(ffnum), non_blocking=True, auto_close_duration=2)

def porterror():
    sg.PopupAutoClose('Something went wrong', 'Make sure you have the correct port selected in the list box', non_blocking=True, auto_close_duration=2)

# NOTE: leaving this here just in case
    # def ExecutePortList(command, *args):
    #     """executes commands through cmd.exe, used here to call powershell to get a list of available COM ports

    
    #     Args:
    #         command (string): [command to be passed to cmd.exe]
    #     """
    #     try:
    #         sp = subprocess.Popen([command, *args], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #         out, err = sp.communicate()
    #         if out:
    #         #     #portlist = out.decode('utf-8')
    #             print(out.decode("utf-8"))
    #         if err:
    #             print(err.decode("utf-8"))
    #     except:
    #         sg.PopupError('executeportlist error')
    
    #     return (out)

def ExecutePortList():
    """
    vid and pid for the XBee S2C are stored here.
    if this model is used, configuration should be easier, requiring less user input
    if a different model is used, the user would need to figure out which COM port their
    device is using (probably using cmd.exe and switch it manually with the combobox

    """
    ## XBee S2C device vendor and part numbers
    vid="0403"
    pid="6015"
    #sernum="DN069Y7GA"
    device_found = False
    my_com_port = None
    description = None
    ports = list(serial.tools.list_ports.comports())

    for p in ports:
        try:
            if vid and pid in p.hwid:
                description = p.hwid
                my_com_port = p.device
                device_found = True

                return(my_com_port, description, device_found)
        except:
            print('The SFSS device wasnt found :(')
            print('We use the Vendor Number and Part Number to locate it.')
            print('Are you using the original device [XBee S2C]?')
            print("If not, refer to 'About'-'Help' from the menu above")
            break
    # print(my_comm_port)

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

def serialToList(ser):
    
    decoded_parsed_rawdata = ser.readline().decode('utf-8').split()
    return(decoded_parsed_rawdata)

def listToDataFrame(datalist):
    header = ['microcntr', 'temp', 'movement', 'fall', 'heartrate', 'motor']
    bool_columns = ['motor']
    float_columns = ['temp', 'movement', 'fall', 'heartrate']
    dataframe = pd.DataFrame([datalist], columns = header, index=None)
    dataframe[bool_columns] = dataframe[bool_columns].astype(bool)
    dataframe[float_columns] = dataframe[float_columns].astype(float)
    return(dataframe)

def logAllData(dataframe, ffnumber):
    dataframe.to_csv(ffnumber, sep=',', float_format='%04f', mode='a', header=None)

# def csvWriter(portname, filename, ffnumber):

#     print('writing data for: ', ffnumber)
#     with serial.Serial(portname, 115200, timeout=2) as ser, open(filename, 'w+b') as csv_file:
#         # if not ser.is_open:
#         #     # ser.open()
#         #i=0
#         while True:
#             #i+=1
#             x=ser.readline()
#             #print(i, x)
#             #data = [i,x]
#             data = x
#             csv_file.write(data)
#             csv_file.flush()
#             time.sleep(1)

def createLogFile(filename):
    """creates an initial log file, and places "logheader" at the top

    Args:
        filename (string): name for the file
    """
    # setting header for the log csv
    logheader = ['i', 'microcntr', 'temp', 'movement', 'fall', 'heartrate', 'motor']
    with open(filename,'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(logheader)

        #print('done with header')
        
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

def SetLED(window, key, color):
    graph = window.FindElement(key)
    graph.Erase()
    graph.DrawCircle((0, 0), 20, fill_color=color, line_color=color)

def setLEDStatus(w, fftabkey, maintabkey, color):
    SetLED(w, fftabkey, color)
    SetLED(w, maintabkey, color)
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

    comlist = ['-------', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8',
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
        [sg.Button('Update All', pad=(5,2), key='_UPDATEALL_'), sg.Button('Stop Updates', pad=(5,2), key='_TABDEFAULTSTOPUP_'),
         sg.Checkbox('Enable PopUps', default = True, enable_events = True, key='_TOGGLEPOPUPALL_')]
        ]

    cold2 = [[sg.Frame('Firefighter Status', cold2_frame_layout, relief=sg.RELIEF_RAISED, element_justification='justified')]]

    cola1_frame_layout = [
        [sg.Text("Heart Rate", font=('calibri', 12), justification='right'),
        LEDIndicator('_FF1HRLED_'), sg.Multiline(font=('calibri', 15, 'bold'), disabled=True,  key='_HRTEXT1_'),
        sg.Text('Max Recorded HR:', justification='right'), sg.Multiline(font=('calibri', 15, 'bold'), disabled=True,  key='_MAXHRTEXT1_'),
        sg.Button('FF1 RAW Heart Rate', key='_RAWHR1_')]
        ]

    cola1 = [[sg.Frame('Heart Rate', cola1_frame_layout, element_justification='center')]]

    cola2_frame_layout = [
        [sg.Text('Movement', font=('calibri', 12), justification='right'),
        LEDIndicator('_FF1MOVLED_'), sg.Multiline(font=('calibri', 15, 'bold'), disabled=True,  key='_MOVTEXT1_'),
        sg.Text('Movement Warnings:', justification='right'), sg.Multiline(font=('calibri', 15, 'bold'), disabled=True,  key='_MOVWARN1_'),
        sg.Button('FF1 RAW Movement', key='_RAWMOV1_')]
    ]

    cola2 = [[sg.Frame('Movement', cola2_frame_layout)]]

    cola3_frame_layout = [
        [sg.Text('Temperature', font=('calibri', 12), justification='right'),
        LEDIndicator('_FF1TEMPLED_'), sg.Multiline(font=('calibri', 15, 'bold'), disabled=True,  key='_TEMPTEXT1_'),
        sg.Text('Temperature Warnings:', justification='right'), sg.Multiline(font=('calibri', 15, 'bold'), disabled=True,  key='_TEMPWARN1_'),
        sg.Button('FF1 RAW Temperature', key='_RAWTEMP1_')]
    ]

    cola3 = [[sg.Frame('Temperature', cola3_frame_layout)]]


    colb1_frame_layout = [
        [sg.Text("Heart Rate", font=('calibri', 12, 'bold'), justification='right'),
        LEDIndicator('_FF2HRLED_'), sg.Multiline(font=('calibri', 15, 'bold'), disabled=True,  key='_HRTEXT2_'),
        sg.Text('Max Recorded HR:', justification='right'), sg.Multiline(font=('calibri', 15, 'bold'), disabled=True,  key='_MAXHRTEXT2_'),
        sg.ReadButton('FF2 RAW Heart Rate', key='_RAWHR2_')]
    ]

    colb1 = [[sg.Frame('Heart Rate', colb1_frame_layout)]]

    colb2_frame_layout = [
        [sg.Text('Movement', font=('calibri', 12), justification='right'),
        LEDIndicator('_FF2MOVLED_'), sg.Multiline(font=('calibri', 15, 'bold'), disabled=True,  key='_MOVTEXT2_'),
        sg.Text('Movement Warnings:', justification='right'), sg.Multiline(font=('calibri', 15, 'bold'), disabled=True,  key='_MOVWARN2_'),
        sg.Button('FF2 RAW Movement', key='_RAWMOV2_')]
    ]

    colb2 = [[sg.Frame('Movement', colb2_frame_layout)]]

    colb3_frame_layout = [
        [sg.Text('Temperature', font=('calibri', 12), justification='right'),
        LEDIndicator('_FF2TEMPLED_'), sg.Multiline(font=('calibri', 15, 'bold'), disabled=True,  key='_TEMPTEXT2_'),
        sg.Text('Temperature Warnings:', justification='right'), sg.Multiline(font=('calibri', 15, 'bold'), disabled=True,  key='_TEMPWARN2_'),
        sg.Button('FF2 RAW Temp', key='_RAWTEMP2_')]
    ]

    colb3 = [[sg.Frame('Temperature', colb3_frame_layout)]]

    colc1_frame_layout = [
        [sg.Text("Heart Rate", font=('calibri', 12), justification='right'),
        LEDIndicator('_FF3HRLED_'), sg.Multiline(font=('calibri', 15, 'bold'), disabled=True,  key='_HRTEXT3_'),
        sg.Text('Max Recorded HR:', justification='right'), sg.Multiline(font=('calibri', 15, 'bold'), disabled=True,  key='_MAXHRTEXT3_'),
        sg.ReadButton('FF3 RAW Heart Rate', key='_RAWHR3_')]
    ]

    colc1 = [[sg.Frame('Heart Rate', colc1_frame_layout)]]

    colc2_frame_layout = [
        [sg.Text('Movement', font=('calibri', 12), justification='right'),
        LEDIndicator('_FF3MOVLED_'), sg.Multiline(font=('calibri', 15, 'bold'), disabled=True,  key='_MOVTEXT3_'),
        sg.Text('Movement Warnings:', justification='right'), sg.Multiline(font=('calibri', 15, 'bold'), disabled=True,  key='_MOVWARN3_'),
        sg.Button('FF3 RAW Movement', key='_RAWMOV3_')]
    ]

    colc2 = [[sg.Frame('Movement', colc2_frame_layout)]]

    colc3_frame_layout = [
        [sg.Text('Temperature', font=('calibri', 12), justification='right'),
        LEDIndicator('_FF3TEMPLED_'), sg.Multiline(font=('calibri', 15, 'bold'), disabled=True,  key='_TEMPTEXT3_'),
        sg.Text('Temperature Warnings:', justification='right'), sg.Multiline(font=('calibri', 15, 'bold'), disabled=True,  key='_TEMPWARN3_'),
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
                    [sg.Column(cola1,justification='center', element_justification='center')],
                    [sg.Column(cola2,justification='center', element_justification='center')],
                    [sg.Column(cola3,justification='center', element_justification='center')],
                    [sg.Button('Update', key='_UPDATETAB1_'), sg.Button('Stop Updates', key='_STOPUPTAB1_'),
                    sg.Button('Show Graph', key='_HRGRAPH1_')]
    ]

    tab2_layout =  [
                    [sg.Text('Firefighter 2', font=('calibri', 15, 'bold'))],
                    [sg.Column(colb1, justification='center', element_justification='center')],
                    [sg.Column(colb2, justification='center', element_justification='center')],
                    [sg.Column(colb3, justification='center', element_justification='center')],
                    [sg.Button('Update', key='_UPDATETAB2_'), sg.Button('Stop Updates', key='_STOPUPTAB2_'),
                    sg.Button('Show Graph', key='_HRGRAPH2_')]
    ]

    tab3_layout =  [
                    [sg.Text('Firefighter 3', font=('calibri', 15, 'bold'))],
                    [sg.Column(colc1,justification='center', element_justification='center')],
                    [sg.Column(colc2,justification='center', element_justification='center')],
                    [sg.Column(colc3,justification='center', element_justification='center')],
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

    window = sg.Window("Smart Firefighter Support System", default_element_size=(20, 5), auto_size_text=False,
                            auto_size_buttons=True, element_padding=(2,2), grab_anywhere=False,
                            default_button_element_size=(5, 1), resizable=True, element_justification='center',
                            finalize=True).Layout(layout)

# -------------------------------- EVENT LOOP -------------------------------- #
    ff1_list = []
    ff2_list = []
    ff3_list = []

    createLogFile('FF1.log')
    createLogFile('FF2.log')
    createLogFile('FF3.log')

    while True:
        event, values = window.Read()
        popups_enabled = values['_TOGGLEPOPUPALL_']
        #
        # if values['_TOGGLEPOPUPALL_'] == False:
        #     popups_enabled
        if event == None or event == 'Exit':
            if ser.is_open:
                ser.close()
            #P.terminate()
            #Pff1.terminate()
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
            try:
                file_update_ff1 = 1
                ser.open()
            except:
                sg.PopupError('make sure you set up the COM port first')
                continue

            while True:
                event, values = window.Read(timeout=200)

                if event is None:
                    ser.close()
                    break
                elif event == '_STOPUPTAB1_' or event=='_TABDEFAULTSTOPUP_':
                    file_update_ff1 = not file_update_ff1
                    ser.close()
                    break
                elif file_update_ff1:
                    popups_enabled = values['_TOGGLEPOPUPALL_']

                    try:
                        time.sleep(.1)
                        # createLogFile('ff1.log')
                        ff1_list = serialToList(ser)
                        df1 = listToDataFrame(ff1_list)
                        logAllData(df1, 'ff1.log')


                        # ------------ strip the csv of quotes & parse the it into columns ----------- #

                        last_row_display_1h = df1['heartrate'].iloc[0]
                        window['_HRTEXT1_'].Update(df1['heartrate'].iloc[0])
                        if  values['_HRTEXT1_'] > values['_MAXHRTEXT1_']:
                            window['_MAXHRTEXT1_'].Update(values['_HRTEXT1_'])
                        else:
                            pass

    # --------------    ------------------- FF1heartrate -------------------------------- #

                        FF1_HR_UPPER = 0.7
                        FF1_HR_LOWER = 0.5
                        FF1_HR_CAUTION = 0.65

                        if  last_row_display_1h.item() <= FF1_HR_LOWER or last_row_display_1h.item() >= FF1_HR_UPPER:
                            setLEDStatus(window, '_FF1HRLED_', '_TABDEFAULTFF1HRLED_', 'red')

                            if not popups_enabled:
                                pass
                            else:
                                statusWarningPopup('FF1','Heart Rate', 'firebrick')

                        elif FF1_HR_CAUTION < last_row_display_1h.item() < FF1_HR_UPPER:
                            setLEDStatus(window, '_FF1HRLED_', '_TABDEFAULTFF1HRLED_', 'orange')

                        else:
                            setLEDStatus(window, '_FF1HRLED_', '_TABDEFAULTFF1HRLED_', 'green')

    # --------------    ------------------- FF1movement --------------------------------- #

                        last_row_display_1m = df1['movement'].iloc[0]
                        window['_MOVTEXT1_'].Update(df1['movement'].iloc[0])

                        FF1_MOV_UPPER = 9.8
                        FF1_MOV_LOWER = 0.1
                        #FF1_MOV_CAUTION = 0.65

                        if  last_row_display_1m.item() <= FF1_MOV_LOWER or last_row_display_1m.item() >= FF1_MOV_UPPER:
                            setLEDStatus(window, '_FF1MOVLED_', '_TABDEFAULTFF1MOVLED_', 'red')
                            window['_MOVWARN1_'].Update('Low movement')

                            if not popups_enabled:
                                pass
                            else:
                                statusWarningPopup('FF1','Movement', 'darkorange')

                                # time.sleep(.1)

                        # commented out in case we need to establish movement thresholds
                        # elif FF1_HR_CAUTION < last_row_display_m1.item() < FF1_HR_UPPER:
                        #     setLEDStatus(window, '_FF1MOVLED_', '_TABDEFAULTFF1MOVLED_', 'orange')

                        else:
                            setLEDStatus(window, '_FF1MOVLED_', '_TABDEFAULTFF1MOVLED_', 'green')

    # --------------    ------------------ FF1temperature ------------------------------- #


                        last_row_display_1t = df1['temp'].iloc[-1]
                        window['_TEMPTEXT1_'].Update(last_row_display_1t)

                        FF1_TEMP_UPPER = 500
                        #FF1_TEMP_LOWER = 10
                        FF1_TEMP_CAUTION = 400

                        if  last_row_display_1t.item() > FF1_TEMP_UPPER:
                            setLEDStatus(window, '_FF1TEMPLED_', '_TABDEFAULTFF1TEMPLED_', 'red')
                            window['_TEMPWARN1_'].Update('High Temperature')

                            if not popups_enabled:
                                pass
                            else:
                                statusWarningPopup('FF1','Temperature', 'orangered')

                        elif FF1_TEMP_CAUTION < last_row_display_1t.all() < FF1_TEMP_UPPER:
                            setLEDStatus(window, '_FF1TEMPLED_', '_TABDEFAULTFF1TEMPLED_', 'orange')
                            window['_TEMPWARN1_'].Update('Moderate Temperature')

                        else:
                            setLEDStatus(window, '_FF1TEMPLED_', '_TABDEFAULTFF1TEMPLED_', 'green')
                            window['_TEMPWARN1_'].Update('No warnings')

                    except:
                        # if not dataError:
                        dataError('FF1')
                #ser.flushInput()
                # time.sleep(.1)
# ------------------------------- FIREFIGHTER2 ------------------------------- #

    # ------------------------------- updating FF2 ------------------------------- #

        if event == '_UPDATETAB2_' or event =='_UPDATEALL_':
            file_update_ff2 = 1

            while True:
                event, values = window.Read(timeout=500)
                if event is None:
                    break
                elif event == '_STOPUPTAB2_' or event=='_TABDEFAULTSTOPUP_':
                    file_update_ff2 = not file_update_ff2
                    break
                elif file_update_ff2:
                    df2 = pd.read_csv('data2.csv', names=['time', 'heartrate'], index_col=['time'])
                    maxhr2 = df2['heartrate'].max()
                    last_row_display2 = df2['heartrate'].iloc[-1]
                    window['_HRTEXT2_'].Update(last_row_display2)
                    window['_MAXHRTEXT2_'].Update(maxhr2)

    # --------------------------------- FF2heartrate -------------------------------- #


                    if last_row_display2.item() >= 230:
                        SetLED(window, '_FF2HRLED_', 'red' if last_row_display2.all() > 230 else 'red')
                        SetLED(window, '_TABDEFAULTFF2HRLED_', 'red' if last_row_display2.all() > 230 else 'red')
                        sg.PopupAutoClose('WARNING! HEART RATE IS HIGH!', auto_close_duration=3, non_blocking=True,
                        background_color='firebrick',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False, location=(600,150))
                    elif last_row_display2.item() <=50:
                        SetLED(window, '_FF2HRLED_', 'red' if last_row_display2.all() <= 50  else 'red')
                        SetLED(window, '_TABDEFAULTFF2HRLED_', 'red' if last_row_display2.all() <= 50 else 'red')
                        sg.PopupAutoClose('WARNING! HEART RATE IS LOW!', auto_close_duration=3, non_blocking=True,
                        background_color='lightblue',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False, location=(600,150))
                    elif last_row_display2.item() > 200 and last_row_display2.item() < 230:
                        SetLED(window, '_FF2HRLED_', 'orange' if last_row_display2.all()  > 200 and last_row_display2.all() <230  else 'orange')
                        SetLED(window, '_TABDEFAULTFF2HRLED_', 'orange' if last_row_display2.all()  > 200 and last_row_display2.all() <230  else 'orange')
                    else:
                        SetLED(window, '_FF2HRLED_', 'green' if last_row_display2.all() < 230 else 'green')
                        SetLED(window, '_TABDEFAULTFF2HRLED_', 'green' if last_row_display2.all() < 230 else 'green')

    # --------------------------------- FF2movement --------------------------------- #
    
                    df2m = pd.read_csv('data2mov.csv', names=['time', 'movement'], index_col=['time'])
                    #movwarn1 = df1['movement'].max()
                    last_row_display2m = df2m['movement'].iloc[-1]
                    window['_MOVTEXT2_'].Update(last_row_display2m)
                    if last_row_display2m.item() < 1:
                        window['_MOVWARN2_'].Update('Low movement')
                        SetLED(window, '_FF2MOVLED_', 'red' if last_row_display2m.all() < 1 else 'red')
                        SetLED(window, '_TABDEFAULTFF2MOVLED_', 'red' if last_row_display2.all() < 1 else 'red')
                        sg.PopupAutoClose('WARNING! LOW MOVEMENT DETECTED!', auto_close_duration=3, non_blocking=True,
                        background_color='darkorange',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False, location=(750,150))
                    else:
                        window['_MOVWARN2_'].Update('No warnings')
                        SetLED(window, '_FF2MOVLED_', 'green' if last_row_display2m.all() > 1 else 'green')
                        SetLED(window, '_TABDEFAULTFF2MOVLED_', 'green' if last_row_display2m.all() > 1 else 'green')
    
    # -------------------------------- FF2temperature ------------------------------- #
    
                    df2t = pd.read_csv('data2temp.csv', names=['time', 'temp'], index_col=['time'])
                    #movwarn2 = df2['movement'].max()
                    last_row_display2t = df2t['temp'].iloc[-1]
                    window['_TEMPTEXT2_'].Update(last_row_display2t)
                    if last_row_display2t.item() > 500:
                        window['_TEMPWARN2_'].Update('High Temperature')
                        SetLED(window, '_FF2TEMPLED_', 'red' if last_row_display2t.all() > 500 else 'red')
                        SetLED(window, '_TABDEFAULTFF2TEMPLED_', 'red' if last_row_display2.all() > 500 else 'red')
                        sg.PopupAutoClose('WARNING! HIGH TEMPERATURE DETECTED!', auto_close_duration=3, non_blocking=True,
                        background_color='orangered',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False, location=(450,150))
                    elif last_row_display2t.item() > 400 and last_row_display2t.item() < 500:
                        window['_TEMPWARN2_'].Update('Moderate Temperature')
                        SetLED(window, '_FF2TEMPLED_', 'orange' if last_row_display2t.all()  > 400 and last_row_display2t.all() < 500  else 'orange')
                        SetLED(window, '_TABDEFAULTFF2TEMPLED_', 'orange' if last_row_display2t.all()  > 400 and last_row_display2t.all() < 500  else 'orange')
                    else:
                        window['_TEMPWARN2_'].Update('No warnings')
                        SetLED(window, '_FF2TEMPLED_', 'green' if last_row_display2t.all() < 500 else 'green')
                        SetLED(window, '_TABDEFAULTFF2TEMPLED_', 'green' if last_row_display2t.all() < 500 else 'green')

# ------------------------------- FIREFIGHTER3 ------------------------------- #

    # ------------------------------- updating FF3 ------------------------------- #

        if event == '_UPDATETAB3_' or event =='_UPDATEALL_':

            file_update_ff3 = 1

            while True:
                event, values = window.Read(timeout=500)
                if event is None:
                    break
                elif event == '_STOPUPTAB2_' or event=='_TABDEFAULTSTOPUP_':
                    file_update_ff3 = not file_update_ff3
                    break
                elif file_update_ff3:
                    df3 = pd.read_csv('data3.csv', names=['time', 'heartrate'], index_col=['time'])
                    maxhr3 = df3['heartrate'].max()
                    last_row_display3 = df3['heartrate'].iloc[-1]
                    window['_HRTEXT3_'].Update(last_row_display3)
                    window['_MAXHRTEXT3_'].Update(maxhr3)

    # ------------------------------- FF3heartrate ------------------------------- #

                    if last_row_display3.item() >= 230:
                        SetLED(window, '_FF3HRLED_', 'red' if last_row_display3.all() > 230  else 'red')
                        SetLED(window, '_TABDEFAULTFF3HRLED_', 'red' if last_row_display3.all() > 230 else 'red')
                        sg.PopupAutoClose('WARNING! HEART RATE IS HIGH!', auto_close_duration=3, non_blocking=True,
                        background_color='firebrick',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False, location=(600,150))
                    elif last_row_display3.item() <=50:
                        SetLED(window, '_FF3HRLED_', 'red' if last_row_display3.all() <= 50  else 'red')
                        SetLED(window, '_TABDEFAULTFF3HRLED_', 'red' if last_row_display3.all() <= 50 else 'red')
                        sg.PopupAutoClose('WARNING! HEART RATE IS LOW!', auto_close_duration=3, non_blocking=True,
                        background_color='lightblue',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False, location=(600,150))
                    elif last_row_display3.item() > 200 and last_row_display3.item() < 230:
                        SetLED(window, '_FF3HRLED_', 'orange' if last_row_display3.all()  > 200 and last_row_display3.all() <230  else 'orange')
                        SetLED(window, '_TABDEFAULTFF3HRLED_', 'orange' if last_row_display3.all()  > 200 and last_row_display3.all() <230  else 'orange')
                    else:
                        SetLED(window, '_FF3HRLED_', 'green' if last_row_display3.all() < 230 else 'green')
                        SetLED(window, '_TABDEFAULTFF3HRLED_', 'green' if last_row_display3.all() < 230 else 'green')

    # --------------------------------- FF3movement --------------------------------- #
        
                    df3m = pd.read_csv('data3mov.csv', names=['time', 'movement'], index_col=['time'])
                    #movwarn1 = df1['movement'].max()
                    last_row_display3m = df3m['movement'].iloc[-1]
                    window['_MOVTEXT3_'].Update(last_row_display3m)
                    if last_row_display3m.item() < 1:
                        window['_MOVWARN3_'].Update('Low movement')
                        SetLED(window, '_FF3MOVLED_', 'red' if last_row_display3m.all() < 1 else 'red')
                        SetLED(window, '_TABDEFAULTFF3MOVLED_', 'red' if last_row_display3.all() < 1 else 'red')
                        sg.PopupAutoClose('WARNING! LOW MOVEMENT DETECTED!', auto_close_duration=3, non_blocking=True,
                        background_color='darkorange',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False, location=(750,150))
                    else:
                        window['_MOVWARN3_'].Update('No warnings')
                        SetLED(window, '_FF3MOVLED_', 'green' if last_row_display3m.all() > 1 else 'green')
                        SetLED(window, '_TABDEFAULTFF3MOVLED_', 'green' if last_row_display3m.all() > 1 else 'green')
        
    # -------------------------------- FF3temperature ------------------------------- #

                    df3t = pd.read_csv('data3temp.csv', names=['time', 'temp'], index_col=['time'])
                    #movwarn3 = df3['movement'].max()
                    last_row_display3t = df3t['temp'].iloc[-1]
                    window['_TEMPTEXT3_'].Update(last_row_display3t)
                    if last_row_display3t.item() > 500:
                        window['_TEMPWARN3_'].Update('High Temperature')
                        SetLED(window, '_FF3TEMPLED_', 'red' if last_row_display3t.all() > 500 else 'red')
                        SetLED(window, '_TABDEFAULTFF3TEMPLED_', 'red' if last_row_display3.all() > 500 else 'red')
                        sg.PopupAutoClose('WARNING! HIGH TEMPERATURE DETECTED!', auto_close_duration=3, non_blocking=True,
                        background_color='orangered',  font=('calibri', 15, 'bold'), grab_anywhere=True, keep_on_top=False, location=(450,150))
                    elif last_row_display3t.item() > 400 and last_row_display3t.item() < 500:
                        window['_TEMPWARN3_'].Update('Moderate Temperature')
                        SetLED(window, '_FF3TEMPLED_', 'orange' if last_row_display3t.all()  > 400 and last_row_display3t.all() < 500  else 'orange')
                        SetLED(window, '_TABDEFAULTFF3TEMPLED_', 'orange' if last_row_display3t.all()  > 400 and last_row_display3t.all() < 500  else 'orange')
                    else:
                        window['_TEMPWARN3_'].Update('No warnings')
                        SetLED(window, '_FF3TEMPLED_', 'green' if last_row_display3t.all() < 500 else 'green')
                        SetLED(window, '_TABDEFAULTFF3TEMPLED_', 'green' if last_row_display3t.all() < 500 else 'green')

# ----------------------------------- setup ---------------------------------- #

        if event == 'Check COM Ports':
            # foo = ExecutePortList('powershell', '[System.IO.Ports.SerialPort]::getportnames()')
            print('Searching for your device...')
            foo, desc, found = ExecutePortList()
            # print("Searching... \n ... \n >>> Your COM port is: {} \n >>> Select it from the ComboBox below,\n >>> then click 'Configure COM Port'".format(foo.decode("utf-8")))
            if found:
                print(' >>> SFSS Found!')
                print(' >>> Device: ', desc)
                print(" \n >>> Your COM port is: {} \n >>> Click 'Configure COM Port'".format(foo))
            if not found:
                print(" >>> Device not found. Refer to the 'Help' section in the menu above")
            window.Refresh()

        if event == 'Configure COM Port':
            foo, desc, found = ExecutePortList()
            ser = serial.Serial()
            ser.baudrate=BAUDRATE
            ser.timeout=TIMEOUT

            if found:
                try:
                    #portToConfig = foo
                    print('\nConfiguring', foo)
                    ser.port = foo
                    if not ser.is_open:
                        ser.open()
                    print('\n >>> The port opened is: {}'.format(ser.name))
                    print(' >>> The Baudrate is: {}'.format(ser.baudrate))
                    print(' >>> The Bytesize is: {}'.format(ser.bytesize))
                    print(' >>> The Parity is: {}'.format(ser.parity))
                    print(' >>> Is it readable?: {}'.format(ser.readable()))
                    print(' >>> Is the port really open??: {}'.format(ser.is_open))
                    print(' >>> SUCESS!!')
                    print(' >>> You have been configured to work with the SFSS!')
                    ser.close()
                    pass
                except:
                    print(' >>> Unable to automatically configure your port.')
                    print(" >>> Select {} in the combobox and click 'Configure COM Port'".format(foo))
                    pass

            if not found:
                if values['_LISTBOX_'] == '-------':
                    print('\n >>> Your device is unable to be configured automatically')
                    print(" >>> 1. Select {} from the ComboBox below".format(foo))
                    print(" >>> 2. Click 'Configure COM Port'")
                try:
                    if values['_LISTBOX_'] is not '-------':
                        portToConfig = values['_LISTBOX_']
                        print('\n >>> The port you have selected is: ', portToConfig)
                        print('\nConfiguring', portToConfig)
                        ser.port = portToConfig
                        if not ser.is_open:
                            ser.open()
                        print(' >>> The port opened is: {}'.format(ser.name))
                        print(' >>> The Baudrate is: {}'.format(ser.baudrate))
                        print(' >>> The Bytesize is: {}'.format(ser.bytesize))
                        print(' >>> The Parity is: {}'.format(ser.parity))
                        print(' >>> Is it readable?: {}'.format(ser.readable()))
                        print(' >>> Is the port really open??: {}'.format(ser.is_open))
                        print(' >>> SUCESS!!')
                        print(' >>> You have been configured to work with the SFSS!')
                        ser.close()
                        pass
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
    #     event, values = window.Read()
    #     print(event, values)
    #     if event in(None, 'Exit'):        # always,  always give a way out!
    #         break

if __name__ == '__main__':
    main()
