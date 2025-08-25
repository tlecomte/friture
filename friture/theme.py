#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timothée Lecomte

# This file is part of Friture.
#
# Friture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Friture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Friture.  If not, see <http://www.gnu.org/licenses/>.

import logging
from PyQt5 import QtWidgets, QtGui, QtCore


class ThemeManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.app = QtWidgets.QApplication.instance()

    def apply_theme(self, theme_name):
        """Apply the selected theme to the application"""
        self.logger.info(f"Applying theme: {theme_name}")
        
        if theme_name == "Dark":
            self._apply_dark_theme()
        elif theme_name == "Light":
            self._apply_light_theme()
        else:  # System Default
            self._apply_system_theme()

    def _apply_dark_theme(self):
        """Apply dark theme"""
        dark_palette = QtGui.QPalette()
        
        # Window colors
        dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(255, 255, 255))
        
        # Base colors (for text input fields)
        dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
        dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
        
        # Text colors
        dark_palette.setColor(QtGui.QPalette.Text, QtGui.QColor(255, 255, 255))
        
        # Button colors
        dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(255, 255, 255))
        
        # Highlight colors
        dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
        dark_palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(0, 0, 0))
        
        # Disabled colors
        dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, QtGui.QColor(127, 127, 127))
        dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtGui.QColor(127, 127, 127))
        dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, QtGui.QColor(127, 127, 127))
        
        self.app.setPalette(dark_palette)
        
        # Set style sheet for better dark theme appearance
        dark_style = """
            QToolTip {
                color: #ffffff;
                background-color: #2a2a2a;
                border: 1px solid white;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
                color: #ffffff;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ffffff;
            }
            
            QLabel {
                color: #ffffff;
            }
            
            /* Form controls styling for dark theme */
            QComboBox {
                background-color: #353535;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
            }
            
            QComboBox:editable {
                background-color: #191919;
            }
            
            QComboBox:on {
                padding-top: 3px;
                padding-left: 4px;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: #555555;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
                background-color: #353535;
            }
            
            QComboBox::down-arrow {
                width: 0;
                height: 0;
                border: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-left: 2px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #353535;
                color: #ffffff;
                border: 1px solid #555555;
                selection-background-color: #2a82da;
            }
            
            QSpinBox, QDoubleSpinBox {
                background-color: #191919;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
            }
            
            QSpinBox::up-button, QDoubleSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 16px;
                background-color: #353535;
                border-left: 1px solid #555555;
            }
            
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 16px;
                background-color: #353535;
                border-left: 1px solid #555555;
            }
            
            QCheckBox {
                color: #ffffff;
                spacing: 5px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                background-color: #191919;
                border: 1px solid #555555;
                border-radius: 3px;
            }
            
            QCheckBox::indicator:checked {
                background-color: #2a82da;
                border-color: #2a82da;
            }
            
            QCheckBox::indicator:checked:hover {
                background-color: #3a92ea;
            }
            
            QRadioButton {
                color: #ffffff;
                spacing: 5px;
            }
            
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                background-color: #191919;
                border: 1px solid #555555;
                border-radius: 9px;
            }
            
            QRadioButton::indicator:checked {
                background-color: #2a82da;
                border-color: #2a82da;
            }
            
            /* Tab widget styling */
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #353535;
            }
            
            QTabBar::tab {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #555555;
                border-bottom-color: #555555;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 8ex;
                padding: 8px;
            }
            
            QTabBar::tab:selected {
                background-color: #353535;
                border-bottom-color: #353535;
            }
            
            QTabBar::tab:hover {
                background-color: #404040;
            }
            
            /* Dialog buttons styling */
            QPushButton {
                background-color: #353535;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: #404040;
            }
            
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
        """
        self.app.setStyleSheet(dark_style)

    def _apply_light_theme(self):
        """Apply light theme"""
        light_palette = QtGui.QPalette()
        
        # Window colors
        light_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(240, 240, 240))
        light_palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(0, 0, 0))
        
        # Base colors (for text input fields)
        light_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(255, 255, 255))
        light_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(233, 231, 227))
        
        # Text colors
        light_palette.setColor(QtGui.QPalette.Text, QtGui.QColor(0, 0, 0))
        
        # Button colors
        light_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(240, 240, 240))
        light_palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(0, 0, 0))
        
        # Highlight colors
        light_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(76, 163, 224))
        light_palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))
        
        # Disabled colors
        light_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, QtGui.QColor(120, 120, 120))
        light_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtGui.QColor(120, 120, 120))
        light_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, QtGui.QColor(120, 120, 120))
        
        self.app.setPalette(light_palette)
        
        # Clear any custom stylesheet
        self.app.setStyleSheet("")

    def _apply_system_theme(self):
        """Apply system default theme"""
        # Reset to system default palette
        self.app.setPalette(self.app.style().standardPalette())
        # Clear any custom stylesheet
        self.app.setStyleSheet("")


# Global theme manager instance
_theme_manager = None


def get_theme_manager():
    """Get the global theme manager instance"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager


def apply_theme(theme_name):
    """Convenience function to apply a theme"""
    get_theme_manager().apply_theme(theme_name)
