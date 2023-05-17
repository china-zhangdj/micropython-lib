#!/usr/bin/python3 
# -*- coding: utf-8 -*-
# @Time    : 2023/2/8 15:30
# @Author  : engineer-zhangdj
# @File    : i2c.py
# @Software: PyCharm

from fcntl import ioctl
import os

class I2C:
    __IOCTL_I2C_SLAVE = 0x0703
    __IOCTL_I2C_SLAVE_FORCE = 0x0706
    def __init__(self,devpath:str,addr:int):
        '''
        创建设备对象
        :param devpath: 接口文件
        :param addr: 从机地址
        '''
        self.dpath = devpath
        self.addr = addr
        try :
            self.fd = os.open(self.dpath,os.O_RDWR)
        except Exception as e :
            raise OSError("{} not open failed! {}".format(self.dpath,e))
            return None
        r = ioctl(self.fd,self.__IOCTL_I2C_SLAVE,self.addr)
        if r :
            raise OSError("device address already used !")
        pass

    def read(self,raddr:int,length:int=1):
        '''
        读取n字节数据
        :param raddr: 寄存器地址
        :param length: 读取长度
        :return:
        '''
        if self.fd :
            os.write(self.fd,raddr.to_bytes(1,"little"))
            buff = os.read(self.fd,length)
            return buff
        else:
            return b''

    def write(self,raddr:int,data:bytes):
        '''
        写入n字节数据
        :param raddr: 寄存器地址
        :param data: 写入的数据
        :return:
        '''
        if self.fd :
            length = len(data)
            os.write(self.fd,raddr.to_bytes(1,"little") + data)
            return length
        else:
            return 0

