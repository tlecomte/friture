import QtQuick 2.9
import QtQuick.Window 2.2
import QtQuick.Layouts 1.15

Rectangle {
    SystemPalette { id: myPalette; colorGroup: SystemPalette.Active }
    color: myPalette.window
    width: levelLayout.width
    height: levelLayout.height

    function level_to_text(dB) {
        if (dB < -150.) {
            return "-Inf";
        }

        return dB.toFixed(1);
    }

    Column {
        id: levelLayout
        spacing: 6
        width: peakValues.width

        Text {
            id: peakValues
            text: level_settings.two_channels ? "1: " + level_to_text(level_data_slow.level_max) + "\n2: " + level_to_text(level_data_slow_2.level_max) : level_to_text(level_data_slow.level_max)
            font.pointSize: 14
            font.bold: true
            verticalAlignment: Text.AlignBottom
            horizontalAlignment: Text.AlignRight
            anchors.right: parent.right
        }

        Text {
            id: peakLegend
            text: "dB FS\nPeak"
            verticalAlignment: Text.AlignTop
            horizontalAlignment: Text.AlignRight
            anchors.right: parent.right
        }

        Text {
            id: rmsValues
            text: level_settings.two_channels ? "1: " + level_to_text(level_data_slow.level_rms) + "\n2: " + level_to_text(level_data_slow_2.level_rms) : level_to_text(level_data_slow.level_rms)
            font.pointSize: 14
            font.bold: true
            verticalAlignment: Text.AlignBottom
            horizontalAlignment: Text.AlignRight
            anchors.right: parent.right
        }

        Text {
            id: rmsLegend
            text: "dB FS\nRMS"
            verticalAlignment: Text.AlignTop
            horizontalAlignment: Text.AlignRight
            anchors.right: parent.right
        }
    }
}