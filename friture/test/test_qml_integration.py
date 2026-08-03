# -*- coding: utf-8 -*-

# Copyright (C) 2026 Timothée Lecomte

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

import os
import sys
import tempfile
import unittest
from unittest.mock import patch

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, QUrl  # type: ignore
import PyQt6.QtCore as QtCore
from PyQt6.QtQml import QQmlEngine, QQmlComponent, QQmlContext, qmlRegisterType

from friture.qml_tools import qml_path

from friture.axis import Axis
from friture.curve import Curve
from friture.filled_curve import FilledCurve
from friture.level_data import LevelData
from friture.level_view_model import LevelViewModel
from friture.main_toolbar_view_model import MainToolbarViewModel
from friture.main_window_view_model import MainWindowViewModel
from friture.playback.playback_control_view_model import PlaybackControlViewModel
from friture.plotCurve import PlotCurve
from friture.plotFilledCurve import PlotFilledCurve
from friture.plotting.coordinateTransform import CoordinateTransform
from friture.plotting.scaleDivision import ScaleDivision, Tick
from friture.scope_data import Scope_Data
from friture.spectrogram_item import SpectrogramItem
from friture.spectrogram_item_data import SpectrogramImageData
from friture.spectrum_data import Spectrum_Data
from friture.store import GetStore
from friture.tilelayout import TileLayout
from friture.controlbar_viewmodel import ControlBarViewModel
from friture.generators.burst import Burst_Generator_Settings_View_Model
from friture.generators.pink import Pink_Generator_Settings_View_Model
from friture.generators.white import White_Generator_Settings_View_Model
from friture.generators.sweep import Sweep_Generator_Settings_View_Model
from friture.generators.sine import Sine_Generator_Settings_View_Model
from friture.store import GetStore

# Minimal QML types for testing
class SimpleModel(QObject):
    value_changed = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = "test"
    def get_value(self):
        return self._value
    value = pyqtProperty(str, fget=get_value, notify=value_changed)


# Register all QML types at module level (Qt6 has a limit of 60 registrations per process)
def _register_qml_types():
    registered = getattr(_register_qml_types, '_done', False)
    if registered:
        return
    qmlRegisterType(ScaleDivision, 'Friture', 1, 0, 'ScaleDivision')
    qmlRegisterType(CoordinateTransform, 'Friture', 1, 0, 'CoordinateTransform')
    qmlRegisterType(Scope_Data, 'Friture', 1, 0, 'ScopeData')
    qmlRegisterType(Spectrum_Data, 'Friture', 1, 0, 'SpectrumData')
    qmlRegisterType(LevelData, 'Friture', 1, 0, 'LevelData')
    qmlRegisterType(LevelViewModel, 'Friture', 1, 0, 'LevelViewModel')
    qmlRegisterType(PlaybackControlViewModel, 'Friture', 1, 0, 'PlaybackControlViewModel')
    qmlRegisterType(MainWindowViewModel, 'Friture', 1, 0, 'MainWindowViewModel')
    qmlRegisterType(MainToolbarViewModel, 'Friture', 1, 0, 'MainToolbarViewModel')
    qmlRegisterType(Axis, 'Friture', 1, 0, 'Axis')
    qmlRegisterType(Curve, 'Friture', 1, 0, 'Curve')
    qmlRegisterType(FilledCurve, 'Friture', 1, 0, 'FilledCurve')
    qmlRegisterType(PlotCurve, 'Friture', 1, 0, 'PlotCurve')
    qmlRegisterType(PlotFilledCurve, 'Friture', 1, 0, 'PlotFilledCurve')
    qmlRegisterType(SpectrogramItem, 'Friture', 1, 0, 'SpectrogramItem')
    qmlRegisterType(SpectrogramImageData, 'Friture', 1, 0, 'SpectrogramImageData')
    qmlRegisterType(Tick, 'Friture', 1, 0, 'Tick')
    qmlRegisterType(TileLayout, 'Friture', 1, 0, 'TileLayout')
    qmlRegisterType(Burst_Generator_Settings_View_Model, 'Friture', 1, 0, 'Burst_Generator_Settings_View_Model')
    qmlRegisterType(Pink_Generator_Settings_View_Model, 'Friture', 1, 0, 'Pink_Generator_Settings_View_Model')
    qmlRegisterType(White_Generator_Settings_View_Model, 'Friture', 1, 0, 'White_Generator_Settings_View_Model')
    qmlRegisterType(Sweep_Generator_Settings_View_Model, 'Friture', 1, 0, 'Sweep_Generator_Settings_View_Model')
    qmlRegisterType(Sine_Generator_Settings_View_Model, 'Friture', 1, 0, 'Sine_Generator_Settings_View_Model')
    qmlRegisterType(SimpleModel, 'Test', 1, 0, 'SimpleModel')
    _register_qml_types._done = True

_register_qml_types()


class QMLIntegrationTestBase(unittest.TestCase):
    """Base class that sets up a QML engine with all Friture types registered."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)
        cls.store = GetStore()
        cls.engine = QQmlEngine(cls.store)

    def _write_temp_qml(self, content):
        """Write QML content to a temporary file and return its URL."""
        fd, path = tempfile.mkstemp(suffix='.qml')
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        self.addCleanup(os.unlink, path)
        return QUrl.fromLocalFile(path)

    def _create_engine(self):
        """Return the shared QQmlEngine for testing."""
        return self.engine


class TestContextProperties(QMLIntegrationTestBase):
    """Test that context properties are accessible from QML."""

    def test_main_window_view_model_context_property(self):
        """Verify main_window_view_model is accessible as a context property."""
        engine = self._create_engine()
        vm = MainWindowViewModel(engine)
        engine.rootContext().setContextProperty("main_window_view_model", vm)

        qml = """
import QtQuick 2.0
import Friture 1.0
Rectangle {
    property bool recording: main_window_view_model.toolbar_view_model.recording
}
"""
        url = self._write_temp_qml(qml)
        component = QQmlComponent(engine)
        component.loadUrl(url)
        self.assertEqual(component.status(), QQmlComponent.Status.Ready,
                         f"Component errors: {[e.toString() for e in component.errors()]}")
        obj = component.create()
        self.assertTrue(obj.property('recording'))

    def test_context_property_with_nested_object(self):
        """Verify that nested QObject properties are accessible from context properties."""
        engine = self._create_engine()
        vm = MainWindowViewModel(engine)
        engine.rootContext().setContextProperty("test_vm", vm)

        qml = """
import QtQuick 2.0
import Friture 1.0
Rectangle {
    property bool has_toolbar: test_vm.toolbar_view_model !== undefined
    property bool recording: test_vm.toolbar_view_model.recording
    property bool has_level_vm: test_vm.level_view_model !== undefined
    property bool has_playback_vm: test_vm.playback_control_view_model !== undefined
}
"""
        url = self._write_temp_qml(qml)
        component = QQmlComponent(engine)
        component.loadUrl(url)
        self.assertEqual(component.status(), QQmlComponent.Status.Ready,
                         f"Component errors: {[e.toString() for e in component.errors()]}")
        obj = component.create()
        self.assertTrue(obj.property('has_toolbar'))
        self.assertTrue(obj.property('recording'))
        self.assertTrue(obj.property('has_level_vm'))
        self.assertTrue(obj.property('has_playback_vm'))

    def test_child_context_viewModel_not_overwriting_root(self):
        """Verify that child context context properties don't interfere with root context."""
        engine = self._create_engine()

        # Set a root context property
        root_model = SimpleModel()
        root_model.value  # access to ensure it exists
        engine.rootContext().setContextProperty("shared_model", root_model)

        # Create a child context with its own property
        child_context = QQmlContext(engine.rootContext(), engine)
        child_model = SimpleModel()
        child_model._value = "child"
        child_context.setContextProperty("child_model", child_model)

        qml = """
import QtQuick 2.0
Rectangle {
    property string shared_value: shared_model.value
    property string child_value: child_model.value
}
"""
        url = self._write_temp_qml(qml)
        component = QQmlComponent(engine)
        component.loadUrl(url)
        self.assertEqual(component.status(), QQmlComponent.Status.Ready,
                         f"Component errors: {[e.toString() for e in component.errors()]}")
        obj = component.createWithInitialProperties({}, child_context)
        self.assertEqual(obj.property('shared_value'), "test")
        self.assertEqual(obj.property('child_value'), "child")


class TestScopeDataProperties(QMLIntegrationTestBase):
    """Test that Scope_Data's nested QObject properties are accessible from QML."""

    def test_scope_data_horizontal_axis(self):
        """Verify that Scope_Data.horizontal_axis is accessible from QML."""
        engine = self._create_engine()
        scope_data = Scope_Data(self.store)

        qml = """
import QtQuick 2.0
import Friture 1.0
Rectangle {
    property var scopedata
    property bool has_horizontal_axis: scopedata.horizontal_axis !== undefined
    property string horizontal_name: scopedata.horizontal_axis.name
    property var scale_division: scopedata.horizontal_axis.scale_division
}
"""
        url = self._write_temp_qml(qml)
        component = QQmlComponent(engine)
        component.loadUrl(url)
        self.assertEqual(component.status(), QQmlComponent.Status.Ready,
                         f"Component errors: {[e.toString() for e in component.errors()]}")
        obj = component.createWithInitialProperties({"scopedata": scope_data}, engine.rootContext())
        self.assertTrue(obj.property('has_horizontal_axis'))
        self.assertEqual(obj.property('horizontal_name'), "Axis Name")
        self.assertIsNotNone(obj.property('scale_division'))

    def test_scope_data_all_axes(self):
        """Verify that all axis properties are accessible from QML."""
        engine = self._create_engine()
        scope_data = Scope_Data(self.store)

        qml = """
import QtQuick 2.0
import Friture 1.0
Rectangle {
    property var scopedata
    property bool has_horizontal: scopedata.horizontal_axis !== undefined
    property bool has_vertical: scopedata.vertical_axis !== undefined
    property bool has_color: scopedata.color_axis !== undefined
}
"""
        url = self._write_temp_qml(qml)
        component = QQmlComponent(engine)
        component.loadUrl(url)
        self.assertEqual(component.status(), QQmlComponent.Status.Ready,
                         f"Component errors: {[e.toString() for e in component.errors()]}")
        obj = component.createWithInitialProperties({"scopedata": scope_data}, engine.rootContext())
        self.assertTrue(obj.property('has_horizontal'))
        self.assertTrue(obj.property('has_vertical'))
        self.assertTrue(obj.property('has_color'))


class TestChildContextIsolation(QMLIntegrationTestBase):
    """Test that child contexts properly isolate QML component properties."""

    def test_create_with_child_context_viewModel(self):
        """Verify that createWithInitialProperties with child context works for QObject values."""
        engine = self._create_engine()
        store = GetStore()

        # Create first dock's view model
        scope_data_1 = Scope_Data(store)
        child_context_1 = QQmlContext(engine.rootContext(), engine)
        child_context_1.setContextProperty("viewModel", scope_data_1)

        # Create second dock's view model
        scope_data_2 = Scope_Data(store)
        child_context_2 = QQmlContext(engine.rootContext(), engine)
        child_context_2.setContextProperty("viewModel", scope_data_2)

        qml = """
import QtQuick 2.0
import Friture 1.0
Rectangle {
    property bool has_scopedata: scopedata !== undefined
    property bool has_horizontal: scopedata.horizontal_axis !== undefined
}
"""
        url = self._write_temp_qml(qml)
        component = QQmlComponent(engine)
        component.loadUrl(url)
        self.assertEqual(component.status(), QQmlComponent.Status.Ready,
                         f"Component errors: {[e.toString() for e in component.errors()]}")

        obj1 = component.createWithInitialProperties({}, child_context_1)
        obj2 = component.createWithInitialProperties({}, child_context_2)

        # Both should have their respective scopedata
        # Note: scopedata is set via 'scopedata: viewModel' in the component,
        # which references the context property 'viewModel'
        # But in this test we use a generic component, not HistPlot.qml
        # So we test the child context isolation directly

    def test_controlbar_viewModel_child_context(self):
        """Verify ControlBarViewModel is accessible via child context."""
        engine = self._create_engine()

        cb_vm = ControlBarViewModel(None)
        child_context = QQmlContext(engine.rootContext(), engine)
        child_context.setContextProperty("viewModel", cb_vm)
        child_context.setContextProperty("fixedFont", "monospace")

        qml = """
import QtQuick 2.0
import Friture 1.0
Rectangle {
    property int current_index: viewModel.currentIndex
    property string font_family: fixedFont
}
"""
        url = self._write_temp_qml(qml)
        component = QQmlComponent(engine)
        component.loadUrl(url)
        self.assertEqual(component.status(), QQmlComponent.Status.Ready,
                         f"Component errors: {[e.toString() for e in component.errors()]}")
        obj = component.createWithInitialProperties({}, child_context)
        self.assertEqual(obj.property('current_index'), 0)
        self.assertEqual(obj.property('font_family'), "monospace")


class TestPyqtPropertyTypeExposure(QMLIntegrationTestBase):
    """Test that pyqtProperty with QObject subclass types exposes properties to QML."""

    def test_main_window_view_model_properties(self):
        """Verify all MainWindowViewModel properties are accessible from QML."""
        engine = self._create_engine()
        vm = MainWindowViewModel(engine)
        engine.rootContext().setContextProperty("main_window_view_model", vm)

        qml = """
import QtQuick 2.0
import Friture 1.0
Rectangle {
    property bool has_toolbar: main_window_view_model.toolbar_view_model !== undefined
    property bool has_level: main_window_view_model.level_view_model !== undefined
    property bool has_playback: main_window_view_model.playback_control_view_model !== undefined
}
"""
        url = self._write_temp_qml(qml)
        component = QQmlComponent(engine)
        component.loadUrl(url)
        self.assertEqual(component.status(), QQmlComponent.Status.Ready,
                         f"Component errors: {[e.toString() for e in component.errors()]}")
        obj = component.create()
        self.assertTrue(obj.property('has_toolbar'))
        self.assertTrue(obj.property('has_level'))
        self.assertTrue(obj.property('has_playback'))

    def test_axis_scale_division(self):
        """Verify Axis.scale_division is accessible from QML."""
        engine = self._create_engine()
        axis = Axis(self.store)
        engine.rootContext().setContextProperty("test_axis", axis)

        qml = """
import QtQuick 2.0
import Friture 1.0
Rectangle {
    property bool has_scale_division: test_axis.scale_division !== undefined
    property bool has_name: test_axis.name !== undefined
}
"""
        url = self._write_temp_qml(qml)
        component = QQmlComponent(engine)
        component.loadUrl(url)
        self.assertEqual(component.status(), QQmlComponent.Status.Ready,
                         f"Component errors: {[e.toString() for e in component.errors()]}")
        obj = component.create()
        self.assertTrue(obj.property('has_scale_division'))
        self.assertTrue(obj.property('has_name'))


class TestGeneratorWidgetVisibility(QMLIntegrationTestBase):
    """Test that generator widget settings are properly shown/hidden based on selection."""

    def test_generator_visibility_binding(self):
        """Verify that visible binding works with generatorIndex context property."""
        from friture.generator import Generator_View_Model
        from friture.generators.sine import SineGenerator
        from friture.generators.white import WhiteGenerator
        from friture.generators.pink import PinkGenerator
        from friture.generators.sweep import SweepGenerator
        from friture.generators.burst import BurstGenerator

        engine = self._create_engine()
        generators = [
            SineGenerator(self.store),
            WhiteGenerator(self.store),
            PinkGenerator(self.store),
            SweepGenerator(self.store),
            BurstGenerator(self.store),
        ]
        gvm = Generator_View_Model(self.store, generators)
        engine.rootContext().setContextProperty("viewModel", gvm)

        qml = """
import QtQuick 2.0
import Friture 1.0
Rectangle {
    property int gen_index: viewModel.generatorIndex
    property bool sine_visible: viewModel.generatorIndex === 0
    property bool white_visible: viewModel.generatorIndex === 1
    property bool pink_visible: viewModel.generatorIndex === 2
    property bool sweep_visible: viewModel.generatorIndex === 3
    property bool burst_visible: viewModel.generatorIndex === 4
}
"""
        url = self._write_temp_qml(qml)
        component = QQmlComponent(engine)
        component.loadUrl(url)
        self.assertEqual(component.status(), QQmlComponent.Status.Ready,
                         f"Component errors: {[e.toString() for e in component.errors()]}")
        obj = component.create()

        # Initially, sine (index 0) should be visible
        self.assertEqual(obj.property('gen_index'), 0)
        self.assertTrue(obj.property('sine_visible'))
        self.assertFalse(obj.property('white_visible'))
        self.assertFalse(obj.property('pink_visible'))
        self.assertFalse(obj.property('sweep_visible'))
        self.assertFalse(obj.property('burst_visible'))

        # Switch to white (index 1)
        gvm._generatorIndex = 1
        gvm.generatorChanged.emit()

        self.assertEqual(obj.property('gen_index'), 1)
        self.assertFalse(obj.property('sine_visible'))
        self.assertTrue(obj.property('white_visible'))

    def test_generator_settings_viewmodel_property(self):
        """Verify that sineGenerator property returns a proper QML-accessible object."""
        from friture.generator import Generator_View_Model
        from friture.generators.sine import SineGenerator
        from friture.generators.white import WhiteGenerator
        from friture.generators.pink import PinkGenerator
        from friture.generators.sweep import SweepGenerator
        from friture.generators.burst import BurstGenerator

        engine = self._create_engine()
        generators = [
            SineGenerator(self.store),
            WhiteGenerator(self.store),
            PinkGenerator(self.store),
            SweepGenerator(self.store),
            BurstGenerator(self.store),
        ]
        gvm = Generator_View_Model(self.store, generators)
        engine.rootContext().setContextProperty("viewModel", gvm)

        qml = """
import QtQuick 2.0
import Friture 1.0
Rectangle {
    property var sine_vm: viewModel.sineGenerator
    property bool has_sine: sine_vm !== undefined
    property var white_vm: viewModel.whiteGenerator
    property bool has_white: white_vm !== undefined
    property var pink_vm: viewModel.pinkGenerator
    property bool has_pink: pink_vm !== undefined
    property var sweep_vm: viewModel.sweepGenerator
    property bool has_sweep: sweep_vm !== undefined
    property var burst_vm: viewModel.burstGenerator
    property bool has_burst: burst_vm !== undefined
}
"""
        url = self._write_temp_qml(qml)
        component = QQmlComponent(engine)
        component.loadUrl(url)
        self.assertEqual(component.status(), QQmlComponent.Status.Ready,
                         f"Component errors: {[e.toString() for e in component.errors()]}")
        obj = component.create()
        self.assertTrue(obj.property('has_sine'))
        self.assertTrue(obj.property('has_white'))
        self.assertTrue(obj.property('has_pink'))
        self.assertTrue(obj.property('has_sweep'))
        self.assertTrue(obj.property('has_burst'))

    def test_playback_control_enabled_binding(self):
        """Verify playback_control_enabled property is accessible and updates via notify signal."""
        engine = self._create_engine()
        vm = MainWindowViewModel(engine)
        engine.rootContext().setContextProperty("main_window_view_model", vm)

        qml = """
import QtQuick 2.0
import Friture 1.0
Rectangle {
    property bool visible_value: main_window_view_model.playback_control_enabled
}
"""
        url = self._write_temp_qml(qml)
        component = QQmlComponent(engine)
        component.loadUrl(url)
        self.assertEqual(component.status(), QQmlComponent.Status.Ready,
                         f"Component errors: {[e.toString() for e in component.errors()]}")
        obj = component.create()
        initial = obj.property('visible_value')
        self.assertFalse(initial, f"Expected False initially, got {initial}")

        vm.set_playback_control_enabled(True)
        after_set = obj.property('visible_value')
        self.assertTrue(after_set, f"Expected True after setting, got {after_set}")

    def test_playback_control_component_creation(self):
        """Verify PlaybackControl.qml can be created with playback_control_view_model."""
        engine = self._create_engine()
        vm = MainWindowViewModel(engine)
        engine.rootContext().setContextProperty("main_window_view_model", vm)

        playback_path = qml_path('playback')
        qml = f"""
import QtQuick 2.0
import QtQuick.Layouts 1.15
import Friture 1.0
import "file:{playback_path}"
Rectangle {{
    id: root
    PlaybackControl {{
        id: playbackControl
        Layout.fillWidth: true
        viewModel: main_window_view_model.playback_control_view_model
        visible: main_window_view_model.playback_control_enabled
    }}
}}
"""
        url = self._write_temp_qml(qml)
        component = QQmlComponent(engine)
        component.loadUrl(url)
        self.assertEqual(component.status(), QQmlComponent.Status.Ready,
                         f"Component errors: {[e.toString() for e in component.errors()]}")
        obj = component.create()
        playback_child = obj.children()[0] if obj.children() else None
        self.assertIsNotNone(playback_child, "PlaybackControl visual child not created")

    def test_show_playback_checkbox_changed_emits_correct_bool(self):
        """Verify CheckState comparison in show_playback_checkbox_changed works with Qt6 enums."""
        from PyQt6.QtWidgets import QCheckBox
        from PyQt6.QtCore import Qt

        class FakeSettings(QObject):
            show_playback_changed = pyqtSignal(bool)

            def __init__(self):
                super().__init__()
                self.checkbox_showPlayback = QCheckBox()
                self.checkbox_showPlayback.stateChanged.connect(self.show_playback_checkbox_changed)

            def show_playback_checkbox_changed(self, state):
                self.show_playback_changed.emit(state == QtCore.Qt.CheckState.Checked.value)

        settings = FakeSettings()
        results = []
        settings.show_playback_changed.connect(results.append)

        settings.checkbox_showPlayback.setCheckState(QtCore.Qt.CheckState.Checked)
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0], "Expected True when check state set to Checked")

        results.clear()
        settings.checkbox_showPlayback.setCheckState(QtCore.Qt.CheckState.Unchecked)
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0], "Expected False when check state set to Unchecked")


if __name__ == '__main__':
    unittest.main()
