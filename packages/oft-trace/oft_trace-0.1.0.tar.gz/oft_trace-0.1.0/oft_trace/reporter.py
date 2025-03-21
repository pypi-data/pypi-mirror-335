"""Report generation for aspec trace analysis."""
from typing import Dict, List, Optional
from datetime import datetime
import os

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from oft_trace.visualizer import create_rich_tree, create_ascii_chain

console = Console()

def print_report_header(aspec_file, output_file=False):
    """Print the report header with file information."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_info = f"Report generated from {os.path.abspath(aspec_file)} on {now}"
    
    if output_file:
        print("\n" + "=" * 80)
        print(f"{file_info:^80}")
        print("=" * 80 + "\n")
    else:
        console.print(Panel(f"[bold]{file_info}[/]", width=80))

def display_coverage_summary(analyzer, output_file=False):
    """Display an overview of all items in the report with improved categorization."""
    # Calculate stats
    total_items = len(analyzer.spec_items)
    categories = analyzer.categorize_items_by_coverage()
    
    covered_items = len(categories["COVERED"])
    orphaned_items = len(categories["ORPHANED"])
    shallow_items = len(categories["SHALLOW"])
    outdated_items = len(categories["OUTDATED"])
    uncovered_items = len(categories["UNCOVERED"])
    unknown_items = len(categories["UNKNOWN"])
    
    # Group by doctype
    by_doctype = analyzer.count_coverage_by_doctype()
    
    # Print summary
    if output_file:
        print("\n" + "=" * 80)
        print("COVERAGE SUMMARY".center(80))
        print("=" * 80)
        print(f"Total Items: {total_items}")
        print(f"✅ Covered: {covered_items} ({covered_items/total_items*100:.1f}%)")
        print(f"🔍 Orphaned: {orphaned_items} ({orphaned_items/total_items*100:.1f}%)")
        print(f"⚠️ Shallow covered: {shallow_items} ({shallow_items/total_items*100:.1f}%)")
        print(f"♻️ Outdated: {outdated_items} ({outdated_items/total_items*100:.1f}%)")
        print(f"❌ Uncovered: {uncovered_items} ({uncovered_items/total_items*100:.1f}%)")
        print(f"Other: {unknown_items}")
        print("\nBY DOCUMENT TYPE:")
        print("-" * 100)
        print(f"{'Type':<15} {'Total':<8} {'Covered':<8} {'Orphaned':<10} {'Shallow':<8} {'Outdated':<8} {'Uncovered':<10} {'Coverage %':<10}")
        print("-" * 100)
        
        for doctype, stats in sorted(by_doctype.items()):
            coverage_pct = stats["covered"] / stats["total"] * 100 if stats["total"] > 0 else 0
            print(f"{doctype:<15} {stats['total']:<8} {stats['covered']:<8} {stats['orphaned']:<10} "
                  f"{stats['shallow']:<8} {stats['outdated']:<8} {stats['uncovered']:<10} {coverage_pct:.1f}%")
    else:
        console.print("\n[bold]COVERAGE SUMMARY[/]")
        console.print(f"Total Items: {total_items}")
        console.print(f"✅ Covered: [green]{covered_items}[/] ({covered_items/total_items*100:.1f}%)")
        console.print(f"🔍 Orphaned: [cyan]{orphaned_items}[/] ({orphaned_items/total_items*100:.1f}%)")
        console.print(f"⚠️ Shallow covered: [yellow]{shallow_items}[/] ({shallow_items/total_items*100:.1f}%)")
        console.print(f"♻️ Outdated: [orange3]{outdated_items}[/] ({outdated_items/total_items*100:.1f}%)")
        console.print(f"❌ Uncovered: [red]{uncovered_items}[/] ({uncovered_items/total_items*100:.1f}%)")
        console.print(f"Other: {unknown_items}")
        
        # Create a table for doctypes
        table = Table(title="By Document Type")
        table.add_column("Type", style="cyan")
        table.add_column("Total", justify="right")
        table.add_column("✅ Covered", justify="right", style="green")
        table.add_column("🔍 Orphaned", justify="right", style="cyan")
        table.add_column("⚠️ Shallow", justify="right", style="yellow")
        table.add_column("♻️ Outdated", justify="right", style="orange3")
        table.add_column("❌ Uncovered", justify="right", style="red")
        table.add_column("Coverage %", justify="right")
        
        for doctype, stats in sorted(by_doctype.items()):
            coverage_pct = stats["covered"] / stats["total"] * 100 if stats["total"] > 0 else 0
            table.add_row(
                doctype,
                str(stats["total"]),
                str(stats["covered"]),
                str(stats["orphaned"]),
                str(stats["shallow"]),
                str(stats["outdated"]),
                str(stats["uncovered"]),
                f"{coverage_pct:.1f}%"
            )
        
        console.print(table)
        
        if uncovered_items + orphaned_items + shallow_items + outdated_items > 0:
            console.print("\n[bold yellow]There are issues in the trace report.[/]")
            console.print("Use [cyan]trace-failures[/] command to analyze broken chains.")

def analyze_and_display_failure(analyzer, item_key, index, total, output_file=False):
    """Analyze and display a single broken chain with improved details."""
    item = analyzer.spec_items.get(item_key)
    if not item:
        return  # Skip if item not found
    
    # Get failure reason
    failure_reasons = analyzer.determine_failure_reasons(item_key)
    
    # Get coverage type and appropriate icon
    coverage_type = item.coverage_type
    
    if coverage_type == "ORPHANED":
        icon = "🔍"
        color = "cyan"
    elif coverage_type == "SHALLOW":
        icon = "⚠️"
        color = "yellow"
    elif coverage_type == "OUTDATED":
        icon = "♻️"
        color = "orange3"
    elif coverage_type == "UNCOVERED":
        icon = "❌"
        color = "red"
    else:
        icon = "❓"
        color = "white"
    
    # Header
    if output_file:
        print(f"\nFAILURE {index}/{total}: {item_key} [{item.doctype}] ({coverage_type})")
        print(f"Title: {getattr(item, 'shortdesc', 'N/A')}")
        if item.sourcefile:
            print(f"Source: {item.sourcefile}" + (f":{item.sourceline}" if item.sourceline else ""))
        print("\nFailure reasons:")
        for reason in failure_reasons:
            print(f"- {reason}")
    else:
        console.print(f"\n[bold {color}]{icon} FAILURE {index}/{total}:[/] [cyan]{item_key}[/] [blue][{item.doctype}][/] ([{color}]{coverage_type}[/])")
        console.print(f"[bold]Title:[/] {getattr(item, 'shortdesc', 'N/A')}")
        if item.sourcefile:
            console.print(f"[bold]Source:[/] {item.sourcefile}" + 
                         (f":{item.sourceline}" if item.sourceline else ""))
        
        console.print("\n[bold]Failure reasons:[/]")
        for reason in failure_reasons:
            console.print(f"- {reason}")
    
    # Show visual representation
    if output_file:
        print("\nTrace chain visualization:")
        create_ascii_chain(analyzer, item_key, direction='both')
    else:
        console.print("\n[bold]Trace chain visualization:[/]")
        tree = create_rich_tree(analyzer, item_key, direction='both')
        console.print(tree)