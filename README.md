# fanslow-omen-2021
Better fan control for HP OMEN laptop.
My OMEN fans always run at a crazy speed.
HP refused to provide any control software for Linux.
So I have to craft this script myself.
This script is based on [marhop/fanslow-probook430g2](https://github.com/marhop/fanslow-probook430g2).

## How it works

The fan speed is controlled by the embedded controller (EC).
One can use the `probook_ec` to read and write EC registers.
If you can set EC registers correctly, you can make the fan slower.

On my omen, "0x2e" and "0x2f" of the register of EC are fan speeds of CPU and GPU.
However, these two are read-only properties. Changing them takes no effect.
So I have to modify "0x48" and "0xb7", which are the CPU and GPU temperatures.
The logic for my laptop's fan control w.r.t temperature is
```
if gpu temperature ("0xb7") < 60:
    fanspeed depends on cpu temperature ("0x48"). Specifically,
    if cpu temperature <= 38:
        gpu fan stop
    else:
        both fans run
else:
    fans are very noisy.
```
So I set CPU temp to 39 and GPU temp to 45. Under this condition, both fans run at about 40% of max speed.

## How to use

* Clone the repo.
* Run the script.
    * Either run it in terminal, 
    * or copy the `my-slow.service` file to `/etc/systemd/system/my-slow.service` and run as a service `sudo systemctl start my-slow`.
Remember to change the path in `my-slow.service`.
    * If you are a fanatic for bash, `omenslow` is for you. But this bash script is not as flexible as the python one.

* Enjoy it!

## Feature

* Auto-adapting the update interval of EC.
* Using Python which is more user-friendly than bash. Only by using Python can one control the time precisely.
