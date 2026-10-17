"""Marca empacotada; remove apenas o fundo branco da logo azul e grafite."""
from pathlib import Path
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtCore import Qt

ASSET = Path(__file__).parent / 'assets' / 'logo_soutech.png'


def logo_image():
    image = QImage(str(ASSET)).convertToFormat(QImage.Format.Format_ARGB32)
    if image.isNull():
        raise RuntimeError('Recurso da logo SOUTECH não encontrado.')
    width, height = image.width(), image.height()
    # A marca fornecida usa azul e grafite; o branco é fundo, inclusive
    # nos espaços internos das letras. Os pixels coloridos ficam intactos.
    for y in range(height):
        for x in range(width):
            color = image.pixelColor(x, y)
            if min(color.red(), color.green(), color.blue()) >= 235:
                color.setAlpha(0)
                image.setPixelColor(x, y, color)
    return image


def logo_icon():
    # Tela quadrada transparente mantém a proporção da marca no ícone Windows.
    from PySide6.QtGui import QPainter
    canvas = QPixmap(256, 256)
    canvas.fill(Qt.GlobalColor.transparent)
    logo = QPixmap.fromImage(logo_image()).scaled(240, 240, Qt.AspectRatioMode.KeepAspectRatio,
                                                Qt.TransformationMode.SmoothTransformation)
    painter = QPainter(canvas)
    painter.drawPixmap((256-logo.width())//2, (256-logo.height())//2, logo)
    painter.end()
    return QIcon(canvas)
