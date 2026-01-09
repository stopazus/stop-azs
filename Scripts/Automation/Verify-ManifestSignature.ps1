# =========================
# File: Scripts/Automation/Verify-ManifestSignature.ps1
# Purpose: Verify tamper-evidence for sha256-manifest-*.json:
#          - recompute row canonical strings
#          - recompute per-row HMACs (HMAC-SHA256)
#          - recompute master SHA256 over all canonical rows
#          - recompute master HMAC over all row HMACs
# =========================
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$ManifestJsonPath,

    [Parameter()]
    [string]$ManifestKeyId = $(if ($env:MANIFEST_KEY_ID) { $env:MANIFEST_KEY_ID } else { "" }),

    [Parameter()]
    [string]$ManifestHmacKey = $(if ($env:MANIFEST_HMAC_KEY) { $env:MANIFEST_HMAC_KEY } else { "" }),

    [Parameter()]
    [switch]$ManifestHmacKeyIsBase64 = $(if ($env:MANIFEST_HMAC_KEY_IS_BASE64 -eq "true") { $true } else { $false }),

    [Parameter()]
    [switch]$FailIfUnsigned = $true
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-BytesSha256Hex {
    param([Parameter(Mandatory)][byte[]]$Bytes)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { ($sha.ComputeHash($Bytes) | ForEach-Object { $_.ToString("x2") }) -join "" }
    finally { $sha.Dispose() }
}

function Resolve-HmacKeyBytes {
    param([Parameter(Mandatory)][string]$Key, [Parameter()][switch]$IsBase64)
    if ($IsBase64) { return [Convert]::FromBase64String($Key) }
    [System.Text.Encoding]::UTF8.GetBytes($Key)
}

function Compute-HmacSha256Hex {
    param([Parameter(Mandatory)][byte[]]$KeyBytes, [Parameter(Mandatory)][string]$Data)
    $h = [System.Security.Cryptography.HMACSHA256]::new($KeyBytes)
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Data)
        ($h.ComputeHash($bytes) | ForEach-Object { $_.ToString("x2") }) -join ""
    } finally { $h.Dispose() }
}

function Escape-Canon([string]$s) {
    if ($null -eq $s) { return "" }
    $s.Replace("\", "\\").Replace("|", "\|").Replace("`r", "\r").Replace("`n", "\n")
}

function Canonicalize-ManifestRow {
    param([Parameter(Mandatory)]$Row)

    $pairs = @(
        "timestampUtc=$(Escape-Canon $Row.timestampUtc)"
        "sourceProvider=$(Escape-Canon $Row.sourceProvider)"
        "operation=$(Escape-Canon $Row.operation)"
        "sourcePath=$(Escape-Canon $Row.sourcePath)"
        "destinationPath=$(Escape-Canon $Row.destinationPath)"
        "bytes=$(Escape-Canon ([string]$Row.bytes))"
        "sourceSha256=$(Escape-Canon $Row.sourceSha256)"
        "destinationSha256=$(Escape-Canon $Row.destinationSha256)"
        "verifySize=$(Escape-Canon ([string]$Row.verifySize))"
        "verifyHash=$(Escape-Canon ([string]$Row.verifyHash))"
        "verifyXml=$(Escape-Canon ([string]$Row.verifyXml))"
        "verifyOk=$(Escape-Canon ([string]$Row.verifyOk))"
        "attempts=$(Escape-Canon ([string]$Row.attempts))"
        "retried=$(Escape-Canon ([string]$Row.retried))"
        "quarantinePath=$(Escape-Canon $Row.quarantinePath)"
        "originalPath=$(Escape-Canon $Row.originalPath)"
    )
    $pairs -join "|"
}

if (-not (Test-Path -LiteralPath $ManifestJsonPath)) { throw "Manifest JSON not found: $ManifestJsonPath" }

$envl = Get-Content -LiteralPath $ManifestJsonPath -Raw | ConvertFrom-Json -ErrorAction Stop
if (-not $envl.header -or -not $envl.rows) { throw "Invalid manifest JSON structure (missing header/rows)." }

$hdr = $envl.header
$rows = @($envl.rows)

if ($hdr.algorithm -ne "HMAC-SHA256") { throw "Unsupported algorithm: $($hdr.algorithm)" }
if (-not [string]::IsNullOrWhiteSpace($ManifestKeyId) -and -not [string]::IsNullOrWhiteSpace($hdr.keyId) -and ($hdr.keyId -ne $ManifestKeyId)) {
    throw "KeyId mismatch. manifest='$($hdr.keyId)' env/param='$ManifestKeyId'"
}

$signed = [bool]$hdr.signed
if ($FailIfUnsigned -and -not $signed) { throw "Manifest is unsigned but -FailIfUnsigned was set." }

$keyBytes = $null
if ($signed) {
    if ([string]::IsNullOrWhiteSpace($ManifestHmacKey)) { throw "Signed manifest requires MANIFEST_HMAC_KEY (or -ManifestHmacKey)." }
    $keyBytes = Resolve-HmacKeyBytes -Key $ManifestHmacKey -IsBase64:$ManifestHmacKeyIsBase64
}

$failures = New-Object System.Collections.Generic.List[string]

$rowHmacs = New-Object System.Collections.Generic.List[string]
$canonRows = New-Object System.Collections.Generic.List[string]

for ($i = 0; $i -lt $rows.Count; $i++) {
    $r = $rows[$i]

    $canon = Canonicalize-ManifestRow -Row $r
    $canonRows.Add($canon) | Out-Null

    $canonSha = Get-BytesSha256Hex -Bytes ([System.Text.Encoding]::UTF8.GetBytes($canon))

    if ($r.rowCanonical -and ($r.rowCanonical -ne $canon)) {
        $failures.Add("Row[$i] rowCanonical mismatch") | Out-Null
    }
    if ($r.rowCanonicalSha256 -and ($r.rowCanonicalSha256 -ne $canonSha)) {
        $failures.Add("Row[$i] rowCanonicalSha256 mismatch") | Out-Null
    }

    if ($signed) {
        $h = Compute-HmacSha256Hex -KeyBytes $keyBytes -Data $canon
        $rowHmacs.Add($h) | Out-Null

        if ($r.rowHmacSha256 -and ($r.rowHmacSha256 -ne $h)) {
            $failures.Add("Row[$i] rowHmacSha256 mismatch") | Out-Null
        }
        if (-not $r.rowHmacSha256) {
            $failures.Add("Row[$i] missing rowHmacSha256") | Out-Null
        }
    }
}

$canonAll = ($canonRows -join "`n")
$masterSha = Get-BytesSha256Hex -Bytes ([System.Text.Encoding]::UTF8.GetBytes($canonAll))
if ($hdr.masterSha256 -and ($hdr.masterSha256 -ne $masterSha)) {
    $failures.Add("header.masterSha256 mismatch") | Out-Null
}

$masterHmac = $null
if ($signed) {
    $rowHmacAll = ($rowHmacs -join "`n")
    $masterHmac = Compute-HmacSha256Hex -KeyBytes $keyBytes -Data $rowHmacAll
    if ($hdr.masterHmacSha256 -and ($hdr.masterHmacSha256 -ne $masterHmac)) {
        $failures.Add("header.masterHmacSha256 mismatch") | Out-Null
    }
    if (-not $hdr.masterHmacSha256) {
        $failures.Add("header missing masterHmacSha256") | Out-Null
    }
}

if ($failures.Count -gt 0) {
    Write-Host "FAIL: manifest signature verification"
    foreach ($f in $failures) { Write-Host " - $f" }
    throw "Manifest verification failed with $($failures.Count) issue(s)."
}

Write-Host "PASS: manifest verified"
Write-Host ("rows={0} signed={1} masterSha256={2} masterHmacSha256={3}" -f $rows.Count, $signed, $masterSha, ($masterHmac ?? ""))
exit 0
