"""Interface visível; coleta disparada exclusivamente pelo clique do colaborador."""
import sys
from pathlib import Path
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QPushButton, QProgressBar, QPlainTextEdit)
from .collector import collect
from .branding import logo_image, logo_icon
from .transport import load_transport, DeliveryError


class Worker(QThread):
    progress = Signal(str)
    report_ready = Signal(object)
    completed = Signal(str)
    failed = Signal(str)

    def run(self):
        try:
            base = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parents[2]
            transport = load_transport(base / 'config.json')
            report = collect(self.progress.emit)
            self.report_ready.emit(report)
            self.progress.emit('Simulando envio…')
            self.completed.emit(transport.send(report).message)
        except DeliveryError as exc:
            self.failed.emit(str(exc))
        except Exception:
            self.failed.emit('Não foi possível concluir a operação. Verifique config.json e tente novamente. O relatório disponível permanece nesta janela. Nenhum envio real está habilitado nesta versão.')


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.report = None
        self.worker = None
        self.setWindowTitle('Coletor')
        self.setWindowIcon(logo_icon())
        self.resize(550, 420)
        self.setMinimumSize(440, 400)
        body = QWidget()
        self.setCentralWidget(body)
        layout = QVBoxLayout(body)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(7)

        def label(text, name=None):
            widget = QLabel(text)
            widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            widget.setWordWrap(True)
            if name:
                widget.setObjectName(name)
            layout.addWidget(widget)
            return widget

        logo = label('')
        logo.setPixmap(QPixmap.fromImage(logo_image()).scaledToWidth(
            140, Qt.TransformationMode.SmoothTransformation))
        logo.setAccessibleName('SOUTECH')
        label('Coletor', 'title')
        label('ACIJ • Informações técnicas para o suporte de TI', 'muted')
        label('DADOS PARA <b>SOUTECH</b>', 'heading')
        label('Coleta de informações técnicas do computador e Microsoft Office.', 'muted')
        self.start = QPushButton('Enviar para Andrew')
        self.start.setMinimumHeight(48)
        self.start.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start.clicked.connect(self.run_collection)
        layout.addWidget(self.start)
        label('Modo de testes — nenhum e-mail será enviado.', 'muted')
        self.status = label('Pronto para coletar.', 'status')
        self.bar = QProgressBar()
        self.bar.setRange(0, 1)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(4)
        layout.addWidget(self.bar)
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setMinimumHeight(70)
        self.output.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.output.setPlaceholderText('O relatório técnico aparecerá aqui após a coleta.')
        self.output.setAccessibleName('Relatório técnico')
        layout.addWidget(self.output, 1)
        self.setStyleSheet('''
            QMainWindow, QWidget { background: #111827; color: #e5e7eb; font-family: "Segoe UI"; font-size: 12px; }
            QLabel#title { font-size: 25px; font-weight: 700; color: #ffffff; }
            QLabel#heading { font-size: 16px; color: #f1f5f9; margin-top: 5px; }
            QLabel#muted { color: #a8b5c8; font-size: 11px; }
            QLabel#status { color: #b9d9fa; font-size: 11px; }
            QPushButton { background: #2563eb; color: white; border: none; border-radius: 9px; font-size: 17px; font-weight: 700; }
            QPushButton:hover { background: #1d4ed8; }
            QPushButton:focus { border: 2px solid #7dd3fc; }
            QPushButton:disabled { background: #374151; color: #9ca3af; }
            QPlainTextEdit { background: #0b1220; border: none; border-radius: 8px; padding: 8px; }
            QProgressBar { border: none; background: #253248; border-radius: 2px; }
            QProgressBar::chunk { background: #38bdf8; }
        ''')
        screen = self.screen().availableGeometry()
        self.move(screen.center() - self.rect().center())

    def run_collection(self):
        if self.worker and self.worker.isRunning():
            return
        self.report = None
        self.output.clear()
        self.start.setEnabled(False)
        self.bar.setRange(0, 0)
        self.worker = Worker(self)
        self.worker.progress.connect(self.status.setText)
        self.worker.report_ready.connect(self.show_report)
        self.worker.completed.connect(self.status.setText)
        self.worker.failed.connect(self.status.setText)
        self.worker.finished.connect(self.finish)
        self.worker.start()

    def show_report(self, report):
        self.report = report
        self.output.setPlainText(report.text() + '\n\nAssunto previsto: ' + report.subject)

    def finish(self):
        self.bar.setRange(0, 1)
        self.bar.setValue(1)
        self.start.setEnabled(True)

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.status.setText('Aguarde a consulta terminar para fechar (consultas têm tempo limite).')
            event.ignore()
        else:
            event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = Window()
    window.show()
    return app.exec()
