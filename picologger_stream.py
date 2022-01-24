# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 08:28:49 2022

@author: Aleksander
"""

#
# Copyright (C) 2018-2019 Pico Technology Ltd. See LICENSE file for terms.
#
# PS2000 Series (A API) STREAMING MODE EXAMPLE
# This example demonstrates how to call the ps4000A driver API functions in order to open a device, setup 2 channels and collects streamed data (1 buffer).
# This data is then plotted as mV against time in ns.

import ctypes
import numpy as np
from picosdk.ps4000a import ps4000a as ps
from picosdk.functions import assert_pico_ok
import time
from datetime import datetime
import h5py
import os


script_dir = os.path.dirname(os.path.realpath(__file__))
log_path = os.path.join('C:/', 'Logfiles')
try:
    os.mkdir(log_path)
except:
    print("directory exists")


nextSample = int()
autoStopOuter = False
wasCalledBack = False
stopflag=False

def convert_channel_range(val):
    if val == 6:
        val = 1
    if val == 7:
        val = 2
    if val == 8:
        val = 5
    if val == 9:
        val = 10
    return int(val)

def stream(serial_number=b'', sample_interval=int, size_of_one_buffer=int, channels_to_setup=int, channel_range=int, flag=stopflag, f_id=str):
    
    # Create chandle and status ready for use
    chandle = ctypes.c_int16()
    status = {}
    converted_channel_range = convert_channel_range(channel_range)
    print(converted_channel_range)
    # Open PicoScope x000 Series device
    # Returns handle to chandle for use in future API functions
    status["openunit"] = ps.ps4000aOpenUnit(ctypes.byref(chandle), None)
    
    try:
        assert_pico_ok(status["openunit"])
    except:
    
        powerStatus = status["openunit"]
    
        if powerStatus == 286:
            status["changePowerSource"] = ps.ps4000aChangePowerSource(chandle, powerStatus)
        else:
            raise
    
        assert_pico_ok(status["changePowerSource"])
    enabled = 1
    disabled = 0
    analogue_offset = 0.0
    # Size of capture
    sizeOfOneBuffer = size_of_one_buffer#100000 
    numBuffersToCapture = 1
    totalSamples = sizeOfOneBuffer * numBuffersToCapture
    
    channels_ = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    for i in range(channels_to_setup):
        x = channels_[i]
        channel_range = channel_range
        # Set up channel X
        # handle = chandle
        # channel = PS4000A_CHANNEL_A = 0
        # enabled = 1
        # coupling type = PS4000A_DC = 1
        # range = PS4000A_2V = 7
        # analogue offset = 0 V
        status[f'setCh{x}'] = ps.ps4000aSetChannel(chandle,
                                                    ps.PS4000A_CHANNEL[f'PS4000A_CHANNEL_{x}'],
                                                    enabled,
                                                    ps.PS4000A_COUPLING['PS4000A_DC'],
                                                    channel_range,
                                                    analogue_offset)
        assert_pico_ok(status[f"setCh{x}"])
        
    # Create buffers ready for assigning pointers for data collection    
    bufferAMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
    bufferBMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
    bufferCMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
    bufferDMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
    bufferEMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
    bufferFMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
    bufferGMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
    bufferHMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
    
    memory_segment = 0

    buffers = [bufferAMax,bufferBMax,bufferCMax,bufferDMax,bufferEMax,bufferFMax,bufferGMax,bufferHMax]
    for i in range(channels_to_setup):
        x = channels_[i]
        # Set data buffer location for data collection from channel A
        # handle = chandle
        # source = PS4000A_CHANNEL_A = 0
        # pointer to buffer max = ctypes.byref(bufferAMax)
        # pointer to buffer min = ctypes.byref(bufferAMin)
        # buffer length = maxSamples
        # segment index = 0
        # ratio mode = PS4000A_RATIO_MODE_NONE = 0
        status[f"setDataBuffers{x}"] = ps.ps4000aSetDataBuffers(chandle,
                                                              ps.PS4000A_CHANNEL[f'PS4000A_CHANNEL_{x}'],
                                                              buffers[i].ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                              None,
                                                              sizeOfOneBuffer,
                                                              memory_segment,
                                                              ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
        assert_pico_ok(status[f"setDataBuffers{x}"])
    
    # Begin streaming mode:
    sampleInterval = ctypes.c_int32(sample_interval) #10000
    
    sampleUnits = ps.PS4000A_TIME_UNITS['PS4000A_NS']
    # We are not triggering:
    maxPreTriggerSamples = 0
    autoStopOn = 0
    # No downsampling:
    downsampleRatio = 1
    
    def streaming_callback(handle, noOfSamples, startIndex, overflow, triggerAt, triggered, autoStop, param):
        nonlocal nextSample, autoStopOuter, wasCalledBack
        wasCalledBack = True
        destEnd = nextSample + noOfSamples
        sourceEnd = startIndex + noOfSamples
        bufferCompleteA[nextSample:destEnd] = bufferAMax[startIndex:sourceEnd]
        bufferCompleteB[nextSample:destEnd] = bufferBMax[startIndex:sourceEnd]
        bufferCompleteC[nextSample:destEnd] = bufferCMax[startIndex:sourceEnd]
        bufferCompleteD[nextSample:destEnd] = bufferDMax[startIndex:sourceEnd]
        bufferCompleteE[nextSample:destEnd] = bufferAMax[startIndex:sourceEnd]
        bufferCompleteF[nextSample:destEnd] = bufferBMax[startIndex:sourceEnd]
        bufferCompleteG[nextSample:destEnd] = bufferCMax[startIndex:sourceEnd]
        bufferCompleteH[nextSample:destEnd] = bufferDMax[startIndex:sourceEnd]
        nextSample += noOfSamples
        if autoStop:
            autoStopOuter = True
    
    status["runStreaming"] = ps.ps4000aRunStreaming(chandle,
                                                    ctypes.byref(sampleInterval),
                                                    sampleUnits,
                                                    maxPreTriggerSamples,
                                                    totalSamples,
                                                    autoStopOn,
                                                    downsampleRatio,
                                                    ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'],
                                                    sizeOfOneBuffer)
    assert_pico_ok(status["runStreaming"])
    
    durations = []
    time_takens = []
    t_end = time.time() + 6
    actualSampleInterval = sampleInterval.value
    actualSampleIntervalNs = actualSampleInterval
    print(log_path)
    hf = h5py.File(f'{log_path}\{datetime.now().strftime(f"Picoscope_{f_id}_%d-%m-%yT%H%M%S")}.h5', 'a')
    buffer_keys = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    hf.create_dataset('Time', shape=0, chunks=True, maxshape=(None,))
    for i in range(channels_to_setup):
        x = buffer_keys[i]   
        hf.create_dataset(f'channel{x}', shape=0, chunks=True, maxshape=(None,))
        hf[f'channel{x}'].attrs['Sample interval'] = actualSampleInterval * 1e-9  
        hf[f'channel{x}'].attrs['Channel range'] = channel_range
        hf[f'channel{x}'].attrs['Division factor'] = 32767
        
    clock_start = time.time()
    time_start = 0
    track_record = []
    global stopflag
    while flag == False:
    # while time.time() < t_end:
        # We need a big buffer, not registered with the driver, to keep our complete capture in.
        bufferCompleteA = np.zeros(shape=totalSamples, dtype=np.int16)
        bufferCompleteB = np.zeros(shape=totalSamples, dtype=np.int16)
        bufferCompleteC = np.zeros(shape=totalSamples, dtype=np.int16)
        bufferCompleteD = np.zeros(shape=totalSamples, dtype=np.int16)
        bufferCompleteE = np.zeros(shape=totalSamples, dtype=np.int16)
        bufferCompleteF = np.zeros(shape=totalSamples, dtype=np.int16)
        bufferCompleteG = np.zeros(shape=totalSamples, dtype=np.int16)
        bufferCompleteH = np.zeros(shape=totalSamples, dtype=np.int16)
        nextSample = 0
        autoStopOuter = False
        wasCalledBack = False
    
        # Convert the python function into a C function pointer.
        cFuncPtr = ps.StreamingReadyType(streaming_callback)
    
        # Fetch data from the driver in a loop, copying it out of the registered buffers and into our complete one.
        while nextSample < totalSamples and not autoStopOuter:
            wasCalledBack = False
            status["getStreamingLastestValues"] = ps.ps4000aGetStreamingLatestValues(chandle, cFuncPtr, None)
            if not wasCalledBack:
                # If we weren't called back by the driver, this means no data is ready. Sleep for a short while before trying
                # again.
                time.sleep(0.01)
    
        # Find maximum ADC count value
        # handle = chandle
        # pointer to value = ctypes.byref(maxADC)
        maxADC = ctypes.c_int16()
        status["maximumValue"] = ps.ps4000aMaximumValue(chandle, ctypes.byref(maxADC))
        assert_pico_ok(status["maximumValue"])

        # Create time data
        end = (totalSamples - 1) * actualSampleIntervalNs+time_start
        duration = np.linspace(time_start, end, totalSamples)
        track_record.append(end)
        time_start = track_record[-1]
    
        hf['Time'].resize((hf['Time'].shape[0] + duration.shape[0]), axis=0)
        hf['Time'][-duration.shape[0]:] = duration
        raw_buffer = [bufferCompleteA, bufferCompleteB, bufferCompleteC, bufferCompleteD, bufferCompleteE, bufferCompleteF, bufferCompleteG, bufferCompleteH]
        for i in range(channels_to_setup):
            x = buffer_keys[i]   
            hf[f'channel{x}'].resize((hf[f'channel{x}'].shape[0] + raw_buffer[i].shape[0]), axis=0)
            hf[f'channel{x}'][-raw_buffer[i].shape[0]:] = (raw_buffer[i] / 32767) * converted_channel_range
            
        if stopflag == True:
            break


    hf.close()
    time_taken = time.time()-clock_start
    print((duration[-1]*1e-9))

    # Stop the scope
    # handle = chandle
    status["stop"] = ps.ps4000aStop(chandle)
    assert_pico_ok(status["stop"])

    # Disconnect the scope
    # handle = chandle
    status["close"] = ps.ps4000aCloseUnit(chandle)
    assert_pico_ok(status["close"])

    # Display status returns
    print(status)  


if __name__ == '__main__':
    # serial_number, no_channels = get_ser_and_chCount()
    stream(serial_number=b'', sample_interval=1000, size_of_one_buffer=1000000, channels_to_setup=3, channel_range=7)


    
    
    
    
    
    
    
    