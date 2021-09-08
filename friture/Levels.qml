import QtQuick 2.9
import QtQuick.Window 2.2
import QtQuick.Layouts 1.15
import Friture 1.0

Rectangle {
    id: levels
    SystemPalette { id: myPalette; colorGroup: SystemPalette.Active }
    color: myPalette.window

    property var stateId
    property LevelViewModel level_view_model: Store.dock_states[stateId]  

    width: peakValues.width
    anchors.top: parent.top
    anchors.bottom: parent.bottom

    ColumnLayout {
        id: levelColumnLayout
        spacing: 6

        anchors.top: parent.top
        anchors.bottom: parent.bottom

        width: levelLayout.width

        Text {
            id: peakValues
            text: level_view_model.two_channels ? "1: " + level_to_text(level_view_model.level_data_slow.level_max) + "\n2: " + level_to_text(level_view_model.level_data_slow_2.level_max) : level_to_text(level_view_model.level_data_slow.level_max)
            font.pointSize: 14
            font.bold: true
            verticalAlignment: Text.AlignBottom
            horizontalAlignment: Text.AlignRight
            Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
            Layout.bottomMargin: 6
            height: contentHeight
        }

        Text {
            id: peakLegend
            text: "dB FS\nPeak"
            verticalAlignment: Text.AlignTop
            horizontalAlignment: Text.AlignRight
            Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
            height: contentHeight
        }

        Text {
            id: rmsValues
            text: level_view_model.two_channels ? "1: " + level_to_text(level_view_model.level_data_slow.level_rms) + "\n2: " + level_to_text(level_view_model.level_data_slow_2.level_rms) : level_to_text(level_view_model.level_data_slow.level_rms)
            font.pointSize: 14
            font.bold: true
            verticalAlignment: Text.AlignBottom
            horizontalAlignment: Text.AlignRight
            Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
            height: contentHeight
        }

        Text {
            id: rmsLegend
            text: "dB FS\nRMS"
            verticalAlignment: Text.AlignTop
            horizontalAlignment: Text.AlignRight
            Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
            height: contentHeight
        }

        LevelsMeter {
            Layout.fillHeight: true
            Layout.fillWidth: true
            level_view_model: levels.level_view_model
        }
    }

    function level_to_text(dB) {
        if (dB < -150.) {
            return "-Inf";
        }

        return dB.toFixed(1);
    }
}