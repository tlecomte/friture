#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets


def create_form_layout(dialog: QtWidgets.QDialog) -> QtWidgets.QFormLayout:
    form_layout = QtWidgets.QFormLayout()
    main_layout = QtWidgets.QVBoxLayout(dialog)
    main_layout.addLayout(form_layout)
    button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close, dialog)
    main_layout.addWidget(button_box)
    button_box.rejected.connect(dialog.close)
    return form_layout
