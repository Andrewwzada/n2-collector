"""Regressões da interface executadas também pelo build Windows."""
import os
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
try:
    from PySide6.QtWidgets import QApplication, QPushButton
    from PySide6.QtCore import Qt
    from n2_collector.app import Window, Worker
    from n2_collector.branding import logo_image, logo_icon
    from n2_collector.model import Report
    QT_AVAILABLE = True
except ModuleNotFoundError as exc:
    if exc.name != 'PySide6':
        raise
    QT_AVAILABLE = False


@unittest.skipUnless(QT_AVAILABLE, 'PySide6 indisponível neste ambiente')
class InterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = Window()

    def tearDown(self):
        self.window.close()

    def test_compact_single_button(self):
        self.assertEqual(self.window.windowTitle(), 'Coletor')
        self.assertEqual((self.window.width(), self.window.height()), (550, 420))
        self.assertEqual([b.text() for b in self.window.findChildren(QPushButton)],
                         ['Enviar para Andrew'])
        self.assertIsNone(self.window.worker)
        self.assertFalse(self.window.windowIcon().isNull())

    def test_logo_transparency_preserves_colored_pixels(self):
        from PySide6.QtGui import QImage
        from n2_collector.branding import ASSET
        original = QImage(str(ASSET))
        image = logo_image()
        self.assertEqual(image.size(), original.size())
        self.assertEqual(image.pixelColor(0, 0).alpha(), 0)
        for y in range(image.height()):
            for x in range(image.width()):
                color = original.pixelColor(x, y)
                if min(color.red(), color.green(), color.blue()) < 235:
                    self.assertEqual(image.pixelColor(x, y), color)
        self.assertFalse(logo_icon().isNull())

    def test_long_report_does_not_enlarge_window(self):
        self.window.show()
        self.app.processEvents()
        size = self.window.size()
        self.window.show_report(Report(notes=['Linha técnica\n' * 100]))
        self.app.processEvents()
        self.assertEqual(self.window.size(), size)
        self.assertGreater(self.window.output.verticalScrollBar().maximum(), 0)
        self.assertIn('Coletor — relatório técnico', self.window.output.toPlainText())
        self.assertTrue(self.window.output.isReadOnly())

    def test_worker_collects_and_simulates(self):
        worker = Worker()
        report = Report(hostname='PC-TESTE')
        reports, completed, errors, progress = [], [], [], []
        worker.report_ready.connect(reports.append)
        worker.completed.connect(completed.append)
        worker.failed.connect(errors.append)
        worker.progress.connect(progress.append)
        with patch('n2_collector.app.collect', return_value=report) as collect:
            worker.run()
        collect.assert_called_once()
        self.assertEqual(reports, [report])
        self.assertFalse(errors)
        self.assertIn('Nenhum dado enviado', completed[0])
        self.assertIn('Simulando envio…', progress)

    def test_collection_failure_is_presented(self):
        worker = Worker()
        errors, completed = [], []
        worker.failed.connect(errors.append)
        worker.completed.connect(completed.append)
        with patch('n2_collector.app.collect', side_effect=RuntimeError('falha')):
            worker.run()
        self.assertEqual(len(errors), 1)
        self.assertFalse(completed)
        self.assertNotIn('CSV', errors[0])


class PackagingTests(unittest.TestCase):
    def test_branding_is_included_in_build(self):
        root = Path(__file__).resolve().parents[1]
        spec = (root / 'N2Collector.spec').read_text()
        self.assertIn("name='Coletor'", spec)
        self.assertIn("icon='build/Coletor.ico'", spec)
        self.assertIn("('src/n2_collector/assets/logo_soutech.png', 'n2_collector/assets')", spec)
        self.assertEqual((root / 'logo_soutech.png').read_bytes(),
                         (root / 'src/n2_collector/assets/logo_soutech.png').read_bytes())
