#powershell Az CLI, ImportExcel
#Install-Module ImportExcel
# --no-wait 외 기타 옵션은 필요에 따라서 적절하게



### 구독 정보 수동 입력 - 내 구독에서 테스트
#az account set -s 9293264d-b823-4d1d-b070-aca11b1ab5e1


# 경로 지정
$excel_path = "/Users/hojaelee/Desktop/powershell/test.xlsx"


# 변수 지정
$snapshot = Import-Excel -WorksheetName "Snapshot" -Path $excel_path


#여기서 lun은 그냥 디스크 갯수 구하기 위한거야. lun으로 접근하지 않는다.
$lun = az vm show -g HJ -n snapshot-test-vm --query "storageProfile" -o yaml | grep lun


### Snapshot
# osDisk
foreach ($row in $snapshot) {
    $os_disk_name = $(az vm show -g $row.group -n $row.name --query "storageProfile.osDisk.name")
    az snapshot create -g $row.group -n $os_disk_name"_snapshot" --source $os_disk_name
}


# dataDisks
foreach ($row in $snapshot) {
    for ($i = 0; $i -lt $lun.length; $i++) {
        $data_disk_name = $(az vm show -g $row.group -n $row.name --query "storageProfile.dataDisks[$i].name")
        az snapshot create -g $row.group -n $data_disk_name"_snapshot" --source $data_disk_name
    }
}
