from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon, QImage, QPixmap


app = QApplication([])
app.setQuitOnLastWindowClosed(False)

image = QImage(64, 64, QImage.Format_ARGB32)
image.fill(0x00ff0000) # Fill with transparent background

# ... use QPainter to draw on the image if needed ...
pixmap = QPixmap.fromImage(image)
icon = QIcon(pixmap) # Use the pixmap as the icon
tray = QSystemTrayIcon()
tray.setIcon(icon)

tray.setVisible(True)

menu = QMenu()
entries = ["One", "Two", "Three"]
for entry in entries:
    action = QAction(entry)
    menu.addAction(action)
    action.triggered.connect(app.quit)

tray.setContextMenu(menu)

app.exec_()