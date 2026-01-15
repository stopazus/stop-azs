param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('add', 'update', 'remove', 'list')]
    [string]$Action,

    [Parameter(Mandatory = $false)]
    [string]$Title,

    [Parameter(Mandatory = $false)]
    [ValidateSet('active', 'blocked', 'done', 'icebox', 'pending')]
    [string]$Status,

    [Parameter(Mandatory = $false)]
    [int]$Priority,

    [Parameter(Mandatory = $false)]
    [string]$Tags,

    [Parameter(Mandatory = $false)]
    [string]$Description,

    [Parameter(Mandatory = $false)]
    [string]$File = "tasks.json"
)

function Normalize-Tags {
    param([string]$TagString)
    if ([string]::IsNullOrWhiteSpace($TagString)) {
        return @()
    }

    return $TagString -split ',' |
        ForEach-Object { $_.Trim() } |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
}

function Load-Tasks {
    param([string]$Path)
    if (-not (Test-Path -Path $Path)) {
        return @()
    }

    $content = Get-Content -Path $Path -Raw
    if ([string]::IsNullOrWhiteSpace($content)) {
        return @()
    }

    try {
        $parsed = $content | ConvertFrom-Json
    } catch {
        throw "The tasks file '$Path' contains invalid JSON."
    }

    if ($null -eq $parsed) {
        return @()
    }

    return @($parsed)
}

function Save-Tasks {
    param(
        [Parameter(Mandatory = $true)][array]$Tasks,
        [Parameter(Mandatory = $true)][string]$Path
    )

    $json = $Tasks | ConvertTo-Json -Depth 5
    Set-Content -Path $Path -Value $json -Encoding UTF8
}

function Ensure-Title {
    param([string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) {
        throw "A non-empty -Title value is required for this action."
    }
}

$tasks = Load-Tasks -Path $File

switch ($Action) {
    'list' {
        if ($tasks.Count -eq 0) {
            Write-Output "No tasks found in '$File'."
            break
        }

        $tasks | Sort-Object Priority, Title | ForEach-Object {
            $tagList = if ($_.Tags) { ($_.Tags -join ', ') } else { 'none' }
            Write-Output "- Title: $($_.Title) | Status: $($_.Status) | Priority: $($_.Priority) | Tags: $tagList"
            if ($_.Description) {
                Write-Output "  Description: $($_.Description)"
            }
        }
    }
    'add' {
        Ensure-Title -Value $Title
        if ($tasks | Where-Object { $_.Title -eq $Title }) {
            throw "A task titled '$Title' already exists. Use -Action update to modify it."
        }

        $newTask = [ordered]@{
            Title       = $Title
            Status      = $Status
            Priority    = $Priority
            Tags        = Normalize-Tags -TagString $Tags
            Description = $Description
        }

        $tasks += [pscustomobject]$newTask
        Save-Tasks -Tasks $tasks -Path $File
        Write-Output "Added task '$Title' to '$File'."
    }
    'update' {
        Ensure-Title -Value $Title

        $existing = $tasks | Where-Object { $_.Title -eq $Title }
        if (-not $existing) {
            Write-Output "Task '$Title' not found. Creating a new entry."
            $tasks += [pscustomobject]@{
                Title       = $Title
                Status      = $Status
                Priority    = $Priority
                Tags        = Normalize-Tags -TagString $Tags
                Description = $Description
            }
        } else {
            foreach ($task in $existing) {
                if ($PSBoundParameters.ContainsKey('Status')) { $task.Status = $Status }
                if ($PSBoundParameters.ContainsKey('Priority')) { $task.Priority = $Priority }
                if ($PSBoundParameters.ContainsKey('Tags')) { $task.Tags = Normalize-Tags -TagString $Tags }
                if ($PSBoundParameters.ContainsKey('Description')) { $task.Description = $Description }
            }
        }

        Save-Tasks -Tasks $tasks -Path $File
        Write-Output "Updated task '$Title' in '$File'."
    }
    'remove' {
        Ensure-Title -Value $Title
        $remaining = $tasks | Where-Object { $_.Title -ne $Title }
        if ($remaining.Count -eq $tasks.Count) {
            throw "No task titled '$Title' exists in '$File'."
        }

        Save-Tasks -Tasks $remaining -Path $File
        Write-Output "Removed task '$Title' from '$File'."
    }
}
