#!/usr/bin/env python3
"""Parse a FinCEN XSD schema file and extract element, type, and enumeration definitions.

This script parses an XSD (XML Schema Definition) file and outputs a YAML-like
listing of:
- Top-level element names
- Top-level type names (complexType and simpleType)
- Enumeration values for simpleType restrictions

Usage:
    python3 scripts/parse_fincen_xsd.py <path_to_xsd_file>

Example:
    python3 scripts/parse_fincen_xsd.py schemas/FinCENReferenceCodes.xsd

Dependencies:
    - Python 3.6+ (uses xml.etree.ElementTree from standard library)
    - lxml (optional, will use xml.etree.ElementTree if not available)

Output Format:
    The script outputs a YAML-like structure showing:
    - Elements: Top-level xs:element declarations
    - ComplexTypes: Top-level xs:complexType declarations
    - SimpleTypes: Top-level xs:simpleType declarations with enumerations

Author: stopazus/stop-azs
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Try to use lxml for better namespace handling, fall back to xml.etree
try:
    from lxml import etree as ET
    USING_LXML = True
except ImportError:
    import xml.etree.ElementTree as ET
    USING_LXML = False


# XML Schema namespace
XS_NS = "http://www.w3.org/2001/XMLSchema"


def parse_xsd_file(xsd_path: Path) -> Dict[str, Any]:
    """Parse an XSD file and extract schema information.
    
    Args:
        xsd_path: Path to the XSD file
        
    Returns:
        Dictionary containing elements, complex types, and simple types
    """
    if not xsd_path.exists():
        raise FileNotFoundError(f"XSD file not found: {xsd_path}")
    
    # Parse the XML file
    if USING_LXML:
        tree = ET.parse(str(xsd_path))
        root = tree.getroot()
    else:
        tree = ET.parse(xsd_path)
        root = tree.getroot()
    
    # Extract namespace map
    nsmap = {"xs": XS_NS}
    
    # Initialize result structure
    result = {
        "elements": [],
        "complex_types": [],
        "simple_types": [],
    }
    
    # Find all top-level elements
    for elem in root.findall("xs:element", nsmap):
        name = elem.get("name")
        elem_type = elem.get("type")
        if name:
            result["elements"].append({
                "name": name,
                "type": elem_type if elem_type else "(anonymous)"
            })
    
    # Find all top-level complexType definitions
    for ctype in root.findall("xs:complexType", nsmap):
        name = ctype.get("name")
        if name:
            result["complex_types"].append({"name": name})
    
    # Find all top-level simpleType definitions
    for stype in root.findall("xs:simpleType", nsmap):
        name = stype.get("name")
        if name:
            # Check for enumerations
            enums = []
            restriction = stype.find("xs:restriction", nsmap)
            if restriction is not None:
                base = restriction.get("base")
                for enum in restriction.findall("xs:enumeration", nsmap):
                    value = enum.get("value")
                    if value:
                        # Try to get documentation/annotation
                        doc = None
                        annotation = enum.find("xs:annotation", nsmap)
                        if annotation is not None:
                            documentation = annotation.find("xs:documentation", nsmap)
                            if documentation is not None and documentation.text:
                                doc = documentation.text.strip()
                        
                        enums.append({
                            "value": value,
                            "documentation": doc
                        })
                
                result["simple_types"].append({
                    "name": name,
                    "base": base,
                    "enumerations": enums if enums else None
                })
            else:
                result["simple_types"].append({
                    "name": name,
                    "enumerations": None
                })
    
    return result


def format_output(data: Dict[str, Any]) -> str:
    """Format the parsed data as YAML-like output.
    
    Args:
        data: Parsed schema data
        
    Returns:
        Formatted string output
    """
    lines = []
    
    # Elements section
    if data["elements"]:
        lines.append("Elements:")
        for elem in data["elements"]:
            lines.append(f"  - name: {elem['name']}")
            lines.append(f"    type: {elem['type']}")
        lines.append("")
    
    # ComplexTypes section
    if data["complex_types"]:
        lines.append("ComplexTypes:")
        for ctype in data["complex_types"]:
            lines.append(f"  - {ctype['name']}")
        lines.append("")
    
    # SimpleTypes section
    if data["simple_types"]:
        lines.append("SimpleTypes:")
        for stype in data["simple_types"]:
            lines.append(f"  - name: {stype['name']}")
            if "base" in stype:
                lines.append(f"    base: {stype['base']}")
            
            if stype.get("enumerations"):
                lines.append("    enumerations:")
                for enum in stype["enumerations"]:
                    lines.append(f"      - value: {enum['value']}")
                    if enum.get("documentation"):
                        # Indent multi-line documentation
                        doc_lines = enum["documentation"].split("\n")
                        lines.append(f"        doc: {doc_lines[0]}")
                        for doc_line in doc_lines[1:]:
                            if doc_line.strip():
                                lines.append(f"             {doc_line.strip()}")
        lines.append("")
    
    return "\n".join(lines)


def main():
    """Main entry point for the script."""
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/parse_fincen_xsd.py <path_to_xsd_file>", file=sys.stderr)
        print("", file=sys.stderr)
        print("Example:", file=sys.stderr)
        print("  python3 scripts/parse_fincen_xsd.py schemas/FinCENReferenceCodes.xsd", file=sys.stderr)
        sys.exit(1)
    
    xsd_file = Path(sys.argv[1])
    
    try:
        # Parse the XSD file
        data = parse_xsd_file(xsd_file)
        
        # Print header
        print(f"# XSD Schema Analysis: {xsd_file.name}")
        print(f"# Parser: {'lxml' if USING_LXML else 'xml.etree.ElementTree'}")
        print("")
        
        # Format and print output
        output = format_output(data)
        print(output)
        
        # Print summary
        elem_count = len(data["elements"])
        ctype_count = len(data["complex_types"])
        stype_count = len(data["simple_types"])
        enum_count = sum(1 for st in data["simple_types"] if st.get("enumerations"))
        
        print(f"# Summary: {elem_count} elements, {ctype_count} complex types, "
              f"{stype_count} simple types ({enum_count} with enumerations)")
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ET.ParseError as e:
        print(f"Error parsing XSD file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
