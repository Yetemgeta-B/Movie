# PowerShell script to download default icons for the Movie Tracker application

# Create the icons directory if it doesn't exist
$iconsDir = "ui/assets/icons"
if (-not (Test-Path $iconsDir)) {
    New-Item -ItemType Directory -Path $iconsDir -Force | Out-Null
    Write-Host "Created icons directory: $iconsDir"
}

# Function to download an icon
function Download-Icon {
    param (
        [string]$Url,
        [string]$OutputFile
    )
    
    try {
        Invoke-WebRequest -Uri $Url -OutFile $OutputFile
        Write-Host "Downloaded $OutputFile successfully"
    }
    catch {
        Write-Host "Failed to download $OutputFile from $Url : $_" -ForegroundColor Red
    }
}

# Default icons from public icon repositories
$icons = @{
    "default.ico" = "https://icons.iconarchive.com/icons/designbolts/cute-social-2014/128/Movie-icon.ico"
    "film.ico" = "https://icons.iconarchive.com/icons/designbolts/cute-social-2014/128/Video-icon.ico"
    "tv.ico" = "https://icons.iconarchive.com/icons/dakirby309/simply-styled/128/TV-Shows-icon.ico"
    "document.ico" = "https://icons.iconarchive.com/icons/designbolts/cute-social-2014/128/Notes-icon.ico"
    "drama.ico" = "https://icons.iconarchive.com/icons/bokehlicia/captiva/128/emotes-face-smile-icon.ico"
    "game.ico" = "https://icons.iconarchive.com/icons/designbolts/cute-social-2014/128/GameCube-icon.ico"
}

# Download each icon
foreach ($icon in $icons.GetEnumerator()) {
    $outputPath = Join-Path $iconsDir $icon.Key
    Write-Host "Downloading $($icon.Key)..."
    Download-Icon -Url $icon.Value -OutputFile $outputPath
}

Write-Host "Icon download complete!" -ForegroundColor Green 