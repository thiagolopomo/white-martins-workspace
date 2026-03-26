#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Theme White Martins - SLATE + GREEN + AMBER.
Nao e mais Palmeiras. Visual corporativo premium.
"""


def build_app_qss(font_family: str = "Segoe UI") -> str:
    return f"""

/* ============================================
   GLOBAL
   ============================================ */
* {{
    font-family: "{font_family}", "Segoe UI", sans-serif;
    font-size: 13px;
    outline: none;
}}

/* ============================================
   SHELL - Fundo slate suave
   ============================================ */
#ShellRoot {{
    background: #F3F4F6;
}}

#ContentWrap {{
    background: transparent;
}}

#MainStack {{
    background: transparent;
}}

/* ============================================
   TOP BAR - Dark slate (nao verde!)
   ============================================ */
#TopBar {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0F172A, stop:0.4 #1E293B, stop:1 #334155);
    border: none;
}}

#TopBarBrand {{
    color: white;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 2px;
}}

#LogoPill {{
    background: rgba(255,255,255,0.95);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 10px;
}}

#TopBarSep {{
    background: rgba(255,255,255,0.12);
}}

#TopBarTagMain {{
    color: rgba(255,255,255,0.85);
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 0.5px;
}}

#TopBarTagSub {{
    color: rgba(255,255,255,0.35);
    font-size: 10px;
    font-weight: 400;
    letter-spacing: 0.3px;
}}

/* Status */
#StatusDot {{
    background: #00E070;
    border-radius: 4px;
    border: 1px solid rgba(0, 224, 112, 0.35);
}}

#StatusText {{
    color: rgba(255,255,255,0.50);
    font-size: 10px;
    font-weight: 500;
}}

/* Session pill */
#SessionPill {{
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
}}

#SessionAvatar {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #F59E0B, stop:1 #D97706);
    color: white;
    font-size: 11px;
    font-weight: 700;
    border-radius: 13px;
}}

#SessionUser {{
    color: rgba(255,255,255,0.85);
    font-size: 11px;
    font-weight: 500;
}}

#SessionMachine {{
    color: rgba(255,255,255,0.40);
    font-size: 9px;
}}

/* ============================================
   WORKSPACE BAR (Nav unificada com hero)
   ============================================ */
#WorkspaceBar {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0F172A, stop:0.4 #1E293B, stop:1 #334155);
    border: none;
}}

#WBarEyebrow {{
    color: #F59E0B;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 2px;
}}

#WBarDesc {{
    color: rgba(255,255,255,0.45);
    font-size: 11px;
    font-weight: 400;
}}

#ModernNavBtn {{
    background: rgba(255,255,255,0.05);
    color: rgba(255,255,255,0.55);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 8px 18px;
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.2px;
    min-height: 36px;
}}

#ModernNavBtn:hover {{
    background: rgba(255,255,255,0.10);
    color: rgba(255,255,255,0.85);
    border: 1px solid rgba(255,255,255,0.15);
}}

#ModernNavBtn:checked {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(0, 166, 81, 0.40), stop:1 rgba(0, 166, 81, 0.25));
    color: #FFFFFF;
    border: 1px solid rgba(0, 204, 102, 0.50);
    font-weight: 700;
}}

#NavBtnTitle {{
    color: rgba(255,255,255,0.55);
    font-size: 12px;
    font-weight: 600;
}}

#ModernNavBtn:hover #NavBtnTitle {{
    color: rgba(255,255,255,0.85);
}}

#ModernNavBtn:checked #NavBtnTitle {{
    color: #FFFFFF;
    font-weight: 700;
}}

#NavBtnSub {{
    color: rgba(255,255,255,0.30);
    font-size: 9px;
    font-weight: 400;
    padding-left: 22px;
}}

#ModernNavBtn:checked #NavBtnSub {{
    color: rgba(255,255,255,0.65);
}}

/* Version badge */
#VersionBadge {{
    background: rgba(245, 158, 11, 0.08);
    color: #D97706;
    border: 1px solid rgba(245, 158, 11, 0.15);
    border-radius: 10px;
    padding: 4px 12px;
    font-size: 10px;
    font-weight: 600;
}}

/* ============================================
   FOOTER
   ============================================ */
#FooterBar {{
    background: rgba(255,255,255,0.80);
    border-top: 1px solid rgba(30,41,59,0.05);
}}

#FooterText {{
    color: #94A3B8;
    font-size: 10px;
}}

/* ============================================
   DASHBOARD HERO - Dark slate gradient
   ============================================ */
#WorkspaceHero {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0F172A, stop:0.4 #1E293B, stop:0.8 #334155, stop:1 #475569);
    border: none;
    border-radius: 16px;
}}

#HeroTitle {{
    color: white;
    font-size: 22px;
    font-weight: 500;
    letter-spacing: 0.3px;
}}

#HeroText {{
    color: rgba(255,255,255,0.60);
    font-size: 13px;
}}

#SectionEyebrow {{
    color: #F59E0B;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
}}

#WorkspaceHero #SectionEyebrow {{
    color: #F59E0B;
}}

#SectionDivider {{
    color: rgba(255,255,255,0.08);
    max-height: 1px;
}}

/* ============================================
   STAT CARDS
   ============================================ */
#StatCard {{
    background: rgba(255,255,255,0.95);
    border: 1px solid rgba(30,41,59,0.06);
    border-radius: 12px;
}}

#StatCard[hover="true"] {{
    border: 1px solid rgba(59, 130, 246, 0.20);
}}

#StatAccentLine {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3B82F6, stop:0.5 #00A651, stop:1 rgba(0,166,81,0.10));
    border-radius: 1px;
}}

#StatIcon {{
    color: #3B82F6;
    font-size: 14px;
    font-weight: 700;
}}

#StatLabel {{
    color: #94A3B8;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.8px;
}}

#StatValue {{
    color: #0F172A;
    font-size: 18px;
    font-weight: 700;
}}

#StatSub {{
    color: #94A3B8;
    font-size: 10px;
    font-weight: 400;
}}

/* ============================================
   MODULE CARDS
   ============================================ */
#WorkspaceModuleCard {{
    background: rgba(255,255,255,0.95);
    border: 1px solid rgba(30,41,59,0.06);
    border-radius: 14px;
}}

#WorkspaceModuleCard[hover="true"] {{
    border: 1px solid rgba(59, 130, 246, 0.18);
}}

#ModuleIcon {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #1E293B, stop:1 #334155);
    border-radius: 10px;
}}

#ModuleIconText {{
    color: white;
    font-size: 13px;
    font-weight: 700;
}}

#ModuleTitle {{
    color: #0F172A;
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 0.1px;
}}

#ModuleDesc {{
    color: #64748B;
    font-size: 12px;
    font-weight: 400;
    line-height: 1.5;
}}

#ModuleBullet {{
    color: #475569;
    font-size: 12px;
    font-weight: 400;
}}

/* ============================================
   WORKFLOW BAND
   ============================================ */
#WorkspaceBand {{
    background: rgba(255,255,255,0.95);
    border: 1px solid rgba(30,41,59,0.06);
    border-radius: 14px;
}}

/* ============================================
   PAGE HERO - Slate gradient
   ============================================ */
#PageHeroCard {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0F172A, stop:0.5 #1E293B, stop:1 #334155);
    border: none;
    border-radius: 14px;
}}

#PageHeroCard #SectionEyebrow {{
    color: #F59E0B;
}}

#HeroIconFrame {{
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
}}

#HeroIconText {{
    color: white;
    font-size: 15px;
    font-weight: 700;
}}

#PageHeroCard #FieldTitle {{
    color: white;
    font-size: 15px;
    font-weight: 500;
    letter-spacing: 0.2px;
}}

#PageHeroCard #FieldText {{
    color: rgba(255,255,255,0.65);
    font-size: 12px;
}}

/* ============================================
   PREMIUM CARDS
   ============================================ */
#PremiumPathCard, #PremiumExecCard, #PremiumLogCard, #PremiumSummaryCard {{
    background: rgba(255,255,255,0.95);
    border: 1px solid rgba(30,41,59,0.06);
    border-radius: 14px;
}}

#PremiumPathCard[hover="true"],
#PremiumExecCard[hover="true"],
#PremiumLogCard[hover="true"],
#PremiumSummaryCard[hover="true"] {{
    border: 1px solid rgba(59, 130, 246, 0.18);
}}

#CardAccentLine {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3B82F6, stop:0.3 #00A651, stop:0.7 #F59E0B, stop:1 rgba(245,158,11,0.10));
    border-radius: 1px;
}}

/* ============================================
   TYPOGRAPHY
   ============================================ */
#FieldTitle {{
    color: #0F172A;
    font-size: 13px;
    font-weight: 500;
    letter-spacing: 0.1px;
}}

#FieldText {{
    color: #64748B;
    font-size: 12px;
    font-weight: 400;
    line-height: 1.5;
}}

/* ============================================
   INPUTS
   ============================================ */
#PathInput, QLineEdit {{
    background: #F8FAFC;
    color: #0F172A;
    border: 1px solid rgba(30,41,59,0.10);
    border-radius: 10px;
    padding: 9px 14px;
    font-size: 12px;
    selection-background-color: #BFDBFE;
}}

#PathInput:focus, QLineEdit:focus {{
    border: 1.5px solid #3B82F6;
    background: white;
}}

QTextEdit {{
    background: #F8FAFC;
    color: #0F172A;
    border: 1px solid rgba(30,41,59,0.10);
    border-radius: 10px;
    padding: 10px;
    font-size: 12px;
    font-family: "Cascadia Code", "Consolas", monospace;
    selection-background-color: #BFDBFE;
}}

QTextEdit:focus {{
    border: 1.5px solid #3B82F6;
    background: white;
}}

QComboBox {{
    background: #F8FAFC;
    color: #0F172A;
    border: 1px solid rgba(30,41,59,0.10);
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 12px;
    min-height: 32px;
}}

QComboBox:hover {{
    border: 1px solid rgba(59, 130, 246, 0.30);
}}

QComboBox:focus {{
    border: 1.5px solid #3B82F6;
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 28px;
    border: none;
}}

QComboBox QAbstractItemView {{
    background: white;
    color: #0F172A;
    border: 1px solid rgba(30,41,59,0.10);
    border-radius: 10px;
    selection-background-color: rgba(59, 130, 246, 0.08);
    selection-color: #1E293B;
    padding: 4px;
}}

QCheckBox {{
    color: #0F172A;
    font-size: 12px;
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1.5px solid rgba(30,41,59,0.20);
    background: white;
}}

QCheckBox::indicator:checked {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #3B82F6, stop:1 #2563EB);
    border-color: #3B82F6;
}}

/* ============================================
   BUTTONS
   ============================================ */
#PrimaryButton, QPushButton[objectName="PrimaryButton"] {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #00CC66, stop:0.5 #00B85A, stop:1 #00A651);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 24px;
    font-size: 13px;
    font-weight: 600;
}}

#PrimaryButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #00E070, stop:1 #00CC66);
}}

#PrimaryButton:pressed {{
    background: #007A3D;
}}

#PrimaryButton:disabled {{
    background: #CBD5E1;
    color: rgba(255,255,255,0.5);
}}

#SecondaryButton {{
    background: rgba(30, 41, 59, 0.04);
    color: #334155;
    border: 1px solid rgba(30, 41, 59, 0.12);
    border-radius: 10px;
    padding: 8px 18px;
    font-size: 12px;
    font-weight: 500;
}}

#SecondaryButton:hover {{
    background: rgba(30, 41, 59, 0.08);
    border-color: rgba(30, 41, 59, 0.18);
}}

#GhostButton {{
    background: transparent;
    color: #3B82F6;
    border: none;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 500;
}}

#GhostButton:hover {{
    background: rgba(59, 130, 246, 0.06);
    border-radius: 10px;
}}

/* ============================================
   PROGRESS BAR - Multi-color gradient
   ============================================ */
QProgressBar {{
    background: rgba(30,41,59,0.06);
    border: none;
    border-radius: 7px;
    text-align: center;
    color: #1E293B;
    font-size: 11px;
    font-weight: 600;
    min-height: 14px;
    max-height: 14px;
}}

QProgressBar::chunk {{
    border-radius: 7px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3B82F6, stop:0.4 #00A651, stop:0.7 #00CC66, stop:1 #F59E0B);
}}

/* ============================================
   TABS
   ============================================ */
QTabWidget::pane {{
    background: rgba(255,255,255,0.95);
    border: 1px solid rgba(30,41,59,0.06);
    border-radius: 0 0 12px 12px;
    border-top: 2px solid #3B82F6;
}}

QTabBar::tab {{
    background: rgba(30,41,59,0.03);
    color: #64748B;
    border: 1px solid rgba(30,41,59,0.06);
    border-bottom: none;
    border-radius: 10px 10px 0 0;
    padding: 9px 20px;
    font-size: 12px;
    font-weight: 500;
    margin-right: 2px;
}}

QTabBar::tab:selected {{
    background: rgba(255,255,255,0.95);
    color: #1E293B;
    font-weight: 600;
}}

QTabBar::tab:hover:!selected {{
    background: rgba(59, 130, 246, 0.04);
}}

/* ============================================
   SCROLLBARS
   ============================================ */
QScrollArea {{
    background: transparent;
    border: none;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 4px 0;
    border-radius: 3px;
}}

QScrollBar::handle:vertical {{
    background: rgba(30, 41, 59, 0.10);
    border-radius: 3px;
    min-height: 36px;
}}

QScrollBar::handle:vertical:hover {{
    background: rgba(30, 41, 59, 0.22);
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
    margin: 0 4px;
    border-radius: 3px;
}}

QScrollBar::handle:horizontal {{
    background: rgba(30, 41, 59, 0.10);
    border-radius: 3px;
    min-width: 36px;
}}

QScrollBar::handle:horizontal:hover {{
    background: rgba(30, 41, 59, 0.22);
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ============================================
   TOOLTIPS
   ============================================ */
QToolTip {{
    background: #0F172A;
    color: rgba(255,255,255,0.90);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 11px;
}}

"""
