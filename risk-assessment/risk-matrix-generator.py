#!/usr/bin/env python3
"""
Risk Assessment Matrix Generator
Generates risk matrices, registers, and visual reports
Part of MAPELEAD GRC Toolkit

Usage:
    python risk-matrix-generator.py --interactive
    python risk-matrix-generator.py --file risks.csv
"""

import csv
import argparse
from enum import IntEnum
from dataclasses import dataclass, field
from typing import List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
import pyfiglet

console = Console()

class Likelihood(IntEnum):
    RARE = 1
    UNLIKELY = 2
    POSSIBLE = 3
    LIKELY = 4
    ALMOST_CERTAIN = 5

class Impact(IntEnum):
    NEGLIGIBLE = 1
    MINOR = 2
    MODERATE = 3
    SIGNIFICANT = 4
    SEVERE = 5

@dataclass
class Risk:
    id: str
    name: str
    description: str
    category: str
    likelihood: Likelihood
    impact: Impact
    current_controls: List[str] = field(default_factory=list)
    owner: str = ""
    status: str = "Open"

    @property
    def score(self) -> int:
        return int(self.likelihood) * int(self.impact)

    @property
    def level(self) -> str:
        if self.score <= 4: return "Low"
        elif self.score <= 9: return "Medium"
        elif self.score <= 14: return "High"
        else: return "Critical"

    @property
    def level_color(self) -> str:
        if self.score <= 4: return "green"
        elif self.score <= 9: return "yellow"
        elif self.score <= 14: return "orange3"
        else: return "red"


class RiskAssessment:
    def __init__(self):
        self.risks: List[Risk] = []

    def add_risk(self, risk: Risk):
        """Add a risk to the assessment."""
        self.risks.append(risk)

    def display_matrix(self):
        """Display a visual risk matrix."""
        console.print(pyfiglet.figlet_format("Risk Matrix", font="small"))
        
        # Create the matrix grid
        matrix = {}
        for l in range(5, 0, -1):
            for i in range(1, 6):
                score = l * i
                if score <= 4: color = "green"
                elif score <= 9: color = "yellow"
                elif score <= 14: color = "orange3"
                else: color = "red"
                matrix[(l, i)] = (score, color)

        # Display risks in each cell
        cell_risks = {}
        for risk in self.risks:
            key = (int(risk.likelihood), int(risk.impact))
            if key not in cell_risks:
                cell_risks[key] = []
            cell_risks[key].append(risk.id)

        # Print matrix header
        console.print("\n[bold]Risk Matrix (Likelihood × Impact)[/bold]")
        console.print("Impact →")
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Likelihood \\ Impact", style="bold", justify="center")
        for i in Impact:
            table.add_column(i.name, justify="center")

        for l in reversed(range(1, 6)):
            likelihood_name = Likelihood(l).name
            row = [likelihood_name]
            
            for i in range(1, 6):
                score, color = matrix[(l, i)]
                risks_in_cell = cell_risks.get((l, i), [])
                risk_str = ", ".join(risks_in_cell) if risks_in_cell else ""
                
                cell_content = f"[{color}]{score}[/{color}]"
                if risk_str:
                    cell_content += f"\n[cyan]{risk_str}[/cyan]"
                row.append(cell_content)
            
            table.add_row(*row)

        console.print(table)

        # Legend
        console.print("\n[bold]Risk Levels:[/bold]")
        console.print("  [green]1-4: Low[/green]    [yellow]5-9: Medium[/yellow]    [orange3]10-14: High[/orange3]    [red]15-25: Critical[/red]")

    def display_register(self):
        """Display risk register as a table."""
        if not self.risks:
            console.print("[yellow]No risks registered.[/yellow]")
            return

        console.print("\n[bold]Risk Register[/bold]")
        
        table = Table(title=f"Total Risks: {len(self.risks)}")
        table.add_column("ID", style="cyan", width=8)
        table.add_column("Risk Name", style="white", width=30)
        table.add_column("Category", style="yellow")
        table.add_column("L", justify="center")
        table.add_column("I", justify="center")
        table.add_column("Score", justify="center")
        table.add_column("Level", style="bold")
        table.add_column("Owner", style="green")
        table.add_column("Status", style="blue")

        for risk in self.risks:
            table.add_row(
                risk.id,
                risk.name,
                risk.category,
                str(int(risk.likelihood)),
                str(int(risk.impact)),
                str(risk.score),
                f"[{risk.level_color}]{risk.level}[/{risk.level_color}]",
                risk.owner,
                risk.status
            )

        console.print(table)

    def generate_summary(self):
        """Generate risk summary statistics."""
        if not self.risks:
            return

        total = len(self.risks)
        by_level = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
        by_category = {}

        for risk in self.risks:
            by_level[risk.level] += 1
            by_category[risk.category] = by_category.get(risk.category, 0) + 1

        console.print(Panel.fit(
            f"[bold]Risk Summary[/bold]\n\n"
            f"Total Risks: {total}\n"
            f"[red]Critical: {by_level['Critical']}[/red] | "
            f"[orange3]High: {by_level['High']}[/orange3] | "
            f"[yellow]Medium: {by_level['Medium']}[/yellow] | "
            f"[green]Low: {by_level['Low']}[/green]\n\n"
            f"By Category:\n" +
            "\n".join(f"  {cat}: {count}" for cat, count in sorted(by_category.items(), key=lambda x: -x[1])),
            title="Executive Summary"
        ))

    def export_csv(self, filename: str = "risk-register.csv"):
        """Export risk register to CSV."""
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Name', 'Description', 'Category', 'Likelihood',
                           'Impact', 'Score', 'Level', 'Owner', 'Status', 'Controls'])
            for risk in self.risks:
                writer.writerow([
                    risk.id, risk.name, risk.description, risk.category,
                    risk.likelihood.name, risk.impact.name, risk.score,
                    risk.level, risk.owner, risk.status,
                    '; '.join(risk.current_controls)
                ])
        console.print(f"[green]Risk register exported to {filename}[/green]")


def interactive_mode():
    """Run interactive risk assessment."""
    console.print(pyfiglet.figlet_format("GRC Risk", font="small"))
    console.print("[bold]Interactive Risk Assessment[/bold]\n")

    assessment = RiskAssessment()
    
    # Add sample risks
    sample_risks = [
        Risk("R001", "Ransomware Attack", "Encryption of critical business data by ransomware",
             "Cyber Threat", Likelihood.LIKELY, Impact.SEVERE,
             ["Antivirus", "Email filtering"], "IT Security"),
        Risk("R002", "Data Breach", "Unauthorized access to customer PII",
             "Data Protection", Likelihood.POSSIBLE, Impact.SEVERE,
             ["Encryption", "Access controls"], "Data Protection Officer"),
        Risk("R003", "Insider Threat", "Malicious activity by authorized user",
             "Insider Risk", Likelihood.UNLIKELY, Impact.SIGNIFICANT,
             ["DLP", "Monitoring"], "HR / Security"),
        Risk("R004", "DDoS Attack", "Service disruption from denial of service",
             "Availability", Likelihood.POSSIBLE, Impact.MODERATE,
             ["CDN", "Rate limiting"], "Network Team"),
        Risk("R005", "Cloud Misconfiguration", "Exposed resources due to config error",
             "Cloud Security", Likelihood.LIKELY, Impact.SIGNIFICANT,
             ["CSPM", "IaC"], "Cloud Team"),
        Risk("R006", "Supply Chain Attack", "Compromised third-party software",
             "Third Party", Likelihood.RARE, Impact.SEVERE,
             ["Vendor assessments"], "Procurement"),
        Risk("R007", "Physical Theft", "Theft of company equipment",
             "Physical", Likelihood.UNLIKELY, Impact.MODERATE,
             ["Encryption", "Asset tags"], "Facilities"),
        Risk("R008", "Phishing Campaign", "Credential theft via email",
             "Social Engineering", Likelihood.ALMOST_CERTAIN, Impact.MODERATE,
             ["Email security", "Training"], "Security Awareness"),
    ]

    for risk in sample_risks:
        assessment.add_risk(risk)

    # Display results
    assessment.display_matrix()
    assessment.display_register()
    assessment.generate_summary()

    # Ask to export
    console.print("\n[bold]Export Options:[/bold]")
    console.print("1. Export to CSV")
    console.print("2. Continue without export")
    
    try:
        choice = console.input("\nSelect option (1-2): ")
        if choice == "1":
            filename = console.input("Filename [risk-register.csv]: ") or "risk-register.csv"
            assessment.export_csv(filename)
    except (EOFError, KeyboardInterrupt):
        console.print("\n[yellow]Export skipped.[/yellow]")


def main():
    parser = argparse.ArgumentParser(description='Risk Assessment Matrix Generator')
    parser.add_argument('--interactive', action='store_true', help='Run interactive mode')
    parser.add_argument('--file', help='Import risks from CSV file')
    args = parser.parse_args()

    if args.interactive or not args.file:
        interactive_mode()


if __name__ == "__main__":
    main()
