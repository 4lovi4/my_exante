#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import dbus
import sys

def set_br(level:int):

    bus = dbus.SystemBus()
    kbd_blight_proxy = bus.get_object('org.freedesktop.UPower', '/org/freedesktop/UPower/KbdBacklight')
    kbd_blight = dbus.Interface(kbd_blight_proxy, 'org.freedesktop.UPower.KbdBacklight')
    maximum = kbd_blight.GetMaxBrightness()
    current = kbd_blight.GetBrightness()
    if level > maximum and level < 0:
        print('Wrong brightness level value {}'.format(level))
        return None
    kbd_blight.SetBrightness(level)
    current = kbd_blight.GetBrightness()
    return(current)


if __name__ == '__main__':

    try:
        level = int(sys.argv[1])
    except ValueError as err:
        print('ValueError: {}'.format(sys.argv[1]))
        sys.exit(1)
    if len(sys.argv) != 2 or not isinstance(level, int):
        print('Exit')
        sys.exit(1)

    print(set_br(level))
    exit(0)
