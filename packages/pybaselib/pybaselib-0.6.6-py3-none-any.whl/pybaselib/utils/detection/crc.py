# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2024/12/25 15:08
import crcmod


class CRC16X25:
    def __init__(self):
        self.crc_func = crcmod.mkCrcFun(0x11021, initCrc=0x0000, xorOut=0xFFFF, rev=True)

    def reverse_hex(self, hex_str: str) -> str:
        if len(hex_str) != 4:
            raise ValueError("输入必须是 4位十六进制字符串")
        reversed_str = hex_str[2:] + hex_str[:2]
        return reversed_str.upper()

    def calculate_crc(self, hex_string: str, rev=False) -> int:
        """
        计算十六进制字符串 校验值
        :param rev:
        :param hex_string:
        :return: 计算后的CRC值
        """
        data_bytes = bytes.fromhex(hex_string)
        crc_data = f"{self.crc_func(data_bytes):04X}"

        if rev:
            return int(self.reverse_hex(crc_data), 16)
        else:
            return int(crc_data, 16)


def cal_msg_crc(message: str, beacon_state: int, pixel_service: int) -> int:
    hex_string = str(message.encode('utf-8').hex()) + f"{beacon_state:02X}" + f"{pixel_service:02X}"
    print(f"hex_string: {hex_string}")

    crc = CRC16X25()
    return crc.calculate_crc(hex_string, rev=True)

if __name__ == "__main__":
    print(cal_msg_crc("[jp3]TEST [fl]Flashing[/fl]",0,0))
