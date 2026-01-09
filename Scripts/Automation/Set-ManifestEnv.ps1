# =========================
# File: Scripts/Automation/Set-ManifestEnv.ps1
# Purpose: Set MANIFEST_* env vars for the current session AND persist them for GitHub Actions via $GITHUB_ENV.
# =========================
[CmdletBinding()]
param(
    [Parameter()]
    [string]$KeyId = $(if ($env:MANIFEST_KEY_ID) { $env:MANIFEST_KEY_ID } else { "" }),

    [Parameter()]
    [string]$HmacKey = $(if ($env:MANIFEST_HMAC_KEY) { $env:MANIFEST_HMAC_KEY } else { "" }),

    [Parameter()]
    [switch]$HmacKeyIsBase64 = $(if ($env:MANIFEST_HMAC_KEY_IS_BASE64 -eq "true") { $true } else { $false }),

    [Parameter()]
    [switch]$FailIfMissing
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Set-EnvVar([Parameter(Mandatory)][string]$Name, [Parameter(Mandatory)][string]$Value) {
    Set-Item -Path "Env:$Name" -Value $Value

    if ($env:GITHUB_ENV) {
        $delim = "EOF_$([Guid]::NewGuid().ToString('N'))"
        Add-Content -LiteralPath $env:GITHUB_ENV -Value ("{0}<<{1}`n{2}`n{1}" -f $Name, $delim, $Value)
    }
}

if ([string]::IsNullOrWhiteSpace($KeyId) -or [string]::IsNullOrWhiteSpace($HmacKey)) {
    if ($FailIfMissing) {
        throw "Missing manifest env vars. Require MANIFEST_KEY_ID and MANIFEST_HMAC_KEY (or -KeyId/-HmacKey)."
    }
}

Set-EnvVar -Name "MANIFEST_KEY_ID" -Value ($KeyId ?? "")
Set-EnvVar -Name "MANIFEST_HMAC_KEY" -Value ($HmacKey ?? "")
Set-EnvVar -Name "MANIFEST_HMAC_KEY_IS_BASE64" -Value ($(if ($HmacKeyIsBase64) { "true" } else { "false" }))

Write-Host ("Manifest env synced. MANIFEST_KEY_ID='{0}', HMAC set={1}, base64={2}" -f $KeyId, (-not [string]::IsNullOrWhiteSpace($HmacKey)), $HmacKeyIsBase64)
