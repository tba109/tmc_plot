#!/usr/bin/env python

######################################################
# Tyler Anderson Thu Mar 10 13:10:22 EST 2016
# 
# A python command line interface for ploting data 
# values from the TMC electronics. 
# 
# Pass a datafile list, and the command line will
# parse it and pick out the relevant values
######################################################

import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import time
import re
import matplotlib.dates as md
from scipy import interpolate

###############################################################
# Calculate the mean and normalize it
def mean_sub_norm(x):
    return ((x-np.mean(x))/np.max(x-np.mean(x)))

###############################################################
# Take the moving average
def moving_average(interval, window_size):
    window = np.ones(int(window_size))/float(window_size)
    result = np.convolve(interval, window, 'same')
    # print 'Result is length = %d' % len(result)
    for i in range(len(result)):
        if i < window_size:
            #print "%d: replacing %f with %f" % (i,result[i],np.sum(interval[:i+1])/float(i+1))
            result[i] = np.sum(interval[:i+1])/float(i+1)
        elif i > (len(result)-window_size-1):
            #print "%d: replacing %f with %f" % (i,result[i],np.sum(interval[i:])/float(len(result)-i))
            result[i] = np.sum(interval[i:])/float(len(result)-i)
            
    
    # print result[0],result[len(result)-1]
    return result

###############################################################
# Take the moving average.
# This one is a pure history function: avoids discontinuity at
# the boundaries
def moving_average2(interval, window_size):
    window = np.ones(int(window_size))/float(window_size)
    result = np.zeros(len(interval))
    # print 'Result is length = %d' % len(result)
    for i in range(len(result)):
        if i < window_size:
            #print "%d: replacing %f with %f" % (i,result[i],np.sum(interval[:i+1])/float(i+1))
            result[i] = np.sum(interval[:i+1])/float(i+1)
        else:
            #print "%d: replacing %f with %f" % (i,result[i],np.sum(interval[i:])/float(len(result)-i))
            result[i] = np.sum(interval[i-window_size:i])/float(window_size)
            
    
    print result[0],result[len(result)-1]
    return result

    
###############################################################
# For returning timestamps
def timestamp(date):
    return time.mktime(date.timetuple())

###############################################################
# For returning datetime
def datetimeit(date):
    return dt.datetime(int(date[0]),
                       int(date[1]),
                       int(date[2]),
                       int(date[3]),
                       int(date[4]),
                       int(date[5]))

###############################################################
# For returning a timestamp from a datestring
def datestr_to_tstart(s_time):
    if s_time is not None:
        split_date = re.split(r'[\t:/\n-]\s*',s_time)
        return timestamp(datetimeit(split_date))
    else:
        return 0

###############################################################
# For returning a timestamp from a datestring
def datestr_to_tstop(s_time):
    if s_time is not None:
        split_date = re.split(r'[\t:/\n-]\s*',s_time)
        return timestamp(datetimeit(split_date))
    else:
        return 0xFFFFFFFF

###############################################################
# For reading 2n2222 data from a file
def read_2n2222(fname, s_data, s_time, verbose, tstart, tstop):
    tstart_ts = datestr_to_tstart(tstart)
    tstop_ts = datestr_to_tstop(tstop)
    f_data = open(fname)
    n = 0
    for line in f_data:
        # print line.split('\t')[1].split(' ')[0]
        date = re.split(r'[\t:/\n-]\s*',line)
        now = datetimeit(date)
        tnow_ts = timestamp(now)
        # print tstart, tstart_ts, date, tnow_ts, tstop, tstop_ts
        if (tnow_ts > tstart_ts) and (tnow_ts < tstop_ts):
                s_time.append(now)
                s_data.append(float(line.split('\t')[1]))
        if verbose:
            print n, line[:-1]
        n+=1
    f_data.close()

###############################################################
# For reading test currents from a file
def read_current(fname, s_data, s_time, verbose, adc, tstart, tstop):
    tstart_ts = datestr_to_tstart(tstart)
    tstop_ts = datestr_to_tstop(tstop)
    f_data = open(fname)
    n = 0
    for line in f_data:
        date = re.split(r'[\t:/\n-]\s*',line)
        now = datetimeit(date)
        tnow_ts = timestamp(now)
        # s_time.append(timestamp(now))
        if (tnow_ts > tstart_ts) and (tnow_ts < tstop_ts):
            s_time.append(now)
            split_line = line.split('\t')[1].split(' ')
            s_data.append(float(split_line[adc]))
        if verbose:
            print n, line[:-1]
        n+=1
    f_data.close()

###############################################################
# For reading board temperatures
def read_board_temp(fname, s_data, s_time, verbose, bd, tstart, tstop):
    tstart_ts = datestr_to_tstart(tstart)
    tstop_ts = datestr_to_tstop(tstop)
    f_data = open(fname)
    n = 0
    for line in f_data:
        date = re.split(r'[\t:/\n-]\s*',line)
        now = datetimeit(date)
        tnow_ts = timestamp(now)
        if (tnow_ts > tstart_ts) and (tnow_ts < tstop_ts):
            s_time.append(now)
            split_line = line.split('\t')[1].split(' ')
            s_data.append(float(split_line[bd]))
        if verbose:
            print n, line[:-1]
        n+=1
    f_data.close()
    
###############################################################
# For running independently
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(prog="tmc_plot",description="A tool for plotting TMC data.")
    parser.add_argument('--file_list',type=str,help='List of datafiles to plot')
    parser.add_argument('--tstart',type=str,help='Start time to analyze, format YYYY/MM/DD-hh:mm:ss')
    parser.add_argument('--tstop',type=str,help='Stop time to analyze, format YYYY/MM/DD-hh:mm:ss')
    parser.add_argument('--save_dir',type=str,help='Directory in which to save plots')
    parser.add_argument('--version',action='version',version='%(prog)s 2.0')
    parser.add_argument('--verbose',help='Print additional debugging info',action='store_true')
    
    args = parser.parse_args()    
    
    voltage_2n2222 = []
    time_2n2222 = []
    baseline = []
    time_baseline = []
    current = []
    time_current = []
    adc_temp = []
    time_adc_temp = []
    board_temp = []
    time_board_temp = []
    adc = 0
    ch = 0
    bd = 0
    
    f_data = open(args.file_list)
    for filename in f_data:
        if filename[0] is '#':
            print "Continue on ", filename[:-1]
            continue;
        if '2N2222' in filename:
            print 'Processing ', filename[:-1]
            read_2n2222(filename[:-1],voltage_2n2222,time_2n2222,args.verbose,args.tstart,args.tstop)
            sch = (filename.split('-'))[1].split('_')[0] # System channel number: sch = 3*adc + ch
            ch = int(sch)%6
            adc = int(sch)/6
            bd = int(adc/3)
        elif 'TestCurrent' in filename:
            print 'Processing %s, TestCurrents for %d %d' %(filename[:-1],adc,ch)
            read_current(filename[:-1],current,time_current,args.verbose,adc,args.tstart,args.tstop)
        elif 'ADCBaseline' in filename:
            print 'Processing %s, ADCBaseline for %d %d' %(filename[:-1],adc,ch)
            read_current(filename[:-1],baseline,time_baseline,args.verbose,adc,args.tstart,args.tstop)
        elif 'ADCTemps' in filename:
            print 'Processing %s, ADCTemps for %d' % (filename[:-1],adc)
            read_current(filename[:-1],adc_temp,time_adc_temp,args.verbose,adc,args.tstart,args.tstop)
        elif 'BoardTemps' in filename:
            print 'Processing %s, BoardTemps for %d' % (filename[:-1],bd)
            read_board_temp(filename[:-1],board_temp,time_board_temp,args.verbose,bd,args.tstart,args.tstop)
        
    voltage_2n2222 = [1.E6*x for x in voltage_2n2222]
    board_temp = [x-273 for x in board_temp]
    baseline = [1.E6*x for x in baseline]

    ax1 = plt.subplot(515)
    plt.ylabel('2N2222 (uV)')
    plt.setp(ax1.get_xticklabels(), fontsize=8)
    plt.plot(time_2n2222,voltage_2n2222)
    
    ax2 = plt.subplot(514, sharex=ax1)
    plt.ylabel('Current (uA)')
    plt.setp(ax2.get_xticklabels(), visible=False)
    plt.plot(time_current,current)
    
    ax3 = plt.subplot(513, sharex=ax1)
    plt.ylabel('ATemp (degC)')
    plt.setp(ax3.get_xticklabels(), visible=False)
    plt.plot(time_adc_temp,adc_temp)
    
    ax4 = plt.subplot(512, sharex=ax1)
    plt.ylabel('BTemp (degC)')
    plt.setp(ax4.get_xticklabels(), visible=False)
    plt.plot(time_board_temp,board_temp)
    
    ax5 = plt.subplot(511, sharex=ax1)
    plt.ylabel('Baseline (uV)')
    plt.setp(ax5.get_xticklabels(), visible=False)
    plt.plot(time_baseline,baseline)
    # mng = plt.get_current_fig_manager()
    # mng.full_screen_toggle()
    figure = plt.gcf() # get current figure
    figure.set_size_inches(16, 12)
    # when saving, specify the DPI
    if args.save_dir is not None:
        figure.savefig("./"+args.save_dir+"/"+sch+".png", dpi = 100)
        print "./"+args.save_dir+sch+".png"
    else:
        figure.savefig(sch+".png", dpi = 100)
    plt.show()

    ###########################################################################
    # Create a bunch of time interpolating functions for all of the variables
    # (much easier to work with)
    # First, we need to create all of the timestamps
    timestamp_2n2222 = [timestamp(x) for x in time_2n2222]
    timestamp_current = [timestamp(x) for x in time_current]
    timestamp_baseline = [timestamp(x) for x in time_baseline]
    timestamp_board_temp = [timestamp(x) for x in time_board_temp]
    timestamp_adc_temp = [timestamp(x) for x in time_adc_temp]
    f_2nv = interpolate.interp1d(timestamp_2n2222,voltage_2n2222)
    f_cur = interpolate.interp1d(timestamp_current,current)
    f_bsln = interpolate.interp1d(timestamp_baseline,baseline)
    f_atemp = interpolate.interp1d(timestamp_adc_temp,adc_temp)
    f_btemp = interpolate.interp1d(timestamp_board_temp,board_temp)

    # Create time variables to work with from here out
    time_dt = time_2n2222[10:-10] # This peels off some problematic boundaries
    time_ts = [timestamp(x) for x in time_dt]
    
    # # Check the interpolations
    # plt.plot(time_dt,f_2nv(time_ts))
    # plt.show()
    # plt.plot(time_dt,f_cur(time_ts))
    # plt.show()
    # plt.plot(time_dt,f_bsln(time_ts))
    # plt.show()
    # plt.plot(time_dt,f_atemp(time_ts))
    # plt.show()
    # plt.plot(time_dt,f_btemp(time_ts))
    # plt.show()

    # Calculate the offset drift from the average baseline
    bsln_avg = moving_average2(f_bsln(time_ts),2000)
    offset = bsln_avg - bsln_avg[-1]
    plt.plot(time_dt,f_bsln(time_ts),color='b')
    plt.plot(time_dt,bsln_avg,color='r',linewidth=2.0)
    plt.xlabel('Date')
    plt.ylabel('Baseline ' + '(' + r'$\mu$'+'V)')
    plt.show()
    
    # Correct for ADC drift (the slow thing):
    # 1.) Convert all signals back to uV, 
    # 2.) correct the baseline 
    # 3.) convert back to native units 
    sig_offc_2nv_uv = f_2nv(time_ts) - offset
    sig_offc_cur_uv = (f_cur(time_ts)*1.E4 - offset)
    sig_offc_bsln_uv = (f_bsln(time_ts) - offset)
    sig_offc_btemp_uv = (f_btemp(time_ts)*1000. - offset)
    sig_offc_btemp_degc = (f_btemp(time_ts)*1000. - offset)/1000.
    
    # A cleaner quantity: averaged over 1 minute
    sig_offc_2nv_uv_avg = moving_average2(sig_offc_2nv_uv,20)
    sig_offc_cur_uv_avg = moving_average2(sig_offc_cur_uv,20)
    sig_offc_bsln_uv_avg = moving_average2(sig_offc_bsln_uv,20)
    sig_offc_atemp_degc_avg = moving_average2(f_atemp(time_ts),20)
    sig_offc_btemp_degc_avg = moving_average2(sig_offc_btemp_degc,20)

    ######################################################################
    # How does the HVAC component of the baseline compare to the current
    # in uV?
    plt.plot(time_dt,sig_offc_cur_uv_avg-np.mean(sig_offc_cur_uv_avg),color='b')
    plt.plot(time_dt,sig_offc_bsln_uv_avg-np.mean(sig_offc_bsln_uv_avg),color='g')
    # Do the subtraction and plot on top
    sig_bcor_offc_cur_uv = sig_offc_cur_uv_avg - sig_offc_bsln_uv_avg
    plt.plot(time_dt,sig_bcor_offc_cur_uv-np.mean(sig_bcor_offc_cur_uv),color='r')
    plt.ylabel('Current and Baseline ' + '(' + r'$\mu$'+'V)')
    plt.xlabel('Date')
    plt.xticks(rotation=25)
    plt.show()

    #######################################################################
    # Now remove the baseline from the 2n2222 voltage
    sig_bcor_offc_2nv_uv = sig_offc_2nv_uv - sig_offc_bsln_uv_avg
    plt.plot(time_dt,sig_offc_2nv_uv-np.mean(sig_offc_2nv_uv),color='b')
    plt.plot(time_dt,sig_bcor_offc_2nv_uv-np.mean(sig_bcor_offc_2nv_uv),color='g')
    plt.show()

    #######################################################################
    # Finally, compare the current to the voltage seen. As a first pass, 
    # plot them mean subtracted, and onthe same scale
    sig_bcor_offc_2nv_uv_avg = moving_average(sig_bcor_offc_2nv_uv,20)
    plt.plot(time_dt,sig_bcor_offc_2nv_uv_avg-np.mean(sig_bcor_offc_2nv_uv_avg),color='b')
    plt.plot(time_dt,(sig_bcor_offc_cur_uv-np.mean(sig_bcor_offc_cur_uv))/7.7,color='g')
    plt.show()

    sig_ccor_bcor_offc_2nc_uv = sig_bcor_offc_2nv_uv - sig_bcor_offc_cur_uv/7.7
    rms_2nv = np.std(sig_ccor_bcor_offc_2nc_uv)
    print '2N2222 RMS = %f uV, (%f mK)' % (rms_2nv,rms_2nv/2.5)
    plt.plot(time_dt,sig_ccor_bcor_offc_2nc_uv)
    sig_ccor_bcor_offc_2nc_uv_avg = moving_average(sig_ccor_bcor_offc_2nc_uv,20)
    plt.ylabel('Corrected 2N2222 Voltage ' + '(' + r'$\mu$'+'V)')
    plt.xlabel('Date')
    plt.plot(time_dt,sig_ccor_bcor_offc_2nc_uv_avg,'r')
    plt.show()

    #######################################################################
    # The result plot, all corrected up
    plt.plot(time_dt,(sig_ccor_bcor_offc_2nc_uv_avg-np.mean(sig_ccor_bcor_offc_2nc_uv_avg))/-2.5,'b')
    rms_2nv = np.std(sig_ccor_bcor_offc_2nc_uv_avg)
    print '2N2222 RMS = %f uV, (%f mK)' % (rms_2nv,rms_2nv/2.5)
    plt.ylabel('2N2222 Signal (mK)')
    plt.xlabel('Date')
    plt.ylim(-1,1)
    plt.show()
