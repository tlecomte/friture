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

    anchors.top: parent.top
    anchors.bottom: parent.bottom

    // make width dependent on the text labels
    // but do not bind directly to their widths
    // to avoid frequent costly resizes
    //due to level changes or variations in the width of the font characters
    implicitWidth: 2 + fontMetrics.boundingRect(level_view_model.two_channels ? "2: -88.8" : "-88:8").width

    FontMetrics {
        id: fontMetrics
        font.pointSize: 14
        font.bold: true
    }

    ColumnLayout {
        id: levelColumnLayout
        spacing: 6

        anchors.top: parent.top
        anchors.bottom: parent.bottom

        Text {
            id: peakValues
            textFormat: Text.PlainText
            text: level_view_model.two_channels ? "1: " + level_to_text(level_view_model.level_data_slow.level_max) + "\n2: " + level_to_text(level_view_model.level_data_slow_2.level_max) : level_to_text(level_view_model.level_data_slow.level_max)
            font.pointSize: 14
            font.bold: true
            verticalAlignment: Text.AlignBottom
            horizontalAlignment: Text.AlignRight
            Layout.alignment: Qt.AlignBottom | Qt.AlignRight
        }

        Text {
            id: peakLegend
            textFormat: Text.PlainText
            text: "dB FS\nPeak"
            verticalAlignment: Text.AlignTop
            horizontalAlignment: Text.AlignRight
            Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
        }

        Text {
            id: rmsValues
            textFormat: Text.PlainText
            text: level_view_model.two_channels ? "1: " + level_to_text(level_view_model.level_data_slow.level_rms) + "\n2: " + level_to_text(level_view_model.level_data_slow_2.level_rms) : level_to_text(level_view_model.level_data_slow.level_rms)
            font.pointSize: 14
            font.bold: true
            verticalAlignment: Text.AlignBottom
            horizontalAlignment: Text.AlignRight
            Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
        }

        Text {
            id: rmsLegend
            textFormat: Text.PlainText
            text: "dB FS\nRMS"
            verticalAlignment: Text.AlignTop
            horizontalAlignment: Text.AlignRight
            Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
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