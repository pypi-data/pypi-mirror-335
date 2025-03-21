import re
import socket
from typing import List

import psutil
import wmi

from mag_tools.bean.sys.cpu import Cpu
from mag_tools.bean.sys.memory import Memory
from mag_tools.bean.sys.disk import Disk
from mag_tools.bean.sys.computer import Computer
from mag_tools.bean.sys.usb_device import UsbDevice
from mag_tools.model.usb_type import UsbType
from mag_tools.model.computer_type import ComputerType
from mag_tools.model.disk_type import DiskType
from mag_tools.model.fs_type import FsType


class DeviceUtils:
    @staticmethod
    def list_usb(usb_type: UsbType = None):
        c = wmi.WMI()
        usb_devices = c.Win32_USBHub()
        device_list = []
        for device in usb_devices:
            match = re.search(r'VID[_]?([0-9A-F]+).*PID[_]?([0-9A-F]+)', device.PNPDeviceID, re.I)
            if not match:
                match = re.search(r'USB\\(?:ROOT_HUB30|HASP)\\([0-9A-F]+)&([0-9A-F]+)', device.PNPDeviceID, re.I)

            vendor_id = match.group(1) if match else None
            product_id = match.group(2) if match else None

            device_info = UsbDevice(vendor_id, product_id, device.DeviceID, device.Caption, device.SystemName, device.Status, device.Description)
            if usb_type is None or (usb_type.desc in device_info.description or usb_type.code in device_info.description):
                device_list.append(device_info)
        return device_list


