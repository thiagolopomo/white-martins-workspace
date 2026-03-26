#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reconciliacao - SEM SCROLL. Tudo cabe na tela.
Log tem scroll interno. Grafico de resultados.
"""

import os
from PySide6.QtCore import Qt, QEasingCurve, QPropertyAnimation, QPointF, QRectF, QTimer
from PySide6.QtGui import QColor, QPainter, QPainterPath, QLinearGradient, QPen, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QFileDialog, QMessageBox, QTextEdit, QLineEdit, QSizePolicy, QProgressBar,
    QGraphicsDropShadowEffect
)

from resources import criar_icone_vetorial
from workers.recon_worker import ReconWorker


class AnimatedHero(QFrame):
    """
    Hero com animação de progresso integrada.
    Um glow suave se expande da esquerda pra direita conforme set_progress().
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PageHeroCard")
        self._progress = 0.0
        self._pulse_alpha = 0
        self._pulse_dir = 1
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._pulse_tick)

    def set_progress(self, pct: int):
        self._progress = max(0.0, min(1.0, pct / 100.0))
        if pct > 0 and pct < 100 and not self._pulse_timer.isActive():
            self._pulse_timer.start(40)
        elif pct >= 100 or pct == 0:
            self._pulse_timer.stop()
            self._pulse_alpha = 0
        self.update()

    def _pulse_tick(self):
        self._pulse_alpha += self._pulse_dir * 3
        if self._pulse_alpha > 30:
            self._pulse_alpha = 30
            self._pulse_dir = -1
        elif self._pulse_alpha < 0:
            self._pulse_alpha = 0
            self._pulse_dir = 1
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        rect = QRectF(0, 0, w, h)

        base = QLinearGradient(0, 0, w, h)
        base.setColorAt(0.0, QColor("#0F172A"))
        base.setColorAt(0.5, QColor("#1E293B"))
        base.setColorAt(1.0, QColor("#334155"))

        path = QPainterPath()
        path.addRoundedRect(rect, 14, 14)
        p.fillPath(path, base)

        if self._progress > 0:
            glow_w = w * self._progress
            p.save()
            p.setClipPath(path)

            if self._progress >= 1.0:
                # Completo - verde aurora suave
                glow = QLinearGradient(0, 0, w, 0)
                glow.setColorAt(0.0, QColor(0, 166, 81, 30))
                glow.setColorAt(0.3, QColor(0, 220, 110, 20))
                glow.setColorAt(0.6, QColor(0, 200, 100, 15))
                glow.setColorAt(1.0, QColor(0, 166, 81, 5))
                p.fillPath(path, glow)
            else:
                # Aurora boreal animada - mais vibrante
                alpha = 25 + self._pulse_alpha * 2
                # Camada 1: azul→verde
                glow1 = QLinearGradient(0, 0, glow_w, h * 0.5)
                glow1.setColorAt(0.0, QColor(59, 130, 246, int(alpha * 0.9)))
                glow1.setColorAt(0.4, QColor(0, 200, 130, int(alpha * 0.7)))
                glow1.setColorAt(0.7, QColor(245, 158, 11, int(alpha * 0.5)))
                glow1.setColorAt(1.0, QColor(255, 255, 255, 0))
                glow_path1 = QPainterPath()
                glow_path1.addRoundedRect(QRectF(0, 0, glow_w, h), 14, 14)
                p.fillPath(glow_path1, glow1)

                # Camada 2: reflexo no topo (aurora)
                from PySide6.QtGui import QRadialGradient
                pulse_x = glow_w * 0.7
                aurora = QRadialGradient(pulse_x, h * 0.3, glow_w * 0.5)
                aurora.setColorAt(0.0, QColor(0, 220, 150, int(alpha * 0.6)))
                aurora.setColorAt(0.5, QColor(59, 130, 246, int(alpha * 0.3)))
                aurora.setColorAt(1.0, QColor(0, 0, 0, 0))
                p.fillPath(glow_path1, aurora)

            p.restore()

            # Progress line at bottom - mais brilhante
            line_w = w * self._progress
            if self._progress >= 1.0:
                pen = QPen(QColor(0, 200, 100, 120))
            else:
                pen = QPen(QColor(59, 130, 246, 100))
            pen.setWidthF(2.5)
            p.setPen(pen)
            p.drawLine(QPointF(0, h - 1), QPointF(line_w, h - 1))

        p.setPen(Qt.NoPen)
        for i in range(4):
            for j in range(2):
                alpha = 8 + i * 5
                p.setBrush(QColor(255, 255, 255, alpha))
                p.drawEllipse(QPointF(w - 150 + i * 22, h * 0.25 + j * 18), 1.5, 1.5)

        pen2 = QPen(QColor(255, 255, 255, 12))
        pen2.setWidthF(1)
        p.setPen(pen2)
        p.drawArc(QRectF(w - 60, -20, 90, 90), 120 * 16, 200 * 16)
        p.end()


PageHeroDecor = None


class HoverCard(QFrame):
    def __init__(self):
        super().__init__()
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(10)
        self._shadow.setOffset(0, 2)
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


class ReconBarChart(QWidget):
    """Grafico de barras horizontal: conciliados vs nao conciliados por empresa."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(40)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.data = {"Gilda": (0, 0), "Gine": (0, 0), "Gino": (0, 0)}

    def set_data(self, data: dict):
        self.data = data
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        if not self.data:
            p.end(); return

        n = len(self.data)
        label_w = 45
        chart_x = label_w + 6
        chart_w = w - chart_x - 6
        bar_h = max(6, min(14, (h - (n - 1) * 4 - 16) / (n * 2)))
        group_h = bar_h * 2 + 3
        total_h = n * group_h + (n - 1) * 4
        y_start = max(0, (h - total_h - 16) / 2)

        max_val = 1
        for conc, nconc in self.data.values():
            max_val = max(max_val, conc, nconc)

        colors = {"conc": QColor("#00A651"), "nconc": QColor("#E85D4A")}
        fs = max(7, min(9, int(h / 12)))
        font_label = QFont("Segoe UI", fs, QFont.DemiBold)
        font_val = QFont("Segoe UI", max(6, fs - 1))

        for i, (empresa, (conc, nconc)) in enumerate(self.data.items()):
            y = y_start + i * (group_h + 4)

            p.setPen(QColor("#3A4E3A"))
            p.setFont(font_label)
            p.drawText(QRectF(0, y, label_w, group_h), Qt.AlignVCenter | Qt.AlignRight, empresa)

            bw_conc = (conc / max_val) * chart_w if max_val > 0 else 0
            bar_rect = QRectF(chart_x, y, max(2, bw_conc), bar_h)
            path = QPainterPath(); path.addRoundedRect(bar_rect, 3, 3)
            p.fillPath(path, colors["conc"])

            bw_nconc = (nconc / max_val) * chart_w if max_val > 0 else 0
            bar_rect2 = QRectF(chart_x, y + bar_h + 3, max(2, bw_nconc), bar_h)
            path2 = QPainterPath(); path2.addRoundedRect(bar_rect2, 3, 3)
            p.fillPath(path2, colors["nconc"])

            p.setPen(QColor("#5A6E5A"))
            p.setFont(font_val)
            if conc > 0:
                p.drawText(QRectF(chart_x + bw_conc + 3, y, 50, bar_h),
                           Qt.AlignVCenter | Qt.AlignLeft, str(conc))
            if nconc > 0:
                p.drawText(QRectF(chart_x + bw_nconc + 3, y + bar_h + 3, 50, bar_h),
                           Qt.AlignVCenter | Qt.AlignLeft, str(nconc))

        legend_y = h - 14
        p.setFont(QFont("Segoe UI", max(6, fs - 1)))
        legend_x = w - 200

        pill1 = QPainterPath()
        pill1.addRoundedRect(QRectF(legend_x, legend_y - 1, 80, 14), 7, 7)
        p.fillPath(pill1, QColor(0, 166, 81, 15))
        p.setPen(Qt.NoPen)
        p.fillRect(QRectF(legend_x + 5, legend_y + 2, 7, 7), colors["conc"])
        p.setPen(QColor("#334155"))
        p.drawText(QRectF(legend_x + 15, legend_y, 60, 14), Qt.AlignVCenter, "Conciliados")

        pill2 = QPainterPath()
        pill2.addRoundedRect(QRectF(legend_x + 88, legend_y - 1, 110, 14), 7, 7)
        p.fillPath(pill2, QColor(232, 93, 74, 12))
        p.setPen(Qt.NoPen)
        p.fillRect(QRectF(legend_x + 93, legend_y + 2, 7, 7), colors["nconc"])
        p.setPen(QColor("#334155"))
        p.drawText(QRectF(legend_x + 103, legend_y, 95, 14), Qt.AlignVCenter, "Não conciliados")

        p.end()


class ReconPage(QWidget):
    def __init__(self):
        super().__init__()
        self._worker = None

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)

        # ---- HERO ANIMADO ----
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
        icon_lbl.setPixmap(criar_icone_vetorial("link", 20, "#FFFFFF"))
        icon_lbl.setAlignment(Qt.AlignCenter)
        ifl.addWidget(icon_lbl)
        hl.addWidget(icon_frame)

        tc = QVBoxLayout()
        tc.setSpacing(1)
        t1 = QLabel("Reconciliação")
        t1.setObjectName("FieldTitle")
        tc.addWidget(t1)
        t2 = QLabel("Selecione Razão e Fiscal para cruzar. Pipeline: Consolidação → Conciliação → CSV.")
        t2.setObjectName("FieldText")
        t2.setWordWrap(True)
        tc.addWidget(t2)
        hl.addLayout(tc, 1)

        root.addWidget(self.hero)

        # ---- MIDDLE ROW: Config + Chart ----
        mid = QHBoxLayout()
        mid.setSpacing(8)

        files_card = HoverCard()
        files_card.setObjectName("PremiumPathCard")
        files_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        fl = QVBoxLayout(files_card)
        fl.setContentsMargins(12, 10, 12, 10)
        fl.setSpacing(6)

        acc = QFrame(); acc.setObjectName("CardAccentLine"); acc.setFixedHeight(2)
        fl.addWidget(acc)
        el = QLabel("ARQUIVOS DE ENTRADA"); el.setObjectName("SectionEyebrow")
        fl.addWidget(el)

        for label_text, attr_name, placeholder, is_file in [
            ("Razão:", "input_razao", "Clique para selecionar o arquivo CSV do Razão", True),
            ("Fiscal:", "input_fiscal", "Clique para selecionar o arquivo CSV do Fiscal", True),
            ("Saída:", "input_saida", "Clique para selecionar a pasta de saída", False),
        ]:
            row = QHBoxLayout()
            row.setSpacing(4)
            lb = QLabel(label_text)
            lb.setObjectName("FieldTitle")
            lb.setFixedWidth(50)
            row.addWidget(lb)
            inp = QLineEdit()
            inp.setObjectName("PathInput")
            inp.setReadOnly(True)
            inp.setPlaceholderText(placeholder)
            inp.setCursor(Qt.PointingHandCursor)
            setattr(self, attr_name, inp)
            row.addWidget(inp, 1)
            btn = QPushButton("Selecionar")
            btn.setObjectName("SecondaryButton")
            btn.setMinimumHeight(28)
            btn.setCursor(Qt.PointingHandCursor)
            if is_file:
                handler = lambda checked, a=attr_name: self._sel_file(a)
                btn.clicked.connect(handler)
                inp.mousePressEvent = lambda e, a=attr_name: self._sel_file(a)
            else:
                btn.clicked.connect(self._sel_folder)
                inp.mousePressEvent = lambda e: self._sel_folder()
            row.addWidget(btn)
            fl.addLayout(row)

        fl.addStretch(1)
        mid.addWidget(files_card, 3)

        chart_card = HoverCard()
        chart_card.setObjectName("PremiumSummaryCard")
        chart_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        ccl = QVBoxLayout(chart_card)
        ccl.setContentsMargins(12, 10, 12, 10)
        ccl.setSpacing(4)

        acc2 = QFrame(); acc2.setObjectName("CardAccentLine"); acc2.setFixedHeight(2)
        ccl.addWidget(acc2)
        cl = QLabel("RESULTADO POR EMPRESA"); cl.setObjectName("SectionEyebrow")
        cl_sub = QLabel("Conciliados vs. não conciliados")
        cl_sub.setObjectName("FieldText")
        ccl.addWidget(cl_sub)
        ccl.addWidget(cl)

        self.recon_chart = ReconBarChart()
        ccl.addWidget(self.recon_chart, 1)

        mid.addWidget(chart_card, 2)
        root.addLayout(mid)

        # ---- EXEC ROW ----
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

        self.btn_executar = QPushButton("Executar Reconciliação")
        self.btn_executar.setObjectName("PrimaryButton")
        self.btn_executar.setMinimumHeight(36)
        self.btn_executar.setMinimumWidth(130)
        self.btn_executar.clicked.connect(self._executar)
        ecl.addWidget(self.btn_executar, 0, Qt.AlignVCenter)

        root.addWidget(exec_card)

        # ---- BOTTOM: Info + Log ----
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
        ie = QLabel("INDICADORES"); ie.setObjectName("SectionEyebrow")
        icl.addWidget(ie)

        stats_info = [
            ("pdf",    "Etapa 1 - Parquet",       "Aguardando", "#3B82F6"),
            ("link",   "Etapa 2 - Consolidação",   "Aguardando", "#F59E0B"),
            ("search", "Etapa 3 - Conciliação",    "Aguardando", "#00A651"),
            ("chart",  "Etapa 4 - Exportação",     "Aguardando", "#EF4444"),
            ("folder", "Linhas Razão",             "—", "#8B5CF6"),
            ("folder", "Linhas Fiscal",            "—", "#06B6D4"),
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

    def _sel_file(self, attr):
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar arquivo", "", "CSV (*.csv);;Todos (*.*)")
        if path:
            getattr(self, attr).setText(path)

    def _sel_folder(self):
        pasta = QFileDialog.getExistingDirectory(self, "Selecionar pasta")
        if pasta:
            self.input_saida.setText(pasta)

    def _executar(self):
        razao = self.input_razao.text()
        fiscal = self.input_fiscal.text()
        saida = self.input_saida.text()

        if not razao or not os.path.isfile(razao):
            QMessageBox.warning(self, "Aviso", "Selecione o arquivo Razao."); return
        if not fiscal or not os.path.isfile(fiscal):
            QMessageBox.warning(self, "Aviso", "Selecione o arquivo Fiscal."); return
        if not saida:
            QMessageBox.warning(self, "Aviso", "Selecione a pasta de saida."); return

        # Validação de empresa
        from logic.empresa_detect import validar_mesma_empresa
        empresa, erro = validar_mesma_empresa(razao, fiscal)
        if erro:
            QMessageBox.critical(self, "Erro - Empresas Diferentes", erro)
            return

        self._empresa_detectada = empresa

        self.btn_executar.setEnabled(False)
        self.progress.setValue(0)
        self.log_output.clear()

        if empresa:
            self.status_label.setText(f"Iniciando pipeline... (Empresa: {empresa})")
            self.log_output.append(f"Empresa detectada: {empresa}")
        else:
            self.status_label.setText("Iniciando pipeline...")

        self._worker = ReconWorker(razao, fiscal, saida)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.stats.connect(self._on_stats)
        self._worker.start()

    def _on_progress(self, pct, msg):
        self.progress.setValue(pct)
        self.hero.set_progress(pct)
        self.status_label.setText(msg)
        self.log_output.append(msg)

        m = msg.lower()
        if "etapa 1" in m:
            self._info_labels["Etapa 1 - Parquet"].setText("Em andamento...")
            self._info_labels["Etapa 1 - Parquet"].setStyleSheet("color: #3B82F6; font-size: 11px; font-weight: 600;")
        if "etapa 1 conclu" in m:
            self._info_labels["Etapa 1 - Parquet"].setText("Concluída")
            self._info_labels["Etapa 1 - Parquet"].setStyleSheet("color: #00A651; font-size: 11px; font-weight: 600;")
        if "etapa 2" in m:
            self._info_labels["Etapa 2 - Consolidação"].setText("Em andamento...")
            self._info_labels["Etapa 2 - Consolidação"].setStyleSheet("color: #F59E0B; font-size: 11px; font-weight: 600;")
        if "etapa 2 conclu" in m:
            self._info_labels["Etapa 2 - Consolidação"].setText("Concluída")
            self._info_labels["Etapa 2 - Consolidação"].setStyleSheet("color: #00A651; font-size: 11px; font-weight: 600;")
        if "etapa 3" in m:
            self._info_labels["Etapa 3 - Conciliação"].setText("Em andamento...")
        if "etapa 3 conclu" in m:
            self._info_labels["Etapa 3 - Conciliação"].setText("Concluída")
            self._info_labels["Etapa 3 - Conciliação"].setStyleSheet("color: #00A651; font-size: 11px; font-weight: 600;")
        if "etapa 4" in m:
            self._info_labels["Etapa 4 - Exportação"].setText("Em andamento...")
        if "etapa 4 conclu" in m or "exporta" in m and "conclu" in m:
            self._info_labels["Etapa 4 - Exportação"].setText("Concluída")
            self._info_labels["Etapa 4 - Exportação"].setStyleSheet("color: #00A651; font-size: 11px; font-weight: 600;")

    def _on_stats(self, stats):
        """Atualiza indicadores e gráfico com dados reais."""
        lr = stats.get("linhas_razao", 0)
        lf = stats.get("linhas_fiscal", 0)
        conc = stats.get("conciliados", 0)
        nconc = stats.get("nao_conciliados", 0)

        self._info_labels["Linhas Razão"].setText(f"{lr:,}".replace(",", "."))
        self._info_labels["Linhas Razão"].setStyleSheet("color: #8B5CF6; font-size: 11px; font-weight: 600;")
        self._info_labels["Linhas Fiscal"].setText(f"{lf:,}".replace(",", "."))
        self._info_labels["Linhas Fiscal"].setStyleSheet("color: #06B6D4; font-size: 11px; font-weight: 600;")

        # Atualiza gráfico com empresa detectada
        empresa = getattr(self, "_empresa_detectada", None) or "Empresa"
        self.recon_chart.set_data({empresa: (conc, nconc)})

        self.log_output.append(f"\nConciliados: {conc:,} | Não conciliados: {nconc:,}".replace(",", "."))

    def _on_finished(self, pasta_csvs):
        self.progress.setValue(100)
        self.hero.set_progress(100)
        self.status_label.setText(f"Concluído! CSVs em: {pasta_csvs}")
        self.log_output.append(f"Pipeline finalizado! Saída: {pasta_csvs}")
        self.btn_executar.setEnabled(True)
        for key in self._info_labels:
            if "Etapa" in key:
                self._info_labels[key].setText("Concluída")
                self._info_labels[key].setStyleSheet("color: #00A651; font-size: 11px; font-weight: 600;")

    def _on_error(self, msg):
        self.progress.setValue(0)
        self.status_label.setText("Erro!")
        self.log_output.append(f"ERRO: {msg}")
        self.btn_executar.setEnabled(True)
        QMessageBox.critical(self, "Erro", msg)
