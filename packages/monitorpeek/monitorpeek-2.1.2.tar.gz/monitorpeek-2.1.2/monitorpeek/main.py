import sys
import mss
import numpy as np
import cv2
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor, QIcon, QPen
from PyQt6.QtCore import Qt, QTimer, QSettings
import os
import win32api
import win32con

__version__ = "2.1.1"  # Added version number

class ScreenCapture:
    """Handles screen capture and image processing."""
    
    def __init__(self, monitor_index=2):
        self.monitor_index = monitor_index
    
    def capture(self):
        """Captures a screenshot and returns the image."""
        try:
            with mss.mss() as sct:
                monitors = sct.monitors
                if len(monitors) <= self.monitor_index:
                    return None  # Exit if monitor not found

                screenshot = sct.grab(monitors[self.monitor_index])
                img = np.array(screenshot)
                return cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)  # Convert color format
        except Exception as e:
            print(f"Error capturing screen: {e}")
            return None

class MonitorPeek(QMainWindow):
    def __init__(self, monitor_index=2):
        super().__init__()
        self.monitor_index = monitor_index
        self.aspect_ratio = 16 / 9  # Always maintain 16:9 aspect ratio
        self.capture = ScreenCapture(monitor_index)
        
        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(40)  # Update ~25 FPS
        
        self.loadWindowSettings()

        self.is_dragging = False  # Flag for dragging state
        self.drag_position = None  # Holds the position where the user clicked to drag

    def initUI(self):
        self.setWindowTitle(f"MonitorPeek v{__version__}")  # Updated title with version
        # Set window flags to stay on top and allow both corner and edge resizing
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Window |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint
        )
        
        # Set the custom icon
        icon_path = os.path.join(os.path.dirname(__file__), "final_icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.label)

        self.setMinimumSize(160, 90)  # Enforce smallest 16:9 size
        
        # Set cursor to default (no resize cursors)
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def get_cursor_position(self):
        """Get the cursor position relative to the captured monitor."""
        try:
            with mss.mss() as sct:
                monitors = sct.monitors
                if len(monitors) <= self.monitor_index:
                    return None

                # Get cursor position
                cursor_x, cursor_y = win32api.GetCursorPos()
                
                # Get monitor position and size
                monitor = monitors[self.monitor_index]
                monitor_x = monitor["left"]
                monitor_y = monitor["top"]
                monitor_width = monitor["width"]
                monitor_height = monitor["height"]
                
                # Check if cursor is within the monitor
                if (monitor_x <= cursor_x < monitor_x + monitor_width and 
                    monitor_y <= cursor_y < monitor_y + monitor_height):
                    # Convert to relative coordinates
                    relative_x = cursor_x - monitor_x
                    relative_y = cursor_y - monitor_y
                    return (relative_x, relative_y)
                return None
        except Exception as e:
            print(f"Error getting cursor position: {e}")
            return None

    def update_frame(self):
        """Update the frame captured from the monitor."""
        img = self.capture.capture()
        if img is None:
            return

        window_width = self.width()
        window_height = self.height()
        
        # Calculate dimensions to maintain 16:9 aspect ratio for the content
        if window_width / window_height > self.aspect_ratio:
            # Window is wider than aspect ratio, adjust height
            content_height = window_height
            content_width = int(content_height * self.aspect_ratio)
        else:
            # Window is taller than aspect ratio, adjust width
            content_width = window_width
            content_height = int(content_width / self.aspect_ratio)

        # Resize image to maintain aspect ratio
        img_resized = cv2.resize(img, (content_width, content_height))

        # Create a black background
        background = np.zeros((window_height, window_width, 3), dtype=np.uint8)
        
        # Calculate position to center the content
        x_offset = (window_width - content_width) // 2
        y_offset = (window_height - content_height) // 2
        
        # Place the resized image on the background
        background[y_offset:y_offset + content_height, x_offset:x_offset + content_width] = img_resized

        # Get cursor position and draw indicator
        cursor_pos = self.get_cursor_position()
        if cursor_pos:
            # Convert cursor position to window coordinates
            cursor_x = int(cursor_pos[0] * content_width / img.shape[1]) + x_offset
            cursor_y = int(cursor_pos[1] * content_height / img.shape[0]) + y_offset
            
            # Draw cursor indicator (a small bright red dot)
            cv2.circle(background, (cursor_x, cursor_y), 2, (0, 0, 255), -1)  # BGR format: (0, 0, 255) is red
            # Add a white center to make it more visible
            cv2.circle(background, (cursor_x, cursor_y), 1, (255, 255, 255), -1)

        qt_img = self.convert_to_qimage(background)
        self.label.setPixmap(QPixmap.fromImage(qt_img))

    def convert_to_qimage(self, img):
        """Convert OpenCV image to QImage."""
        h, w, ch = img.shape
        bytes_per_line = ch * w
        return QImage(img.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

    def create_pixmap(self, qt_img, window_width, window_height):
        """Create a pixmap that fills the entire window."""
        return QPixmap.fromImage(qt_img)

    def resizeEvent(self, event):
        """Handle window resizing."""
        # Get the new size
        new_size = event.size()
        
        # Ensure minimum size
        if new_size.height() < self.minimumHeight():
            new_size.setHeight(self.minimumHeight())
        if new_size.width() < self.minimumWidth():
            new_size.setWidth(self.minimumWidth())
        
        # Apply the new size
        self.resize(new_size)

    def closeEvent(self, event):
        """Save the window size and position when closing."""
        self.saveWindowSettings()
        event.accept()

    def saveWindowSettings(self):
        """Save the window's size and position using QSettings."""
        settings = QSettings("MyApp", "MonitorPeek")
        settings.setValue("window/geometry", self.geometry())

    def loadWindowSettings(self):
        """Load the window's size and position using QSettings."""
        settings = QSettings("MyApp", "MonitorPeek")
        geometry = settings.value("window/geometry")
        
        if geometry:
            self.setGeometry(geometry)
        else:
            self.setGeometry(100, 100, 320, 180)

    def mousePressEvent(self, event):
        """Handle the mouse press event to start dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        """Handle the mouse move event for dragging."""
        if self.is_dragging:
            delta = event.globalPosition().toPoint() - self.drag_position
            self.move(self.pos() + delta)
            self.drag_position = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        """Handle the mouse release event to stop dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False

def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    
    # Set the application icon (this affects taskbar)
    icon_path = os.path.join(os.path.dirname(__file__), "final_icon.ico")
    app_icon = QIcon(icon_path)
    app.setWindowIcon(app_icon)
    
    window = MonitorPeek()
    # Set the window icon explicitly (this affects title bar)
    window.setWindowIcon(app_icon)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 