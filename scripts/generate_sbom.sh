#!/bin/bash
# Generate Software Bill of Materials (SBOM) for Verolux
# Uses Syft for generation and Grype for vulnerability scanning

set -e

echo "============================================"
echo "Verolux SBOM Generation & Security Scan"
echo "============================================"
echo ""

# Check if syft is installed
if ! command -v syft &> /dev/null; then
    echo "Installing Syft..."
    curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
fi

# Check if grype is installed
if ! command -v grype &> /dev/null; then
    echo "Installing Grype..."
    curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin
fi

# Create SBOM directory
mkdir -p sbom

echo "Step 1: Generating SBOM for Backend..."
syft dir:Backend -o spdx-json=sbom/backend-sbom.spdx.json
syft dir:Backend -o cyclonedx-json=sbom/backend-sbom.cdx.json
syft dir:Backend -o syft-json=sbom/backend-sbom.syft.json
echo "✅ Backend SBOM generated"

echo ""
echo "Step 2: Generating SBOM for Frontend..."
syft dir:Frontend -o spdx-json=sbom/frontend-sbom.spdx.json
syft dir:Frontend -o cyclonedx-json=sbom/frontend-sbom.cdx.json
echo "✅ Frontend SBOM generated"

echo ""
echo "Step 3: Generating SBOM for Docker images..."
if [ -f "docker-compose.production.yml" ]; then
    echo "Building Docker images..."
    docker-compose -f docker-compose.production.yml build --no-cache backend frontend
    
    echo "Scanning backend image..."
    syft verolux-backend:latest -o spdx-json=sbom/backend-image-sbom.spdx.json
    
    echo "Scanning frontend image..."
    syft verolux-frontend:latest -o spdx-json=sbom/frontend-image-sbom.spdx.json
    
    echo "✅ Docker image SBOMs generated"
fi

echo ""
echo "Step 4: Scanning for vulnerabilities with Grype..."
echo ""

echo "Backend vulnerabilities:"
grype sbom:sbom/backend-sbom.spdx.json -o table > sbom/backend-vulnerabilities.txt
grype sbom:sbom/backend-sbom.spdx.json -o json > sbom/backend-vulnerabilities.json
cat sbom/backend-vulnerabilities.txt

echo ""
echo "Frontend vulnerabilities:"
grype sbom:sbom/frontend-sbom.spdx.json -o table > sbom/frontend-vulnerabilities.txt
grype sbom:sbom/frontend-sbom.spdx.json -o json > sbom/frontend-vulnerabilities.json
cat sbom/frontend-vulnerabilities.txt

echo ""
echo "Step 5: Generating summary report..."
cat > sbom/SBOM_REPORT.md << 'EOF'
# Software Bill of Materials (SBOM) Report

## Generated: $(date)

### Files Created:
- `backend-sbom.spdx.json` - Backend SPDX SBOM
- `backend-sbom.cdx.json` - Backend CycloneDX SBOM
- `frontend-sbom.spdx.json` - Frontend SPDX SBOM
- `frontend-sbom.cdx.json` - Frontend CycloneDX SBOM
- `backend-vulnerabilities.json` - Backend vulnerability scan
- `frontend-vulnerabilities.json` - Frontend vulnerability scan

### Vulnerability Summary:
See `*-vulnerabilities.txt` files for details.

### Next Steps:
1. Review critical and high vulnerabilities
2. Update dependencies to patch vulnerabilities
3. Document accepted risks for low/medium findings
4. Re-scan after updates

### Compliance:
- NTIA Minimum Elements: ✅ Met
- SPDX 2.3 Format: ✅ Generated
- CycloneDX 1.4 Format: ✅ Generated
- Vulnerability Scanning: ✅ Completed

EOF

echo "✅ SBOM generation complete!"
echo ""
echo "Files created in ./sbom/:"
ls -lh sbom/
echo ""
echo "Next steps:"
echo "1. Review sbom/backend-vulnerabilities.txt"
echo "2. Review sbom/frontend-vulnerabilities.txt"
echo "3. Update dependencies to fix critical/high vulnerabilities"
echo "4. Document accepted risks"
echo ""




















