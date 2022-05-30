# from sla import *
from xml.etree.ElementTree import register_namespace
from openpyxl import load_workbook
import os
import subprocess
import warnings
import json  # for string to json
warnings.simplefilter("ignore")

wb = load_workbook("/Users/hojaelee/Desktop/powershell/hanwha.xlsx")
ws = wb['3.3 SLA 분석 평가']
os.system('az account set -s ca9621d4-bfba-4a66-8f48-c4c7eaa0a21f')

# type이 Virtual machine, SQL Virtual machine일 경우, SLA 계산
# 우선 VM이 SLA 계산도 고려해야 할 것도 많고 복잡해서 자동화 타겟으로 정함.

# 1. 동일한 Region에서 / 2개 이상의 AZ에 / 배포된 2개 이상의 인스턴스는 /, 그 중 적어도 한 인스턴스는 99.99% /
# 그럼 가장 높은 SLA의 VM만 99.99% /, 나머지는 single instance SLA 따라감
# 2. 동일한 AVset / or Dedicated host group에서 / 배포된 2개 이상의 인스턴스는 /, 그 중 적어도 한 인스턴스는 99.95% /
# 그럼 가장 높은 SLA의 VM만 99.99% /, 나머지는 single instance SLA 따라감

# Future work : 1) 엑셀에서 SLA 고려안 할 대상 행 삭제

max_row = 500  # (수동으로 최대 row 값 입력해줄 것. ws.max_row 이 값을 제대로 못읽어옴.)
current_row = 6  # 엑셀에서 데이터가 6행부터 시작
# API 호출은 한 번만.
vm_data_obj = json.loads(os.popen(('az vm list --output json')).read())
vm_cnt = 0

while max_row > 0:
    if ws['D'+str(current_row)].value == ('Virtual machine' or 'SQL virtual machine'):
        rg_name = str(ws['E'+str(current_row)].value)  # 엑셀에서 rg, vm name 읽어옴
        vm_name = str(ws['C'+str(current_row)].value)
        region = str(ws['F'+str(current_row)].value)
        region_check = []
        av_zone = []
        print("vm name : "+vm_data_obj[vm_cnt]["name"])
    # get disk info (Future work? : 매번 정보를 받아올 필요가 없다. 디스크 정보 시트를 따로 만들고 거기서 긁어오면 처리 시간 훨씬 단축 가능. 속도만 보자면.)
        print('vm_cnt : '+str(vm_cnt))
        total_data_disks = len(
            vm_data_obj[vm_cnt]["storageProfile"]["dataDisks"])
        print("total_data_disks : "+str(total_data_disks))
        data_disk = []
        os_disk = []
        data_disk_cnt = 0

        # data disk type check
        while total_data_disks > data_disk_cnt:
            data_disk.append(vm_data_obj[vm_cnt]["storageProfile"]["dataDisks"][data_disk_cnt]
                             ["managedDisk"]["storageAccountType"])
            data_disk_cnt += 1
        # os disk type check
        os_disk = vm_data_obj[vm_cnt]["storageProfile"]["osDisk"]["managedDisk"]["storageAccountType"]
        print("os_disk : "+os_disk)
        print('disk_data : '+str(data_disk))

        # Single vm instance
        pre_ssd_cnt = 0
        std_ssd_cnt = 0
        std_hdd_cnt = 0

        # os_disk type count
        if os_disk == 'Premium_LRS':
            pre_ssd_cnt += 1
        elif os_disk == 'StandardSSD_LRS':
            std_ssd_cnt += 1
        elif os_disk == 'Standard_LRS':
            std_hdd_cnt += 1

        # data_disks type count
        for idx, value in enumerate(data_disk[:-1]):
            print(str(idx)+' : '+value)
            if value == 'Premium_LRS':  # or 'Ultradisk??_LRS???' :  # ultradisk 추가 요망
                pre_ssd_cnt += 1
            elif value == 'StandardSSD_LRS':
                std_ssd_cnt += 1
            elif value == 'Standard_LRS':
                std_hdd_cnt += 1
            else:
                print("ultradisk이거나 VM이 꺼져있습니다.\n")

        print('Premium ssd : '+str(pre_ssd_cnt))
        print('standard ssd : '+str(std_ssd_cnt))
        print('hdd : '+str(std_hdd_cnt))

        # Single VM instance's SLA check
        if std_hdd_cnt >= 1:
            ws['K'+str(current_row)].value = '99%'
            print("99%\n------\n")
        elif std_hdd_cnt == 0 and std_ssd_cnt >= 1:
            ws['K'+str(current_row)].value = '99.5%'
            print("99.5%\n------\n")
        elif std_hdd_cnt == 0 and std_ssd_cnt == 0 and pre_ssd_cnt >= 1:
            ws['K'+str(current_row)].value = '99.9%'
            print("99.9%\n------\n")
        else:
            # 반드시 os disk는 존재하므로, os_disk가 ultradisk 아닌 이상 위 3개 조건에 해당하지 않으면 vm stopped 간주 가능.
            ws['K'+str(current_row)].value = 'VM stopped'
            print("해당 VM이 켜져있는지 확인하세요.\n------\n")

        vm_cnt += 1

    current_row += 1
    max_row -= 1


wb.save("/Users/hojaelee/desktop/powershell/hanwha.xlsx")
