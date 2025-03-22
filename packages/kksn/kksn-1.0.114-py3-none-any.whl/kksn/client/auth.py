# -*- coding: utf-8 -*-
import time
import uuid
import wmi
import hashlib
from itertools import zip_longest
import base64
import ntplib
from datetime import datetime, timezone, timedelta


def get_ntp_time(server='ntp1.aliyun.com'):
    count = 0
    while True:
        try:
            client = ntplib.NTPClient()
            response = client.request(server)
            ntp_time = response.tx_time
            utc_time = datetime.fromtimestamp(ntp_time, timezone.utc)
            china_time = utc_time + timedelta(hours=8)
        except Exception as e:
            china_time = None

        if china_time is not None:
            break

        count += 1
        if count > 2:
            break

        time.sleep(1)

    return china_time


def get_a_guid():
    guid = uuid.uuid4().__str__()
    return guid.upper()


def get_hard_info():
    c = wmi.WMI()

    # 获取第一个硬盘的序列号
    disk_number = ''
    for physical_disk in c.Win32_DiskDrive():
        disk_number = physical_disk.SerialNumber.strip()
        break

    # 获取第一个CPU的序列号
    cpu_number = ''
    for cpu in c.Win32_Processor():
        cpu_number = cpu.ProcessorId.strip()
        break

    # 获取第一个BIOS的序列号
    bios_number = ''
    for bios in c.Win32_BIOS():
        bios_number = bios.SerialNumber.strip()
        break

    return disk_number, cpu_number, bios_number


def get_license_txt(disk_number, cpu_number, bios_number):
    uid = get_a_guid()
    paired = zip_longest(disk_number, cpu_number, bios_number, uid, fillvalue='.*.')
    result = '=1='.join([''.join(pair) for pair in paired])
    content = hashlib.md5(result.encode('utf-8')).hexdigest().upper()
    return f'{content}=={uid}'


def auth_license(
        key_file_path='',
        pwd='',
        disk_number='',
        cpu_number='',
        bios_number='',
        ntp=None,
        error_message='',
        expired_message='',
        ntp_error_message=''
):
    china_time = None
    if ntp is not None:
        china_time = get_ntp_time(ntp)

        if china_time is None:
            return False, ntp_error_message

    # 读取授权文件内容
    with open(key_file_path, 'rb') as f:
        key_res = f.read()

    res = base64.b64decode(key_res).decode('utf-8')

    s_list = res.split('==')

    # 没有两个等号的内容，无法通过
    if len(s_list) != 4:
        return False, error_message

    uid = s_list[1]
    paired = zip_longest(disk_number, cpu_number, bios_number, uid, fillvalue='.*.')
    result = '=1='.join([''.join(pair) for pair in paired])
    content = hashlib.md5(result.encode('utf-8')).hexdigest().upper()

    pwd_md5 = hashlib.md5(pwd.encode('utf-8')).hexdigest()
    paired = zip_longest(content, pwd_md5, fillvalue='00')
    content = '//'.join([''.join(pair) for pair in paired])

    # 序列号不一致，无法通过
    if content != s_list[0]:
        return False, error_message

    try:
        timestamp = int(s_list[2])
    except Exception as e:
        # 无法变为时间戳，无法通过
        return False, error_message

    if china_time is None:
        now_timestamp = int(datetime.now().timestamp())
    else:
        now_timestamp = int(china_time.timestamp())

    # 在有效时间内，通过
    if now_timestamp <= timestamp:
        return True, ''

    return False, expired_message
