# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/2/19 19:33

def string_to_bytes_length(string: str) -> int:
    """
    字符串对应字节长度
    :param string:
    :return:
    """
    # byte = len(str(string.encode('utf-8').hex()))/2
    # print(byte)
    return len(string.encode('utf-8'))


if __name__ == "__main__":
    print(string_to_bytes_length("FFFFFF0700010000C0A8017A"))