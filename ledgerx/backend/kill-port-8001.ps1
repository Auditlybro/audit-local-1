# Free port 8001 so LedgerX backend can bind (run from repo root or ledgerx/backend)
$p = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($p) { Stop-Process -Id $p -Force; Write-Host "Stopped process on 8001" } else { Write-Host "Nothing listening on 8001" }
