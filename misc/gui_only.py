#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Author: 			Robert Wells
# Project Title: 	Smart Firefighter Support System
# FileName: 		gui_only.py
# Path: 			c:...2019 Fall\Design 2\GUI\Git\SFSS\sfss\misc\gui_only.py
# Created Date: 	Saturday, October 26th 2019, 20:08:05 pm
# -----
# Last Modified: 	Saturday, October 26th 2019, 20:39:01 pm
# Modified By: 		Robert Wells
# -----
# Copyright (c) 2019 Your Company
# 
# GNU General Public License v3.0
# https://spdx.org/licenses/LGPL-3.0-only.html
# -----
# HISTORY:
# Date      			By		Comments
# ----------			---		----------------------------------------------------------
# 2019-10-26 20:10:56	RW		just getting the gui only part of the code out there
###

"""
This is the code for the SFSS GUI.
Everything here should run swimmingly as long as the correct imports are called as below.
This is basically just put up as a resource in case anyone comes along and wants a reference
as to how to buid a (decently) working gui using the **AWESOME** PySimpleGUI library
"""

import PySimpleGUI as sg
import os
import subprocess

def LEDIndicator(key=None, radius=40):
    """draws the "LEDs" on each tab by utilizing tkinter's canvas

    Args:
        key (str, optional): indicates where to draw using the items key. Defaults to None.
        radius (int, optional): size of the canvas. Defaults to 40.

    Returns:
        canvas: the LED
    """
    return sg.Graph(canvas_size=(radius, radius),
             graph_bottom_left=(-radius, -radius),
             graph_top_right=(radius, radius),
             pad=(0, 0), key=key)

def main():

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

    while True:
        event, values = window.Read()
        if event in (None,'Exit'):
            break

# ----------------------------------- Menu ----------------------------------- #

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
                if event in (None, 'Exit'):
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

if __name__ == '__main__':
    main()