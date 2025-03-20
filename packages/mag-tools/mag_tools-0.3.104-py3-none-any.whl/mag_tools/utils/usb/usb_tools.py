import re
import wmi
from mag_tools.bean.usb_device import UsbDevice
from mag_tools.model.usb_type import UsbType

class UsbTools:
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