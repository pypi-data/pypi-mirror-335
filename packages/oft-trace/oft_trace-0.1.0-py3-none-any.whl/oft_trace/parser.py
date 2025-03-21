"""Parser for aspec XML files."""
import os
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from oft_trace.models import SpecItem

console = Console()

def parse_aspec_file(aspec_file: str) -> Tuple[Dict[str, SpecItem], defaultdict, defaultdict, defaultdict, List[str]]:
    """Parse an aspec XML file and return the items and relationship maps."""
    spec_items = {}  # Dictionary of all items by id~version
    id_map = defaultdict(list)  # Map of ID to all versions
    covering_map = defaultdict(list)  # Map of what each item covers (outgoing)
    covered_by_map = defaultdict(list)  # Map of what covers each item (incoming)
    broken_chains = []  # List of items with broken chains

    try:
        tree = ET.parse(aspec_file)
        root = tree.getroot()
        
        # Find all spec objects across all doctypes
        for spec_objects in root.findall('.//*[@doctype]'):
            doctype = spec_objects.get('doctype')
            
            for spec_object in spec_objects.findall('./specobject'):
                item = parse_spec_object(spec_object, doctype)
                if item:
                    item_key = f"{item.id}~{item.version}"
                    spec_items[item_key] = item
                    id_map[item.id].append(item_key)
        
        # Build relationship maps
        build_relationship_maps(spec_items, covering_map, covered_by_map)
        
        # Find broken chains
        broken_chains = identify_broken_chains(spec_items)
        
        return spec_items, id_map, covering_map, covered_by_map, broken_chains
    
    except Exception as e:
        console.print(f"[bold red]Error parsing aspec file:[/] {e}")
        sys.exit(1)

def parse_spec_object(spec_object, doctype) -> Optional[SpecItem]:
    """Parse a spec object element into a SpecItem object."""
    # Extract ID
    id_elem = spec_object.find('./id')
    if id_elem is None or not id_elem.text:
        return None  # Skip items without ID
    
    # Extract version
    version_elem = spec_object.find('./version')
    version = version_elem.text if version_elem is not None and version_elem.text else '0'
    
    # Create spec item
    item = SpecItem(id_elem.text, version, doctype)
    
    # Extract title/description
    for field in ['shortdesc', 'description', 'status', 'sourcefile', 'sourceline']:
        elem = spec_object.find(f'./{field}')
        if elem is not None and elem.text:
            setattr(item, field, elem.text)
    
    # Extract coverage status
    coverage_elem = spec_object.find('./coverage')
    if coverage_elem is not None:
        item.coverage = {}
        
        # Shallow and deep coverage status
        for status_type in ['shallowCoverageStatus', 'deepCoverageStatus']:
            status_elem = coverage_elem.find(f'./{status_type}')
            if status_elem is not None and status_elem.text:
                item.coverage[status_type] = status_elem.text
        
        # Items that cover this item
        covering_items = []
        covering_objects = coverage_elem.find('./coveringSpecObjects')
        if covering_objects is not None:
            for covering_obj in covering_objects.findall('./coveringSpecObject'):
                covering_item = {}
                
                # Extract basic info about the covering item
                for field in ['id', 'version', 'doctype', 'status']:
                    field_elem = covering_obj.find(f'./{field}')
                    if field_elem is not None and field_elem.text:
                        covering_item[field] = field_elem.text
                
                # Extract coverage statuses
                for status_type in ['ownCoverageStatus', 'deepCoverageStatus', 'coveringStatus']:
                    status_elem = covering_obj.find(f'./{status_type}')
                    if status_elem is not None and status_elem.text:
                        covering_item[status_type] = status_elem.text
                
                covering_items.append(covering_item)
        
        item.coverage['coveringItems'] = covering_items
        
        # Extract covered and uncovered types
        for types_field in ['coveredTypes', 'uncoveredTypes']:
            types = []
            types_elem = coverage_elem.find(f'./{types_field}')
            if types_elem is not None:
                for type_elem in types_elem.findall(f'./*Type'):
                    if type_elem.text:
                        types.append(type_elem.text)
            
            item.coverage[types_field] = types
    
    # Extract items that this item covers
    covering_elem = spec_object.find('./covering')
    if covering_elem is not None:
        covered_items = []
        for covered_type in covering_elem.findall('./coveredType'):
            covered_item = {}
            
            for field in ['id', 'version', 'doctype']:
                field_elem = covered_type.find(f'./{field}')
                if field_elem is not None and field_elem.text:
                    covered_item[field] = field_elem.text
            
            covered_items.append(covered_item)
        
        item.covers = covered_items
    
    return item

def build_relationship_maps(spec_items, covering_map, covered_by_map):
    """Build the maps for tracing relationships between items."""
    for item_key, item in spec_items.items():
        # Map what this item covers
        for covered in item.covers:
            covered_key = f"{covered['id']}~{covered.get('version', '1')}"
            covering_map[item_key].append(covered_key)
        
        # Map what covers this item
        for covering in item.coverage.get('coveringItems', []):
            covering_key = f"{covering['id']}~{covering.get('version', '1')}"
            covered_by_map[item_key].append(covering_key)

def identify_broken_chains(spec_items):
    """Identify items with broken trace chains."""
    broken_chains = []
    for item_key, item in spec_items.items():
        if item.coverage_type != "COVERED":
            broken_chains.append(item_key)
    return broken_chains