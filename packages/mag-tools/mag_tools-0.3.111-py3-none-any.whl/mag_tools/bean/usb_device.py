from typing import Optional
import usb.core
import usb.util

class UsbDevice:
    def __init__(self, vendor_id: Optional[int or str], product_id: Optional[int or str], device_id: Optional[str]=None,
                 caption: Optional[str] = None, system_name: Optional[str] = None, status: Optional[str] = None, description: Optional[str] = None) -> None:
        self.vendor_id = int(vendor_id, 16) if isinstance(vendor_id, str) else vendor_id
        self.product_id = int(product_id, 16) if isinstance(product_id, str) else product_id
        self.device_id = device_id
        self.caption = caption
        self.system_name = system_name
        self.status = status
        self.description = description
        self.manufacturer = None
        self.product = None
        self.serial_number = None
        self.__device = None

    def initialize(self):
        self.__device = self.__find(self.vendor_id, self.product_id, self.device_id)
        self.manufacturer = usb.util.get_string(self.__device, self.__device.iManufacturer)
        self.product = usb.util.get_string(self.__device, self.__device.iProduct)
        self.serial_number = usb.util.get_string(self.__device, self.__device.iSerialNumber)

    def read_data(self, endpoint, size):
        try:
            return self.__device.read(endpoint, size)
        except usb.core.USBError as e:
            raise f"读取数据失败: {e}"

    def write_data(self, endpoint, data):
        try:
            self.__device.write(endpoint, data)
        except usb.core.USBError as e:
            raise f"写入数据失败: {e}"

    def __str__(self):
        return (f"UsbDevice(VendorID={hex(self.vendor_id) if self.vendor_id else None}, "
                f"ProductID={hex(self.product_id) if self.product_id else None}, DeviceID={self.device_id}, "
                f"Caption={self.caption}, SystemName={self.system_name}, Status={self.status}, Description={self.description}, "
                f"Manufacturer={self.manufacturer}, Product={self.product}, SerialNumber={self.serial_number})")

    @classmethod
    def __find(cls, vendor_id: Optional[int] = None, product_id: Optional[int] = None, device_id: Optional[str] = None,):
        device = usb.core.find(idVendor= vendor_id, idProduct = product_id)
        if device:
            if device_id is None or device.serial_number == device_id:
                device.set_configuration()
                return device

        raise ValueError(f"[{vendor_id}.{product_id}]设备未找到")

# 示例使用
if __name__ == "__main__":
    _vendor_id = 0x781  #0x0529
    _product_id = 0x55ab    #0x1

    # 创建 UsbDevice 实例
    usb_device = UsbDevice(_vendor_id, _product_id)
    usb_device.initialize()
    print("设备信息:", usb_device)

    # 打印设备信息
    print(usb_device)

    # 查找设备
    _device = usb.core.find(idVendor=_vendor_id, idProduct=_product_id)
    if _device is None:
        raise ValueError("设备未找到")

    # 读取数据
    endpoint_in = 0x81  # 替换为你的设备的输入端点地址
    _data = UsbDevice.read_data(_device, endpoint_in, 64)
    if _data:
        print("读取的数据:", _data)

    # 写入数据
    endpoint_out = 0x01  # 替换为你的设备的输出端点地址
    UsbDevice.write_data(_device, endpoint_out, b"Hello USB")