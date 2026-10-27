from __future__ import annotations

import csv
import json
import re
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, QRunnable, Qt, QSettings, QThreadPool, Signal, Slot
from PySide6.QtGui import QAction, QColor, QFont, QKeySequence, QPalette, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

try:  # pragma: no cover - runtime fallback for bundled execution
    from .bridge import InteractionCallbacks
    from .service import AuthenticationError, TokenExtractorService
except ImportError:
    from token_extractor_gui.bridge import InteractionCallbacks
    from token_extractor_gui.service import AuthenticationError, TokenExtractorService

ANSI_ESCAPE_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")

def _chevron_path() -> str:
    candidates = [Path(__file__).resolve().parent / "assets" / "chevron-down.svg"]
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(Path(meipass) / "assets" / "chevron-down.svg")
    for path in candidates:
        if path.is_file():
            return path.as_posix()
    return ""


def _stylesheet() -> str:
    chevron = _chevron_path()
    # Quoted so a Windows path such as C:/... does not end the CSS rule at the colon.
    arrow = f'image: url("{chevron}");' if chevron else "image: none;"
    return STYLESHEET.replace("image: url(__CHEVRON__);", arrow)


STYLESHEET = """
QWidget {
    color: #f5f5f7;
    font-size: 13px;
}
QFrame#sidebar {
    background: #161618;
    border-right: 1px solid #2c2c2e;
}
QFrame#main, QFrame#footer {
    background: #1c1c1e;
}
QFrame#footer {
    border-top: 1px solid #2c2c2e;
}
QFrame#segment {
    background: #1c1c1e;
    border-radius: 10px;
}
QFrame#selectionBar {
    background: #2c2c2e;
    border-radius: 12px;
}
QLabel#kicker {
    color: #0a84ff;
    font-size: 11px;
    font-weight: 600;
}
QLabel#appTitle, QLabel#pageTitle, QLabel#placeholderTitle {
    font-size: 22px;
    font-weight: 600;
}
QLabel#subtitle, QLabel#hint, QLabel#selectionHint {
    color: #98989d;
}
QLabel#countBadge {
    background: #2c2c2e;
    color: #98989d;
    border-radius: 9px;
    padding: 2px 8px;
    font-size: 12px;
}
QLabel#fieldLabel {
    color: #98989d;
    font-size: 12px;
    font-weight: 600;
}
QLineEdit, QComboBox, QPlainTextEdit {
    background: #1c1c1e;
    color: #f5f5f7;
    border: 1px solid #3a3a3c;
    border-radius: 8px;
    padding: 8px 10px;
    selection-background-color: #0a84ff;
}
QComboBox {
    padding-right: 28px;
}
QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus {
    border: 1px solid #0a84ff;
}
QLineEdit:disabled, QComboBox:disabled {
    color: #636366;
    background: #1c1c1e;
}
QComboBox::drop-down {
    border: none;
    width: 28px;
}
QComboBox::down-arrow {
    image: url(__CHEVRON__);
    width: 12px;
    height: 12px;
}
QComboBox QAbstractItemView {
    background: #2c2c2e;
    color: #f5f5f7;
    border: 1px solid #48484a;
    selection-background-color: #0a84ff;
    outline: none;
    padding: 4px;
}
QCheckBox {
    spacing: 8px;
}
QPushButton {
    background: #48484a;
    color: #f5f5f7;
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
}
QPushButton:hover {
    background: #636366;
}
QPushButton:pressed {
    background: #3a3a3c;
}
QPushButton:disabled {
    background: #2c2c2e;
    color: #636366;
}
QPushButton#primary {
    background: #0a84ff;
    color: white;
    font-weight: 600;
    padding: 10px 16px;
}
QPushButton#primary:hover {
    background: #409cff;
}
QPushButton#primary:pressed {
    background: #0070e0;
}
QPushButton#primary:disabled {
    background: #1f4f86;
    color: #d0d0d4;
}
QPushButton#ghost {
    background: transparent;
    color: #0a84ff;
    padding: 8px 10px;
}
QPushButton#ghost:hover {
    background: #2c2c2e;
}
QPushButton#ghost:disabled {
    background: transparent;
    color: #636366;
}
QPushButton#segmentButton {
    background: transparent;
    color: #98989d;
    border-radius: 8px;
    padding: 8px 12px;
    font-weight: 600;
}
QPushButton#segmentButton:hover {
    background: transparent;
    color: #f5f5f7;
}
QPushButton#segmentButton:checked {
    background: #3a3a3c;
    color: #f5f5f7;
}
QPushButton#segmentButton:disabled {
    background: transparent;
    color: #636366;
}
QTreeWidget {
    background: #161618;
    border: 1px solid #2c2c2e;
    border-radius: 12px;
    outline: none;
    padding: 4px;
}
QTreeWidget::item {
    padding: 6px 4px;
    border-radius: 6px;
}
QTreeWidget::item:hover {
    background: #2c2c2e;
}
QTreeWidget::item:selected {
    background: #0a84ff;
    color: white;
}
QHeaderView::section {
    background: #161618;
    color: #8e8e93;
    border: none;
    border-bottom: 1px solid #2c2c2e;
    padding: 8px 10px;
    font-size: 11px;
    font-weight: 600;
}
QProgressBar {
    background: #2c2c2e;
    border: none;
    border-radius: 3px;
    max-height: 6px;
    min-height: 6px;
}
QProgressBar::chunk {
    background: #0a84ff;
    border-radius: 3px;
}
QPlainTextEdit#log {
    background: #111113;
    color: #d1d1d6;
    border: none;
    border-radius: 0;
    padding: 8px 12px;
}
QMenu {
    background: #2c2c2e;
    color: #f5f5f7;
    border: 1px solid #48484a;
    border-radius: 8px;
    padding: 4px;
}
QMenu::item {
    padding: 6px 18px;
    border-radius: 6px;
}
QMenu::item:selected {
    background: #0a84ff;
}
QMenu::separator {
    height: 1px;
    background: #48484a;
    margin: 4px 8px;
}
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 4px 2px;
}
QScrollBar::handle:vertical {
    background: #48484a;
    border-radius: 4px;
    min-height: 24px;
}
QScrollBar:horizontal {
    background: transparent;
    height: 10px;
    margin: 2px 4px;
}
QScrollBar::handle:horizontal {
    background: #48484a;
    border-radius: 4px;
    min-width: 24px;
}
QScrollBar::add-line, QScrollBar::sub-line,
QScrollBar::add-page, QScrollBar::sub-page {
    background: transparent;
    height: 0;
    width: 0;
}
QDialog {
    background: #2c2c2e;
}
"""


def get_user_friendly_error(exception: Exception) -> str:
    """Convert technical exceptions to user-friendly error messages."""
    error_str = str(exception).lower()

    if "connection" in error_str or "network" in error_str:
        return (
            "Network Connection Error\n\n"
            "Could not connect to Xiaomi Cloud servers.\n\n"
            "Please check:\n"
            "• Your internet connection is active\n"
            "• Firewall is not blocking the application\n"
            "• VPN or proxy settings if applicable"
        )
    elif "timeout" in error_str:
        return (
            "Request Timeout\n\n"
            "The server took too long to respond.\n\n"
            "Please try again. If the problem persists:\n"
            "• Check your internet speed\n"
            "• Try a different server region"
        )
    elif "authentication" in error_str or "login" in error_str or "password" in error_str:
        return (
            "Authentication Failed\n\n"
            "Could not log in with the provided credentials.\n\n"
            "Please verify:\n"
            "• Username and password are correct\n"
            "• Account is a Xiaomi Cloud account (not Roborock or other brands)\n"
            "• Two-factor authentication code is valid"
        )
    elif "captcha" in error_str:
        return (
            "CAPTCHA Verification Failed\n\n"
            "The CAPTCHA solution was incorrect.\n\n"
            "Please try again and enter the CAPTCHA carefully."
        )
    elif "qr" in error_str or "scan" in error_str:
        return (
            "QR Code Login Failed\n\n"
            "The QR code was not scanned or expired.\n\n"
            "Please:\n"
            "• Scan the QR code with your Xiaomi Home app\n"
            "• Make sure you're using the correct Xiaomi account\n"
            "• Try generating a new QR code"
        )
    elif "token" in error_str and "service" in error_str:
        return (
            "Session Token Error\n\n"
            "Failed to obtain authentication token.\n\n"
            "This is usually temporary. Please:\n"
            "• Wait a few minutes and try again\n"
            "• Restart the application\n"
            "• Try using QR code login instead"
        )
    else:
        return (
            f"An Error Occurred\n\n"
            f"{str(exception)}\n\n"
            f"If this problem persists, please try:\n"
            f"• Restarting the application\n"
            f"• Checking your internet connection\n"
            f"• Using a different server region"
        )


def apply_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    palette = QPalette()
    base = QColor("#1c1c1e")
    alt = QColor("#2c2c2e")
    text = QColor("#f5f5f7")
    disabled = QColor("#636366")
    highlight = QColor("#0a84ff")
    palette.setColor(QPalette.Window, base)
    palette.setColor(QPalette.WindowText, text)
    palette.setColor(QPalette.Base, QColor("#161618"))
    palette.setColor(QPalette.AlternateBase, alt)
    palette.setColor(QPalette.ToolTipBase, alt)
    palette.setColor(QPalette.ToolTipText, text)
    palette.setColor(QPalette.Text, text)
    palette.setColor(QPalette.Button, alt)
    palette.setColor(QPalette.ButtonText, text)
    palette.setColor(QPalette.BrightText, QColor("#ff453a"))
    palette.setColor(QPalette.Highlight, highlight)
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    palette.setColor(QPalette.PlaceholderText, disabled)
    palette.setColor(QPalette.Disabled, QPalette.Text, disabled)
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, disabled)
    palette.setColor(QPalette.Disabled, QPalette.WindowText, disabled)
    app.setPalette(palette)
    app.setStyleSheet(_stylesheet())


class ResponseFuture:
    def __init__(self) -> None:
        self._event = threading.Event()
        self._value: Optional[str] = None

    def set_result(self, value: Optional[str]) -> None:
        self._value = value
        self._event.set()

    def wait(self) -> Optional[str]:
        self._event.wait()
        return self._value


class WorkerSignals(QObject):
    log = Signal(str)
    finished = Signal(object)
    error = Signal(str)
    captcha = Signal(bytes, str, object)
    twofactor = Signal(str, object)
    qr = Signal(bytes, str, str)


@dataclass
class WorkerConfig:
    mode: str
    username: Optional[str] = None
    password: Optional[str] = None
    servers: Optional[List[str]] = None
    include_ble_keys: bool = True


class TokenExtractorWorker(QRunnable):
    def __init__(self, config: WorkerConfig) -> None:
        super().__init__()
        self.config = config
        self.signals = WorkerSignals()

    def _log(self, message: str) -> None:
        self.signals.log.emit(message)

    def _request_captcha(self, image_bytes: bytes, url: str) -> Optional[str]:
        future = ResponseFuture()
        self.signals.captcha.emit(image_bytes, url, future)
        return future.wait()

    def _request_twofactor(self, prompt: str) -> Optional[str]:
        future = ResponseFuture()
        self.signals.twofactor.emit(prompt, future)
        return future.wait()

    def _display_qr(self, image_bytes: bytes, login_url: str, image_url: str) -> None:
        self.signals.qr.emit(image_bytes, login_url, image_url)

    def run(self) -> None:
        callbacks = InteractionCallbacks(
            log=self._log,
            request_captcha=self._request_captcha,
            request_twofactor=self._request_twofactor,
            display_qr=self._display_qr,
        )
        try:
            service = TokenExtractorService(callbacks, include_ble_keys=self.config.include_ble_keys)
            servers = self.config.servers
            if self.config.mode == "password":
                if not self.config.username or not self.config.password:
                    raise ValueError("Username and password are required.")
                service.authenticate_with_password(self.config.username, self.config.password)
            elif self.config.mode == "qr":
                service.authenticate_with_qr()
            else:
                raise ValueError(f"Unsupported mode {self.config.mode}")
            data = service.fetch_devices(servers=servers)
            self.signals.finished.emit(data)
        except AuthenticationError as exc:
            self.signals.error.emit(get_user_friendly_error(exc))
        except ConnectionError as exc:
            self.signals.error.emit(get_user_friendly_error(exc))
        except Exception as exc:  # pragma: no cover - defensive logging
            self.signals.error.emit(get_user_friendly_error(exc))


class QrImageLabel(QLabel):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._source: Optional[QPixmap] = None
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(260, 260)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_qr(self, pixmap: QPixmap) -> None:
        self._source = pixmap
        self._rescale()

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt API
        super().resizeEvent(event)
        self._rescale()

    def _rescale(self) -> None:
        if self._source is None or self._source.isNull():
            return
        side = max(180, min(self.width() - 24, self.height() - 24, 360))
        scaled = self._source.scaled(side, side, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        super().setPixmap(scaled)


class CaptchaDialog(QDialog):
    def __init__(self, image_bytes: bytes, image_url: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Captcha Verification")
        self.setMinimumWidth(380)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Enter the characters")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        hint = QLabel("The check is case-sensitive.")
        hint.setObjectName("hint")
        layout.addWidget(hint)

        pixmap = QPixmap()
        pixmap.loadFromData(image_bytes)
        if pixmap.width() > 420:
            pixmap = pixmap.scaledToWidth(420, Qt.SmoothTransformation)
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setPixmap(pixmap)
        layout.addWidget(image_label)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Captcha code")
        layout.addWidget(self._input)

        link = QLabel(image_url)
        link.setObjectName("hint")
        link.setWordWrap(True)
        link.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(link)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self._input.setFocus()

    def code(self) -> str:
        return self._input.text().strip()


class TwoFactorDialog(QDialog):
    def __init__(self, prompt: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Two-Factor Authentication")
        self.setMinimumWidth(380)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Check your email")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        message = QLabel(prompt)
        message.setWordWrap(True)
        message.setObjectName("hint")
        layout.addWidget(message)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Verification code")
        layout.addWidget(self._input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self._input.setFocus()

    def code(self) -> str:
        return self._input.text().strip()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Xiaomi Cloud Token Extractor")
        self.resize(1120, 740)
        self.setMinimumSize(960, 640)
        self.pool = QThreadPool.globalInstance()
        self._current_worker: Optional[TokenExtractorWorker] = None
        self._device_data: Optional[List[Dict[str, Any]]] = None
        self._busy = False
        self._mono_font = QFont()
        self._mono_font.setFamilies(["Menlo", "Consolas", "DejaVu Sans Mono", "monospace"])
        self._mono_font.setPointSize(12)
        self._build_ui()

        copy_action = QAction("Copy", self.device_tree)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        copy_action.triggered.connect(self._copy_selected_items)
        self.device_tree.addAction(copy_action)

        self.restore_settings()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self._build_sidebar())
        root_layout.addWidget(self._build_main(), 1)
        self._set_placeholder(
            "No devices yet",
            "Sign in on the left with your Xiaomi account. Tokens for the selected region show up here.",
        )
        self._show_page("placeholder")
        self._set_status("Ready")

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(340)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 24, 20, 20)
        layout.setSpacing(16)

        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(4)
        kicker = QLabel("XIAOMI CLOUD")
        kicker.setObjectName("kicker")
        title = QLabel("Token Extractor")
        title.setObjectName("appTitle")
        subtitle = QLabel("Sign in, then copy device tokens for your home.")
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)
        header_layout.addWidget(kicker)
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addWidget(header)

        segment = QFrame()
        segment.setObjectName("segment")
        segment_layout = QHBoxLayout(segment)
        segment_layout.setContentsMargins(4, 4, 4, 4)
        segment_layout.setSpacing(4)
        self.password_mode_button = self._segment_button("Password")
        self.qr_mode_button = self._segment_button("QR code")
        segment_layout.addWidget(self.password_mode_button)
        segment_layout.addWidget(self.qr_mode_button)
        self.mode_group = QButtonGroup(self)
        self.mode_group.setExclusive(True)
        self.mode_group.addButton(self.password_mode_button, 0)
        self.mode_group.addButton(self.qr_mode_button, 1)
        self.password_mode_button.setChecked(True)
        self.mode_group.idClicked.connect(self._on_mode_changed)
        layout.addWidget(segment)

        self.auth_stack = QStackedWidget()
        self.auth_stack.addWidget(self._build_password_page())
        self.auth_stack.addWidget(self._build_qr_page())
        self.auth_stack.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        layout.addWidget(self.auth_stack)

        self.server_combo = self._make_server_combo()
        layout.addWidget(self._labeled("Region", self.server_combo))

        self.include_ble_checkbox = QCheckBox("Include Bluetooth encryption keys")
        self.include_ble_checkbox.setChecked(True)
        layout.addWidget(self.include_ble_checkbox)

        layout.addStretch(1)

        self.fetch_button = QPushButton("Fetch devices")
        self.fetch_button.setObjectName("primary")
        self.fetch_button.setCursor(Qt.PointingHandCursor)
        self.fetch_button.setMinimumHeight(40)
        self.fetch_button.clicked.connect(self._on_fetch)
        layout.addWidget(self.fetch_button)
        return sidebar

    def _segment_button(self, text: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName("segmentButton")
        button.setCheckable(True)
        button.setCursor(Qt.PointingHandCursor)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return button

    def _labeled(self, text: str, widget: QWidget) -> QWidget:
        wrap = QWidget()
        layout = QVBoxLayout(wrap)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        label = QLabel(text)
        label.setObjectName("fieldLabel")
        layout.addWidget(label)
        layout.addWidget(widget)
        return wrap

    def _build_password_page(self) -> QWidget:
        page = QWidget()
        page.setMinimumHeight(168)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Email, phone, or user ID")
        self.username_input.returnPressed.connect(self._on_fetch)
        layout.addWidget(self._labeled("Username", self.username_input))

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Xiaomi account password")
        self.password_input.returnPressed.connect(self._on_fetch)
        self.toggle_password_button = QPushButton("Show")
        self.toggle_password_button.setObjectName("ghost")
        self.toggle_password_button.setCheckable(True)
        self.toggle_password_button.setCursor(Qt.PointingHandCursor)
        self.toggle_password_button.toggled.connect(self._toggle_password_visible)
        password_row = QWidget()
        password_layout = QHBoxLayout(password_row)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(4)
        password_layout.addWidget(self.password_input, 1)
        password_layout.addWidget(self.toggle_password_button)
        layout.addWidget(self._labeled("Password", password_row))
        return page

    def _build_qr_page(self) -> QWidget:
        page = QWidget()
        page.setMinimumHeight(168)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        hint = QLabel(
            "A QR code opens on the right. Scan it with Xiaomi Home on the same account that owns the devices."
        )
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        layout.addStretch(1)
        return page

    def _build_main(self) -> QFrame:
        main = QFrame()
        main.setObjectName("main")
        layout = QVBoxLayout(main)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 24, 24, 16)
        content_layout.setSpacing(16)

        header = QHBoxLayout()
        self.page_title = QLabel("Devices")
        self.page_title.setObjectName("pageTitle")
        self.count_badge = QLabel("0")
        self.count_badge.setObjectName("countBadge")
        header.addWidget(self.page_title)
        header.addWidget(self.count_badge)
        header.addStretch(1)
        content_layout.addLayout(header)

        self.stack = QStackedWidget()
        self.placeholder_page = self._build_placeholder_page()
        self.qr_page = self._build_qr_view()
        self.devices_page = self._build_devices_page()
        self.stack.addWidget(self.placeholder_page)
        self.stack.addWidget(self.qr_page)
        self.stack.addWidget(self.devices_page)
        content_layout.addWidget(self.stack, 1)
        layout.addWidget(content, 1)
        layout.addWidget(self._build_footer())
        return main

    def _build_placeholder_page(self) -> QWidget:
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.addStretch(1)
        row = QHBoxLayout()
        row.addStretch(1)
        column = QVBoxLayout()
        column.setSpacing(8)
        self.placeholder_title = QLabel()
        self.placeholder_title.setObjectName("placeholderTitle")
        self.placeholder_title.setAlignment(Qt.AlignCenter)
        self.placeholder_body = QLabel()
        self.placeholder_body.setObjectName("hint")
        self.placeholder_body.setAlignment(Qt.AlignCenter)
        self.placeholder_body.setWordWrap(True)
        self.placeholder_body.setFixedWidth(420)
        column.addWidget(self.placeholder_title)
        column.addWidget(self.placeholder_body)
        row.addLayout(column)
        row.addStretch(1)
        outer.addLayout(row)
        outer.addStretch(1)
        return page

    def _build_qr_view(self) -> QWidget:
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.addStretch(1)
        self.qr_label = QrImageLabel()
        outer.addWidget(self.qr_label, 1)
        caption = QLabel("Scan with Xiaomi Home")
        caption.setObjectName("placeholderTitle")
        caption.setAlignment(Qt.AlignCenter)
        body = QLabel("Open the app and scan this code. Waiting continues until you confirm it.")
        body.setObjectName("hint")
        body.setAlignment(Qt.AlignCenter)
        body.setWordWrap(True)
        self.qr_link = QLabel()
        self.qr_link.setObjectName("hint")
        self.qr_link.setAlignment(Qt.AlignCenter)
        self.qr_link.setWordWrap(True)
        self.qr_link.setTextInteractionFlags(Qt.TextSelectableByMouse)
        outer.addWidget(caption)
        outer.addWidget(body)
        outer.addWidget(self.qr_link)
        outer.addStretch(1)
        return page

    def _build_devices_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search name, token, IP, MAC, or model")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._filter_devices)
        layout.addWidget(self.search_input)

        self.device_tree = QTreeWidget()
        self.device_tree.setColumnCount(7)
        self.device_tree.setHeaderLabels(["Name", "Device ID", "Token", "IP", "MAC", "Model", "BLE Key"])
        self.device_tree.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.device_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.device_tree.customContextMenuRequested.connect(self._show_context_menu)
        self.device_tree.setSortingEnabled(True)
        self.device_tree.setUniformRowHeights(True)
        self.device_tree.setAnimated(True)
        self.device_tree.setIndentation(16)
        self.device_tree.itemSelectionChanged.connect(self._update_selection_bar)
        self.device_tree.setTextElideMode(Qt.ElideNone)
        header = self.device_tree.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setMinimumSectionSize(72)
        layout.addWidget(self.device_tree, 1)

        self.selection_bar = QFrame()
        self.selection_bar.setObjectName("selectionBar")
        bar = QHBoxLayout(self.selection_bar)
        bar.setContentsMargins(12, 8, 8, 8)
        bar.setSpacing(4)
        self.selection_label = QLabel("Select a device to copy its token.")
        self.selection_label.setObjectName("selectionHint")
        bar.addWidget(self.selection_label, 1)
        self.copy_token_button = self._copy_button("Copy token", 2, "token")
        self.copy_ip_button = self._copy_button("Copy IP", 3, "IP address")
        self.copy_mac_button = self._copy_button("Copy MAC", 4, "MAC address")
        self.copy_ble_button = self._copy_button("Copy BLE", 6, "BLE key")
        for button in (
            self.copy_token_button,
            self.copy_ip_button,
            self.copy_mac_button,
            self.copy_ble_button,
        ):
            bar.addWidget(button)
        layout.addWidget(self.selection_bar)
        self._update_selection_bar()
        return page

    def _copy_button(self, text: str, column: int, label: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName("ghost")
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(lambda: self._copy_column(column, label))
        return button

    def _build_footer(self) -> QFrame:
        footer = QFrame()
        footer.setObjectName("footer")
        layout = QVBoxLayout(footer)
        layout.setContentsMargins(24, 12, 24, 12)
        layout.setSpacing(8)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        row = QHBoxLayout()
        row.setSpacing(8)
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("hint")
        row.addWidget(self.status_label, 1)

        self.log_toggle = QPushButton("Show log")
        self.log_toggle.setCheckable(True)
        self.log_toggle.setCursor(Qt.PointingHandCursor)
        self.log_toggle.toggled.connect(self._toggle_log)
        row.addWidget(self.log_toggle)

        self.export_json_button = self._export_button("JSON", self._on_export_json)
        self.export_yaml_button = self._export_button("YAML", self._on_export_yaml)
        self.export_csv_button = self._export_button("CSV", self._on_export_csv)
        row.addWidget(self.export_json_button)
        row.addWidget(self.export_yaml_button)
        row.addWidget(self.export_csv_button)
        layout.addLayout(row)

        self.log_view = QPlainTextEdit()
        self.log_view.setObjectName("log")
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumBlockCount(2000)
        self.log_view.setFixedHeight(160)
        self.log_view.setVisible(False)
        log_font = QFont()
        log_font.setFamilies(["Menlo", "Consolas", "DejaVu Sans Mono", "monospace"])
        log_font.setPointSize(11)
        self.log_view.setFont(log_font)
        layout.addWidget(self.log_view)
        return footer

    def _export_button(self, text: str, handler) -> QPushButton:
        button = QPushButton(text)
        button.setCursor(Qt.PointingHandCursor)
        button.setEnabled(False)
        button.clicked.connect(handler)
        return button

    def _make_server_combo(self) -> QComboBox:
        combo = QComboBox()
        combo.addItem("All regions", None)
        for server in TokenExtractorService.available_servers():
            combo.addItem(server.upper(), server)
        return combo

    def _selected_servers(self) -> List[str]:
        data = self.server_combo.currentData()
        if data:
            return [data]
        return TokenExtractorService.available_servers()

    def _qr_mode(self) -> bool:
        return self.mode_group.checkedId() == 1

    @Slot(int)
    def _on_mode_changed(self, _mode_id: int) -> None:
        self.auth_stack.setCurrentIndex(1 if self._qr_mode() else 0)
        if not self._busy:
            self.fetch_button.setText("Sign in with QR" if self._qr_mode() else "Fetch devices")
        if self.stack.currentWidget() is self.qr_page and not self._qr_mode():
            if self._has_devices():
                self._show_page("devices")
            else:
                self._set_placeholder(
                    "No devices yet",
                    "Sign in on the left with your Xiaomi account. Tokens for the selected region show up here.",
                )
                self._show_page("placeholder")

    @Slot(bool)
    def _toggle_password_visible(self, visible: bool) -> None:
        self.password_input.setEchoMode(QLineEdit.Normal if visible else QLineEdit.Password)
        self.toggle_password_button.setText("Hide" if visible else "Show")

    @Slot(bool)
    def _toggle_log(self, open_log: bool) -> None:
        self.log_view.setVisible(open_log)
        self.log_toggle.setText("Hide log" if open_log else "Show log")

    def _set_placeholder(self, title: str, body: str) -> None:
        self.placeholder_title.setText(title)
        self.placeholder_body.setText(body)

    def _show_page(self, name: str) -> None:
        pages = {"placeholder": 0, "qr": 1, "devices": 2}
        titles = {"placeholder": "Devices", "qr": "Scan to sign in", "devices": "Devices"}
        self.stack.setCurrentIndex(pages[name])
        self.page_title.setText(titles[name])
        self.count_badge.setVisible(name == "devices")

    def _set_status(self, text: str) -> None:
        flat = " ".join(text.split())
        if len(flat) > 160:
            flat = flat[:157] + "…"
        self.status_label.setText(flat)

    @Slot()
    def _on_fetch(self) -> None:
        if self._busy:
            return
        if self._qr_mode():
            config = WorkerConfig(
                mode="qr",
                servers=self._selected_servers(),
                include_ble_keys=self.include_ble_checkbox.isChecked(),
            )
        else:
            username = self.username_input.text().strip()
            password = self.password_input.text()
            if not username or not password:
                QMessageBox.warning(self, "Missing credentials", "Please provide both username and password.")
                return
            config = WorkerConfig(
                mode="password",
                username=username,
                password=password,
                servers=self._selected_servers(),
                include_ble_keys=self.include_ble_checkbox.isChecked(),
            )
        self._start_worker(config)

    def _start_worker(self, config: WorkerConfig) -> None:
        self._device_data = None
        self.search_input.clear()
        self.device_tree.clear()
        self._set_busy(True)
        if config.mode == "qr":
            self._set_placeholder(
                "Preparing a QR code",
                "Keep Xiaomi Home ready. The code will show up here in a moment.",
            )
        else:
            self._set_placeholder(
                "Fetching devices",
                "Signing in and loading devices from Xiaomi Cloud.",
            )
        self._show_page("placeholder")
        self._set_status("Starting extraction…")
        self.log_view.appendPlainText("Starting extraction...")
        self._current_worker = TokenExtractorWorker(config)
        worker = self._current_worker
        worker.signals.log.connect(self._append_log)
        worker.signals.error.connect(self._handle_error)
        worker.signals.finished.connect(self._handle_finished)
        worker.signals.captcha.connect(self._handle_captcha)
        worker.signals.twofactor.connect(self._handle_twofactor)
        worker.signals.qr.connect(self._handle_qr_image)
        self.pool.start(worker)

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        self.fetch_button.setDisabled(busy)
        self.password_mode_button.setDisabled(busy)
        self.qr_mode_button.setDisabled(busy)
        self.username_input.setDisabled(busy)
        self.password_input.setDisabled(busy)
        self.toggle_password_button.setDisabled(busy)
        self.server_combo.setDisabled(busy)
        self.include_ble_checkbox.setDisabled(busy)
        can_export = (not busy) and self._has_devices()
        self.export_csv_button.setEnabled(can_export)
        self.export_json_button.setEnabled(can_export)
        self.export_yaml_button.setEnabled(can_export)
        self.progress_bar.setVisible(busy)
        if busy:
            self.progress_bar.setRange(0, 0)
            self.fetch_button.setText("Working…")
        else:
            self.progress_bar.setRange(0, 1)
            self.progress_bar.setValue(0)
            self.fetch_button.setText("Sign in with QR" if self._qr_mode() else "Fetch devices")

    def _has_devices(self) -> bool:
        return self._device_count() > 0

    def _device_count(self) -> int:
        if not self._device_data:
            return 0
        return sum(
            len(home.get("devices") or [])
            for server in self._device_data
            for home in server.get("homes", [])
        )

    @Slot(str)
    def _append_log(self, message: str) -> None:
        clean = ANSI_ESCAPE_RE.sub("", message).strip()
        if clean:
            self.log_view.appendPlainText(clean)
            self._set_status(clean)

    @Slot(object)
    def _handle_finished(self, data) -> None:
        self._device_data = data
        self._set_busy(False)
        self._populate_devices(data)
        self.log_view.appendPlainText("Extraction completed.")
        count = self._device_count()
        if count:
            self._show_page("devices")
            noun = "device" if count == 1 else "devices"
            self._set_status(f"Loaded {count} {noun}.")
        else:
            self._set_placeholder(
                "No devices found",
                "This region returned nothing. Choose All regions, or confirm the devices appear in Xiaomi Home.",
            )
            self._show_page("placeholder")
            self._set_status("No devices found.")

    @Slot(str)
    def _handle_error(self, message: str) -> None:
        self._set_busy(False)
        self._set_placeholder(
            "Sign-in did not finish",
            "The details are in the dialog. Adjust the account or region and try again.",
        )
        self._show_page("placeholder")
        self._set_status("Something went wrong.")
        QMessageBox.critical(self, "Error", message)

    @Slot(bytes, str, object)
    def _handle_captcha(self, image_bytes: bytes, image_url: str, future: ResponseFuture) -> None:
        try:
            dialog = CaptchaDialog(image_bytes, image_url, self)
            if dialog.exec() == QDialog.Accepted:
                future.set_result(dialog.code())
            else:
                future.set_result(None)
        except Exception:
            future.set_result(None)

    @Slot(str, object)
    def _handle_twofactor(self, prompt: str, future: ResponseFuture) -> None:
        try:
            dialog = TwoFactorDialog(prompt, self)
            if dialog.exec() == QDialog.Accepted:
                future.set_result(dialog.code())
            else:
                future.set_result(None)
        except Exception:
            future.set_result(None)

    @Slot(bytes, str, str)
    def _handle_qr_image(self, image_bytes: bytes, login_url: str, image_url: str) -> None:
        pixmap = QPixmap()
        pixmap.loadFromData(image_bytes)
        self.qr_label.set_qr(pixmap)
        link = login_url or image_url
        self.qr_link.setText(link)
        self._show_page("qr")
        instruction = "Scan the QR code with your Xiaomi Home app."
        if link:
            instruction = f"{instruction} Alternate login URL: {link}"
        self.log_view.appendPlainText(instruction)
        self._set_status("Scan the QR code with Xiaomi Home.")

    def _populate_devices(self, data) -> None:
        self.device_tree.setSortingEnabled(False)
        self.device_tree.clear()
        if not data:
            self._update_count_badge()
            return
        group_font = QFont(self.font())
        group_font.setBold(True)
        muted = QColor("#98989d")
        for server_entry in data:
            server_name = server_entry.get("server", "").upper()
            server_item = QTreeWidgetItem([server_name, "", "", "", "", "", ""])
            server_item.setFont(0, group_font)
            server_item.setForeground(0, muted)
            server_item.setFlags(server_item.flags() & ~Qt.ItemIsSelectable)
            for home in server_entry.get("homes", []):
                home_label = f'Home {home.get("home_id", "")}'
                home_item = QTreeWidgetItem([home_label, "", "", "", "", "", ""])
                home_item.setFont(0, group_font)
                home_item.setForeground(0, muted)
                home_item.setFlags(home_item.flags() & ~Qt.ItemIsSelectable)
                for device in home.get("devices", []):
                    ble_key = ""
                    if "BLE_DATA" in device:
                        ble_key = device["BLE_DATA"].get("beaconkey", "")
                    tree_item = QTreeWidgetItem(
                        [
                            device.get("name", ""),
                            device.get("did", ""),
                            device.get("token", ""),
                            device.get("localip", ""),
                            device.get("mac", ""),
                            device.get("model", ""),
                            ble_key,
                        ]
                    )
                    for column in (1, 2, 4, 6):
                        tree_item.setFont(column, self._mono_font)
                    home_item.addChild(tree_item)
                server_item.addChild(home_item)
            self.device_tree.addTopLevelItem(server_item)
        self.device_tree.expandToDepth(1)
        self.device_tree.setSortingEnabled(True)
        self._update_count_badge()

    def _selected_devices(self) -> List[QTreeWidgetItem]:
        return [item for item in self.device_tree.selectedItems() if item.childCount() == 0]

    @Slot()
    def _update_selection_bar(self) -> None:
        devices = self._selected_devices()
        has_selection = bool(devices)
        for button in (
            self.copy_token_button,
            self.copy_ip_button,
            self.copy_mac_button,
            self.copy_ble_button,
        ):
            button.setEnabled(has_selection)
        if not devices:
            self.selection_label.setText("Select a device, or right-click a row.")
        elif len(devices) == 1:
            self.selection_label.setText(devices[0].text(0) or "Selected device")
        else:
            self.selection_label.setText(f"{len(devices)} devices selected")

    def _copy_column(self, column: int, label: str) -> None:
        values = [item.text(column) for item in self._selected_devices() if item.text(column)]
        if not values:
            self._set_status(f"No {label} on the selection.")
            return
        QApplication.clipboard().setText("\n".join(values))
        message = f"Copied {label}." if len(values) == 1 else f"Copied {len(values)} {label} values."
        self._set_status(message)
        self.log_view.appendPlainText(message)

    @Slot()
    def _on_export_csv(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Devices to CSV",
            str(Path.home() / "xiaomi_devices.csv"),
            "CSV Files (*.csv);;All Files (*)",
        )
        if not file_path:
            return
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(
                    [
                        "Server",
                        "Home ID",
                        "Device Name",
                        "Device ID",
                        "Token",
                        "IP Address",
                        "MAC Address",
                        "Model",
                        "BLE Key",
                    ]
                )
                for server_idx in range(self.device_tree.topLevelItemCount()):
                    server_item = self.device_tree.topLevelItem(server_idx)
                    server_name = server_item.text(0)
                    for home_idx in range(server_item.childCount()):
                        home_item = server_item.child(home_idx)
                        home_id = home_item.text(0)
                        for device_idx in range(home_item.childCount()):
                            device_item = home_item.child(device_idx)
                            writer.writerow(
                                [
                                    server_name,
                                    home_id,
                                    device_item.text(0),
                                    device_item.text(1),
                                    device_item.text(2),
                                    device_item.text(3),
                                    device_item.text(4),
                                    device_item.text(5),
                                    device_item.text(6),
                                ]
                            )
            self.log_view.appendPlainText(f"Devices exported to: {file_path}")
            self._set_status("Exported CSV.")
            QMessageBox.information(self, "Export Successful", f"Devices exported successfully to:\n{file_path}")
        except Exception as exc:
            self.log_view.appendPlainText(f"Export failed: {exc}")
            QMessageBox.critical(self, "Export Failed", f"Failed to export devices:\n{exc}")

    @Slot()
    def _on_export_json(self) -> None:
        if not self._device_data:
            QMessageBox.warning(self, "No Data", "No device data available to export.")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Devices to JSON",
            str(Path.home() / "xiaomi_devices.json"),
            "JSON Files (*.json);;All Files (*)",
        )
        if not file_path:
            return
        try:
            with open(file_path, "w", encoding="utf-8") as jsonfile:
                json.dump(self._device_data, jsonfile, indent=2, ensure_ascii=False)
            self.log_view.appendPlainText(f"Devices exported to JSON: {file_path}")
            self._set_status("Exported JSON.")
            QMessageBox.information(self, "Export Successful", f"Devices exported successfully to:\n{file_path}")
        except Exception as exc:
            self.log_view.appendPlainText(f"JSON export failed: {exc}")
            QMessageBox.critical(self, "Export Failed", f"Failed to export devices to JSON:\n{exc}")

    @Slot()
    def _on_export_yaml(self) -> None:
        if not self._device_data:
            QMessageBox.warning(self, "No Data", "No device data available to export.")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Devices to YAML",
            str(Path.home() / "xiaomi_devices.yaml"),
            "YAML Files (*.yaml *.yml);;All Files (*)",
        )
        if not file_path:
            return
        try:
            try:
                import yaml
            except ImportError:
                QMessageBox.warning(
                    self,
                    "YAML Not Available",
                    "YAML export requires the PyYAML package.\n\n"
                    "The application was built without YAML support.\n"
                    "Please use JSON or CSV export instead.",
                )
                return
            with open(file_path, "w", encoding="utf-8") as yamlfile:
                yaml.dump(self._device_data, yamlfile, default_flow_style=False, allow_unicode=True)
            self.log_view.appendPlainText(f"Devices exported to YAML: {file_path}")
            self._set_status("Exported YAML.")
            QMessageBox.information(self, "Export Successful", f"Devices exported successfully to:\n{file_path}")
        except Exception as exc:
            self.log_view.appendPlainText(f"YAML export failed: {exc}")
            QMessageBox.critical(self, "Export Failed", f"Failed to export devices to YAML:\n{exc}")

    @Slot(object)
    def _show_context_menu(self, position) -> None:
        item = self.device_tree.itemAt(position)
        if not item or item.childCount() > 0:
            return
        menu = QMenu(self)
        actions = [
            (menu.addAction("Copy Name"), 0),
            (menu.addAction("Copy Device ID"), 1),
            (menu.addAction("Copy Token"), 2),
            (menu.addAction("Copy IP Address"), 3),
            (menu.addAction("Copy MAC Address"), 4),
            (menu.addAction("Copy Model"), 5),
            (menu.addAction("Copy BLE Key"), 6),
        ]
        menu.addSeparator()
        copy_row = menu.addAction("Copy Row (Tab-separated)")
        copy_all = menu.addAction("Copy All Selected Devices")
        chosen = menu.exec(self.device_tree.viewport().mapToGlobal(position))
        labels = ["name", "device ID", "token", "IP address", "MAC address", "model", "BLE key"]
        for action, column in actions:
            if chosen == action:
                self._copy_text(item.text(column), labels[column])
                return
        if chosen == copy_row:
            self._copy_row_to_clipboard(item)
        elif chosen == copy_all:
            self._copy_selected_items()

    def _copy_text(self, text: str, label: str) -> None:
        if not text:
            self._set_status(f"No {label} on this device.")
            return
        QApplication.clipboard().setText(text)
        self._set_status(f"Copied {label}.")
        self.log_view.appendPlainText(f"Copied {label}.")

    def _copy_row_to_clipboard(self, item: QTreeWidgetItem) -> None:
        text = "\t".join(item.text(column) for column in range(7))
        QApplication.clipboard().setText(text)
        self._set_status("Copied row.")
        self.log_view.appendPlainText("Copied row.")

    @Slot()
    def _copy_selected_items(self) -> None:
        device_items = self._selected_devices()
        if not device_items:
            self._set_status("No devices selected to copy.")
            return
        lines = ["\t".join(["Name", "Device ID", "Token", "IP", "MAC", "Model", "BLE Key"])]
        for item in device_items:
            lines.append("\t".join(item.text(column) for column in range(7)))
        QApplication.clipboard().setText("\n".join(lines))
        self._set_status(f"Copied {len(device_items)} device(s).")
        self.log_view.appendPlainText(f"Copied {len(device_items)} device(s).")

    @Slot(str)
    def _filter_devices(self, search_text: str) -> None:
        search_text = search_text.lower().strip()
        for server_idx in range(self.device_tree.topLevelItemCount()):
            server_item = self.device_tree.topLevelItem(server_idx)
            server_has_visible_device = False
            for home_idx in range(server_item.childCount()):
                home_item = server_item.child(home_idx)
                home_has_visible_device = False
                for device_idx in range(home_item.childCount()):
                    device_item = home_item.child(device_idx)
                    if not search_text:
                        matches = True
                    else:
                        matches = any(search_text in device_item.text(col).lower() for col in range(7))
                    device_item.setHidden(not matches)
                    if matches:
                        home_has_visible_device = True
                home_item.setHidden(not home_has_visible_device)
                if home_has_visible_device:
                    server_has_visible_device = True
                    home_item.setExpanded(True)
            server_item.setHidden(not server_has_visible_device)
            if server_has_visible_device:
                server_item.setExpanded(True)
        self._update_count_badge()

    def _visible_device_count(self) -> int:
        count = 0
        for server_idx in range(self.device_tree.topLevelItemCount()):
            server_item = self.device_tree.topLevelItem(server_idx)
            for home_idx in range(server_item.childCount()):
                home_item = server_item.child(home_idx)
                for device_idx in range(home_item.childCount()):
                    if not home_item.child(device_idx).isHidden():
                        count += 1
        return count

    def _update_count_badge(self) -> None:
        total = self._device_count()
        if self.search_input.text().strip():
            self.count_badge.setText(f"{self._visible_device_count()} of {total}")
        else:
            self.count_badge.setText(str(total))

    def save_settings(self) -> None:
        settings = QSettings("XiaomiTools", "TokenExtractor")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        server = self.server_combo.currentData()
        settings.setValue("lastPasswordServer", server)
        settings.setValue("lastQRServer", server)
        settings.setValue("includeBLE", self.include_ble_checkbox.isChecked())
        settings.setValue("lastUsername", self.username_input.text())
        settings.setValue("logOpen", self.log_toggle.isChecked())
        settings.setValue("loginMode", "qr" if self._qr_mode() else "password")
        self.log_view.appendPlainText("Settings saved")

    def restore_settings(self) -> None:
        settings = QSettings("XiaomiTools", "TokenExtractor")
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        window_state = settings.value("windowState")
        if window_state:
            self.restoreState(window_state)

        last_server = settings.value("lastPasswordServer")
        if last_server in (None, ""):
            last_server = settings.value("lastQRServer")
        if last_server:
            index = self.server_combo.findData(last_server)
            if index >= 0:
                self.server_combo.setCurrentIndex(index)

        include_ble = settings.value("includeBLE", True, type=bool)
        self.include_ble_checkbox.setChecked(include_ble)

        last_username = settings.value("lastUsername", "")
        if last_username:
            self.username_input.setText(str(last_username))

        if settings.value("loginMode") == "qr":
            self.qr_mode_button.setChecked(True)
            self._on_mode_changed(1)

        log_open = settings.value("logOpen", False, type=bool)
        self.log_toggle.setChecked(bool(log_open))
        self.log_view.appendPlainText("Settings restored")
        self._set_status("Ready")

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt API
        if self._current_worker:
            self.log_view.appendPlainText("Cancelling ongoing operations...")
            self.pool.clear()
            self.pool.waitForDone(5000)
        self.save_settings()
        event.accept()


def run() -> None:
    app = QApplication(sys.argv)
    apply_theme(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
