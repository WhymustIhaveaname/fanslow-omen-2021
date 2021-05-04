Better fan control for HP ProBook 430 G2.

On my HP ProBook 430 G2 laptop running Debian or Arch Linux, the fan is much
too zealous to my taste, running quite fast even when there's nearly no load
on the system. These scripts take control of the fan and apply a more moderate
policy. On my laptop this works better than the original fan control software,
meaning that the fan runs much less, but your mileage may vary. And of course,
it's nobody's fault if you wreck your hardware!

The core scripts `probook_ec` and `fanslow` are taken from
<https://github.com/k3mpaxl/fanspeed> with no or only minimal modifications.
Further information on the original scripts can be found at
<http://ubuntuforums.org/showthread.php?t=2008756>.

# Overview of the components

The `probook_ec` script is used to change several hardware settings of a
laptop. Useful things you can do with it include switching the fan off and
resetting the embedded controller (I guess that means something like returning
control of the fan to the firmware):

    # probook_ec FANOFF
    # probook_ec FANRST

The `fanslow` script monitors the temperature and sets the fan speed as
needed.

The `fanslow.service` file is a systemd service unit file used for
autostarting and running the `fanslow` script as a background daemon.

# Installation

On Arch Linux, you can install from the AUR:
<https://aur.archlinux.org/packages/fanslow-probook430g2/>

On other distributions, use the Makefile for installation and removal. If you
are picky about your installation paths (like `/usr/` vs. `/usr/local/`) you
should probably adapt the Makefile as well as the `fanslow` and
`fanslow.service` files prior to installation.

    # make install
    # systemctl enable fanslow
    # systemctl start fanslow

    # systemctl stop fanslow
    # systemctl disable fanslow
    # make uninstall

You can watch the script working with the usual systemd tools:

    # systemctl status fanslow
    # journalctl -u fanslow

