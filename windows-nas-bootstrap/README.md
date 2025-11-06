# Windows NAS Bootstrap

This bundle installs apps via winget and maps your NAS drives.

**Generated:** 2025-11-05 21:04

## Features

### Applications Installed
- **Python 3.12** - Latest Python programming language
- **Git** - Version control system
- **rclone** - Cloud storage sync tool
- **VS Code** - Visual Studio Code editor
- **7-Zip** - File archiver
- **VLC** - Media player
- **WinSCP** - SFTP/FTP client
- **PuTTY** - SSH client

### NAS Drives Mapped
- **G:** → `\\nas\Cloud-GDrive` (Google Drive)
- **I:** → `\\nas\Cloud-iCloud` (iCloud)
- **O:** → `\\nas\Cloud-OneDrive` (OneDrive)

### Additional Features
- Prompts for NAS password securely
- Maps drives with persistent connections
- Optional 1 GiB network speed test
- Color-coded output for easy monitoring

## Requirements

- Windows 10 or Windows 11
- Administrator privileges
- winget (App Installer) - pre-installed on Windows 11, available from Microsoft Store for Windows 10
- Network access to `\\nas` server

## How to Run

1. **Right-click** on `run-setup.bat`
2. Select **"Run as administrator"**
3. Enter NAS password for user **"downloader"** when prompted
4. Watch the installation progress
5. Optionally run the 1 GiB speed test when prompted

## What Happens During Setup

1. **Winget Check** - Verifies winget is available
2. **App Installation** - Installs all 8 applications via winget
3. **Credential Prompt** - Asks for NAS password
4. **Drive Mapping** - Maps all three cloud storage drives
5. **Speed Test** (optional) - Tests network performance with 1 GiB file

## Files

- `run-setup.bat` - Batch file launcher (run this as administrator)
- `setup.ps1` - PowerShell script that performs all operations
- `README.md` - This documentation file

## Troubleshooting

### "winget is not available"
- Install App Installer from the Microsoft Store
- Restart your terminal/PowerShell session

### "This script must be run as administrator"
- Right-click `run-setup.bat` and select "Run as administrator"
- Do not double-click the file

### Drive Mapping Fails
- Verify network connectivity to `\\nas`
- Check that the username "downloader" has access
- Ensure the password is correct
- Check if drives G:, I:, or O: are already in use

### App Installation Fails
- Check internet connectivity
- Some apps may already be installed (this is normal)
- Review the summary at the end for details

## Security Notes

- Password is entered securely (characters are hidden)
- Password is only stored in memory during execution
- Drives are mapped with persistent connections
- Script requires administrator privileges (indicated by `#Requires -RunAsAdministrator`)

## Manual Cleanup

To remove mapped drives manually:
```cmd
net use G: /delete
net use I: /delete
net use O: /delete
```

To uninstall apps manually:
```cmd
winget uninstall --id Python.Python.3.12
winget uninstall --id Git.Git
winget uninstall --id Rclone.Rclone
winget uninstall --id Microsoft.VisualStudioCode
winget uninstall --id 7zip.7zip
winget uninstall --id VideoLAN.VLC
winget uninstall --id WinSCP.WinSCP
winget uninstall --id PuTTY.PuTTY
```

## Support

For issues or questions, refer to the main repository documentation or contact your system administrator.
