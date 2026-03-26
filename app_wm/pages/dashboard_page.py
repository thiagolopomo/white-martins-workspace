#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dashboard White Martins - TOTALMENTE RESPONSIVO.
Tudo escala com a resolução: textos, ícones, margens, espaçamentos.
"""

from PySide6.QtCore import Qt, QEasingCurve, QPropertyAnimation, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPainterPath, QLinearGradient, QPen, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QSizePolicy, QGraphicsDropShadowEffect
)

from resources import criar_icone_vetorial


class MiniBarChart(QWidget):
    def __init__(self, values=None, color="#00A651", parent=None):
        super().__init__(parent)
        self.values = values or [40, 65, 45, 80]
        self.color = QColor(color)
        self.setMinimumSize(20, 10)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        n = len(self.values)
        max_val = max(self.values) or 1
        bar_w = max(2, (w - (n - 1) * 2) / n)
        for i, v in enumerate(self.values):
            x = i * (bar_w + 2)
            bar_h = (v / max_val) * (h - 2)
            y = h - bar_h
            c = QColor(self.color); c.setAlpha(int(100 + (v / max_val) * 155))
            path = QPainterPath(); path.addRoundedRect(QRectF(x, y, bar_w, bar_h), 1.5, 1.5)
            p.fillPath(path, c)
        p.end()


class MiniLineChart(QWidget):
    def __init__(self, values=None, color="#00A651", parent=None):
        super().__init__(parent)
        self.values = values or [30, 45, 38, 62, 55, 75, 68, 85, 78, 92]
        self.color = QColor(color)
        self.setMinimumSize(30, 12)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        n = len(self.values)
        if n < 2: return
        max_val = max(self.values) or 1
        min_val = min(self.values)
        rng = max_val - min_val or 1
        m = 3
        points = []
        for i, v in enumerate(self.values):
            x = m + (i / (n - 1)) * (w - m * 2)
            y = h - m - ((v - min_val) / rng) * (h - m * 2)
            points.append(QPointF(x, y))
        fill = QPainterPath()
        fill.moveTo(points[0].x(), h)
        for pt in points: fill.lineTo(pt)
        fill.lineTo(points[-1].x(), h); fill.closeSubpath()
        grad = QLinearGradient(0, 0, 0, h)
        c1 = QColor(self.color); c1.setAlpha(35); grad.setColorAt(0, c1)
        c2 = QColor(self.color); c2.setAlpha(3); grad.setColorAt(1, c2)
        p.fillPath(fill, grad)
        pen = QPen(self.color); pen.setWidthF(1.6); pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        for i in range(len(points) - 1): p.drawLine(points[i], points[i + 1])
        p.setBrush(self.color); p.setPen(Qt.NoPen)
        p.drawEllipse(points[-1], 2.5, 2.5)
        p.end()


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


def _s(base, f):
    """Scale inteiro."""
    return max(1, int(base * f))


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self._last_scale = -1

        # Armazena referências pra escalar
        self._scalable = []  # (widget, base_font_size, object_name_or_style)

        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(0, 0, 0, 0)
        self._root.setSpacing(10)

        # ---- STATS ROW ----
        self._stats_row = QHBoxLayout()
        self._stats_row.setSpacing(10)

        stats_data = [
            ("folder", "Módulos",   "4",               "Módulos Disponíveis",   MiniBarChart([60, 80, 70, 95])),
            ("chart",  "Execuções", "0",               "Processamentos",        MiniLineChart([10, 10, 10, 10, 10])),
            ("search", "Status",    "Pronto",          "Sistema Operacional",   MiniBarChart([95, 95, 95, 95], "#3B82F6")),
            ("link",   "Fluxo",     "PDF + XLSB + CSV","Formatos Suportados",   MiniBarChart([85, 70, 60], "#F59E0B")),
        ]

        self._stat_cards = []
        for icon_n, label, value, sub_text, chart in stats_data:
            card = HoverCard()
            card.setObjectName("StatCard")
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(14, 12, 14, 12)
            cl.setSpacing(6)

            accent = QFrame(); accent.setObjectName("StatAccentLine"); accent.setFixedHeight(2)
            cl.addWidget(accent)

            top = QHBoxLayout(); top.setSpacing(6)
            ic = QLabel()
            ic.setPixmap(criar_icone_vetorial(icon_n, 16, "#00A651"))
            ic.setFixedSize(16, 16)
            top.addWidget(ic)
            lb = QLabel(label); lb.setObjectName("StatLabel")
            top.addWidget(lb, 1)
            chart.setMinimumSize(40, 16); chart.setMaximumSize(80, 28)
            top.addWidget(chart)
            cl.addLayout(top)

            vl = QLabel(value); vl.setObjectName("StatValue")
            cl.addWidget(vl)
            sl = QLabel(sub_text); sl.setObjectName("StatSub")
            cl.addWidget(sl)

            self._stat_cards.append({"card": card, "layout": cl, "label": lb, "value": vl, "sub": sl, "icon": ic})
            self._stats_row.addWidget(card)

        self._root.addLayout(self._stats_row)

        # ---- MODULE CARDS 2x2 ----
        self._modules_grid = QGridLayout()
        self._modules_grid.setSpacing(10)

        modules_data = [
            ("pdf",   "CONVERTER PDFs",    "Extração de dados de PDFs ICMS",
             "Importa PDFs do relatório de apoio à apuração do ICMS, extrai os dados fiscais e gera planilha Excel consolidada.",
             ["Seleciona pasta com PDFs", "Identifica empresa automaticamente", "Exporta Excel agrupado por período"]),
            ("split", "SEGREGAR DIVISÕES", "Separação por divisão contábil",
             "Importa planilha .xlsb/.xlsx completa e gera um arquivo individual para cada divisão encontrada.",
             ["Importa planilha .xlsb ou .xlsx", "Detecta divisões automaticamente", "Preserva fórmulas e aba Capa"]),
            ("link",  "RECONCILIAÇÃO",     "Pipeline de reconciliação fiscal",
             "Cruza dados do Razão contábil com o Fiscal, aplicando 3 chaves de conciliação progressiva.",
             ["Seleciona Razão e Fiscal (CSV)", "3 chaves de cruzamento automático", "Exporta CSV com resultado detalhado"]),
            ("chart", "OVERVIEW",          "Resumos e relatórios visuais",
             "Gera overviews consolidados a partir dos CSVs de reconciliação, agrupando resultados.",
             ["Agrupa conciliados e pendentes", "Soma valores por chave e divisão", "Exporta CSV de overview final"]),
        ]

        self._module_cards = []
        for idx, (icon_n, eyebrow, titulo, desc, bullets) in enumerate(modules_data):
            card = HoverCard()
            card.setObjectName("WorkspaceModuleCard")
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            cl = QVBoxLayout(card)
            cl.setContentsMargins(18, 16, 18, 16)
            cl.setSpacing(8)

            top = QHBoxLayout(); top.setSpacing(10)
            icon_frame = QFrame(); icon_frame.setObjectName("ModuleIcon")
            icon_frame.setFixedSize(32, 32)
            il = QVBoxLayout(icon_frame); il.setContentsMargins(0, 0, 0, 0)
            icon_lbl = QLabel()
            icon_lbl.setPixmap(criar_icone_vetorial(icon_n, 18, "#FFFFFF"))
            icon_lbl.setAlignment(Qt.AlignCenter)
            il.addWidget(icon_lbl)
            top.addWidget(icon_frame)

            tc = QVBoxLayout(); tc.setSpacing(1)
            eb = QLabel(eyebrow); eb.setObjectName("SectionEyebrow")
            tc.addWidget(eb)
            tl = QLabel(titulo); tl.setObjectName("ModuleTitle")
            tc.addWidget(tl)
            top.addLayout(tc, 1)
            cl.addLayout(top)

            dl = QLabel(desc); dl.setObjectName("ModuleDesc"); dl.setWordWrap(True)
            cl.addWidget(dl)

            bullet_labels = []
            for b in bullets:
                row = QHBoxLayout(); row.setSpacing(8); row.setContentsMargins(6, 0, 0, 0)
                dot = QFrame(); dot.setFixedSize(5, 5)
                dot.setStyleSheet("background: #F59E0B; border-radius: 2px;")
                row.addWidget(dot, 0, Qt.AlignVCenter)
                bt = QLabel(b); bt.setObjectName("ModuleBullet"); bt.setWordWrap(True)
                row.addWidget(bt, 1)
                cl.addLayout(row)
                bullet_labels.append(bt)

            cl.addStretch(1)
            self._module_cards.append({
                "card": card, "layout": cl, "eyebrow": eb, "title": tl,
                "desc": dl, "bullets": bullet_labels, "icon_frame": icon_frame, "icon_lbl": icon_lbl,
                "icon_n": icon_n,
            })
            self._modules_grid.addWidget(card, idx // 2, idx % 2)

        self._root.addLayout(self._modules_grid, 1)

        # ---- FOOTER BAND ----
        self._band = HoverCard()
        self._band.setObjectName("WorkspaceBand")
        band_layout = QHBoxLayout(self._band)
        band_layout.setContentsMargins(16, 10, 16, 10)
        band_layout.setSpacing(12)

        bl_text = QVBoxLayout(); bl_text.setSpacing(2)
        self._band_eye = QLabel("FLUXO DE TRABALHO"); self._band_eye.setObjectName("SectionEyebrow")
        bl_text.addWidget(self._band_eye)
        self._band_title = QLabel("PDF  →  Segregação  →  Reconciliação  →  Overview")
        self._band_title.setObjectName("FieldTitle")
        bl_text.addWidget(self._band_title)
        band_layout.addLayout(bl_text, 1)

        flow_chart = MiniLineChart([10, 25, 40, 55, 50, 65, 80, 75, 90, 95], "#00A651")
        flow_chart.setMinimumSize(80, 24); flow_chart.setMaximumHeight(40)
        band_layout.addWidget(flow_chart, 0, Qt.AlignVCenter)
        self._root.addWidget(self._band)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        h = self.height()
        w = self.width()

        # Fator de escala baseado na altura (ref: 620px = 1.0)
        f = max(0.55, min(1.3, h / 620.0))
        fw = max(0.7, min(1.2, w / 1300.0))

        # Evita recalcular se o fator não mudou significativamente
        scale_key = int(f * 100)
        if scale_key == self._last_scale:
            return
        self._last_scale = scale_key

        # Espaçamentos globais
        sp = _s(10, f)
        self._root.setSpacing(sp)
        self._stats_row.setSpacing(sp)
        self._modules_grid.setSpacing(sp)

        # Stat cards
        for sc in self._stat_cards:
            m = _s(14, f)
            sc["layout"].setContentsMargins(m, _s(12, f), m, _s(12, f))
            sc["layout"].setSpacing(_s(6, f))
            sc["label"].setStyleSheet(f"color: #94A3B8; font-size: {_s(10, f)}px; font-weight: 600; letter-spacing: 0.8px;")
            sc["value"].setStyleSheet(f"color: #0F172A; font-size: {_s(18, f)}px; font-weight: 700;")
            sc["sub"].setStyleSheet(f"color: #94A3B8; font-size: {_s(10, f)}px;")

        # Module cards
        for mc in self._module_cards:
            m = _s(18, f)
            mc["layout"].setContentsMargins(m, _s(16, f), m, _s(16, f))
            mc["layout"].setSpacing(_s(8, f))

            icon_sz = _s(32, f)
            mc["icon_frame"].setFixedSize(icon_sz, icon_sz)
            pix_sz = _s(18, f)
            mc["icon_lbl"].setPixmap(criar_icone_vetorial(mc["icon_n"], pix_sz, "#FFFFFF"))

            mc["eyebrow"].setStyleSheet(f"color: #F59E0B; font-size: {_s(10, f)}px; font-weight: 700; letter-spacing: 2px;")
            mc["title"].setStyleSheet(f"color: #0F172A; font-size: {_s(14, f)}px; font-weight: 600;")
            mc["desc"].setStyleSheet(f"color: #64748B; font-size: {_s(12, f)}px;")
            for bl in mc["bullets"]:
                bl.setStyleSheet(f"color: #475569; font-size: {_s(12, f)}px;")

        # Band
        bm = _s(16, f)
        self._band.layout().setContentsMargins(bm, _s(10, f), bm, _s(10, f))
        self._band_eye.setStyleSheet(f"color: #F59E0B; font-size: {_s(10, f)}px; font-weight: 700; letter-spacing: 2px;")
        self._band_title.setStyleSheet(f"color: #0F172A; font-size: {_s(13, f)}px; font-weight: 500;")
