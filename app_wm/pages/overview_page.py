#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Overview - SEM SCROLL. Log com scroll interno."""

import os
from PySide6.QtCore import Qt, QEasingCurve, QPropertyAnimation, QPointF
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QFileDialog, QMessageBox, QTextEdit, QLineEdit, QSizePolicy, QProgressBar,
    QGraphicsDropShadowEffect
)

from resources import criar_icone_vetorial
from workers.overview_worker import OverviewWorker
from pages.recon_page import AnimatedHero


class HoverCard(QFrame):
    def __init__(self):
        super().__init__()
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(10); self._shadow.setOffset(0, 2)
        self._shadow.setColor(QColor(0, 80, 40, 14))
        self.setGraphicsEffect(self._shadow)
        self._ab = QPropertyAnimation(self._shadow, b"blurRadius", self)
        self._ab.setDuration(160); self._ab.setEasingCurve(QEasingCurve.OutCubic)
        self._ao = QPropertyAnimation(self._shadow, b"offset", self)
        self._ao.setDuration(160); self._ao.setEasingCurve(QEasingCurve.OutCubic)
        self.setMouseTracking(True)

    def enterEvent(self, e):
        self._ab.stop(); self._ab.setStartValue(self._shadow.blurRadius()); self._ab.setEndValue(20); self._ab.start()
        self._ao.stop(); self._ao.setStartValue(self._shadow.offset()); self._ao.setEndValue(QPointF(0, 4)); self._ao.start()
        self._shadow.setColor(QColor(0, 130, 65, 35))
        self.setProperty("hover", True); self.style().unpolish(self); self.style().polish(self)
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._ab.stop(); self._ab.setStartValue(self._shadow.blurRadius()); self._ab.setEndValue(10); self._ab.start()
        self._ao.stop(); self._ao.setStartValue(self._shadow.offset()); self._ao.setEndValue(QPointF(0, 2)); self._ao.start()
        self._shadow.setColor(QColor(0, 80, 40, 14))
        self.setProperty("hover", False); self.style().unpolish(self); self.style().polish(self)
        super().leaveEvent(e)


class OverviewPage(QWidget):
    def __init__(self):
        super().__init__()
        self._worker = None

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)

        # HERO ANIMADO
        self.hero = AnimatedHero()
        hl = QHBoxLayout(self.hero)
        hl.setContentsMargins(14, 10, 14, 10)
        hl.setSpacing(10)

        icon_frame = QFrame()
        icon_frame.setObjectName("HeroIconFrame")
        icon_frame.setFixedSize(34, 34)
        ifl = QVBoxLayout(icon_frame)
        ifl.setContentsMargins(0, 0, 0, 0)
        icon_lbl = QLabel()
        icon_lbl.setPixmap(criar_icone_vetorial("chart", 20, "#FFFFFF"))
        icon_lbl.setAlignment(Qt.AlignCenter)
        ifl.addWidget(icon_lbl)
        hl.addWidget(icon_frame)

        tc = QVBoxLayout()
        tc.setSpacing(1)
        t1 = QLabel("Overview")
        t1.setObjectName("FieldTitle")
        tc.addWidget(t1)
        t2 = QLabel("Gera relatórios de resumo a partir dos CSVs de reconciliação. Agrupa conciliados e pendentes.")
        t2.setObjectName("FieldText")
        t2.setWordWrap(True)
        tc.addWidget(t2)
        hl.addLayout(tc, 1)
        root.addWidget(self.hero)

        # CONFIG
        cfg = HoverCard()
        cfg.setObjectName("PremiumPathCard")
        cl = QVBoxLayout(cfg)
        cl.setContentsMargins(12, 10, 12, 10)
        cl.setSpacing(6)

        acc = QFrame(); acc.setObjectName("CardAccentLine"); acc.setFixedHeight(2)
        cl.addWidget(acc)
        el = QLabel("ORIGEM"); el.setObjectName("SectionEyebrow")
        cl.addWidget(el)

        row = QHBoxLayout()
        row.setSpacing(4)
        lb = QLabel("Pasta CSVs:")
        lb.setObjectName("FieldTitle")
        lb.setFixedWidth(70)
        row.addWidget(lb)
        self.path_input = QLineEdit()
        self.path_input.setObjectName("PathInput")
        self.path_input.setReadOnly(True)
        self.path_input.setPlaceholderText("Clique para selecionar a pasta com CSVs de reconciliação")
        self.path_input.setCursor(Qt.PointingHandCursor)
        self.path_input.mousePressEvent = lambda e: self._selecionar_pasta()
        row.addWidget(self.path_input, 1)
        btn = QPushButton("Selecionar")
        btn.setObjectName("SecondaryButton")
        btn.setMinimumHeight(28)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self._selecionar_pasta)
        row.addWidget(btn)
        cl.addLayout(row)

        root.addWidget(cfg)

        # EXEC
        exec_card = HoverCard()
        exec_card.setObjectName("PremiumExecCard")
        ecl = QHBoxLayout(exec_card)
        ecl.setContentsMargins(12, 8, 12, 8)
        ecl.setSpacing(10)

        exec_left = QVBoxLayout()
        exec_left.setSpacing(3)
        e3 = QLabel("EXECUÇÃO"); e3.setObjectName("SectionEyebrow")
        exec_left.addWidget(e3)
        self.progress = QProgressBar()
        self.progress.setValue(0)
        exec_left.addWidget(self.progress)
        self.status_label = QLabel("Aguardando...")
        self.status_label.setObjectName("FieldText")
        exec_left.addWidget(self.status_label)
        ecl.addLayout(exec_left, 1)

        self.btn_executar = QPushButton("Gerar Overviews")
        self.btn_executar.setObjectName("PrimaryButton")
        self.btn_executar.setMinimumHeight(36)
        self.btn_executar.setMinimumWidth(150)
        self.btn_executar.clicked.connect(self._executar)
        ecl.addWidget(self.btn_executar, 0, Qt.AlignVCenter)

        root.addWidget(exec_card)

        # BOTTOM: Info + Log
        bottom = QHBoxLayout()
        bottom.setSpacing(8)

        info_card = HoverCard()
        info_card.setObjectName("PremiumSummaryCard")
        info_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        icl = QVBoxLayout(info_card)
        icl.setContentsMargins(12, 8, 12, 8)
        icl.setSpacing(6)

        acc5 = QFrame(); acc5.setObjectName("CardAccentLine"); acc5.setFixedHeight(2)
        icl.addWidget(acc5)
        ie = QLabel("RESUMO"); ie.setObjectName("SectionEyebrow")
        icl.addWidget(ie)

        stats_info = [
            ("folder", "CSVs encontrados",       "—", "#3B82F6"),
            ("link",   "Registros conciliados",   "—", "#00A651"),
            ("search", "Registros pendentes",     "—", "#EF4444"),
            ("chart",  "Empresas processadas",    "—", "#8B5CF6"),
            ("pdf",    "Overviews gerados",       "—", "#F59E0B"),
        ]
        self._info_labels = {}
        for icon_n, label, default, color in stats_info:
            row = QHBoxLayout()
            row.setSpacing(6)
            ic = QLabel()
            ic.setPixmap(criar_icone_vetorial(icon_n, 14))
            ic.setFixedSize(14, 14)
            row.addWidget(ic)
            lb = QLabel(label)
            lb.setObjectName("FieldText")
            row.addWidget(lb, 1)
            val = QLabel(default)
            val.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 600;")
            row.addWidget(val)
            self._info_labels[label] = val
            icl.addLayout(row)

        icl.addStretch(1)
        bottom.addWidget(info_card, 1)

        log_card = HoverCard()
        log_card.setObjectName("PremiumLogCard")
        log_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lcl = QVBoxLayout(log_card)
        lcl.setContentsMargins(12, 8, 12, 8)
        lcl.setSpacing(3)

        acc4 = QFrame(); acc4.setObjectName("CardAccentLine"); acc4.setFixedHeight(2)
        lcl.addWidget(acc4)
        le = QLabel("LOG"); le.setObjectName("SectionEyebrow")
        lcl.addWidget(le)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        lcl.addWidget(self.log_output, 1)

        bottom.addWidget(log_card, 2)
        root.addLayout(bottom, 1)

    def _selecionar_pasta(self):
        pasta = QFileDialog.getExistingDirectory(self, "Selecionar pasta de CSVs")
        if pasta:
            self.path_input.setText(pasta)

    def _executar(self):
        pasta = self.path_input.text()
        if not pasta or not os.path.isdir(pasta):
            QMessageBox.warning(self, "Aviso", "Selecione uma pasta valida."); return

        self.btn_executar.setEnabled(False)
        self.progress.setValue(0)
        self.log_output.clear()
        self.status_label.setText("Gerando overviews...")

        self._worker = OverviewWorker(pasta)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_progress(self, pct, msg):
        self.progress.setValue(pct)
        self.hero.set_progress(pct)
        self.status_label.setText(msg)
        self.log_output.append(msg)

    def _on_finished(self, arquivos):
        self.progress.setValue(100)
        self.hero.set_progress(100)
        self.status_label.setText(f"Concluido! {len(arquivos)} overview(s).")
        for arq in arquivos:
            self.log_output.append(f"  -> {arq}")
        self.btn_executar.setEnabled(True)

    def _on_error(self, msg):
        self.progress.setValue(0)
        self.status_label.setText("Erro!")
        self.log_output.append(f"ERRO: {msg}")
        self.btn_executar.setEnabled(True)
        QMessageBox.critical(self, "Erro", msg)
