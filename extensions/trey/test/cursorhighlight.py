import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QCursor
from PyQt5.QtWidgets import QApplication, QWidget

class CursorHighlighter(QWidget):
    def __init__(self):
        super().__init__()
        
        # Make the window frameless, transparent to clicks, and stay on top
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.WA_TranslucentBackground |
            Qt.WA_TransparentForMouseEvents |
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        # Set highlighter circle size (diameter)
        self.size = 50
        self.resize(self.size, self.size)
        
        # Timer to track global cursor position
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(10)  # ~100 FPS tracking
        
        self.show()

    def update_position(self):
        # Get the global cursor position from QApplication
        pos = QCursor.pos()
        # Alternative modern PyQt5 way to get global cursor position:
        # from PyQt5.QtGui import QCursor
        # pos = QCursor.pos()
        
        # Center the highlight circle around the mouse pointer
        self.move(pos.x() - self.size // 2, pos.y() - self.size // 2)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw a semi-transparent yellow/orange circle
        color = QColor(255, 255, 0, 120)  # RGBA: Yellow with alpha transparency
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, self.size, self.size)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    highlighter = CursorHighlighter()
    sys.exit(app.exec_())