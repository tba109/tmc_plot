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
    parser.add_argument('--plot_individual',help='Make the plots individually',action='store_true')
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

    if args.plot_individual:
        if len(voltage_2n2222):
            # Plot the voltage stuff
            print len(voltage_2n2222)
            ax=plt.gca()
            xfmt = md.DateFormatter('%H:%M:%S')
            ax.xaxis.set_major_formatter(xfmt)
            plt.xlabel('Date')
            plt.ylabel('2N2222 (Volts)')
            plt.xticks( rotation=25 )
            plt.plot(time_2n2222,voltage_2n2222)
            plt.show()
        
        if len(current):
            # Plot the current stuff
            print len(current)
        
            # for x,y in zip(2n2222_time,s_data):
            #     print x,y
            ax=plt.gca()
            xfmt = md.DateFormatter('%H:%M:%S')
            ax.xaxis.set_major_formatter(xfmt)
            plt.xlabel('Date')
            plt.ylabel('2N2222 Current (Amps)')
            plt.xticks( rotation=25 )
            plt.plot(time_current,current)
            plt.show()

        if len(baseline):
            # Plot the current stuff
            print len(baseline)
            
            # for x,y in zip(2n2222_time,s_data):
            #     print x,y
            ax=plt.gca()
            xfmt = md.DateFormatter('%H:%M:%S')
            ax.xaxis.set_major_formatter(xfmt)
            plt.xlabel('Date')
            plt.ylabel('Baseline (Volts)')
            plt.xticks( rotation=25 )
            plt.plot(time_baseline,baseline)
            plt.show()

        if len(adc_temp):
            # Plot the current stuff
            print len(adc_temp)
            
            # for x,y in zip(2n2222_time,s_data):
            #     print x,y
            ax=plt.gca()
            xfmt = md.DateFormatter('%H:%M:%S')
            ax.xaxis.set_major_formatter(xfmt)
            plt.xlabel('Date')
            plt.ylabel('ADC Temperature (Celsius)')
            plt.xticks( rotation=25 )
            plt.plot(time_adc_temp,adc_temp)
            plt.show()

        if len(board_temp):
            # Plot the current stuff
            print len(board_temp)
            
            # for x,y in zip(2n2222_time,s_data):
            #     print x,y
            ax=plt.gca()
            xfmt = md.DateFormatter('%H:%M:%S')
            ax.xaxis.set_major_formatter(xfmt)
            plt.xlabel('Date')
            plt.ylabel('Board Temperature (Celsius)')
            plt.xticks( rotation=25 )
            plt.plot(time_board_temp,board_temp)
            plt.show()
    else:
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

    diff = [x - y for x,y  in zip(voltage_2n2222,baseline)]
    print "stdev of diff = ", np.std(np.array(diff))
    ax=plt.gca()
    xfmt = md.DateFormatter('%H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    plt.xlabel('Date')
    plt.ylabel('Difference between 2N2222 and Baseline (uV)')
    plt.xticks( rotation=25 )
    plt.plot(time_2n2222,diff)
    #plt.show()

    # Take the 1 minute windowed average
    def moving_average(interval, window_size):
        window = np.ones(int(window_size))/float(window_size)
        return np.convolve(interval, window, 'same')
    np_diff = np.array(diff)    
    avg_diff = moving_average(np_diff,20)
    
    timestamp_2n2222 = [timestamp(x) for x in time_2n2222]
    np_timestamp_2n2222 = np.array(timestamp_2n2222)
    np_avg_time_2n2222 = moving_average(np_timestamp_2n2222,20)
    # print np_avg_time_2n2222
    # print np_avg_time_2n2222.shape
    dt_time_2n2222 = [dt.datetime.fromtimestamp(t) for t in np_avg_time_2n2222]
    dt_time_2n2222 = dt_time_2n2222[10:-10]
    avg_diff = avg_diff[10:-10]
    np_avg_time_2n2222 = np_avg_time_2n2222[10:-10]
    plt.plot(dt_time_2n2222,avg_diff,color='r')
    plt.show()
    
    # This is to help find the temperature coefficient
    bt_mean = np.average(np.array(board_temp))
    ac_board_temp = [x-bt_mean for x in board_temp]
    # plt.plot(time_board_temp,ac_board_temp,color='g')
    # plt.show()
    
    # Try to temperature correct it, coeff ~ -1.25uV/degC
    # This doesn't seem to work so well after subtracting baseline
    timestamp_board_temp = [timestamp(x) for x in time_board_temp]
    f1 = interpolate.interp1d(timestamp_board_temp,ac_board_temp)
    ac_temp_interp = f1(np_avg_time_2n2222)
    # plt.plot(ac_temp_interp,avg_diff)
    tcorr_diff = [y-1.25*f1(x) for x,y in zip(np_avg_time_2n2222,avg_diff)]
    plt.plot(dt_time_2n2222,tcorr_diff,color='g')
    plt.plot(dt_time_2n2222,avg_diff,color='b')
    plt.show()

    # Try subtracting off current, 2500Ohm
    timestamp_current = [timestamp(x) for x in time_current]
    timestamp_2n2222 = [timestamp(x) for x in time_2n2222]
    f2 = interpolate.interp1d(timestamp_current,current)
    timestamp_2n2222 = timestamp_2n2222[10:-10]
    current_interp = f2(timestamp_2n2222)
    # plt.plot(ac_temp_interp,avg_diff)
    ccorr = [y-2000*f2(x) for x,y in zip(timestamp_2n2222,voltage_2n2222)]
    dt_time_ccor = [dt.datetime.fromtimestamp(t) for t in timestamp_2n2222]
    plt.xlabel('Date')
    plt.plot(dt_time_ccor,ccorr,color='b')
    plt.show()

    # ####################################################################################
    # # Now calculate the low-pass filtered baseline    
    # # This isn't really working....
    # def butter_lowpass(cutoff, fs, order=5):
    #     print 'inside butter_lowpass'
    #     nyq = 0.5 * fs
    #     print nyq
    #     print cutoff
    #     normal_cutoff = cutoff / nyq
    #     print normal_cutoff
    #     b, a = butter(order, normal_cutoff, btype='low', analog=False)
    #     return b, a

    # def butter_lowpass_filter(data, cutoff, fs, order=5):
    #     b, a = butter_lowpass(cutoff, fs, order=order)
    #     y = lfilter(b, a, data)
    #     return y

    # # Filter requirements.
    # order = 6
    # fs = 1./3           # sample rate, Hz
    # cutoff = 1./(300*60)  # desired cutoff frequency of the filter, Hz. Freq to kill is
    #                     # 1./(30*60)
    
    # from scipy.signal import butter, lfilter, freqz
    # # Get the filter coefficients so we can check its frequency response.
    # b, a = butter_lowpass(cutoff, fs, order)
    
    # # Plot the frequency response.
    # w, h = freqz(b, a, worN=800)
    # plt.subplot(2, 1, 1)
    # plt.plot(0.5*fs*w/np.pi, np.abs(h), 'b')
    # plt.plot(cutoff, 0.5*np.sqrt(2), 'ko')
    # plt.axvline(cutoff, color='k')
    # plt.xlim(0, 20*cutoff)
    # plt.title("Lowpass Filter Frequency Response")
    # plt.xlabel('Frequency [Hz]')
    # plt.grid()
    # plt.show()

    # # Filter the data, and plot both the original and filtered signals.
    # np_baseline = np.array(baseline)
    # y = butter_lowpass_filter(np_baseline, cutoff, fs, order)
    # print np_baseline
    # print type(np_baseline)
    # print len(np_baseline)
    # print y
    # print type(y)
    # print len(y)


    # plt.plot(time_baseline, baseline, 'b-')
    # plt.plot(time_baseline, y, 'g-', linewidth=2)
    # plt.xlabel('Time [sec]')
    # plt.show()

    # ##################################################################################
    # # Now calculate the moving average baseline
    # np_baseline = np.array(baseline)
    # avg_baseline = moving_average(np_baseline,2000)
    # time_baseline = time_baseline[1000:-1000]
    # avg_baseline = avg_baseline[1000:-1000]
    # baseline = baseline[1000:-1000]
    # plt.plot(time_baseline[1000:-1000],baseline[1000:-1000])
    # plt.plot(time_baseline[1000:-1000],avg_baseline[1000:-1000])
    # plt.show()

    # ccorr2 = np.array(ccorr[1000:-1000])
    # avg_baseline = avg_baseline[10:-10]
    # time_baseline = time_baseline[10:-10]
    # print len(ccorr2)
    # print type(ccorr2)
    # print ccorr2
    # print len(avg_baseline)
    # print type(avg_baseline)
    # print avg_baseline
    # print len(time_baseline)
    # print type(time_baseline)
    # # print time_baseline
    # # diff2 = [x1-x2 for x1,x2 in zip(avg_baseline,ccorr2)]
    # diff2 = ccorr2 - avg_baseline
    # plt.plot(time_baseline,ccorr2)
    # plt.show()

    ####################################################################################
    # Now calculate the moving average baseline
    np_baseline = np.array(baseline)
    avg_baseline = moving_average(np_baseline,4000)
    time_baseline = time_baseline[1000:-1000]
    avg_baseline = avg_baseline[1000:-1000]
    baseline = baseline[1000:-1000]
    plt.plot(time_baseline[1000:-1000],baseline[1000:-1000])
    plt.plot(time_baseline[1000:-1000],avg_baseline[1000:-1000])
    plt.show()

    # This subtracts off of the current corrected baseline...not so good
    # ccorr2 = np.array(ccorr[1000:-1000])
    # avg_baseline = avg_baseline[10:-10]
    # time_baseline = time_baseline[10:-10]
    # print len(ccorr2)
    # print type(ccorr2)
    # print ccorr2
    # print len(avg_baseline)
    # print type(avg_baseline)
    # print avg_baseline
    # print len(time_baseline)
    # print type(time_baseline)
    # diff2 = ccorr2 - avg_baseline
    # plt.plot(time_baseline,ccorr2)
    # plt.show()
    
    # This subtracts off of the raw baseline
    voltage_2n2222 = voltage_2n2222[1000:-1000]
    timestamp_2n2222 = timestamp_2n2222[1000:-1000]
    timestamp_baseline = [timestamp(x) for x in time_baseline]
    f3 = interpolate.interp1d(timestamp_baseline,avg_baseline)
    bcorr_diff = [y-f3(x) for y,x in zip(voltage_2n2222,timestamp_2n2222)]
    # plt.plot(timestamp_2n2222,bcorr_diff)
    avg_diff2 = moving_average(bcorr_diff,20)
    plt.plot(timestamp_2n2222[1000:-1000],avg_diff2[1000:-1000],color='r')
    plt.show()

    
