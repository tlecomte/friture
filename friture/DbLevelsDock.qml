import QtQuick 2.15
import QtQuick.Layouts 1.15
import Friture 1.0

Rectangle {
    id: root
    anchors.fill: parent
    SystemPalette { id: systemPalette; colorGroup: SystemPalette.Active }
    color: systemPalette.window

    required property var viewModel
    required property string fixedFont

    readonly property int captionSize: Math.max(11, Math.round(Math.min(width, height) / 22))
    readonly property int valuePixelSize: Math.max(
        32, Math.min(Math.floor(Math.min(width, height) / 3.5), 200))

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Math.max(10, Math.min(width, height) * 0.04)
        spacing: Math.max(6, height * 0.02)

        Text {
            text: "PEAK · " + viewModel.unit_label + viewModel.weighting_suffix
            font.family: fixedFont
            font.pixelSize: captionSize
            font.capitalization: Font.AllUppercase
            color: systemPalette.windowText
            opacity: 0.85
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
        }

        Text {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 48
            font.pixelSize: valuePixelSize
            font.bold: true
            font.family: fixedFont
            color: systemPalette.windowText
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            text: peakText()
        }

        Text {
            text: "RMS · " + viewModel.unit_label + viewModel.weighting_suffix
            font.family: fixedFont
            font.pixelSize: captionSize
            font.capitalization: Font.AllUppercase
            color: systemPalette.windowText
            opacity: 0.85
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
        }

        Text {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 48
            font.pixelSize: valuePixelSize
            font.bold: true
            font.family: fixedFont
            color: systemPalette.windowText
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            text: rmsText()
        }
    }

    function peakText() {
        if (viewModel.two_channels) {
            return level_to_text(viewModel.level_data_slow.level_max)
                + "  ·  "
                + level_to_text(viewModel.level_data_slow_2.level_max);
        }
        return level_to_text(viewModel.level_data_slow.level_max);
    }

    function rmsText() {
        if (viewModel.two_channels) {
            return level_to_text(viewModel.level_data_slow.level_rms)
                + "  ·  "
                + level_to_text(viewModel.level_data_slow_2.level_rms);
        }
        return level_to_text(viewModel.level_data_slow.level_rms);
    }

    function level_to_text(dB) {
        if (dB < -150.) {
            return "-Inf";
        }
        return dB.toFixed(1);
    }
}
