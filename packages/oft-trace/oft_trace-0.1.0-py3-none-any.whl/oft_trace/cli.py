"""Command-line interface for aspec trace analysis."""
import os
import sys
import time
from typing import Optional
from datetime import datetime

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

# Use absolute imports instead of relative
from oft_trace.parser import parse_aspec_file
from oft_trace.analyzer import TraceAnalyzer
from oft_trace.reporter import print_report_header, display_coverage_summary, analyze_and_display_failure
from oft_trace.visualizer import create_rich_tree, create_ascii_chain

app = typer.Typer(help="Analyze and display trace chains for OpenFastTrace specification items")
console = Console()

@app.command()
def trace(
    aspec_file: str = typer.Argument(..., help="Path to the aspec XML file"),
    spec_id: Optional[str] = typer.Argument(None, help="ID of the specification item to analyze (if omitted, shows overview)"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="Specific version of the item to trace"),
    doctype: Optional[str] = typer.Option(None, "--doctype", "-t", help="Filter by document type"),
    direction: str = typer.Option("both", "--direction", "-d", 
                                 help="Direction of links to trace: both, incoming, or outgoing"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", 
                                            help="Path to output file (if not specified, print to console)"),
    show_details: bool = typer.Option(True, "--details/--no-details", 
                                    help="Show detailed trace information"),
    show_visual: bool = typer.Option(True, "--visual/--no-visual", 
                                   help="Show visual representation of trace chain")
):
    """
    Analyze and display the trace chain for a specification item in an aspec XML file.
    
    If spec_id is not provided, shows an overview of the entire report.
    """
    if not os.path.exists(aspec_file):
        console.print(f"[bold red]Error:[/] Aspec file '{aspec_file}' not found.")
        raise typer.Exit(code=1)
    
    if direction not in ["both", "incoming", "outgoing"]:
        console.print(f"[bold red]Error:[/] Direction must be one of: both, incoming, outgoing")
        raise typer.Exit(code=1)
    
    # Load and parse the aspec file
    console.print(f"Loading data from [cyan]{os.path.basename(aspec_file)}[/]...")
    start_time = time.time()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Parsing aspec file...", total=None)
        spec_items, id_map, covering_map, covered_by_map, broken_chains = parse_aspec_file(aspec_file)
        progress.update(task, completed=True)
    
    elapsed = time.time() - start_time
    console.print(f"Loaded [green]{len(spec_items)}[/] items in [cyan]{elapsed:.2f}s[/]")
    
    # Create analyzer
    analyzer = TraceAnalyzer(spec_items, id_map, covering_map, covered_by_map, broken_chains, aspec_file)
    
    # If output file is specified, redirect output
    original_stdout = None
    if output_file:
        original_stdout = sys.stdout
        sys.stdout = open(output_file, 'w')
    
    try:
        # Print report header
        print_report_header(aspec_file, bool(output_file))
        
        if spec_id:
            # Find item by ID and optional doctype/version
            item_key = analyzer.get_item_by_id(spec_id, doctype, version)
            
            if not item_key:
                error_msg = f"Error: Item {spec_id}"
                if version:
                    error_msg += f" with version {version}"
                if doctype:
                    error_msg += f" of type {doctype}"
                error_msg += " not found in the aspec file."
                
                if output_file:
                    print(error_msg)
                else:
                    console.print(f"[bold red]{error_msg}[/]")
                return
            
            # Display single item chain
            header = f"TRACE CHAIN FOR {item_key}"
            if output_file:
                print("\n" + "=" * 80)
                print(f"{header:^80}")
                print("=" * 80 + "\n")
            else:
                from rich.panel import Panel
                console.print(Panel(f"[bold]{header}[/]", width=80))
            
            # Display visual representation
            if show_visual:
                if output_file:
                    print("\nVISUAL REPRESENTATION OF THE TRACE CHAIN\n")
                    create_ascii_chain(analyzer, item_key, direction=direction)
                else:
                    console.print("\n[bold]VISUAL REPRESENTATION OF THE TRACE CHAIN[/]")
                    tree = create_rich_tree(analyzer, item_key, direction=direction)
                    console.print(tree)
        else:
            # Display overview of all items
            display_coverage_summary(analyzer, bool(output_file))
    
    finally:
        # Restore stdout if it was redirected
        if output_file and original_stdout:
            sys.stdout.close()
            sys.stdout = original_stdout
            console.print(f"[green]Trace results written to {output_file}[/]")


@app.command()
def list_items(
    aspec_file: str = typer.Argument(..., help="Path to the aspec XML file"),
    doctype: Optional[str] = typer.Option(None, "--doctype", "-t", help="Filter by document type"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status"),
    coverage: Optional[str] = typer.Option(None, "--coverage", "-c", 
                                         help="Filter by coverage status (COVERED, UNCOVERED, ORPHANED, SHALLOW, OUTDATED)"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", 
                                            help="Path to output file (if not specified, print to console)")
):
    """
    List all specification items in the aspec file with improved filtering.
    """
    if not os.path.exists(aspec_file):
        console.print(f"[bold red]Error:[/] Aspec file '{aspec_file}' not found.")
        raise typer.Exit(code=1)
    
    # Load and parse the aspec file
    console.print(f"Loading data from [cyan]{os.path.basename(aspec_file)}[/]...")
    start_time = time.time()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Parsing aspec file...", total=None)
        spec_items, id_map, covering_map, covered_by_map, broken_chains = parse_aspec_file(aspec_file)
        progress.update(task, completed=True)
    
    elapsed = time.time() - start_time
    console.print(f"Loaded [green]{len(spec_items)}[/] items in [cyan]{elapsed:.2f}s[/]")
    
    # Create analyzer
    analyzer = TraceAnalyzer(spec_items, id_map, covering_map, covered_by_map, broken_chains, aspec_file)
    
    # If output file is specified, redirect output
    original_stdout = None
    if output_file:
        original_stdout = sys.stdout
        sys.stdout = open(output_file, 'w')
    
    try:
        # Filter items based on criteria
        filtered_items = []
        for item_key, item in spec_items.items():
            # Filter by doctype
            if doctype and item.doctype != doctype:
                continue
            
            # Filter by status
            if status and (not hasattr(item, 'status') or item.status != status):
                continue
            
            # Filter by coverage
            if coverage:
                if coverage == "COVERED" and item.coverage_type != "COVERED":
                    continue
                elif coverage == "UNCOVERED" and item.coverage_type != "UNCOVERED":
                    continue
                elif coverage == "ORPHANED" and item.coverage_type != "ORPHANED":
                    continue
                elif coverage == "SHALLOW" and item.coverage_type != "SHALLOW":
                    continue
                elif coverage == "OUTDATED" and item.coverage_type != "OUTDATED":
                    continue
            
            filtered_items.append(item)
        
        # Display items
        if not filtered_items:
            if output_file:
                print("No items match the specified criteria.")
            else:
                console.print("[yellow]No items match the specified criteria.[/]")
            return
        
        if output_file:
            print(f"\nFound {len(filtered_items)} matching items:\n")
            print("=" * 100)
            print(f"{'ID':<15} {'Version':<8} {'Type':<10} {'Status':<12} {'Coverage':<12} {'Source':<20}")
            print("=" * 100)
            
            for item in filtered_items:
                # Get coverage type
                coverage_type = item.coverage_type
                
                # Format source info
                source_info = ""
                if item.sourcefile:
                    source_info = item.sourcefile
                    if item.sourceline:
                        source_info += f":{item.sourceline}"
                
                print(f"{item.id:<15} {item.version:<8} {item.doctype:<10} "
                      f"{getattr(item, 'status', 'unknown'):<12} {coverage_type:<12} {source_info:<20}")
                
                if hasattr(item, 'shortdesc') and item.shortdesc:
                    print(f"  {item.shortdesc}")
                
                print()
            
            print("=" * 100)
        else:
            console.print(f"\n[bold]Found {len(filtered_items)} matching items:[/]\n")
            
            # Create a Rich table for better formatting
            from rich.table import Table
            table = Table(show_header=True, header_style="bold")
            table.add_column("ID")
            table.add_column("Version")
            table.add_column("Type")
            table.add_column("Status")
            table.add_column("Coverage")
            table.add_column("Source")
            table.add_column("Title")
            
            for item in filtered_items:
                # Get coverage type and appropriate styling
                coverage_type = item.coverage_type
                
                if coverage_type == "COVERED":
                    coverage_style = "green"
                    coverage_icon = "✅"
                elif coverage_type == "ORPHANED":
                    coverage_style = "cyan"
                    coverage_icon = "🔍"
                elif coverage_type == "SHALLOW":
                    coverage_style = "yellow"
                    coverage_icon = "⚠️"
                elif coverage_type == "OUTDATED":
                    coverage_style = "orange3" 
                    coverage_icon = "♻️"
                elif coverage_type == "UNCOVERED":
                    coverage_style = "red"
                    coverage_icon = "❌"
                else:
                    coverage_style = "white"
                    coverage_icon = "❓"
                
                # Format source info
                source_info = ""
                if item.sourcefile:
                    source_info = item.sourcefile
                    if item.sourceline:
                        source_info += f":{item.sourceline}"
                
                table.add_row(
                    item.id,
                    item.version,
                    f"[blue]{item.doctype}[/]",
                    getattr(item, 'status', 'unknown'),
                    f"[{coverage_style}]{coverage_icon} {coverage_type}[/]",
                    source_info,
                    getattr(item, 'shortdesc', '')
                )
            
            console.print(table)
    
    finally:
        # Restore stdout if it was redirected
        if output_file and original_stdout:
            sys.stdout.close()
            sys.stdout = original_stdout
            console.print(f"[green]Item list written to {output_file}[/]")


@app.command()
def trace_failures(
    aspec_file: str = typer.Argument(..., help="Path to the aspec XML file"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", 
                                             help="Path to output file (if not specified, print to console)"),
    limit: Optional[int] = typer.Option(None, "--limit", "-l", 
                                      help="Limit the number of failures to analyze"),
    include_covered: bool = typer.Option(False, "--include-covered", "-a",
                                      help="Include all items including covered ones")
):
    """
    Analyze and report on all broken chains in the aspec file with improved clarity.
    
    This command identifies items with coverage issues and analyzes the reasons 
    for the failures in detail.
    """
    if not os.path.exists(aspec_file):
        console.print(f"[bold red]Error:[/] Aspec file '{aspec_file}' not found.")
        raise typer.Exit(code=1)
    
    # Load and parse the aspec file
    console.print(f"Loading data from [cyan]{os.path.basename(aspec_file)}[/]...")
    start_time = time.time()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Parsing aspec file...", total=None)
        spec_items, id_map, covering_map, covered_by_map, broken_chains = parse_aspec_file(aspec_file)
        progress.update(task, completed=True)
    
    elapsed = time.time() - start_time
    console.print(f"Loaded [green]{len(spec_items)}[/] items in [cyan]{elapsed:.2f}s[/]")
    
    # Create analyzer
    analyzer = TraceAnalyzer(spec_items, id_map, covering_map, covered_by_map, broken_chains, aspec_file)
    
    # If output file is specified, redirect output
    original_stdout = None
    if output_file:
        original_stdout = sys.stdout
        sys.stdout = open(output_file, 'w')
    
    try:
        # Print report header
        print_report_header(aspec_file, bool(output_file))
        
        # Get all items or just broken chains
        if include_covered:
            items_to_analyze = list(spec_items.keys())
        else:
            items_to_analyze = broken_chains
        
        # Overview of failures
        if not items_to_analyze:
            if output_file:
                print("\nNo issues found in the report!")
            else:
                console.print("\n[green]No issues found in the report![/]")
            return
        
        # Limit the number of items to analyze
        if limit and limit < len(items_to_analyze):
            items_to_analyze = items_to_analyze[:limit]
        
        # Print header
        if output_file:
            if include_covered:
                print(f"\nAnalyzing {len(items_to_analyze)} items")
            else:
                print(f"\nFound {len(broken_chains)} items with issues")
            
            if limit:
                print(f"Showing first {limit} items")
            print("\n" + "=" * 80)
        else:
            if include_covered:
                console.print(f"\n[bold]Analyzing {len(items_to_analyze)} items[/]")
            else:
                console.print(f"\n[bold]Found {len(broken_chains)} items with issues[/]")
            
            if limit:
                console.print(f"[yellow]Showing first {limit} items[/]")
            console.print("=" * 80)
        
        # Analyze each failure
        for i, item_key in enumerate(items_to_analyze):
            if include_covered or analyzer.spec_items[item_key].coverage_type != "COVERED":
                analyze_and_display_failure(analyzer, item_key, i+1, len(items_to_analyze), bool(output_file))
                
                if output_file:
                    print("\n" + "-" * 80 + "\n")
                else:
                    console.print("\n" + "-" * 80 + "\n")
    
    finally:
        # Restore stdout if it was redirected
        if output_file and original_stdout:
            sys.stdout.close()
            sys.stdout = original_stdout
            console.print(f"[green]Analysis written to {output_file}[/]")


def main():
    """Entry point for the CLI."""
    app()

if __name__ == "__main__":
    app()