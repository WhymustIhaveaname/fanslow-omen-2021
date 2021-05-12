#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import time,sys,traceback,math

LOGLEVEL={0:"DEBUG",1:"INFO",2:"WARN",3:"ERR",4:"FATAL"}
LOGFILE=sys.argv[0].split(".")
LOGFILE[-1]="log"
LOGFILE=".".join(LOGFILE)

def log(msg,l=1,end="\n",logfile=LOGFILE,color=None):
    st=traceback.extract_stack()[-2]
    lstr=LOGLEVEL[l]
    now_str="%s %03d"%(time.strftime("%y/%m/%d %H:%M:%S",time.localtime()),math.modf(time.time())[0]*1000)
    #now_str="%s"%(time.strftime("%y/%b %H:%M:%S",time.localtime()),)
    perfix="%s [%s,%s:%03d]"%(now_str,lstr,st.name,st.lineno)
    if color:
        color="\x1b[%sm"%(color)
        color_rst="\x1b[m"
    else:
        color=""
        color_rst=""
    if l<3:
        tempstr="%s %s%s%s%s"%(perfix,color,str(msg),end,color_rst)
    else:
        tempstr="%s %s:\n%s%s"%(perfix,str(msg),traceback.format_exc(limit=5),end)
    print(tempstr,end="")
    if l>=1:
        with open(logfile,"a") as f:
            f.write(tempstr)

import os
from multiprocessing import Process

def read_val(addr):
    with os.popen('probook_ec ?= %s'%(addr)) as f:
        t=f.read().strip()
    t=t.split()[2]
    return int(t,16)

def write_val(addr,val):
    os.system('probook_ec := %s %x'%(addr,val))

check_pts=(0.6,0.8,1.0)

def coolen_device(addr,interval,t_target,t_boost):
    log("into %s"%(addr))
    last_check=time.time()
    check_ct=len(check_pts)

    while True:
        t=read_val(addr)
        if t!= t_target:
            log("%s changed to %d, past %.2fs"%(addr,t,time.time()-last_check))
            last_check=time.time()
            write_val(addr,t_target)
            check_ct=0
        else:
            check_ct+=1

        if check_ct<len(check_pts):
            this_interval=interval*check_pts[check_ct]
            time_past=(time.time()-last_check)
            if this_interval>time_past:
                time.sleep(this_interval-time_past)
            else:
                log("this_inertval<time_past: %d<%d?"%(this_interval,time_past),l=2)
        else:
            time.sleep(0.1)

def daemon_fan(interval=5.0):
    log("into daemon")
    time.sleep(10)
    raise Exception
    while True:
        log("daemon weak up")
        last_check=time.time()
        cpufan=read_val("0x2e")
        gpufan=read_val("0x2f")
        if cpufan>45 or gpufan>41:
            log("overspeed: %d %d"%(cpufan,gpufan))
        if gpufan<30:
            boost_flag=1
        time.sleep(interval-(time.time()-last_check))

if __name__=="__main__":
    p_cpu=Process(target=coolen_device,args=("0x48",8.0,39,42))
    p_gpu=Process(target=coolen_device,args=("0x1b",4.0,55,55))
    p_deamon=Process(target=daemon_fan)
    p_deamon.start()
    p_cpu.start()
    #p_gpu.start()
