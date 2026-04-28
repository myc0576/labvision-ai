param(
  [string]$OutputRoot = "examples/_outputs"
)
$ErrorActionPreference = "Stop"

$examples = @("01_basic_processing.py", "01_basic_processing_zh.py")
foreach ($example in $examples) {
  $name = [System.IO.Path]::GetFileNameWithoutExtension($example)
  python (Join-Path "examples" $example) --output-dir (Join-Path $OutputRoot $name)
}

$required = @(
  "01_basic_processing/normalized.npy",
  "01_basic_processing/normalized.png",
  "01_basic_processing/run_manifest.json",
  "01_basic_processing/summary.md",
  "01_basic_processing_zh/normalized_zh.npy",
  "01_basic_processing_zh/normalized_zh.png",
  "01_basic_processing_zh/run_manifest.json",
  "01_basic_processing_zh/summary.md"
)
foreach ($relative in $required) {
  $path = Join-Path $OutputRoot $relative
  if (!(Test-Path -LiteralPath $path)) { throw "Expected example artifact missing: $path" }
  if ((Get-Item -LiteralPath $path).Length -le 0) { throw "Expected non-empty example artifact: $path" }
}

Write-Output "Examples completed under $OutputRoot"
