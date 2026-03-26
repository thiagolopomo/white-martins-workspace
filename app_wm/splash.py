#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Splash Screen - Moderno: Logo grande centralizado + barra de carregamento.
Estilo apps modernos: fundo limpo, logo, progress.
"""

from PySide6.QtCore import Qt, QTimer, QRectF, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPainter, QPainterPath, QLinearGradient, QPen
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QProgressBar, QFrame, QGraphicsDropShadowEffect
)

from resources import carregar_logo_wm


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(520, 380)
        self.setFixedSize(520, 380)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.valor = 0
        self._callback_final = None

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)

        self.card = QFrame()
        self.card.setObjectName("SplashCard")
        root.addWidget(self.card)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(50)
        shadow.setOffset(0, 12)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.card.setGraphicsEffect(shadow)

        main = QVBoxLayout(self.card)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        main.setAlignment(Qt.AlignCenter)

        # Logo grande centralizado
        main.addStretch(2)

        self.logo = QLabel()
        self.logo.setAlignment(Qt.AlignCenter)
        self.logo.setStyleSheet("background: transparent;")
        pix = carregar_logo_wm(320)
        if pix:
            self.logo.setPixmap(pix)
        else:
            self.logo.setText("WHITE MARTINS")
            self.logo.setStyleSheet(
                "color: #00A651; font-size: 32px; font-weight: 800; background: transparent;"
            )
        main.addWidget(self.logo, 0, Qt.AlignCenter)

        main.addStretch(1)

        # Status text
        self.status = QLabel("Inicializando...")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet("""
            QLabel {
                color: #94A3B8;
                font-size: 11px;
                font-weight: 500;
                background: transparent;
                padding: 0 40px;
            }
        """)
        main.addWidget(self.status)
        main.addSpacing(10)

        # Progress bar minimalista
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(3)
        self.progress.setStyleSheet("""
            QProgressBar {
                background: #E2E8F0;
                border: none;
                border-radius: 1px;
                margin: 0 60px;
            }
            QProgressBar::chunk {
                border-radius: 1px;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3B82F6,
                    stop:0.5 #00A651,
                    stop:1 #F59E0B
                );
            }
        """)
        main.addWidget(self.progress)
        main.addSpacing(20)

        # Timer & fade
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._avancar)

        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)

    def iniciar(self, callback_final):
        self._callback_final = callback_final
        self.setWindowOpacity(0.0)
        self.show()
        self.anim.start()
        self.timer.start(20)

    def _avancar(self):
        self.valor += 2
        if self.valor > 100:
            self.valor = 100

        self.progress.setValue(self.valor)

        if self.valor <= 25:
            self.status.setText("Carregando identidade visual...")
        elif self.valor <= 50:
            self.status.setText("Preparando módulos fiscais...")
        elif self.valor <= 75:
            self.status.setText("Validando recursos do sistema...")
        elif self.valor <= 95:
            self.status.setText("Organizando workspace...")
        else:
            self.status.setText("Pronto")

        if self.valor >= 100:
            self.timer.stop()
            QTimer.singleShot(300, self._finalizar)

    def _finalizar(self):
        # Fade out
        self.anim_out = QPropertyAnimation(self, b"windowOpacity")
        self.anim_out.setDuration(250)
        self.anim_out.setStartValue(1.0)
        self.anim_out.setEndValue(0.0)
        self.anim_out.setEasingCurve(QEasingCurve.InQuad)
        self.anim_out.finished.connect(self._fechar)
        self.anim_out.start()

    def _fechar(self):
        self.close()
        if self._callback_final:
            self._callback_final()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(16, 16, -16, -16)
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), 20, 20)

        # Fundo branco limpo
        painter.fillPath(path, QColor("#FFFFFF"))

        # Border sutil
        border_pen = QPen(QColor(0, 0, 0, 12))
        border_pen.setWidth(1)
        painter.setPen(border_pen)
        painter.drawPath(path)
