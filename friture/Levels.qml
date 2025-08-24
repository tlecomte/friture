import QtQuick 2.9
import QtQuick.Window 2.2
import QtQuick.Layouts 1.15
import Friture 1.0

Rectangle {
    id: levels
    SystemPalette { id: systemPalette; colorGroup: SystemPalette.Active }
    color: systemPalette.window

    property var stateId
    property LevelViewModel level_view_model: Store.dock_states[stateId]

    property string fixedFont

    // parent here will be unset on exit
    height: parent ? parent.height : 0

    // make width dependent on the text labels
    // but do not bind directly to their widths
    // to avoid frequent costly resizes
    //due to level changes or variations in the width of the font characters
    implicitWidth: 4 + fontMetrics.boundingRect(level_view_model.two_channels ? "2: -88.8" : "-88:8").width

    FontMetrics {
        id: fontMetrics
        font.pointSize: 14
        font.bold: true
        font.family: fixedFont
    }

    ColumnLayout {
        id: levelColumnLayout
        spacing: 6

        anchors.fill: parent

        Text {
            id: peakValues
            textFormat: Text.StyledText
            text: level_view_model.two_channels ? "1: " + level_to_text(level_view_model.level_data_slow.level_max) + "<br />2: " + level_to_text(level_view_model.level_data_slow_2.level_max) : level_to_text(level_view_model.level_data_slow.level_max)
            font.pointSize: 14
            font.bold: true
            font.family: fixedFont
            verticalAlignment: Text.AlignBottom
            horizontalAlignment: Text.AlignRight
            Layout.alignment: Qt.AlignBottom | Qt.AlignRight
            color: systemPalette.windowText
        }

        Text {
            id: peakLegend
            textFormat: Text.PlainText
            text: "dB FS\nPeak"
            verticalAlignment: Text.AlignTop
            horizontalAlignment: Text.AlignRight
            Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
            color: systemPalette.windowText
        }

        Text {
            id: rmsValues
            textFormat: Text.StyledText
            text: level_view_model.two_channels ? "1: " + level_to_text(level_view_model.level_data_slow.level_rms) + "<br />2: " + level_to_text(level_view_model.level_data_slow_2.level_rms) : level_to_text(level_view_model.level_data_slow.level_rms)
            font.pointSize: 14
            font.bold: true
            font.family: fixedFont
            verticalAlignment: Text.AlignBottom
            horizontalAlignment: Text.AlignRight
            Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
            color: systemPalette.windowText
        }

        Text {
            id: rmsLegend
            textFormat: Text.PlainText
            text: "dB FS\nRMS"
            verticalAlignment: Text.AlignTop
            horizontalAlignment: Text.AlignRight
            Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
            color: systemPalette.windowText
        }
		
		Text {
            id: splValues
            textFormat: Text.MarkdownText
            text: level_view_model.two_channels ? "1: " + level_to_text(level_view_model.level_data_slow.level_spl) + "<br />2: " + level_to_text(level_view_model.level_data_slow_2.level_spl) : level_to_text(level_view_model.level_data_slow.level_spl)
            font.pointSize: 14
            font.bold: true
            verticalAlignment: Text.AlignBottom
            horizontalAlignment: Text.AlignRight
            Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
            color: systemPalette.windowText
        }

        Text {
            id: splLegend
            textFormat: Text.PlainText
            text: "dB SPL"
            verticalAlignment: Text.AlignTop
            horizontalAlignment: Text.AlignRight
            Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
            color: systemPalette.windowText
        }

        LevelsMeter {
            Layout.fillHeight: true
            Layout.fillWidth: true
            level_view_model: levels.level_view_model
        }
    }

    function level_to_text(dB) {
        if (dB < -150.) {
            return "`-Inf`";
        }

        return dB.toFixed(1);
    }
}