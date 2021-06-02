#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import time,sys,traceback,math

LOGLEVEL={0:"DEBUG",1:"INFO",2:"WARN",3:"ERR",4:"FATAL"}
LOGFILE=sys.argv[0].split(".")
LOGFILE[-1]="log"
LOGFILE=".".join(LOGFILE)

def log(msg,l=1,end="\n",logfile=LOGFILE,color=None,fileonly=False):
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
    if not fileonly:
        print(tempstr,end="")
    if l>=1:
        with open(logfile,"a") as f:
            f.write(tempstr)

import os
from multiprocessing import Process,Value

def read_val(addr):
    with os.popen('probook_ec ?= %s'%(addr)) as f:
        t=f.read().strip()
    t=t.split()[2]
    return int(t,16)

def write_val(addr,val):
    #log('probook_ec := %s %x'%(addr,val))
    os.system('probook_ec := %s %x'%(addr,val))
    #log(read_val(addr))

check_pts=(0.6,0.94,1.0) #0.2/3.8=0.053
boost_flag=Value("i",0)

def coolen_device(addr,interval,ck_interval,t_target,dt_boost,log_dt):
    interval_log=sys.argv[0].split("/")
    interval_log[-1]="%s.interval"%(addr)
    interval_log="/".join(interval_log)
    interval_inf=interval*0.8
    interval_sup=interval*1.2
    lr=0.05
    ct=0

    last_check=time.time()
    last_ck_cache=last_check
    check_ct=len(check_pts)

    while True:
        if boost_flag.value<=0:
            t_want=t_target
        else:
            #log("found boost_flag set to %d"%(boost_flag.value),l=2)
            t_want=t_target+boost_flag.value*dt_boost
            #log("t_want: %d"%(t_want))

        t=read_val(addr)
        if t!=t_want:
            last_check=time.time()
            ct+=1
            this_interval=last_check-last_ck_cache
            if ct>10 and interval_inf<this_interval<interval_sup:
                interval+=lr*(this_interval-interval)
                interval_hist="update interval to %.4fs"%(interval)
            else:
                interval_hist=""
            log("%s changed to %d, past %.2fs, %s"%(addr,t,this_interval,interval_hist),logfile=interval_log,fileonly=not log_dt)
            last_ck_cache=last_check
            write_val(addr,t_want)
            check_ct=0
        else:
            check_ct+=1

        if check_ct<len(check_pts):
            this_interval=interval*check_pts[check_ct]
            time_past=(time.time()-last_check)
            time.sleep(max(this_interval-time_past,0.05))
        else:
            time.sleep(ck_interval)

def daemon_fan(interval=10.0):
    log("daemon check interval %ds"%(interval))
    while True:
        last_check=time.time()
        cpufan=read_val("0x2e")
        gpufan=read_val("0x2f")

        if cpufan>45 or gpufan>41:
            log("overspeed: %d %d"%(cpufan,gpufan))

        if gpufan<35 or cpufan<35:
            log("subspeed: %d %d"%(cpufan,gpufan),l=2)
            cpufan=read_val("0x2e")
            gpufan=read_val("0x2f")
            if gpufan<35 or cpufan<35:
                with boost_flag.get_lock():
                    boost_flag.value+=1
                log("change boostflag to %d"%(boost_flag.value),l=2)
            else:
                log("fake subspeed, actually %d %d"%(gpufan,cpufan),l=2)
        elif boost_flag.value!=0:
            with boost_flag.get_lock():
                boost_flag.value=0
            log("change boostflag back to %d"%(boost_flag.value),l=2)

        time.sleep(interval-(time.time()-last_check))

if __name__=="__main__":
    log("start slowen")
    # critial temp: 39, 59
    p_cpu=Process(target=coolen_device,args=("0x48",8.4,0.1,39,4,False),name="p_cpu")
    p_gpu=Process(target=coolen_device,args=("0xb7",4.2,0.1,45,10,True),name="p_gpu")
    p_cpu.start()
    p_gpu.start()
    p_deamon=Process(target=daemon_fan,name="p_deamon")
    p_deamon.start()

    while_flag=True
    while while_flag:
        time.sleep(4.0)
        for p in [p_cpu,p_gpu,p_deamon]:
            if not p.is_alive():
                log("%s is not alive!"%(p.name))
                while_flag=False
                break

    for p in [p_cpu,p_gpu,p_deamon]:
        if p.is_alive():
            log("terminate %s"%(p.name))
            p.terminate()
