#!/bin/bash

setreg()
{
    #printf 'read %s: ' $1
    #probook_ec ?= $1
    #printf 'write %s: %s\n' $1 $2
    probook_ec := $1 $2
    #readreg $1
}

readreg()
{
    regv=$(probook_ec ?= $1 | cut --delimiter " " --fields 3)
    #echo $1 == $regv
    return $(printf "%d" $regv)
}

#hex 64  50 46 3b 37 32 2d 28 1e 19
#dec 100 80 70 59 55 50 45 40 30 25

cputemp_target=39 #39 is critical
cputemp_boost=42
boost_flag=0
gputemp_target=55
counter=0
cpu_ct=100
gpu_ct=100

printf "cpu_target: %d, %d; gpu_target: %d\n" $cputemp_target $cputemp_boost $gputemp_target

while true
do
    if (( cpu_ct >= 23 || cpu_ct == 20 || cpu_ct == 12 )); then
        #echo cpu_ct $cpu_ct
        readreg 0x48
        cputemp=$?
        if (( $cputemp != $cputemp_target )); then
            #echo cpu_ct $cpu_ct
            cpu_ct=0
	    if (( boost_flag > 0 )); then
                #printf "got boost_flag set\n"
                setreg 0x48 $(printf %x $cputemp_boost)
            else
                setreg 0x48 $(printf %x $cputemp_target)
            fi
        fi
    fi

    if (( gpu_ct >= 12 || gpu_ct == 10 || gpu_ct == 6 )); then
        #echo gpu_ct $gpu_ct
        readreg 0xb7
        gputemp=$?
        if (( $gputemp != $gputemp_target )); then
	    setreg 0xb7 $(printf %x $gputemp_target)
            #echo gpu_ct $gpu_ct
            gpu_ct=0
        fi
    fi

    if (( $counter == 0 )); then
        readreg 0x2e
        cpufan=$?
        readreg 0x2f
        gpufan=$?
	counter=20

	if (( cpufan > 45 || gpufan > 41 )); then
            printf "fans: %d %d; temps: %d %d\n" $cpufan $gpufan $cputemp $gputemp
        fi

	if (( gpufan < 30 )); then
	    printf "gpufan too low, set boost_flag!\n"
            boost_flag=1
        else
            boost_flag=0
	fi
    fi
    
    ((counter=$counter-1))
    ((cpu_ct=$cpu_ct+1))
    ((gpu_ct=$gpu_ct+1))
    sleep 0.3
    #sleep 0.2; cpu 33(37) 30 20; gpu 17 15 10
    #sleep 0.3; cpu 23(26) 20 12; gpu 12 10 6
    #sleep 0.4; cpu 18(20) 15 10; gpu 9  7  5
done
