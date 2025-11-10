@echo off
REM Generate Software Bill of Materials (SBOM) for Verolux
REM Uses Syft for generation and Grype for vulnerability scanning

echo ============================================
echo Verolux SBOM Generation ^& Security Scan
echo ============================================
echo.

REM Create SBOM directory
if not exist "sbom" mkdir sbom

echo Step 1: Generating SBOM for Backend...
REM Download syft if not installed
where syft >nul 2>nul
if %errorlevel% neq 0 (
    echo Please install Syft from: https://github.com/anchore/syft/releases
    echo Or use: choco install syft
    exit /b 1
)

syft dir:Backend -o spdx-json=sbom/backend-sbom.spdx.json
syft dir:Backend -o cyclonedx-json=sbom/backend-sbom.cdx.json
syft dir:Backend -o syft-json=sbom/backend-sbom.syft.json
echo [OK] Backend SBOM generated

echo.
echo Step 2: Generating SBOM for Frontend...
syft dir:Frontend -o spdx-json=sbom/frontend-sbom.spdx.json
syft dir:Frontend -o cyclonedx-json=sbom/frontend-sbom.cdx.json
echo [OK] Frontend SBOM generated

echo.
echo Step 3: Scanning for vulnerabilities with Grype...
where grype >nul 2>nul
if %errorlevel% neq 0 (
    echo Please install Grype from: https://github.com/anchore/grype/releases
    echo Or use: choco install grype
    exit /b 1
)

echo.
echo Backend vulnerabilities:
grype sbom:sbom/backend-sbom.spdx.json -o table > sbom/backend-vulnerabilities.txt
grype sbom:sbom/backend-sbom.spdx.json -o json > sbom/backend-vulnerabilities.json
type sbom\backend-vulnerabilities.txt

echo.
echo Frontend vulnerabilities:
grype sbom:sbom/frontend-sbom.spdx.json -o table > sbom/frontend-vulnerabilities.txt
grype sbom:sbom/frontend-sbom.spdx.json -o json > sbom/frontend-vulnerabilities.json
type sbom\frontend-vulnerabilities.txt

echo.
echo [OK] SBOM generation complete!
echo.
echo Files created in .\sbom\:
dir /B sbom
echo.
echo Next steps:
echo 1. Review sbom\backend-vulnerabilities.txt
echo 2. Review sbom\frontend-vulnerabilities.txt
echo 3. Update dependencies to fix critical/high vulnerabilities
echo 4. Document accepted risks
echo.

pause




















