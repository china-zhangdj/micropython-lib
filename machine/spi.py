#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2023/2/24 11:20
# @Author  : engineer-zhangdj
# @File    : spi.py
# @Software: PyCharm
import fcntl
import struct
import os

SPI_RD_MODE = const(0x80016b01)
SPI_WR_MODE = const(0x40016b01)
SPI_RD_MAX_SPEED_HZ = const(0x80046b04)
SPI_WR_MAX_SPEED_HZ = const(0x40046b04)
SPI_RD_BITS_PER_WORD = const(0x80016b03)
SPI_WR_BITS_PER_WORD = const(0x40016b03)


class SPI :
    def __init__(self,fpath,mode=False,speed=False,bits_per_word=False):
        self.fd = os.open(fpath,os.O_RDWR)
        if self.speed :
            self.speed = speed
        if self.mode :
            self.mode = mode
        if self.bits_per_word:
            self.bits_per_word = bits_per_word
        pass

    def write(self,data:bytes):
        if self.fd :
            num = os.write(self.fd,data)
            return num
        return False

    def read(self,len:int):
        if self.fd :
            ret = os.read(self.fd,len)
            return ret
        return b''

    @property
    def mode(self):
        if self.fd:
            data = struct.pack("I",0)
            ret = fcntl.ioctl(self.fd,SPI_RD_MODE,data,True)
            if ret == 0 :
                data = struct.unpack("I",data)[0]
                return data
        return False
    @mode.setter
    def mode(self,mode:int):
        if self.fd :
            data = struct.pack("I",mode)
            ret = fcntl.ioctl(self.fd,SPI_WR_MODE,data,True)
            if ret == 0 :
                return True
        return False

    @property
    def speed(self):
        if self.fd :
            data = struct.pack("I",0)
            ret = fcntl.ioctl(self.fd,SPI_RD_MAX_SPEED_HZ,data,True)
            if ret == 0 :
                data = struct.unpack("I",data)[0]
                return data
            pass
        return False

    @speed.setter
    def speed(self,speed_hz:int):
        if self.fd :
            data = struct.pack("I",speed_hz)
            ret = fcntl.ioctl(self.fd,SPI_WR_MAX_SPEED_HZ,data,True)
            if ret == 0 :
                return True
        return False

    @property
    def bits_per_word(self):
        if self.fd:
            data = struct.pack("I", 0)
            ret = fcntl.ioctl(self.fd, SPI_RD_BITS_PER_WORD,data, True)
            if ret == 0:
                data = struct.unpack("I", data)[0]
                return data
            pass
        return False

    @bits_per_word.setter
    def bits_per_word(self, bits_per_word: int):
        if self.fd:
            data = struct.pack("I", bits_per_word)
            ret = fcntl.ioctl(self.fd, SPI_WR_BITS_PER_WORD, data, True)
            if ret == 0:
                return True
        return False

