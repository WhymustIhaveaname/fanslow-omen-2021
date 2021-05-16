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

def coolen_device(addr,interval,t_target,dt_boost):
    interval_log="%s.interval"%(addr)
    last_check=time.time()
    last_ck_cache=last_check
    check_ct=len(check_pts)

    while True:
        if boost_flag.value<=0:
            t_want=t_target
        else:
            log("found boost_flag set to %d"%(boost_flag.value),l=2)
            t_want=t_target+boost_flag.value*dt_boost
            log("t_want: %d"%(t_want))

        t=read_val(addr)
        if t!=t_want:
            last_check=time.time()
            #log("%s changed to %d, past %.2fs"%(addr,t,last_check-last_ck_cache))
            #log("%.3f"%(last_check-last_ck_cache),logfile=interval_log,end=", ")
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
            time.sleep(0.2)

def daemon_fan(interval=5.0):
    while True:
        last_check=time.time()
        cpufan=read_val("0x2e")
        gpufan=read_val("0x2f")

        if cpufan>45 or gpufan>41:
            log("overspeed: %d %d"%(cpufan,gpufan))

        if gpufan<35:
            log("subspeed: %d %d"%(cpufan,gpufan),l=2)
            gpufan=read_val("0x2f")
            if gpufan<30:
                with boost_flag.get_lock():
                    boost_flag.value+=1
                log("change boostflag to %d"%(boost_flag.value),l=2)
            else:
                log("fake subspeed actually %d"%(gpufan,),l=2)
        elif boost_flag.value!=0:
            with boost_flag.get_lock():
                boost_flag.value=0
            log("change boostflag back to %d"%(boost_flag.value),l=2)

        time.sleep(interval-(time.time()-last_check))

if __name__=="__main__":
    log("start slowen")
    p_cpu=Process(target=coolen_device,args=("0x48",8.0,39,2),name="p_cpu")
    p_gpu=Process(target=coolen_device,args=("0xb7",3.8,45,10),name="p_gpu")
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
