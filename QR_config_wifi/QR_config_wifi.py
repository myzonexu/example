#!/usr/bin/env python   
# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
File   Name ： QR_config_wifi.py
Description :  通过二维码配置自动加入wifi
Author      :  simon
Create Time ： 2022.6.20
-------------------------------------------------------------------------------
Change Activity:
               时间:更改内容
-------------------------------------------------------------------------------
"""
__author__ = 'simon'

'''
使用前需安装以下模块:
pip install pywifi comtypes pyzbar
'''

import time
import pywifi
from pywifi import const
import cv2
import numpy as np
from pyzbar import pyzbar
import re

def decode_qr(img):
    """
    解析二维码.
 
    :param img: opencv二维码图像
    :returns: str,二维码解码信息
    :raises: no exception
    """
    _info_list=pyzbar.decode(img)
    if _info_list == []:
        _ret=False
        _info=""
    else:
        _ret=True
        _info=_info_list[0].data.decode("utf-8")
        print(f'二维码信息:{_info}')
    #_info=pyzbar.decode(img)[0].data.decode("utf-8")
    
    return _ret,_info


def decode_wifi_info(info):
    """
    解析wifi信息，获取wifi参数.
    WIFI:T:WPA;S:xxxx;P:xxxx;;
 
    :param info: str,wifi信息
    :returns: wifi参数ssid, akm, key
    :raises: no exception
    """
    _akm_dict={"WPA":const.AKM_TYPE_WPA2PSK,}

    _ssid=re.search( r'S:(.+?);', info).group(1)
    _akm_str=re.search( r'WIFI:T:(.+?);', info).group(1)
    _key=re.search( r'P:(.+?);', info).group(1)
    print(f'wifi信息：\n  ssid：{_ssid}\n  密钥管理类型：{_akm_str}\n  密码：{_key}')
    _akm=_akm_dict.get(_akm_str)
    return _ssid,_akm,_key

def connect_wifi(ssid, akm,  key, auth=const.AUTH_ALG_OPEN,cipher=const.CIPHER_TYPE_CCMP):
    """
    连接wifi.
    
    :param ssid: str,AP的ssid名
    :param akm: AP的密钥管理类型:
                - const.AKM_TYPE_NONE
                - const.AKM_TYPE_WPA
                - const.AKM_TYPE_WPAPSK
                - const.AKM_TYPE_WPA2
                - const.AKM_TYPE_WPA2PSK
    :param key: str,AP的密码
                - 如果cipher不是CIPHER_TYPE_NONE，则应设置此值。
    :param auth: AP的认证算法
                - const.AUTH_ALG_OPEN(大部分为该类型)
                - const.AUTH_SHARED
    :param cipher: AP的密码类型
                - const.CIPHER_TYPE_NONE
                - const.CIPHER_TYPE_WEP
                - const.CIPHER_TYPE_TKIP
                - const.CIPHER_TYPE_CCMP(大部分为该类型)
    :returns: bool,wifi连接是否成功
    :raises: no exception
    """
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    iface.disconnect()
    time.sleep(2)
    wifi_status = iface.status()
    if wifi_status == const.IFACE_DISCONNECTED:
        profile = pywifi.Profile()
        profile.ssid = ssid
        profile.auth = auth
        profile.akm.append(akm)
        profile.cipher = cipher
        if cipher != const.CIPHER_TYPE_NONE:
            profile.key = key
        #iface.remove_all_network_profiles()
        tep_profile = iface.add_network_profile(profile)
        iface.connect(tep_profile)
        time.sleep(2)
        if iface.status() == const.IFACE_CONNECTED:
            print(f'连接wifi: {ssid} 成功')
            return True
        else:
            print(f'连接wifi: {ssid} 失败')
            return False
    return False



if __name__ == "__main__":
    #decode_wifi_info("WIFI:T:WPA;S:xxxx;P:xxxx;;")
    
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    while True:
        # 逐帧捕获
        ret, frame = cap.read()
        # 如果正确读取帧，ret为True
        if not ret:
            break
        # 显示结果帧
        cv2.imshow('frame', frame)
        ret,info=decode_qr(frame)
        if ret:
            wifi_set=decode_wifi_info(info)
            #connect_wifi(wifi_set[0],wifi_set[1],wifi_set[2]) 
            connect_wifi(*wifi_set)

        if cv2.waitKey(1) == ord('q'):
            break
    # 完成所有操作后，释放捕获器
    cap.release()
    cv2.destroyAllWindows()

