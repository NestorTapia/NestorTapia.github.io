$ErrorActionPreference = 'Stop'

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$pageNames = @(
    'index.html',
    'proyecto-demiplie.html',
    'proyecto-florexpress.html',
    'proyecto-mettatalk.html'
)
$assetFolders = @('assets', 'assets1', 'assets2', 'css', 'js', 'docs', 'docs1', 'docs2')

foreach ($folder in $assetFolders) {
    $folderPath = Join-Path $projectRoot $folder
    if (-not (Test-Path -LiteralPath $folderPath -PathType Container)) {
        throw "Falta la carpeta requerida: $folder"
    }

    $fileCount = (Get-ChildItem -LiteralPath $folderPath -File -Recurse).Count
    if ($fileCount -ge 100) {
        throw "La carpeta $folder contiene $fileCount archivos; debe dividirse antes de subirla desde el navegador."
    }
}

foreach ($pageName in $pageNames) {
    if (-not (Test-Path -LiteralPath (Join-Path $projectRoot $pageName) -PathType Leaf)) {
        throw "Falta la página requerida: $pageName"
    }
    if (-not (Test-Path -LiteralPath (Join-Path $projectRoot "docs\$pageName") -PathType Leaf)) {
        throw "Falta la copia requerida en docs: $pageName"
    }
}

Set-Content -LiteralPath (Join-Path $projectRoot '.nojekyll') -Value '' -Encoding ascii

Write-Output 'Sitio listo desde /(root); copia dividida validada en docs, docs1 y docs2.'
