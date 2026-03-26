#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Shell White Martins - PREMIUM.
Header compacto, nav bar moderna com destaque, transições suaves.
"""

import os
import json
from pathlib import Path

from PySide6.QtCore import (
    Qt, Signal, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
    QTimer, QSize, QRectF
)
from PySide6.QtGui import QColor, QPainter, QPixmap, QPainterPath, QLinearGradient
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QStackedWidget, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect, QSizePolicy
)

from resources import carregar_logo_wm, carregar_logo_wm_light, criar_icone_vetorial


class GradientBackground(QWidget):
    def paintEvent(self, event):
        from PySide6.QtGui import QPainter, QLinearGradient, QRadialGradient, QColor
        p = QPainter(self)
        w, h = self.width(), self.height()
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, QColor("#F5F0EB"))
        grad.setColorAt(0.35, QColor("#F0F2F5"))
        grad.setColorAt(0.65, QColor("#F5F2ED"))
        grad.setColorAt(1.0, QColor("#EEF1F5"))
        p.fillRect(self.rect(), grad)
        glow = QRadialGradient(w * 0.15, h * 0.1, w * 0.5)
        glow.setColorAt(0.0, QColor(245, 158, 11, 8))
        glow.setColorAt(1.0, QColor(245, 158, 11, 0))
        p.fillRect(self.rect(), glow)
        glow2 = QRadialGradient(w * 0.85, h * 0.9, w * 0.4)
        glow2.setColorAt(0.0, QColor(59, 130, 246, 6))
        glow2.setColorAt(1.0, QColor(59, 130, 246, 0))
        p.fillRect(self.rect(), glow2)
        p.end()


def obter_versao_app():
    try:
        caminho = Path(__file__).resolve().parent / "app_version.json"
        with open(caminho, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("version", "---")
    except Exception:
        return "---"


class AnimatedStack(QStackedWidget):
    def __init__(self):
        super().__init__()
        self._fading = False

    def setCurrentIndex(self, index):
        if index == self.currentIndex() or self._fading:
            return
        old_widget = self.currentWidget()
        new_widget = self.widget(index)
        if old_widget is None or new_widget is None:
            super().setCurrentIndex(index)
            return

        self._fading = True
        old_effect = QGraphicsOpacityEffect(old_widget)
        old_widget.setGraphicsEffect(old_effect)
        fade_out = QPropertyAnimation(old_effect, b"opacity")
        fade_out.setDuration(120)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.OutQuad)

        def on_fade_out_done():
            super(AnimatedStack, self).setCurrentIndex(index)
            old_widget.setGraphicsEffect(None)
            new_effect = QGraphicsOpacityEffect(new_widget)
            new_widget.setGraphicsEffect(new_effect)
            fade_in = QPropertyAnimation(new_effect, b"opacity")
            fade_in.setDuration(180)
            fade_in.setStartValue(0.0)
            fade_in.setEndValue(1.0)
            fade_in.setEasingCurve(QEasingCurve.InOutQuad)

            def on_fade_in_done():
                new_widget.setGraphicsEffect(None)
                self._fading = False

            fade_in.finished.connect(on_fade_in_done)
            self._fade_in_anim = fade_in
            fade_in.start()

        fade_out.finished.connect(on_fade_out_done)
        self._fade_out_anim = fade_out
        fade_out.start()


class NavButton(QPushButton):
    """Botão de navegação com título + subtítulo descritivo."""
    clicked_index = Signal(int)

    def __init__(self, icone_nome: str, titulo: str, subtitulo: str, index: int):
        super().__init__()
        self.index = index
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("ModernNavBtn")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 6, 10, 6)
        lay.setSpacing(1)

        # Top row: icon + title
        top = QHBoxLayout()
        top.setSpacing(6)
        self._icon_label = QLabel()
        self._icon_label.setFixedSize(16, 16)
        self._icon_label.setStyleSheet("background: transparent;")
        self._icon_normal = criar_icone_vetorial(icone_nome, 14, "rgba(255,255,255,0.55)")
        self._icon_checked = criar_icone_vetorial(icone_nome, 14, "#FFFFFF")
        self._icon_label.setPixmap(self._icon_normal)
        top.addWidget(self._icon_label)

        self._title = QLabel(titulo)
        self._title.setObjectName("NavBtnTitle")
        self._title.setStyleSheet("background: transparent;")
        top.addWidget(self._title, 1)
        lay.addLayout(top)

        # Subtitle
        self._sub = QLabel(subtitulo)
        self._sub.setObjectName("NavBtnSub")
        self._sub.setStyleSheet("background: transparent;")
        lay.addWidget(self._sub)

        self.clicked.connect(lambda: self.clicked_index.emit(self.index))

    def setChecked(self, checked):
        super().setChecked(checked)
        self._icon_label.setPixmap(self._icon_checked if checked else self._icon_normal)


class MainShell(QMainWindow):
    def __init__(self):
        super().__init__()

        self.usuario = os.environ.get("USERNAME", "---")
        self.maquina = os.environ.get("COMPUTERNAME", "---")

        self.setWindowTitle("White Martins Workspace")
        self.setMinimumSize(1100, 680)
        self.resize(1360, 820)

        central = QWidget()
        central.setObjectName("ShellRoot")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # TOP BAR (compacto - só logo + session)
        self.topbar = self._build_topbar()
        root.addWidget(self.topbar, 0)

        # WORKSPACE BAR (nav unificada com hero escuro)
        self.workspace_bar = self._build_workspace_bar()
        root.addWidget(self.workspace_bar, 0)

        # CONTENT
        content_wrap = GradientBackground()
        content_wrap.setObjectName("ContentWrap")
        content_layout = QVBoxLayout(content_wrap)
        content_layout.setContentsMargins(20, 14, 20, 14)
        content_layout.setSpacing(0)

        self.stack = AnimatedStack()
        self.stack.setObjectName("MainStack")
        content_layout.addWidget(self.stack, 1)
        root.addWidget(content_wrap, 1)

        # FOOTER
        self.footer = self._build_footer()
        root.addWidget(self.footer, 0)

        # PAGES
        from pages.dashboard_page import DashboardPage
        self.page_dashboard = DashboardPage()
        self.page_converter = None
        self.page_segregar = None
        self.page_recon = None
        self.page_overview = None

        self.stack.addWidget(self.page_dashboard)
        for _ in range(4):
            self.stack.addWidget(QWidget())

        self._set_current_direct(0)

    def _build_topbar(self):
        bar = QFrame()
        bar.setObjectName("TopBar")
        bar.setFixedHeight(54)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 40, 20, 50))
        bar.setGraphicsEffect(shadow)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(0)

        # Logo (maior, com destaque)
        logo_pix = carregar_logo_wm_light(400)
        if logo_pix:
            logo_label = QLabel()
            scaled = logo_pix.scaledToHeight(40, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled)
            logo_label.setStyleSheet("background: transparent;")
            layout.addWidget(logo_label)
        else:
            brand_name = QLabel("WHITE MARTINS")
            brand_name.setObjectName("TopBarBrand")
            layout.addWidget(brand_name)

        # Separator
        sep = QFrame()
        sep.setObjectName("TopBarSep")
        sep.setFixedSize(1, 26)
        layout.addSpacing(16)
        layout.addWidget(sep)
        layout.addSpacing(16)

        # Tagline central
        tag_col = QVBoxLayout()
        tag_col.setSpacing(0)
        tag1 = QLabel("Workspace Fiscal")
        tag1.setObjectName("TopBarTagMain")
        tag_col.addWidget(tag1)
        tag2 = QLabel("Plataforma de gest\u00e3o tribut\u00e1ria  |  ICMS  |  Reconcilia\u00e7\u00e3o  |  Compliance  |  UPDATE OK!")
        tag2.setObjectName("TopBarTagSub")
        tag_col.addWidget(tag2)
        layout.addLayout(tag_col)

        layout.addStretch(1)

        # Version
        versao = obter_versao_app()
        ver_badge = QLabel(f"v{versao}")
        ver_badge.setObjectName("VersionBadge")
        layout.addWidget(ver_badge)
        layout.addSpacing(14)

        # Status
        status_dot = QFrame()
        status_dot.setObjectName("StatusDot")
        status_dot.setFixedSize(7, 7)
        layout.addWidget(status_dot)
        layout.addSpacing(5)
        status_text = QLabel("Online")
        status_text.setObjectName("StatusText")
        layout.addWidget(status_text)
        layout.addSpacing(14)

        # Session
        session_pill = QFrame()
        session_pill.setObjectName("SessionPill")
        pill_layout = QHBoxLayout(session_pill)
        pill_layout.setContentsMargins(8, 3, 10, 3)
        pill_layout.setSpacing(6)

        avatar = QLabel(self.usuario[0].upper() if self.usuario != "---" else "U")
        avatar.setObjectName("SessionAvatar")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(24, 24)
        pill_layout.addWidget(avatar)

        user_info = QVBoxLayout()
        user_info.setContentsMargins(0, 0, 0, 0)
        user_info.setSpacing(0)
        user_name = QLabel(self.usuario)
        user_name.setObjectName("SessionUser")
        user_info.addWidget(user_name)
        machine_name = QLabel(self.maquina)
        machine_name.setObjectName("SessionMachine")
        user_info.addWidget(machine_name)
        pill_layout.addLayout(user_info)

        layout.addWidget(session_pill)
        return bar

    def _build_workspace_bar(self):
        bar = QFrame()
        bar.setObjectName("WorkspaceBar")

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(24, 12, 24, 12)
        layout.setSpacing(0)

        # Left: workspace info
        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        eyebrow = QLabel("NAVEGAÇÃO")
        eyebrow.setObjectName("WBarEyebrow")
        info_col.addWidget(eyebrow)
        desc = QLabel("Selecione o módulo desejado")
        desc.setObjectName("WBarDesc")
        info_col.addWidget(desc)
        layout.addLayout(info_col)

        layout.addSpacing(30)

        # Nav buttons com subtítulos descritivos
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(5)

        self.nav_buttons = []
        tabs = [
            ("home",   "Início",          "Painel principal",         0),
            ("pdf",    "Converter PDFs",   "Extrair dados ICMS",      1),
            ("link",   "Reconciliação",    "Cruzar Razão x Fiscal",   2),
            ("chart",  "Overview",         "Resumos e gráficos",      3),
            ("split",  "Segregar",         "Divisões por arquivo",    4),
        ]

        for icon_n, titulo, sub, idx in tabs:
            btn = NavButton(icon_n, titulo, sub, idx)
            btn.clicked_index.connect(self.set_current_page)
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        layout.addLayout(nav_layout, 1)
        return bar

    def _build_footer(self):
        footer = QFrame()
        footer.setObjectName("FooterBar")
        footer.setFixedHeight(24)
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(0)
        left = QLabel("White Martins  -  A Linde company")
        left.setObjectName("FooterText")
        layout.addWidget(left)
        layout.addStretch(1)
        right = QLabel("Desenvolvimento: Thiago Lopomo")
        right.setObjectName("FooterText")
        layout.addWidget(right)
        return footer

    def _set_current_direct(self, index):
        QStackedWidget.setCurrentIndex(self.stack, index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def set_current_page(self, index: int):
        if index == 1 and self.page_converter is None:
            from pages.converter_page import ConverterPage
            self.page_converter = ConverterPage()
            old = self.stack.widget(1)
            self.stack.removeWidget(old)
            old.deleteLater()
            self.stack.insertWidget(1, self.page_converter)

        elif index == 2 and self.page_recon is None:
            from pages.recon_page import ReconPage
            self.page_recon = ReconPage()
            old = self.stack.widget(2)
            self.stack.removeWidget(old)
            old.deleteLater()
            self.stack.insertWidget(2, self.page_recon)

        elif index == 3 and self.page_overview is None:
            from pages.overview_page import OverviewPage
            self.page_overview = OverviewPage()
            old = self.stack.widget(3)
            self.stack.removeWidget(old)
            old.deleteLater()
            self.stack.insertWidget(3, self.page_overview)

        elif index == 4 and self.page_segregar is None:
            from pages.segregar_page import SegregarPage
            self.page_segregar = SegregarPage()
            old = self.stack.widget(4)
            self.stack.removeWidget(old)
            old.deleteLater()
            self.stack.insertWidget(4, self.page_segregar)

        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
