"""Gera o ícone Windows usando a mesma logo transparente da interface."""
from pathlib import Path
from PySide6.QtWidgets import QApplication
from n2_collector.branding import logo_icon

app = QApplication([])
output = Path(__file__).resolve().parents[1] / 'build' / 'Coletor.ico'
output.parent.mkdir(parents=True, exist_ok=True)
if not logo_icon().pixmap(256, 256).save(str(output), 'ICO'):
    raise RuntimeError('Não foi possível gerar o ícone do Coletor.')
