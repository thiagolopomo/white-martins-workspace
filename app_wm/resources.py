#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resources White Martins - Logo real + icones coloridos multi-tom.
"""

import os
import sys

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import (
    QIcon, QPixmap, QImage, QFontDatabase, QPainter, QPainterPath,
    QLinearGradient, QColor, QFont, QPen
)

_BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
_ICON_CACHE = None
_LOGO_CACHE = {}
_FONT_FAMILY_CACHE = None
_VECTOR_ICON_CACHE = {}


def caminho_recurso(*partes) -> str:
    return os.path.join(_BASE_DIR, *partes)


def obter_icone() -> QIcon:
    global _ICON_CACHE
    if _ICON_CACHE is not None:
        return _ICON_CACHE
    for nome in ("icone.ico", "icone.png", "white-martins.png", "logowhitemartins.png"):
        caminho = caminho_recurso(nome)
        if os.path.exists(caminho):
            _ICON_CACHE = QIcon(caminho)
            return _ICON_CACHE
    _ICON_CACHE = QIcon()
    return _ICON_CACHE


def carregar_logo_wm_topbar(altura: int = 38):
    """Logo para fundo escuro: converte pixels escuros para branco."""
    key = f"topbar_{altura}"
    if key in _LOGO_CACHE:
        return _LOGO_CACHE[key]

    for nome in ("logowhitemartins.png", "logo_wm.png"):
        caminho = caminho_recurso(nome)
        if os.path.exists(caminho):
            pix = QPixmap(caminho)
            if not pix.isNull():
                scaled = pix.scaledToHeight(altura, Qt.SmoothTransformation)
                # Converter pixels escuros (preto/cinza) para branco
                img = scaled.toImage()
                for y in range(img.height()):
                    for x in range(img.width()):
                        c = QColor(img.pixel(x, y))
                        if c.alpha() > 10:
                            r, g, b = c.red(), c.green(), c.blue()
                            # Se é escuro (preto/cinza do texto "A Linde company")
                            if r < 100 and g < 100 and b < 100:
                                img.setPixelColor(x, y, QColor(255, 255, 255, c.alpha()))
                result = QPixmap.fromImage(img)
                _LOGO_CACHE[key] = result
                return result
    _LOGO_CACHE[key] = None
    return None


def _limpar_logo(pix):
    """Remove fundo preto/branco e recorta ao conteudo."""
    img = pix.toImage().convertToFormat(QImage.Format_ARGB32)
    w, h = img.width(), img.height()

    # Detectar cor do fundo (canto superior esquerdo)
    bg = QColor(img.pixel(0, 0))
    bg_is_dark = (bg.red() + bg.green() + bg.blue()) < 100

    for y in range(h):
        for x in range(w):
            c = QColor(img.pixel(x, y))
            r, g, b = c.red(), c.green(), c.blue()
            if bg_is_dark:
                # Fundo preto: remover pixels escuros sem verde
                if r < 40 and g < 40 and b < 40:
                    img.setPixelColor(x, y, QColor(0, 0, 0, 0))
            else:
                # Fundo branco: remover pixels claros
                if r > 240 and g > 240 and b > 240:
                    img.setPixelColor(x, y, QColor(0, 0, 0, 0))

    # Crop ao conteudo
    min_x, min_y, max_x, max_y = w, h, 0, 0
    for y in range(h):
        for x in range(w):
            if QColor(img.pixel(x, y)).alpha() > 10:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    if max_x <= min_x or max_y <= min_y:
        return QPixmap.fromImage(img)

    pad = 2
    min_x = max(0, min_x - pad)
    min_y = max(0, min_y - pad)
    max_x = min(w - 1, max_x + pad)
    max_y = min(h - 1, max_y + pad)

    cropped = img.copy(min_x, min_y, max_x - min_x, max_y - min_y)
    return QPixmap.fromImage(cropped)


def carregar_logo_wm_light(largura: int = 120):
    """Logo limpo (fundo removido). O logo já deve ter texto branco/verde."""
    key = f"light_{largura}"
    if key in _LOGO_CACHE:
        return _LOGO_CACHE[key]
    for nome in ("white-martins.png", "logowhitemartins.png"):
        caminho = caminho_recurso(nome)
        if os.path.exists(caminho):
            pix = QPixmap(caminho)
            if not pix.isNull():
                pix = _limpar_logo(pix)
                escalado = pix.scaledToWidth(largura, Qt.SmoothTransformation)
                _LOGO_CACHE[key] = escalado
                return escalado
    _LOGO_CACHE[key] = None
    return None


def carregar_logo_wm(largura: int = 120):
    if largura in _LOGO_CACHE:
        return _LOGO_CACHE[largura]
    for nome in ("white-martins.png", "logowhitemartins.png", "logo_wm.png"):
        caminho = caminho_recurso(nome)
        if os.path.exists(caminho):
            pix = QPixmap(caminho)
            if not pix.isNull():
                pix = _limpar_logo(pix)
                escalado = pix.scaledToWidth(largura, Qt.SmoothTransformation)
                _LOGO_CACHE[largura] = escalado
                return escalado
    _LOGO_CACHE[largura] = None
    return None


def criar_icone_vetorial(nome: str, size: int = 32, cor: str = "#00A651") -> QPixmap:
    """
    Icones COLORIDOS multi-tom estilo flat design.
    Cada icone tem cores proprias complementares.
    """
    key = f"{nome}_{size}_{cor}"
    if key in _VECTOR_ICON_CACHE:
        return _VECTOR_ICON_CACHE[key]

    pix = QPixmap(size, size)
    pix.fill(QColor(0, 0, 0, 0))
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)

    m = size * 0.12
    s = size - m * 2

    if nome == "home":
        # Casa - telhado azul slate, corpo warm
        # Roof
        roof = QPainterPath()
        roof.moveTo(m, m + s * 0.42)
        roof.lineTo(m + s * 0.5, m + s * 0.05)
        roof.lineTo(m + s, m + s * 0.42)
        roof.closeSubpath()
        p.fillPath(roof, QColor("#3B82F6"))

        # Body
        body = QPainterPath()
        body.addRoundedRect(QRectF(m + s * 0.15, m + s * 0.42, s * 0.7, s * 0.55), 2, 2)
        p.fillPath(body, QColor("#F59E0B"))

        # Door
        door = QPainterPath()
        door.addRoundedRect(QRectF(m + s * 0.37, m + s * 0.58, s * 0.26, s * 0.39), 2, 2)
        p.fillPath(door, QColor("#1E293B"))

    elif nome == "pdf":
        # Documento - corpo branco/cinza, badge vermelho
        doc = QPainterPath()
        doc.addRoundedRect(QRectF(m + s * 0.12, m + s * 0.05, s * 0.55, s * 0.9), s * 0.06, s * 0.06)
        p.fillPath(doc, QColor("#E2E8F0"))

        # Fold corner
        fold = QPainterPath()
        fold.moveTo(m + s * 0.47, m + s * 0.05)
        fold.lineTo(m + s * 0.67, m + s * 0.05)
        fold.lineTo(m + s * 0.67, m + s * 0.22)
        fold.closeSubpath()
        p.fillPath(fold, QColor("#CBD5E1"))

        # Lines
        pen = QPen(QColor("#94A3B8"))
        pen.setWidthF(size * 0.04)
        p.setPen(pen)
        for i in range(3):
            y = m + s * 0.35 + i * s * 0.15
            p.drawLine(QPointF(m + s * 0.22, y), QPointF(m + s * 0.55, y))
        p.setPen(Qt.NoPen)

        # PDF badge
        badge = QPainterPath()
        badge.addRoundedRect(QRectF(m + s * 0.5, m + s * 0.55, s * 0.42, s * 0.3), s * 0.06, s * 0.06)
        p.fillPath(badge, QColor("#EF4444"))

        p.setPen(QColor("white"))
        font = QFont("Segoe UI", max(5, int(s * 0.13)), QFont.Bold)
        p.setFont(font)
        p.drawText(QRectF(m + s * 0.5, m + s * 0.55, s * 0.42, s * 0.3), Qt.AlignCenter, "PDF")
        p.setPen(Qt.NoPen)

    elif nome == "split":
        # Fork/branch - tronco verde, ramos coloridos
        pen = QPen(QColor("#00A651"))
        pen.setWidthF(size * 0.07)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.drawLine(QPointF(m + s * 0.5, m + s * 0.08), QPointF(m + s * 0.5, m + s * 0.42))

        pen2 = QPen(QColor("#3B82F6"))
        pen2.setWidthF(size * 0.06)
        pen2.setCapStyle(Qt.RoundCap)
        p.setPen(pen2)
        p.drawLine(QPointF(m + s * 0.5, m + s * 0.42), QPointF(m + s * 0.15, m + s * 0.72))

        pen3 = QPen(QColor("#F59E0B"))
        pen3.setWidthF(size * 0.06)
        pen3.setCapStyle(Qt.RoundCap)
        p.setPen(pen3)
        p.drawLine(QPointF(m + s * 0.5, m + s * 0.42), QPointF(m + s * 0.85, m + s * 0.72))
        p.setPen(Qt.NoPen)

        # Nodes
        r = s * 0.09
        p.setBrush(QColor("#00A651"))
        p.drawEllipse(QPointF(m + s * 0.5, m + s * 0.08), r, r)
        p.setBrush(QColor("#3B82F6"))
        p.drawEllipse(QPointF(m + s * 0.15, m + s * 0.72), r * 1.1, r * 1.1)
        p.setBrush(QColor("#F59E0B"))
        p.drawEllipse(QPointF(m + s * 0.85, m + s * 0.72), r * 1.1, r * 1.1)

    elif nome == "link":
        # Chain links - azul e verde
        pen1 = QPen(QColor("#3B82F6"))
        pen1.setWidthF(size * 0.08)
        pen1.setCapStyle(Qt.RoundCap)
        p.setPen(pen1)
        path1 = QPainterPath()
        path1.addRoundedRect(QRectF(m + s * 0.02, m + s * 0.2, s * 0.52, s * 0.24), s * 0.12, s * 0.12)
        p.drawPath(path1)

        pen2 = QPen(QColor("#00A651"))
        pen2.setWidthF(size * 0.08)
        pen2.setCapStyle(Qt.RoundCap)
        p.setPen(pen2)
        path2 = QPainterPath()
        path2.addRoundedRect(QRectF(m + s * 0.46, m + s * 0.56, s * 0.52, s * 0.24), s * 0.12, s * 0.12)
        p.drawPath(path2)

        # Connection dots
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#F59E0B"))
        p.drawEllipse(QPointF(m + s * 0.5, m + s * 0.44), s * 0.05, s * 0.05)
        p.drawEllipse(QPointF(m + s * 0.5, m + s * 0.56), s * 0.05, s * 0.05)

    elif nome == "chart":
        # Bar chart - barras coloridas
        bars_data = [
            (0.08, 0.55, "#3B82F6"),
            (0.28, 0.35, "#00A651"),
            (0.48, 0.7,  "#F59E0B"),
            (0.68, 0.45, "#EF4444"),
        ]
        bw = s * 0.17
        for bx, bh_pct, color in bars_data:
            bar_h = s * bh_pct
            x = m + s * bx
            y = m + s - bar_h - s * 0.05
            path = QPainterPath()
            path.addRoundedRect(QRectF(x, y, bw, bar_h), 2.5, 2.5)
            p.fillPath(path, QColor(color))

        # Baseline
        pen = QPen(QColor("#94A3B8"))
        pen.setWidthF(size * 0.04)
        p.setPen(pen)
        p.drawLine(QPointF(m, m + s * 0.95), QPointF(m + s, m + s * 0.95))

    elif nome == "folder":
        # Pasta - corpo amber, aba escura
        tab = QPainterPath()
        tab.addRoundedRect(QRectF(m, m + s * 0.15, s * 0.4, s * 0.15), 3, 3)
        p.fillPath(tab, QColor("#D97706"))

        body = QPainterPath()
        body.addRoundedRect(QRectF(m, m + s * 0.28, s, s * 0.65), 4, 4)
        p.fillPath(body, QColor("#F59E0B"))

        # Shine
        shine = QPainterPath()
        shine.addRoundedRect(QRectF(m + s * 0.05, m + s * 0.32, s * 0.9, s * 0.12), 2, 2)
        p.fillPath(shine, QColor(255, 255, 255, 50))

    elif nome == "search":
        # Lupa - aro azul, cabo amber
        cx, cy = m + s * 0.38, m + s * 0.38
        r = s * 0.26

        pen = QPen(QColor("#3B82F6"))
        pen.setWidthF(size * 0.08)
        p.setPen(pen)
        p.drawEllipse(QPointF(cx, cy), r, r)

        # Glass fill
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(59, 130, 246, 25))
        p.drawEllipse(QPointF(cx, cy), r - 2, r - 2)

        # Handle
        pen2 = QPen(QColor("#F59E0B"))
        pen2.setWidthF(size * 0.09)
        pen2.setCapStyle(Qt.RoundCap)
        p.setPen(pen2)
        p.drawLine(QPointF(cx + r * 0.7, cy + r * 0.7), QPointF(m + s * 0.88, m + s * 0.88))

    p.end()
    _VECTOR_ICON_CACHE[key] = pix
    return pix


def carregar_fontes_app() -> str:
    global _FONT_FAMILY_CACHE
    if _FONT_FAMILY_CACHE is not None:
        return _FONT_FAMILY_CACHE

    arquivos = [
        caminho_recurso("assets", "fonts", "Inter-Regular.ttf"),
        caminho_recurso("assets", "fonts", "Inter-Medium.ttf"),
        caminho_recurso("assets", "fonts", "Inter-SemiBold.ttf"),
        caminho_recurso("assets", "fonts", "Inter-Bold.ttf"),
        caminho_recurso("assets", "fonts", "Poppins-Regular.ttf"),
        caminho_recurso("assets", "fonts", "Poppins-Medium.ttf"),
        caminho_recurso("assets", "fonts", "Poppins-SemiBold.ttf"),
        caminho_recurso("assets", "fonts", "Poppins-Bold.ttf"),
    ]

    familias = []
    for arq in arquivos:
        if os.path.exists(arq):
            font_id = QFontDatabase.addApplicationFont(arq)
            if font_id != -1:
                familias.extend(QFontDatabase.applicationFontFamilies(font_id))

    for preferida in ("Inter", "Poppins"):
        if preferida in familias:
            _FONT_FAMILY_CACHE = preferida
            return _FONT_FAMILY_CACHE

    _FONT_FAMILY_CACHE = familias[0] if familias else "Segoe UI"
    return _FONT_FAMILY_CACHE
