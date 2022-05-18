#powershell Az CLI, ImportExcel
#Install-Module ImportExcel

#구독 지정
az account set -s ca9621d4-bfba-4a66-8f48-c4c7eaa0a21f

#엑셀 위치 지정
$excel_path = "/Users/hojaelee/Desktop/powershell/gather_metric.xlsx"

#엑셀에 대한 변수 지정
#$metric = Import-Excel -WorksheetName "Metric" -Path $excel_path
#$setting = Import-Excel -WorksheetName "Setting" -Path $excel_path
$max = 0

$raw_data = az monitor metrics list --resource "/subscriptions/ca9621d4-bfba-4a66-8f48-c4c7eaa0a21f/resourceGroups/HJ/providers/Microsoft.Compute/virtualMachines/vm-test" `
    --metric "Percentage CPU" --interval 1m --offset 1d --aggregation Average | grep average

#$raw_data.replace('"average": ', "")
$raw_data = $raw_data -replace ('"average": ', "") -split "," -replace ('              ', '')#파싱을 위해서 빈칸 제거

for ($cnt = 0; $cnt -lt ($raw_data.length - 1); $cnt += 1) {
    if ('null' -eq $raw_data[$cnt]) {
        $raw_data.set($cnt, 0)
    }
}

for ($cnt = 0; $cnt -lt ($raw_data.length - 1); $cnt += 1) {
    if ($raw_data[$cnt] -gt $max) {
        $max = $raw_data[$cnt]
    }
}

Write-Output $max

#echo $raw_data.replace('`n', '')