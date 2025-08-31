import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.2
import Friture 1.0
import "./playback"

Rectangle {
    id: main_window
    SystemPalette { id: systemPalette; colorGroup: SystemPalette.Active }
    color: systemPalette.window
    anchors.fill: parent

    required property MainWindowViewModel main_window_view_model
    required property string fixedFont

    GridLayout {
        objectName: "main_row_layout"
        anchors.fill: parent
        rows: main_window.main_window_view_model.playback_control_enabled ? 2 : 1
        columns: 2
        rowSpacing: 3
        columnSpacing: 3

        Levels {
            level_view_model: main_window.main_window_view_model.level_view_model
            Layout.row: 0
            Layout.rowSpan: main_window.main_window_view_model.playback_control_enabled ? 2 : 1
            Layout.column: 0
            Layout.fillHeight: true
            Layout.margins: 5
            fixedFont: main_window.fixedFont
        }

        TileLayout {
            id: tileLayout
            objectName: "main_tile_layout"
            Layout.row: 0
            Layout.column: 1
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: 5
        }

        PlaybackControl {
            id: playbackControl
            Layout.row: 1
            Layout.column: 1
            Layout.fillWidth: true
            Layout.margins: 5

            viewModel: main_window.main_window_view_model.playback_control_view_model

            visible: main_window.main_window_view_model.playback_control_enabled
        }
    }
}