$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$pythonPath = Join-Path $repoRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Primero crear .venv e instalar requirements.lock como indica README.'
}
Push-Location $repoRoot
try {
    function Invoke-PythonStep {
        param([string[]]$Arguments)
        & $pythonPath @Arguments
        if ($LASTEXITCODE -ne 0) { throw "Paso fallido: python $Arguments" }
    }
    Invoke-PythonStep -Arguments @('-m', 'civia_data.download')
    Invoke-PythonStep -Arguments @('-m', 'civia_data.build')
    Invoke-PythonStep -Arguments @('-m', 'civia_data.train')
    Invoke-PythonStep -Arguments @('-m', 'civia_data.verify')
    Invoke-PythonStep -Arguments @('-m', 'pytest', '-q')
} finally {
    Pop-Location
}
