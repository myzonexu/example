#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
File   Name ： moter_test.py
Description :  测试步科电机
Author      :  simon
Create Time ： 2022.6.14
-------------------------------------------------------------------------------
Change Activity:
               时间:更改内容
-------------------------------------------------------------------------------
"""
__author__ = 'simon'


import serial
import time
import struct

class Frame(object):
    
    def __init__(self):
        """通讯帧."""        
        self._data_bytes=bytes()
        self.id=0  
        self.func=0
        self.index=0
        self.sub_index=0
        self.data_value=0
        self.chks=0
        self._resolution=10000
    
    @property
    def data_bytes(self):
        """
        获取帧字节串.
    
        :returns: bytes,帧字节串
        :raises: no exception
        """
        _bytes_no_chks=struct.pack('<BBHBi',self.id,self.func,self.index,self.sub_index,self.data_value)
        _data_no_chks=struct.unpack('<BBBBBBBBB',_bytes_no_chks) 
        _bytes_chks=struct.pack('<B',self.get_chks(_data_no_chks))
        self._data_bytes=_bytes_no_chks+_bytes_chks
        print(_data_no_chks,self.chks)
        print(self._data_bytes)

        return  self._data_bytes     
    
    def set_id(self,id):
        """
        设置id.
    
        :param id: int,id
        :returns: int,校验码
        :raises: no exception
        """
        self.id=id    

    def set_work_model(self,model):
        """
        设置工作模式.
     
        :param model: int,工作模式
        :returns: no return
        :raises: no exception
        """
        
        self.func=0x2F
        self.index=0x6060
        self.sub_index=0
        self.data_value=model
    
    def set_speed(self,speed_rpm):
        """
        设定速度.
     
        :param speed_rpm: int,速度rpm
        :returns: no return
        :raises: no exception
        """
        self.func=0x23
        self.index=0x60FF
        self.sub_index=0
        self.data_value=self.rpm_to_dec(speed_rpm)
    
    def set_ctrl(self,value):
        """
        设置控制字.
     
        :param value: int,控制字设置值
        :returns: no return
        :raises: no exception
        """
        self.func=0x2B
        self.index=0x6040
        self.sub_index=0
        self.data_value=value

    def get_chks(self,data):
        """
        设置校验码.
    
        :param data: list/tuple,校验数据
        :returns: int,校验码
        :raises: no exception
        """
        _chks=sum(data)
        self.chks=(-_chks) & 0xFF
        return self.chks

    def rpm_to_dec(self,rpm):
        """
        转速RPM换算为DEC,
        DEC=[(RPM*512*编码器分辨率)/1875].
 
        :param rpm: int,转速rpm
        :returns: int,DEC
        :raises: no exception 
        """ 
        return int(rpm*512*self._resolution/1875)


class FrameGroup(object):
    
    def __init__(self):
        """通讯帧组."""        
        self.frames=[]

    def set_motor_speed(self,id,speed_rpm):
        """
        设定电机转速.

        :param id: int,驱动器id
        :param speed_rpm: int,速度rpm
        :returns: list,数据帧组
        :raises: no exception
        """
        self.frames=[]
        _frame=Frame()
        _frame.set_id(id)
        _frame.set_work_model(0x03)
        self.frames.append(_frame.data_bytes)
        _frame.set_speed(speed_rpm)
        self.frames.append(_frame.data_bytes)
        _frame.set_ctrl(0x0F)
        self.frames.append(_frame.data_bytes)
        return self.frames

if __name__ == '__main__':
    #serial_motor=serial.Serial('/dev/ttyS4',38400,timeout=0.5)
    motor_frames=FrameGroup()
    while True:
        print("请输入设定速度：")
        speed=int(input())
        motor_frames.set_motor_speed(1,speed)
        #for _frame in motor_frames.frames:
            #serial_motor.write(_frame)


                          


