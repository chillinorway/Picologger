# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 13:08:26 2022

@author: Aleksander
"""

import tkinter as tk
import tkinter.ttk as ttk
from picosdk.ps4000a import ps4000a as ps
import picologger_stream
from threading import Thread


setup = {}
thread_initiated = False

class App(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        global setup
    
        self.frame_1 = tk.Frame(master)
        self.frame_2 = tk.Frame(master)
        self.frame_3 = tk.Frame(master)
        self.frame_4 = tk.Frame(master)
        
        self.frame_1.grid(row=0, column=0, sticky='nsew')
        self.frame_2.grid(row=1, column=0, sticky='nsew')
        self.frame_3.grid(row=0, column=1, sticky='nsew')
        self.frame_4.grid(row=1, column=1, sticky='nsew')
        
        self.info_label_1 = tk.Label(self.frame_1, text="Picoscope logger", font=("Arial, 24"))
        self.info_label_1.grid(row=0,column=0,sticky='nsew')
        
        self.info_label_2 = tk.Label(self.frame_1, text="Simple\nlogger\nv0.1\n\n\n\n", font=("Arial, 16"))
        self.info_label_2.grid(row=1,column=0,sticky='nsew')

        self.info_label_3 = tk.Label(self.frame_2, text="Connected devices", font=("Arial, 16"))
        self.info_label_3.grid(row=0,column=0,sticky='nsew')
        
        self.info_label_3 = tk.Label(self.frame_4, text="Start Aquisition", font=("Arial, 16"))
        self.info_label_3.grid(row=0,column=0,sticky='nsew')
        
        self.info_label_4 = tk.Label(self.frame_4, text="Stop Aquisition", font=("Arial, 16"))
        self.info_label_4.grid(row=0,column=1,sticky='nsew')
        
        self.info_label_5 = tk.Label(self.frame_2, text="Sample interval [nS]", font=("Arial, 12"))
        self.info_label_5.grid(row=2,column=0,sticky='nsew')
        self.info_label_5 = tk.Label(self.frame_2, text="Buffer size", font=("Arial, 12"))
        self.info_label_5.grid(row=3,column=0,sticky='nsew')
        
        self.info_label_6 = tk.Label(self.frame_2, text="Channel range", font=("Arial, 12"))
        self.info_label_6.grid(row=4,column=0,sticky='nsew')
        
        self.info_label_7 = tk.Label(self.frame_2, text="File identifier", font=("Arial, 12"))
        self.info_label_7.grid(row=5,column=0,sticky='nsew')
        
        self.start_btn = tk.Button(self.frame_4, text='Start', command=lambda: start_thread())
        self.start_btn.grid(row=1,column=0,sticky='nsew', padx=20, pady=20)
        
        self.stop_btn = tk.Button(self.frame_4, text='Stop', command=stop)
        self.stop_btn.grid(row=1,column=1,sticky='nsew', padx=20, pady=20)
        
        serial_number, no_channels = self.get_ser_and_chCount()
        setup['Nr_channels'] = no_channels
        
        devices = [serial_number]
        self.var = tk.StringVar(self)
        self.var.set(devices[0])
        self.drop_down_devices = ttk.Combobox(self.frame_2, values=devices)
        self.drop_down_devices.config(width=20)
        self.drop_down_devices.grid(row=1, column=0,padx=20, pady=20)
        self.drop_down_devices.bind("<<ComboboxSelected>>", lambda f1: self.get_gui_val(key='Serial_nr',val_to_get=self.drop_down_devices))
        
        self.entry_sample_interval = tk.Entry(self.frame_2)
        self.entry_sample_interval.insert(0, 10000)
        self.entry_sample_interval.bind('<FocusOut>', lambda f1: self.get_gui_val(key='Sample_interval',val_to_get=self.entry_sample_interval))
        self.entry_sample_interval.grid(row=2, column=1,padx=10, pady=10)
        setup['Sample_interval'] = 10000
        
        self.entry_buffer_size = tk.Entry(self.frame_2)
        self.entry_buffer_size.insert(0, 100000)
        self.entry_buffer_size.bind('<FocusOut>', lambda f1: self.get_gui_val(key='Buffer_size',val_to_get=self.entry_buffer_size))
        self.entry_buffer_size.grid(row=3, column=1,padx=10, pady=10)
        setup['Buffer_size'] = 100000
        
        ranges = ['1V', '2V', '5V', '10V']
        self.temp_var = tk.StringVar(self)
        self.drop_down_chRange = ttk.Combobox(self.frame_2, values=ranges)
        self.drop_down_chRange.config(width=15)
        self.drop_down_chRange.insert(0, ranges[2])
        self.drop_down_chRange.grid(row=4, column=1)
        self.drop_down_chRange.bind("<<ComboboxSelected>>", lambda f1: self.get_gui_val(key='Channel_range',val_to_get = self.drop_down_chRange))
        setup['Channel_range'] = 8
        
        self.entry_identifier = tk.Entry(self.frame_2)
        self.entry_identifier.insert(0, 'X')
        self.entry_identifier.bind('<FocusOut>', lambda f1: self.get_gui_val(key='File_identifier',val_to_get=self.entry_identifier))
        self.entry_identifier.grid(row=5, column=1,padx=10, pady=10)
        setup['File_identifier'] = 'X'
        
    def get_gui_val(self, key, val_to_get):
        if key == 'Channel_range':
            converted = self.convert_channel_range(val_to_get.get())
            setup[key] = converted
        else:
            setup[key] = val_to_get.get()

    def get_ser_and_chCount(self):    
        info = ps.list_units()[0]
        variant = info[1].decode('utf-8')
        no_channels = int(variant[1])
        serial = info[2]
        return serial, no_channels
    
    def convert_channel_range(self, val):
        if val == '1V':
            val = 6
        if val == '2V':
            val = 7
        if val == '5V':
            val = 8
        if val == '10V':
            val = 9
        return int(val)

def init():
    root = tk.Tk()
    root.title("Picoscope logger")
    root.wm_iconbitmap('spyder.ico')
    app = App(root)
    app.mainloop()

def main():
    print(setup)
    sr_nr = setup['Serial_nr']
    sa_interval = int(setup['Sample_interval'])
    size_buf = setup['Buffer_size']
    channels = setup['Nr_channels']
    ch_range = setup['Channel_range']
    file_id = setup['File_identifier']
    picologger_stream.stream(serial_number=sr_nr,
                              sample_interval=sa_interval, 
                              size_of_one_buffer=size_buf, 
                              channels_to_setup=channels,
                              channel_range=ch_range, 
                              flag=stop, 
                              f_id=file_id)

def stop():
    # Assign global variable and set value to stop
    global stop
    stop = True
    picologger_stream.stopflag = stop
    global thread_initiated
    thread_initiated = False
    
def start_thread():
    global thread_initiated
    if thread_initiated == False:
        global stop
        stop = False
        picologger_stream.stopflag = False
        # Create and launch a thread
        t = Thread(target=main)
        t.start()
        thread_initiated=True 

root = tk.Tk()
root.title("Picoscope logger")
app = App(root)
app.mainloop()
