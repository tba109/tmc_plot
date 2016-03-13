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
# Take the moving average
def moving_average(interval, window_size):
    window = np.ones(int(window_size))/float(window_size)
    result = np.convolve(interval, window, 'same')
    print 'Result is length = %d' % len(result)
    for i in range(len(result)):
        if i < window_size:
            print "%d: replacing %f with %f" % (i,result[i],np.sum(interval[:i+1])/float(i+1))
            result[i] = np.sum(interval[:i+1])/float(i+1)
        elif i > (len(result)-window_size-1):
            print "%d: replacing %f with %f" % (i,result[i],np.sum(interval[i:])/float(len(result)-i))
            result[i] = np.sum(interval[i:])/float(len(result)-i)
            
    
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
    parser.add_argument('--version',action='version',version='%(prog)s 0.4')
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

    # Now calculate the moving average baseline
    np_baseline = np.array(baseline)
    avg_baseline = moving_average(np_baseline,4000)
    plt.plot(time_baseline,baseline)
    plt.plot(time_baseline,avg_baseline,color='r')
    plt.show()
    
    # Now subtract the baseline
    diff = [x - y for x,y in zip(voltage_2n2222,avg_baseline)]
    plt.plot(time_2n2222,diff)
    avg_diff = moving_average(diff,20)
    plt.plot(time_2n2222,avg_diff,color='r')
    print "Stdev = %fuV (~%fmK)" % (np.std(diff),np.std(diff)/2.5)
    plt.show()


    # Let's work with the average difference
    bs_diff = (avg_diff - np.mean(avg_diff)) # baseline subtracted
    na_diff = bs_diff/np.max(bs_diff) # normalized
    bs_btemp = board_temp - np.mean(board_temp)
    na_btemp = bs_btemp/np.max(bs_btemp)
    rs_btemp = na_btemp/2. # re-scaled
    bs_current = current - np.mean(current)
    na_current = bs_current/np.max(bs_current)
    rs_current = na_current/1. # re-scaled
    plt.plot(time_2n2222,na_diff,color='b')
    # plt.plot(time_board_temp,rs_btemp,color='r',linewidth=2.0)
    plt.plot(time_current,rs_current,color='g',linewidth=2.0)
    plt.show()

    # Try subtracting baseline current, tune scaling, for now
    # Convert current back to uV
    timestamp_current = [timestamp(x) for x in time_current]
    timestamp_baseline = [timestamp(x) for x in time_baseline]
    current_uV = [x*1.E4 for x in current]
    plt.plot(current_uV)
    interp_current_uV = interpolate.interp1d(timestamp_current,current_uV)
    plt.show()
    diff_current_uV = [x - y for x,y in zip(interp_current_uV(timestamp_current),avg_baseline)]
    plt.plot(timestamp_current,diff_current_uV)
    # plt.plot(timestamp_baseline,avg_baseline)
    plt.show()

    # Does baseline subtracted current match up? 
    bs_current_uV = (diff_current_uV - np.mean(diff_current_uV))
    na_current_uV = bs_current_uV/(np.max(bs_current_uV)*1.)
    plt.plot(time_2n2222,na_diff,color='b')
    plt.plot(time_current,na_current_uV,color='g')
    plt.show()
    
    # Check the result
    timestamp_2n2222 = [timestamp(x) for x in time_2n2222]
    timestamp_2n2222 = timestamp_2n2222[10:-10]
    time_2n2222 = time_2n2222[10:-10]
    na_diff = na_diff[10:-10]
    interp_diff_current_uV = interpolate.interp1d(timestamp_current,na_current)
    diff_2n2222_curr = [x - y for x,y in zip(na_diff,interp_diff_current_uV(timestamp_2n2222))]
    fixed_2n2222 = diff_2n2222_curr*np.max(bs_diff) + np.mean(avg_diff)
    plt.plot(time_2n2222,diff_2n2222_curr)
    plt.show()

    fixed_2n2222 = diff_2n2222_curr*np.max(bs_diff) + np.mean(avg_diff)
    plt.plot(time_2n2222,fixed_2n2222)
    plt.show()

    
