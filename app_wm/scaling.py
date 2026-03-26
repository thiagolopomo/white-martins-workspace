#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sistema de escala responsiva.
Calcula um fator de escala baseado no tamanho real da tela disponível.
Todas as páginas usam esse fator pra ajustar fonts, paddings, ícones.
"""

from PySide6.QtWidgets import QApplication


def get_scale_factor() -> float:
    """
    Retorna fator de escala (1.0 = referência em 1080p 100%).
    Em 150%: ~0.67, em 200%: ~0.50.
    """
    screen = QApplication.primaryScreen()
    if not screen:
        return 1.0
    geom = screen.availableGeometry()
    # Referência: 1080px de altura lógica
    factor = geom.height() / 1080.0
    # Limitar entre 0.45 e 1.2
    return max(0.45, min(1.2, factor))


def scaled(value: int, factor: float = None) -> int:
    """Escala um valor inteiro pelo fator."""
    if factor is None:
        factor = get_scale_factor()
    return max(1, int(value * factor))


def scaled_font(base_size: int, factor: float = None) -> int:
    """Escala tamanho de fonte. Mínimo 7px."""
    if factor is None:
        factor = get_scale_factor()
    return max(7, int(base_size * factor))
