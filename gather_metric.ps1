#powershell Az CLI, ImportExcel
#Install-Module ImportExcel

#구독 지정
az account set -s ca9621d4-bfba-4a66-8f48-c4c7eaa0a21f

#엑셀 위치 지정
$excel_path = "/Users/hojaelee/Desktop/powershell/gather_metric.xlsx"

#엑셀 워크 시트를 해당 변수로 접근
$metric = Import-Excel -WorksheetName "Metric" -Path $excel_path
$setting = Import-Excel -WorksheetName "Setting" -Path $excel_path
$offset = $setting.offset

foreach ($row in $metric) {
    $vm_id = $(az vm show -g $row.group -n $row.name --query id)
    $result_avg = $(az monitor metrics list --resource $vm_id --metric "Percentage CPU" )
    echo $result_avg
}


$max = 0
$new_dataset = @()
$cnt = 0

#az vm get-instance-view -g stress-linux_group -n stress-linux --query id #resource id 받아올 수 있음.
#az vm show -g stress-linux_group -n stress-linux --query id 이거랑 똑같네
$vm_id = $(az vm show -g $row.group -n $row.name --query id)


$raw_data = az monitor metrics list --resource "/subscriptions/ca9621d4-bfba-4a66-8f48-c4c7eaa0a21f/resourceGroups/HJ/providers/Microsoft.Compute/virtualMachines/vm-test" `
    --metric "Percentage CPU" --interval 1m --offset 30d --aggregation Average | grep average
$raw_data = $raw_data -replace ('"average": ', "") -split "," -replace ('              ', '') #파싱을 위해서 빈칸 제거
$raw_data = $raw_data -replace ('null', "") #string null을 제거
$raw_data = $raw_data.Where({ $_ -ne "" }) #real null을 제거
#echo $raw_data

$raw_data | Measure-Object -AllStats
$total_stats = ($raw_data | Measure-Object -AllStats).maximum

foreach ($i in $raw_data) {
    if ([double]$i -gt 36) {
        $cnt++
        echo $i
    }
}
echo $total_stats
echo 'total cnt:' $cnt

<# Max를 직접 구현하기
for ($cnt = 0; $cnt -lt ($raw_data.length - 1); $cnt += 1) {
    if ('null' -like $raw_data[$cnt]) {
        $raw_data.set($cnt, 0)
    }
    #ADD-Content /Users/hojaelee/Desktop/powershell/type0.txt $raw_data[$cnt] #요건 txt append 함수
    if ([double]$raw_data[$cnt] -gt [double]$max) {
    $max = $raw_data[$cnt]
    }
}
Write-Output $max
#>

