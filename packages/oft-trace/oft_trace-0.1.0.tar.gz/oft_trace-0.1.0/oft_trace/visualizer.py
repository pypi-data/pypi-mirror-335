"""Visualization utilities for trace chains."""
from typing import Dict, Set, Optional, Any
from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel

console = Console()

def create_rich_tree(analyzer, item_key, visited=None, direction='both'):
    """Create a rich tree representation of the trace chain with improved visualization."""
    if visited is None:
        visited = set()
    
    item = analyzer.spec_items.get(item_key)
    if not item:
        return Tree(f"[bold red]NOT FOUND: {item_key}[/]")
    
    # Determine item styling based on coverage type
    coverage_type = item.coverage_type
    
    if coverage_type == "COVERED":
        icon = "✅"
        style = "bold green"
    elif coverage_type == "OUTDATED":
        icon = "♻️"
        style = "bold orange3"
    elif coverage_type == "SHALLOW":
        icon = "⚠️"
        style = "bold yellow"
    elif coverage_type == "ORPHANED":
        icon = "🔍"
        style = "bold cyan"
    elif coverage_type == "UNCOVERED":
        icon = "❌"
        style = "bold red"
    else:
        icon = "❓"
        style = "bold white"
    
    # Create node text with proper styling
    node_text = f"[{style}]{icon} {item.id}[/] [dim](v{item.version})[/] [blue][{item.doctype}][/]"
    
    # Add title if available
    if item.shortdesc:
        node_text += f" - {item.shortdesc}"
    elif hasattr(item, 'title') and item.title:
        node_text += f" - {item.title}"
    
    # Add source file info
    if item.sourcefile:
        node_text += f" [dim]({item.sourcefile}"
        if item.sourceline:
            node_text += f":{item.sourceline}"
        node_text += ")[/]"
    
    # Create the tree
    tree = Tree(node_text)
    
    # Don't continue if we've already visited this item
    if item_key in visited:
        tree.add("[yellow]⟲ CYCLE DETECTED[/]")
        return tree
    
    visited.add(item_key)
    
    # Add covered items (outgoing)
    if direction in ['both', 'outgoing'] and item_key in analyzer.covering_map and analyzer.covering_map[item_key]:
        covers_branch = tree.add("[blue]Covers:[/]")
        for covered_key in analyzer.covering_map[item_key]:
            # Check for version mismatch
            is_mismatch = analyzer.is_version_mismatch(item_key, covered_key)
            
            if covered_key in visited:
                label = f"[yellow]⟲ CYCLE: {covered_key}[/]"
                if is_mismatch:
                    mismatch_details = analyzer.get_version_mismatch_details(item_key, covered_key)
                    if mismatch_details:
                        label = f"[bold red]♻️ VERSION MISMATCH: Covering v{mismatch_details['current']['version']} but v{mismatch_details['expected']['version']} expected[/] " + label
                    else:
                        label = f"[bold red]♻️ VERSION MISMATCH![/] " + label
                covers_branch.add(label)
            else:
                covered_item = analyzer.spec_items.get(covered_key)
                if covered_item:
                    if is_mismatch:
                        mismatch_details = analyzer.get_version_mismatch_details(item_key, covered_key)
                        if mismatch_details:
                            version_branch = covers_branch.add(
                                f"[bold red]♻️ VERSION MISMATCH: Covering v{mismatch_details['current']['version']} but v{mismatch_details['expected']['version']} expected[/]"
                            )
                        else:
                            version_branch = covers_branch.add("[bold red]♻️ VERSION MISMATCH![/]")
                        sub_tree = create_rich_tree(analyzer, covered_key, visited.copy(), 'outgoing')
                        version_branch.add(sub_tree)
                    else:
                        sub_tree = create_rich_tree(analyzer, covered_key, visited.copy(), 'outgoing')
                        covers_branch.add(sub_tree)
                else:
                    label = f"[red]⨯ NOT FOUND: {covered_key}[/]"
                    if is_mismatch:
                        label = f"[bold red]♻️ VERSION MISMATCH![/] " + label
                    covers_branch.add(label)
    
    # Add covering items (incoming)
    if direction in ['both', 'incoming'] and item_key in analyzer.covered_by_map and analyzer.covered_by_map[item_key]:
        covered_by_branch = tree.add("[blue]Covered By:[/]")
        for covering_key in analyzer.covered_by_map[item_key]:
            # Check for version mismatch
            is_mismatch = analyzer.is_version_mismatch(covering_key, item_key)
            
            if covering_key in visited:
                label = f"[yellow]⟲ CYCLE: {covering_key}[/]"
                if is_mismatch:
                    mismatch_details = analyzer.get_version_mismatch_details(covering_key, item_key)
                    if mismatch_details:
                        label = f"[bold red]♻️ VERSION MISMATCH: Covering v{mismatch_details['current']['version']} but v{mismatch_details['expected']['version']} expected[/] " + label
                    else:
                        label = f"[bold red]♻️ VERSION MISMATCH![/] " + label
                covered_by_branch.add(label)
            else:
                covering_item = analyzer.spec_items.get(covering_key)
                if covering_item:
                    if is_mismatch:
                        mismatch_details = analyzer.get_version_mismatch_details(covering_key, item_key)
                        if mismatch_details:
                            version_branch = covered_by_branch.add(
                                f"[bold red]♻️ VERSION MISMATCH: Covering v{mismatch_details['current']['version']} but v{mismatch_details['expected']['version']} expected[/]"
                            )
                        else:
                            version_branch = covered_by_branch.add("[bold red]♻️ VERSION MISMATCH![/]")
                        sub_tree = create_rich_tree(analyzer, covering_key, visited.copy(), 'incoming')
                        version_branch.add(sub_tree)
                    else:
                        sub_tree = create_rich_tree(analyzer, covering_key, visited.copy(), 'incoming')
                        covered_by_branch.add(sub_tree)
                else:
                    label = f"[red]⨯ NOT FOUND: {covering_key}[/]"
                    if is_mismatch:
                        mismatch_details = analyzer.get_version_mismatch_details(covering_key, item_key)
                        if mismatch_details:
                            label = f"[bold red]♻️ VERSION MISMATCH: Covering v{mismatch_details['current']['version']} but v{mismatch_details['expected']['version']} expected[/] " + label
                        else:
                            label = f"[bold red]♻️ VERSION MISMATCH![/] " + label
                    covered_by_branch.add(label)
    
    return tree

def create_ascii_chain(analyzer, item_key, depth=0, prefix="", is_last=True, visited=None, direction='both'):
    """Create an ASCII art representation of the trace chain with improved visualization."""
    if visited is None:
        visited = set()
    
    if item_key in visited:
        print(f"{prefix}{'└── ' if is_last else '├── '}⟲ CYCLE: {item_key}")
        return
    
    visited.add(item_key)
    
    item = analyzer.spec_items.get(item_key)
    if not item:
        print(f"{prefix}{'└── ' if is_last else '├── '}⨯ NOT FOUND: {item_key}")
        return
    
    # Determine the status indicator
    coverage_type = item.coverage_type
    
    if coverage_type == "COVERED":
        status_indicator = "✅"  # Covered item
    elif coverage_type == "OUTDATED":
        status_indicator = "♻️"  # Outdated/wrong version
    elif coverage_type == "SHALLOW":
        status_indicator = "⚠️"  # Partially covered
    elif coverage_type == "ORPHANED":
        status_indicator = "🔍"  # Orphaned item
    elif coverage_type == "UNCOVERED":
        status_indicator = "❌"  # Uncovered item
    else:
        status_indicator = "❓"  # Unknown status
    
    # Display this item with source file info and version
    item_text = f"{status_indicator} {item.id} (v{item.version}) [{item.doctype}]"
    if item.shortdesc:
        item_text += f" - {item.shortdesc}"
    if item.sourcefile:
        item_text += f" ({item.sourcefile}"
        if item.sourceline:
            item_text += f":{item.sourceline}"
        item_text += ")"
    
    print(f"{prefix}{'└── ' if is_last else '├── '}{item_text}")
    
    # Prepare for displaying children
    new_prefix = prefix + ("    " if is_last else "│   ")
    
    # Display outgoing links (what this item covers)
    if direction in ['both', 'outgoing'] and item_key in analyzer.covering_map and analyzer.covering_map[item_key]:
        outgoing_links = analyzer.covering_map[item_key]
        for i, covered_key in enumerate(outgoing_links):
            is_last_child = i == len(outgoing_links) - 1
            
            # Check for version mismatch
            is_mismatch = analyzer.is_version_mismatch(item_key, covered_key)
            
            # For outgoing links, we're only showing downward if direction is 'both'
            if direction == 'both' and covered_key in visited:
                print(f"{new_prefix}{'└── ' if is_last_child else '├── '}⟲ CYCLE: {covered_key}")
            else:
                if is_mismatch:
                    mismatch_details = analyzer.get_version_mismatch_details(item_key, covered_key)
                    if mismatch_details:
                        print(f"{new_prefix}{'└── ' if is_last_child else '├── '}♻️ VERSION MISMATCH: Covering v{mismatch_details['current']['version']} but v{mismatch_details['expected']['version']} expected")
                    else:
                        print(f"{new_prefix}{'└── ' if is_last_child else '├── '}♻️ VERSION MISMATCH!")
                
                create_ascii_chain(analyzer, covered_key, depth + 1, new_prefix, is_last_child, 
                                visited.copy(), 'outgoing')
    
    # Display incoming links (what covers this item)
    if direction in ['both', 'incoming'] and item_key in analyzer.covered_by_map and analyzer.covered_by_map[item_key]:
        incoming_links = analyzer.covered_by_map[item_key]
        for i, covering_key in enumerate(incoming_links):
            is_last_child = i == len(incoming_links) - 1
            
            # Check for version mismatch
            is_mismatch = analyzer.is_version_mismatch(covering_key, item_key)
            
            # For incoming links, we're only showing upward if direction is 'both'
            if direction == 'both' and covering_key in visited:
                print(f"{new_prefix}{'└── ' if is_last_child else '├── '}⟲ CYCLE: {covering_key}")
            else:
                if is_mismatch:
                    mismatch_details = analyzer.get_version_mismatch_details(covering_key, item_key)
                    if mismatch_details:
                        print(f"{new_prefix}{'└── ' if is_last_child else '├── '}♻️ VERSION MISMATCH: Covering v{mismatch_details['current']['version']} but v{mismatch_details['expected']['version']} expected")
                    else:
                        print(f"{new_prefix}{'└── ' if is_last_child else '├── '}♻️ VERSION MISMATCH!")
                
                create_ascii_chain(analyzer, covering_key, depth + 1, new_prefix, is_last_child, 
                                visited.copy(), 'incoming')