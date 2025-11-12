#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Windows NAS Bootstrap - Installs apps and maps NAS drives
.DESCRIPTION
    This script installs essential applications via winget and maps NAS drives.
    Generated: 2025-11-05 21:04
#>

[CmdletBinding()]
param()

# Set error action preference
$ErrorActionPreference = 'Continue'

# Function to write colored output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = 'White'
    )
    Write-Host $Message -ForegroundColor $Color
}

# Function to install an app via winget
function Install-App {
    param(
        [string]$AppId,
        [string]$AppName
    )
    
    Write-ColorOutput "`nInstalling $AppName..." -Color Cyan
    try {
        $installResult = winget install --id $AppId --silent --accept-package-agreements --accept-source-agreements 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ $AppName installed successfully" -Color Green
            return $true
        } else {
            Write-ColorOutput "✗ $AppName installation failed or already installed" -Color Yellow
            return $false
        }
    } catch {
        Write-ColorOutput "✗ Error installing $AppName : $_" -Color Red
        return $false
    }
}

# Function to map network drive
function Map-NetworkDrive {
    param(
        [string]$DriveLetter,
        [string]$NetworkPath,
        [string]$Username,
        [System.Security.SecureString]$Password
    )
    
    Write-ColorOutput "`nMapping $DriveLetter to $NetworkPath..." -Color Cyan
    
    try {
        # Remove existing mapping if it exists
        if (Test-Path "$DriveLetter") {
            Write-ColorOutput "Removing existing mapping for $DriveLetter" -Color Yellow
            net use "$DriveLetter" /delete /y 2>&1 | Out-Null
        }
        
        # Convert SecureString to plain text for net use command
        # Note: Using 'net use' for maximum compatibility with older Windows systems
        # Password is cleared from memory immediately after use
        $secureStringBSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($Password)
        $plainTextPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($secureStringBSTR)
        [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($secureStringBSTR)
        
        # Map the drive with persistence
        $mapResult = net use "$DriveLetter" "$NetworkPath" /user:$Username $plainTextPassword /persistent:yes 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ $DriveLetter mapped successfully" -Color Green
            return $true
        } else {
            Write-ColorOutput "✗ Failed to map $DriveLetter : $mapResult" -Color Red
            return $false
        }
    } catch {
        Write-ColorOutput "✗ Error mapping $DriveLetter : $_" -Color Red
        return $false
    }
}

# Function to perform speed test
function Test-NetworkSpeed {
    param(
        [string]$DriveLetter,
        [int]$testFileSizeMiB = 1024  # 1 GiB = 1024 MiB
    )
    
    Write-ColorOutput "`n=== Network Speed Test ===" -Color Magenta
    Write-ColorOutput "Testing write speed to $DriveLetter (1 GiB file)..." -Color Cyan
    
    $testFile = $null
    try {
        $testFile = "$DriveLetter\speedtest_$(Get-Date -Format 'yyyyMMdd_HHmmss').tmp"
        
        # Create a 1 GiB test file using 64 MiB buffer for better performance
        $startTime = Get-Date
        $bufferSizeMiB = 64
        $bufferSizeBytes = $bufferSizeMiB * 1024 * 1024  # MiB to bytes
        $buffer = New-Object byte[] $bufferSizeBytes
        $random = New-Object System.Random
        $random.NextBytes($buffer)
        
        $stream = $null
        try {
            $stream = [System.IO.File]::OpenWrite($testFile)
            $iterations = [int]($testFileSizeMiB / $bufferSizeMiB)
            for ($i = 0; $i -lt $iterations; $i++) {
                $stream.Write($buffer, 0, $buffer.Length)
                $progress = [int](($i / $iterations) * 100)
                Write-Progress -Activity "Writing test file" -Status "$progress% Complete" -PercentComplete $progress
            }
        } finally {
            if ($null -ne $stream) {
                $stream.Close()
                $stream.Dispose()
            }
        }
        $endTime = Get-Date
        
        $duration = ($endTime - $startTime).TotalSeconds
        $transferSpeedMBps = [math]::Round($testFileSizeMiB / $duration, 2)
        
        Write-ColorOutput "✓ Write Speed: $transferSpeedMBps MiB/s" -Color Green
        
        # Read speed test
        Write-ColorOutput "Testing read speed from $DriveLetter..." -Color Cyan
        $startTime = Get-Date
        $stream = $null
        try {
            $stream = [System.IO.File]::OpenRead($testFile)
            $readBuffer = New-Object byte[] $bufferSizeBytes
            while ($stream.Read($readBuffer, 0, $readBuffer.Length) -gt 0) {
                # Just read, don't process
            }
        } finally {
            if ($null -ne $stream) {
                $stream.Close()
                $stream.Dispose()
            }
        }
        $endTime = Get-Date
        
        $duration = ($endTime - $startTime).TotalSeconds
        $transferSpeedMBps = [math]::Round($testFileSizeMiB / $duration, 2)
        
        Write-ColorOutput "✓ Read Speed: $transferSpeedMBps MiB/s" -Color Green
        
        # Clean up test file
        Remove-Item $testFile -Force
        Write-ColorOutput "✓ Test file cleaned up" -Color Green
        
    } catch {
        Write-ColorOutput "✗ Speed test failed: $_" -Color Red
        if ($null -ne $testFile -and (Test-Path $testFile)) {
            Remove-Item $testFile -Force -ErrorAction SilentlyContinue
        }
    }
}

# Main execution
Write-ColorOutput "========================================" -Color Magenta
Write-ColorOutput "   Windows NAS Bootstrap Setup" -Color Magenta
Write-ColorOutput "   Generated: 2025-11-05 21:04" -Color Magenta
Write-ColorOutput "========================================" -Color Magenta

# Check if winget is available
Write-ColorOutput "`nChecking for winget..." -Color Cyan
try {
    $wingetVersion = winget --version
    Write-ColorOutput "✓ winget is available: $wingetVersion" -Color Green
} catch {
    Write-ColorOutput "✗ winget is not available. Please install App Installer from Microsoft Store." -Color Red
    exit 1
}

# Define apps to install
$applications = @(
    @{ Id = "Python.Python.3.12"; Name = "Python 3.12" },
    @{ Id = "Git.Git"; Name = "Git" },
    @{ Id = "Rclone.Rclone"; Name = "rclone" },
    @{ Id = "Microsoft.VisualStudioCode"; Name = "VS Code" },
    @{ Id = "7zip.7zip"; Name = "7-Zip" },
    @{ Id = "VideoLAN.VLC"; Name = "VLC" },
    @{ Id = "WinSCP.WinSCP"; Name = "WinSCP" },
    @{ Id = "PuTTY.PuTTY"; Name = "PuTTY" }
)

# Install applications
Write-ColorOutput "`n=== Installing Applications ===" -Color Magenta
$successCount = 0
$failCount = 0

foreach ($application in $applications) {
    if (Install-App -AppId $application.Id -AppName $application.Name) {
        $successCount++
    } else {
        $failCount++
    }
}

Write-ColorOutput "`nInstallation Summary: $successCount succeeded, $failCount failed" -Color $(if ($failCount -eq 0) { 'Green' } else { 'Yellow' })

# Prompt for NAS credentials
Write-ColorOutput "`n=== NAS Drive Mapping ===" -Color Magenta
$username = "downloader"
Write-ColorOutput "Enter password for NAS user '$username':" -Color Cyan
$password = Read-Host -AsSecureString

# Define NAS drives
$networkDrives = @(
    @{ Letter = "G:"; Path = "\\nas\Cloud-GDrive"; Description = "Google Drive" },
    @{ Letter = "I:"; Path = "\\nas\Cloud-iCloud"; Description = "iCloud" },
    @{ Letter = "O:"; Path = "\\nas\Cloud-OneDrive"; Description = "OneDrive" }
)

# Map drives
$mappedCount = 0
$firstMappedDrive = $null

foreach ($networkDrive in $networkDrives) {
    Write-ColorOutput "`nMapping $($networkDrive.Letter) → $($networkDrive.Path) ($($networkDrive.Description))" -Color Cyan
    if (Map-NetworkDrive -DriveLetter $networkDrive.Letter -NetworkPath $networkDrive.Path -Username $username -Password $password) {
        $mappedCount++
        if ($null -eq $firstMappedDrive) {
            $firstMappedDrive = $networkDrive.Letter
        }
    }
}

Write-ColorOutput "`nDrive Mapping Summary: $mappedCount of $($networkDrives.Count) drives mapped" -Color $(if ($mappedCount -eq $networkDrives.Count) { 'Green' } else { 'Yellow' })

# Run speed test if at least one drive was mapped
if ($null -ne $firstMappedDrive) {
    $response = Read-Host "`nRun 1 GiB speed test on $firstMappedDrive? (Y/N)"
    if ($response -eq 'Y' -or $response -eq 'y') {
        Test-NetworkSpeed -DriveLetter $firstMappedDrive
    }
}

Write-ColorOutput "`n========================================" -Color Magenta
Write-ColorOutput "   Setup Complete!" -Color Magenta
Write-ColorOutput "========================================" -Color Magenta
Write-ColorOutput "`nPress any key to exit..." -Color Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
