"""Analysis logic for aspec trace chains."""
from typing import Dict, List, Set, Optional, Any
from collections import defaultdict

from oft_trace.models import SpecItem

class TraceAnalyzer:
    """Analyzer for trace chains to identify issues and relationships."""
    
    def __init__(self, spec_items, id_map, covering_map, covered_by_map, broken_chains, aspec_file=None):
        self.spec_items = spec_items
        self.id_map = id_map
        self.covering_map = covering_map
        self.covered_by_map = covered_by_map
        self.broken_chains = broken_chains
        self.aspec_file = aspec_file
    
    def get_item_by_id(self, spec_id, doctype=None, version=None):
        """Find an item by ID and optionally by doctype and version."""
        if version:
            item_key = f"{spec_id}~{version}"
            if item_key in self.spec_items:
                item = self.spec_items[item_key]
                if doctype is None or item.doctype == doctype:
                    return item_key
            return None
        
        # Find by ID and optionally doctype
        for key, item in self.spec_items.items():
            if key.startswith(f"{spec_id}~") and (doctype is None or item.doctype == doctype):
                return key
        
        return None
    
    def is_version_mismatch(self, source_key, target_key):
        """Check if there's a version mismatch between items."""
        if source_key not in self.spec_items or target_key not in self.spec_items:
            return False
        
        source = self.spec_items[source_key]
        target = self.spec_items[target_key]
        
        # If we have coverage details about version mismatches
        for covering in source.coverage.get('coveringItems', []):
            if covering['id'] == target.id:
                if covering.get('coveringStatus') == 'COVERING_WRONG_VERSION':
                    return True
        
        # If the item is in the covering map but with wrong version
        source_id = source_key.split('~')[0]
        target_id = target_key.split('~')[0]
        
        if source_id in self.id_map and target_id in self.id_map:
            for source_variant in self.id_map[source_id]:
                for target_variant in self.id_map[target_id]:
                    if source_variant != source_key or target_variant != target_key:
                        if source_variant in self.covering_map and target_variant in self.covering_map[source_variant]:
                            return True
        
        return False
    
    def get_version_mismatch_details(self, source_key, target_key):
        """Get detailed information about a version mismatch."""
        if source_key not in self.spec_items or target_key not in self.spec_items:
            return None
        
        source = self.spec_items[source_key]
        target = self.spec_items[target_key]
        
        # Check coverage details
        for covering in source.coverage.get('coveringItems', []):
            if covering['id'] == target.id:
                if covering.get('coveringStatus') == 'COVERING_WRONG_VERSION':
                    return {
                        'current': {
                            'id': target.id,
                            'version': target.version
                        },
                        'expected': {
                            'id': target.id,
                            'version': covering.get('version', 'unknown')
                        }
                    }
        
        # Check other versions
        source_id = source_key.split('~')[0]
        target_id = target_key.split('~')[0]
        
        expected_version = None
        for source_variant in self.id_map[source_id]:
            for target_variant in self.id_map[target_id]:
                if source_variant != source_key or target_variant != target_key:
                    if source_variant in self.covering_map and target_variant in self.covering_map[source_variant]:
                        expected_version = target_variant.split('~')[1]
        
        if expected_version:
            return {
                'current': {
                    'id': target.id,
                    'version': target.version
                },
                'expected': {
                    'id': target.id,
                    'version': expected_version
                }
            }
        
        return None
    
    def determine_failure_reasons(self, item_key):
        """Determine the reasons for chain failure with improved clarity."""
        item = self.spec_items.get(item_key)
        if not item:
            return ["Item not found in report"]
        
        reasons = []
        
        # Check for orphaned items
        if item.is_orphaned:
            reasons.append("🔍 Item is not covered by any other items (orphaned)")
        
        # Check for shallow coverage
        if item.is_shallow_covered:
            reasons.append("⚠️ Item has shallow coverage but misses deep coverage")
        
        # Check for version mismatches
        mismatches = item.get_version_mismatches()
        for mismatch in mismatches:
            reasons.append(
                f"♻️ Version mismatch: {mismatch['id']} covers v{mismatch['current_version']} " +
                f"but v{mismatch['expected_version']} is expected"
            )
        
        # Check for uncovered types
        uncovered = item.get_uncovered_types()
        if uncovered:
            reasons.append(f"❌ Missing coverage for types: {', '.join(uncovered)}")
        
        # If no specific reasons found, use the general coverage status
        if not reasons:
            coverage_type = item.coverage_type
            if coverage_type == "UNCOVERED":
                reasons.append("❌ Item is completely uncovered")
            elif coverage_type == "UNKNOWN":
                reasons.append("❓ Unknown coverage issue")
        
        return reasons

    def categorize_items_by_coverage(self):
        """Categorize items by their coverage status for reporting."""
        categories = {
            "COVERED": [],
            "ORPHANED": [],
            "SHALLOW": [],
            "OUTDATED": [],
            "UNCOVERED": [],
            "UNKNOWN": []
        }
        
        for item_key, item in self.spec_items.items():
            categories[item.coverage_type].append(item_key)
        
        return categories
    
    def count_coverage_by_doctype(self):
        """Count coverage statistics by document type."""
        by_doctype = {}
        for item_key, item in self.spec_items.items():
            doctype = item.doctype
            if doctype not in by_doctype:
                by_doctype[doctype] = {
                    "total": 0,
                    "covered": 0,
                    "orphaned": 0,
                    "shallow": 0,
                    "outdated": 0,
                    "uncovered": 0
                }
            
            by_doctype[doctype]["total"] += 1
            
            coverage_type = item.coverage_type
            if coverage_type == "COVERED":
                by_doctype[doctype]["covered"] += 1
            elif coverage_type == "ORPHANED":
                by_doctype[doctype]["orphaned"] += 1
            elif coverage_type == "SHALLOW":
                by_doctype[doctype]["shallow"] += 1
            elif coverage_type == "OUTDATED":
                by_doctype[doctype]["outdated"] += 1
            elif coverage_type == "UNCOVERED":
                by_doctype[doctype]["uncovered"] += 1
        
        return by_doctype