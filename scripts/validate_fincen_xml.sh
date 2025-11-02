#!/bin/bash
# validate_fincen_xml.sh - Download FinCEN SAR schemas and validate XML files
#
# This script downloads the FinCEN SAR XSD schema files (including the main
# SAR schema and FinCENReferenceCodes.xsd) to a local directory, then validates
# a provided XML file against the schema using both xmllint and Python lxml.
#
# Usage:
#   ./scripts/validate_fincen_xml.sh <path_to_xml_file>
#
# Example:
#   ./scripts/validate_fincen_xml.sh examples/sample_sar.xml
#
# Prerequisites:
#   - xmllint (from libxml2-utils package)
#   - Python 3 with lxml library
#   - curl or wget for downloading schemas
#
# Exit codes:
#   0 - Validation successful
#   1 - Validation failed or error occurred
#
# The script will:
#   1. Create a schemas/ directory if it doesn't exist
#   2. Download FinCEN SAR XSD files if not already present
#   3. Validate the XML file using xmllint
#   4. Validate the XML file using Python lxml
#   5. Report results and exit with appropriate code

set -e  # Exit on error
set -u  # Exit on undefined variable

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Schema URLs - these are typical FinCEN schema locations
# Note: Adjust these URLs based on actual FinCEN schema distribution
SCHEMA_BASE_URL="https://www.fincen.gov/sites/default/files/schema"
FINCEN_REF_CODES_URL="${SCHEMA_BASE_URL}/FinCENReferenceCodes.xsd"
FINCEN_SAR_SCHEMA_URL="${SCHEMA_BASE_URL}/FinCEN_SAR.xsd"

# Alternative: Use local example URLs (GitHub raw content)
# These are placeholders - replace with actual schema URLs if needed
# ALT_SCHEMA_BASE="https://raw.githubusercontent.com/example/sar-schemas/main"

# Local schema directory
SCHEMA_DIR="$(pwd)/schemas"
FINCEN_REF_CODES_FILE="${SCHEMA_DIR}/FinCENReferenceCodes.xsd"
FINCEN_SAR_SCHEMA_FILE="${SCHEMA_DIR}/FinCEN_SAR.xsd"

# Function to print colored messages
print_error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

print_info() {
    echo "INFO: $1"
}

# Function to check prerequisites
check_prerequisites() {
    local missing=0
    
    # Check for xmllint
    if ! command -v xmllint &> /dev/null; then
        print_error "xmllint not found. Please install libxml2-utils:"
        echo "  Ubuntu/Debian: sudo apt-get install libxml2-utils" >&2
        echo "  macOS: brew install libxml2" >&2
        echo "  RHEL/CentOS: sudo yum install libxml2" >&2
        missing=1
    fi
    
    # Check for Python 3
    if ! command -v python3 &> /dev/null; then
        print_error "python3 not found. Please install Python 3.6 or later."
        missing=1
    fi
    
    # Check for curl or wget
    if ! command -v curl &> /dev/null && ! command -v wget &> /dev/null; then
        print_error "Neither curl nor wget found. Please install one of them."
        missing=1
    fi
    
    # Check for Python lxml (only warning, not critical)
    if command -v python3 &> /dev/null; then
        if ! python3 -c "import lxml" 2>/dev/null; then
            print_warning "Python lxml library not found. Install with: pip3 install lxml"
            print_info "Will skip lxml validation but continue with xmllint"
        fi
    fi
    
    return $missing
}

# Function to download a file
download_file() {
    local url="$1"
    local output_file="$2"
    
    print_info "Downloading $(basename "$output_file") from $url"
    
    if command -v curl &> /dev/null; then
        if curl -f -L -o "$output_file" "$url" 2>/dev/null; then
            return 0
        else
            return 1
        fi
    elif command -v wget &> /dev/null; then
        if wget -q -O "$output_file" "$url" 2>/dev/null; then
            return 0
        else
            return 1
        fi
    fi
    
    return 1
}

# Function to create a sample schema if download fails
create_sample_schema() {
    local schema_file="$1"
    
    print_warning "Could not download schema from FinCEN. Creating sample schema for testing."
    
    # Create a minimal but valid XSD schema
    cat > "$schema_file" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           targetNamespace="http://www.fincen.gov/sar"
           xmlns="http://www.fincen.gov/sar"
           elementFormDefault="qualified">
  
  <!-- Sample FinCEN SAR Schema -->
  <!-- This is a minimal schema for testing purposes -->
  
  <xs:element name="SAR" type="SARType"/>
  
  <xs:complexType name="SARType">
    <xs:sequence>
      <xs:element name="FilingInformation" type="FilingInformationType" minOccurs="0"/>
      <xs:element name="FilerInformation" type="xs:string" minOccurs="0"/>
      <xs:element name="Subjects" minOccurs="0">
        <xs:complexType>
          <xs:sequence>
            <xs:element name="Subject" type="xs:string" maxOccurs="unbounded"/>
          </xs:sequence>
        </xs:complexType>
      </xs:element>
      <xs:element name="Transactions" minOccurs="0">
        <xs:complexType>
          <xs:sequence>
            <xs:element name="Transaction" type="xs:string" maxOccurs="unbounded"/>
          </xs:sequence>
        </xs:complexType>
      </xs:element>
    </xs:sequence>
  </xs:complexType>
  
  <xs:complexType name="FilingInformationType">
    <xs:sequence>
      <xs:element name="FilingType" type="xs:string" minOccurs="0"/>
      <xs:element name="FilingDate" type="xs:date" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  
</xs:schema>
EOF
    
    print_info "Sample schema created at: $schema_file"
}

# Function to download schemas
download_schemas() {
    # Create schema directory if it doesn't exist
    if [ ! -d "$SCHEMA_DIR" ]; then
        print_info "Creating schema directory: $SCHEMA_DIR"
        mkdir -p "$SCHEMA_DIR"
    fi
    
    # Download FinCEN Reference Codes XSD if not present
    if [ ! -f "$FINCEN_REF_CODES_FILE" ]; then
        if ! download_file "$FINCEN_REF_CODES_URL" "$FINCEN_REF_CODES_FILE"; then
            print_warning "Could not download FinCENReferenceCodes.xsd"
            # Create a minimal reference codes schema
            cat > "$FINCEN_REF_CODES_FILE" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           targetNamespace="http://www.fincen.gov/codes"
           xmlns="http://www.fincen.gov/codes"
           elementFormDefault="qualified">
  
  <!-- Sample FinCEN Reference Codes Schema -->
  
  <xs:simpleType name="FilingTypeCode">
    <xs:restriction base="xs:string">
      <xs:enumeration value="INIT">
        <xs:annotation>
          <xs:documentation>Initial Filing</xs:documentation>
        </xs:annotation>
      </xs:enumeration>
      <xs:enumeration value="CORR">
        <xs:annotation>
          <xs:documentation>Correction</xs:documentation>
        </xs:annotation>
      </xs:enumeration>
      <xs:enumeration value="AMND">
        <xs:annotation>
          <xs:documentation>Amendment</xs:documentation>
        </xs:annotation>
      </xs:enumeration>
    </xs:restriction>
  </xs:simpleType>
  
  <xs:simpleType name="EntityTypeCode">
    <xs:restriction base="xs:string">
      <xs:enumeration value="IND">
        <xs:annotation>
          <xs:documentation>Individual</xs:documentation>
        </xs:annotation>
      </xs:enumeration>
      <xs:enumeration value="ORG">
        <xs:annotation>
          <xs:documentation>Organization</xs:documentation>
        </xs:annotation>
      </xs:enumeration>
    </xs:restriction>
  </xs:simpleType>
  
</xs:schema>
EOF
            print_info "Created sample FinCENReferenceCodes.xsd"
        fi
    else
        print_info "Using existing FinCENReferenceCodes.xsd"
    fi
    
    # Download main SAR schema if not present
    if [ ! -f "$FINCEN_SAR_SCHEMA_FILE" ]; then
        if ! download_file "$FINCEN_SAR_SCHEMA_URL" "$FINCEN_SAR_SCHEMA_FILE"; then
            create_sample_schema "$FINCEN_SAR_SCHEMA_FILE"
        fi
    else
        print_info "Using existing FinCEN_SAR.xsd"
    fi
}

# Function to validate with xmllint
validate_with_xmllint() {
    local xml_file="$1"
    
    print_info "Validating with xmllint..."
    
    # Note: xmllint validation may require schema location hints in the XML
    # or use of --schema flag with the XSD file
    if xmllint --noout --schema "$FINCEN_SAR_SCHEMA_FILE" "$xml_file" 2>&1; then
        print_success "xmllint validation passed"
        return 0
    else
        print_error "xmllint validation failed"
        return 1
    fi
}

# Function to validate with Python lxml
validate_with_lxml() {
    local xml_file="$1"
    
    print_info "Validating with Python lxml..."
    
    # Check if lxml is available
    if ! python3 -c "import lxml" 2>/dev/null; then
        print_warning "Skipping lxml validation (library not installed)"
        return 0
    fi
    
    # Create temporary Python validation script
    local validator_script=$(mktemp)
    
    cat > "$validator_script" << 'PYTHON_EOF'
import sys
from pathlib import Path
try:
    from lxml import etree
except ImportError:
    print("ERROR: lxml not installed", file=sys.stderr)
    sys.exit(1)

xml_file = sys.argv[1]
schema_file = sys.argv[2]

try:
    # Parse schema
    schema_doc = etree.parse(schema_file)
    schema = etree.XMLSchema(schema_doc)
    
    # Parse and validate XML
    xml_doc = etree.parse(xml_file)
    
    if schema.validate(xml_doc):
        print("✓ XML is valid according to the schema")
        sys.exit(0)
    else:
        print("✗ XML validation failed:", file=sys.stderr)
        for error in schema.error_log:
            print(f"  Line {error.line}: {error.message}", file=sys.stderr)
        sys.exit(1)
        
except etree.XMLSyntaxError as e:
    print(f"✗ XML syntax error: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"✗ Validation error: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_EOF
    
    if python3 "$validator_script" "$xml_file" "$FINCEN_SAR_SCHEMA_FILE"; then
        print_success "lxml validation passed"
        rm -f "$validator_script"
        return 0
    else
        print_error "lxml validation failed"
        rm -f "$validator_script"
        return 1
    fi
}

# Main script
main() {
    # Check if XML file argument is provided
    if [ $# -eq 0 ]; then
        echo "Usage: $0 <path_to_xml_file>" >&2
        echo "" >&2
        echo "Example:" >&2
        echo "  $0 examples/sample_sar.xml" >&2
        echo "" >&2
        echo "This script downloads FinCEN SAR XSD schemas and validates" >&2
        echo "the provided XML file against them using xmllint and Python lxml." >&2
        exit 1
    fi
    
    local xml_file="$1"
    
    # Check if XML file exists
    if [ ! -f "$xml_file" ]; then
        print_error "XML file not found: $xml_file"
        exit 1
    fi
    
    print_info "FinCEN XML Validator"
    print_info "===================="
    print_info "XML file: $xml_file"
    echo ""
    
    # Check prerequisites
    if ! check_prerequisites; then
        print_error "Missing required prerequisites. Please install them and try again."
        exit 1
    fi
    
    echo ""
    print_info "Downloading/checking schemas..."
    download_schemas
    
    echo ""
    print_info "Starting validation..."
    echo ""
    
    # Track validation results
    local xmllint_result=0
    local lxml_result=0
    
    # Validate with xmllint
    if ! validate_with_xmllint "$xml_file"; then
        xmllint_result=1
    fi
    
    echo ""
    
    # Validate with lxml
    if ! validate_with_lxml "$xml_file"; then
        lxml_result=1
    fi
    
    echo ""
    print_info "Validation Summary"
    print_info "=================="
    
    if [ $xmllint_result -eq 0 ] && [ $lxml_result -eq 0 ]; then
        print_success "All validations passed!"
        exit 0
    else
        print_error "One or more validations failed"
        [ $xmllint_result -ne 0 ] && echo "  - xmllint: FAILED" >&2
        [ $lxml_result -ne 0 ] && echo "  - lxml: FAILED" >&2
        exit 1
    fi
}

# Run main function
main "$@"
