#-*-coding=utf8 -*-
import os
import re
import time
from scriptUtils.utils import AndroidUtils

class DeviceInfo():
    def __init__(self):
        self.android = AndroidUtils()
    '''
        获取连接上电脑的手机设备，返回一个设备名的list
    '''
    def get_devices(self):
        sno_list = self.android.get_device_list()
        return sno_list

    '''
    根据不同的需求，设计了返回dict和list格式的两个function。
    '''
    def get_devices_as_dict(self):
        try:
            info = {}
            lists = self.get_devices()
            if not lists or len(lists) <= 0:
                print ">>>NO Device connected"
                return None
            for sno in lists:
                sno,phone_brand,phone_model,os_version,dpi,image_resolution,ip = self.get_info(sno)
                info[sno] = {"phone_brand":phone_brand,"phone_model":phone_model,"os_version":os_version,"dpi":dpi,"image_resolution":image_resolution,"ip":ip}
            return info
        except TypeError,e:
            return None

    def get_devices_as_list(self):
        info_list = self.get_devices_as_dict()
        devices_as_lsit = ["All"]
        for i in info_list:
            a = info_list[i]["phone_brand"]
            b = info_list[i]["phone_model"]
            c = info_list[i]["os_version"]
            d = info_list[i]["dpi"]
            e = info_list[i]["image_resolution"]
            f = info_list[i]["ip"]
            t = a+"  ::  "+b+"  ::  "+c+"  ::  "+d+"  ::  "+e+"  ::  "+f
            devices_as_lsit.append(t)
        return devices_as_lsit

    '''
    通过adb命令来获取连接上电脑的设备的信息。
    '''
    def get_info(self,sno):
        try:
            result = self.android.shell(sno, "cat /system/build.prop").stdout.readlines()
            for res in result:
                #系统版本
                if re.search(r"ro\.build\.version\.release",res):
                    os_version = res.split('=')[-1].strip()
                #手机型号
                elif re.search(r"ro\.product\.model",res):
                    phone_model = res.split('=')[-1].strip()
                #手机品牌
                elif re.search(r"ro\.product\.brand",res):
                    phone_brand = res.split('=')[-1].strip()
            ip = self.android.shell(sno,"getprop dhcp.wlan0.ipaddress").stdout.read()
            dpi = self.android.shell(sno, "getprop ro.sf.lcd_density").stdout.read()
            res_4_2 = self.android.shell(sno, "dumpsys window").stdout.read()
            res_4_4 = self.android.shell(sno,"wm size").stdout.read()
            r_4_2 = "init=(\d*x\d*)"
            r_4_4 = "Physical size: (\d*x\d*)"
            reg_4_4 = re.compile(r_4_4)
            reg_4_2 = re.compile(r_4_2)
            image_list_4_4 = re.findall(reg_4_4,res_4_4)
            image_list_4_2 = re.findall(reg_4_2,res_4_2)
            if len(image_list_4_4) > 0:
                image_resolution = image_list_4_4[0]
            elif len(image_list_4_2) > 0:
                image_resolution = image_list_4_2[0]
            else:
                image_resolution = "NULL"
            return sno,phone_brand,phone_model,os_version,dpi,image_resolution,ip
        except Exception,e:
            print ">>> Get device info happend ERROR :"+ str(e)
            return None

    def input_text(self,sno,text):
        text_list = list(text)
        specific_symbol = set(['&','@','#','$','^','*'])
        for i in range(len(text_list)):
            if text_list[i] in specific_symbol:
                if i-1 < 0:
                    text_list.append(text_list[i])
                    text_list[0] = "\\"
                else:
                    text_list[i-1] = text_list[i-1] + "\\"
        seed = ''.join(text_list)
        self.android.shell(sno, 'input text "%s"'%seed)

    def reboot_device(self,sno):
        self.android.adb(sno, "reboot")

    def capture_window(self,sno):
        self.android.shell(sno, "rm /sdcard/screenshot.png")
        self.android.shell(sno, "/system/bin/screencap -p /sdcard/screenshot.png")
        c_time = time.strftime("%Y_%m_%d_%H-%M-%S")
        self.android.adb(sno, 'pull /sdcard/screenshot.png C:/Users/jayzhen/Desktop/%s.png"'%c_time)

