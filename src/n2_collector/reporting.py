"""Exportação explícita, compatível com Excel e protegida contra fórmulas CSV."""
import csv
from pathlib import Path
from .model import Report

def safe_cell(value: str) -> str:
    if value.lstrip().startswith(("=", "+", "-", "@")) or value.startswith(("\t", "\r", "\n")):
        return "'" + value
    return value

def export_csv(report: Report, path: Path) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream, delimiter=";")
        writer.writerow(["Campo", "Valor"])
        writer.writerows((safe_cell(k), safe_cell(v)) for k, v in report.rows())
