<#
Helper PowerShell script to initialize a local git repo, commit changes, and push to GitHub.
Usage:
  .\push_to_github.ps1 -RemoteUrl 'git@github.com:username/repo.git' -Branch 'main' -CommitMessage 'Initial commit'

Notes:
- Run this on your local machine where Git is installed.
- The script will check for `git` and prompt if missing.
- If the repo is already a git repo, it will skip `git init`.
- It will create a commit and attempt to push to the named remote. If authentication is required, configure SSH keys or credentials.
#>
param(
    [Parameter(Mandatory=$true)]
    [string]$RemoteUrl,

    [string]$Branch = 'main',

    [string]$CommitMessage = 'Project: cleaned, documented, ready for deployment',

    [switch]$Force
)

function Exec($cmd) {
    Write-Host "-> $cmd" -ForegroundColor Cyan
    $res = & cmd /c $cmd
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Command failed: $cmd"
        exit $LASTEXITCODE
    }
    return $res
}

# Check git available
try {
    & git --version > $null 2>&1
} catch {
    Write-Error "git is not available in PATH. Please install Git (https://git-scm.com/) and run this script again on your local machine."
    exit 1
}

# Ensure we're at repo root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir\..\

# Check if already git repo
if (Test-Path .git -PathType Container) {
    Write-Host "Repository already initialized (found .git)." -ForegroundColor Yellow
} else {
    Exec 'git init'
}

# Add files
Exec 'git add -A'

# Commit
$hasChanges = (git status --porcelain) -ne $null
if ($hasChanges -and -not $Force) {
    Exec "git commit -m `"$CommitMessage`""
} elseif ($hasChanges -and $Force) {
    Exec "git commit -m `"$CommitMessage`" --allow-empty"
} else {
    Write-Host "No changes to commit." -ForegroundColor Yellow
}

# Add remote
$existingRemote = (git remote) -split "`n" | Where-Object {$_ -eq 'origin'}
if (-not $existingRemote) {
    Exec "git remote add origin $RemoteUrl"
} else {
    Write-Host "Remote 'origin' already exists. Updating URL to $RemoteUrl" -ForegroundColor Yellow
    Exec "git remote set-url origin $RemoteUrl"
}

# Push
Exec "git branch -M $Branch"
Exec "git push -u origin $Branch"

Write-Host 'Push complete.' -ForegroundColor Green
