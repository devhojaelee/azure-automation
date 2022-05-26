#from sla import *
from openpyxl import load_workbook
import os
import subprocess
import warnings
warnings.simplefilter("ignore")

wb = load_workbook("/Users/hojaelee/Desktop/powershell/hanwha.xlsx")
ws = wb['3.3 SLA 분석 평가']
os.system('az account set -s ca9621d4-bfba-4a66-8f48-c4c7eaa0a21f')

# get vm_id
max_row = ws.max_row
while max_row < 0:

    max_row -= 1


vm_id = os.popen(
    'az vm show -g '+str(ws.cell(9, 5).value)+' -n '+str(ws.cell(9, 3).value)+' --query id').read()

# 일단은 동일 리전이라고 가정 (추후 추가)

# get disk info
disk_data = os.popen(
    ('az vm show -g stress-linux_group -n stress-linux --query "storageProfile" |grep "storageAccountType"')).read()

# data parsing
disk_data = disk_data.replace(" ", "").replace(
    '"storageAccountType":', '').replace('"', '')
disk_data = disk_data.split('\n')


# Single vm instance
pre_ssd_cnt = 0
std_ssd_cnt = 0
std_hdd_cnt = 0

for idx, value in enumerate(disk_data[:-1]):
    print(str(idx)+' : '+value)
    if value == 'Premium_LRS':
        pre_ssd_cnt += 1
    elif value == 'StandardSSD_LRS':
        std_ssd_cnt += 1
    elif value == 'Standard_LRS':
        std_hdd_cnt += 1
    else:
        print("추가되지 않은 Disk SKU가 입력되었습니다. 스크립트 개발자에게 알려주세요.")

if pre_ssd_cnt >= 1:
    print("99.9%")
elif pre_ssd_cnt == 0 and std_ssd_cnt >= 1:
    print("99.5%")
elif pre_ssd_cnt == 0 and std_ssd_cnt == 0 and std_hdd_cnt >= 1:
    print("99%")
else:
    print("something wrong")

wb.save("/Users/hojaelee/desktop/powershell/gather_metric.xlsx")
