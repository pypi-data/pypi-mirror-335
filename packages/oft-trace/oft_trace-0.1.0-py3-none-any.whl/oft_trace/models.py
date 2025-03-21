"""Data models for specification items and their relationships."""
from typing import Dict, List, Optional, Any, Set

class SpecItem:
    """Representation of a specification item from an aspec file."""
    
    def __init__(self, item_id: str, version: str, doctype: str):
        self.id = item_id
        self.version = version
        self.doctype = doctype
        self.key = f"{item_id}~{version}"
        self.title = ""
        self.shortdesc = ""
        self.description = ""
        self.status = ""
        self.sourcefile = ""
        self.sourceline = ""
        self.coverage = {}
        self.covers = []
        
    @property
    def is_orphaned(self) -> bool:
        """Check if this item is orphaned (not covered by any other item)."""
        if 'coveringItems' not in self.coverage or not self.coverage['coveringItems']:
            return True
        return False
    
    @property
    def is_outdated(self) -> bool:
        """Check if this item has version mismatch issues."""
        if 'coveringItems' not in self.coverage:
            return False
        
        for covering in self.coverage['coveringItems']:
            if covering.get('coveringStatus') == 'COVERING_WRONG_VERSION':
                return True
        return False
    
    @property
    def is_shallow_covered(self) -> bool:
        """Check if this item has only shallow coverage."""
        if 'deepCoverageStatus' in self.coverage and self.coverage['deepCoverageStatus'] == 'UNCOVERED':
            if 'shallowCoverageStatus' in self.coverage and self.coverage['shallowCoverageStatus'] == 'COVERED':
                return True
        return False
    
    @property 
    def coverage_status(self) -> str:
        """Get the overall coverage status of this item."""
        if 'deepCoverageStatus' in self.coverage:
            return self.coverage['deepCoverageStatus']
        if 'shallowCoverageStatus' in self.coverage:
            return self.coverage['shallowCoverageStatus']
        return "UNKNOWN"
    
    @property
    def coverage_type(self) -> str:
        """Get a descriptive type of coverage issue."""
        if self.is_outdated:
            return "OUTDATED"
        if self.is_shallow_covered:
            return "SHALLOW"
        if self.is_orphaned:
            return "ORPHANED"
        if self.coverage_status == "UNCOVERED":
            return "UNCOVERED"
        if self.coverage_status == "COVERED":
            return "COVERED"
        return "UNKNOWN"
    
    def get_uncovered_types(self) -> List[str]:
        """Get list of uncovered artifact types."""
        if 'uncoveredTypes' in self.coverage:
            return self.coverage['uncoveredTypes']
        return []
    
    def get_version_mismatches(self) -> List[Dict[str, Any]]:
        """Get detailed information about version mismatches."""
        mismatches = []
        if 'coveringItems' not in self.coverage:
            return mismatches
            
        for covering in self.coverage['coveringItems']:
            if covering.get('coveringStatus') == 'COVERING_WRONG_VERSION':
                mismatches.append({
                    'id': covering['id'],
                    'current_version': covering.get('version', 'unknown'),
                    'expected_version': self.version
                })
        
        return mismatches