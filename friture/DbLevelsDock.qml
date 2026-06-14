import QtQuick 2.15
import QtQuick.Controls 2.15
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
    readonly property int monoValuePixelSize: Math.max(
        32, Math.min(Math.floor(Math.min(width, height) / 3.5), 200))
    readonly property int stereoValuePixelSize: fitValuePixelSize(stereoSampleText())

    readonly property real layoutMargin: Math.max(10, Math.min(width, height) * 0.04)
    readonly property real layoutSpacing: Math.max(6, height * 0.02)

    FontMetrics {
        id: valueFontMetrics
        font.family: fixedFont
        font.bold: true
    }

    function stereoSampleText() {
        return level_to_text(viewModel.level_data_slow.level_max)
            + level_to_text(viewModel.level_data_slow_2.level_max);
    }

    function fitValuePixelSize(sampleText) {
        var margin = layoutMargin;
        var columnWidth = Math.max(40, (width - 2 * margin) / 3);
        var size = Math.max(24, Math.min(Math.floor(Math.min(width, height) / 5.5), 120));
        valueFontMetrics.font.pixelSize = size;
        while (size > 20 && valueFontMetrics.advanceWidth(sampleText) > columnWidth * 0.9) {
            size -= 2;
            valueFontMetrics.font.pixelSize = size;
        }
        return size;
    }

    function level_to_text(dB) {
        if (dB < -150.) {
            return "-Inf";
        }
        return dB.toFixed(1);
    }

    function peakCaption() {
        return "PEAK · " + viewModel.unit_label + viewModel.weighting_suffix;
    }

    function rmsCaption() {
        return "RMS · " + viewModel.unit_label + viewModel.weighting_suffix;
    }

    // Single input: large centered readout
    ColumnLayout {
        visible: !viewModel.two_channels
        anchors.fill: parent
        anchors.margins: layoutMargin
        spacing: layoutSpacing

        Text {
            text: peakCaption()
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
            font.pixelSize: monoValuePixelSize
            font.bold: true
            font.family: fixedFont
            color: systemPalette.windowText
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            text: level_to_text(viewModel.level_data_slow.level_max)
        }

        Text {
            text: rmsCaption()
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
            font.pixelSize: monoValuePixelSize
            font.bold: true
            font.family: fixedFont
            color: systemPalette.windowText
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            text: level_to_text(viewModel.level_data_slow.level_rms)
        }
    }

    // Two inputs: one column per channel, captions in the middle
    GridLayout {
        visible: viewModel.two_channels
        anchors.fill: parent
        anchors.margins: layoutMargin
        columns: 3
        rowSpacing: layoutSpacing
        columnSpacing: 4

        Text {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 48
            font.pixelSize: stereoValuePixelSize
            font.bold: true
            font.family: fixedFont
            color: systemPalette.windowText
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            text: level_to_text(viewModel.level_data_slow.level_max)
        }

        Text {
            text: peakCaption()
            font.family: fixedFont
            font.pixelSize: captionSize
            font.capitalization: Font.AllUppercase
            color: systemPalette.windowText
            opacity: 0.85
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        Text {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 48
            font.pixelSize: stereoValuePixelSize
            font.bold: true
            font.family: fixedFont
            color: systemPalette.windowText
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            text: level_to_text(viewModel.level_data_slow_2.level_max)
        }

        Text {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 48
            font.pixelSize: stereoValuePixelSize
            font.bold: true
            font.family: fixedFont
            color: systemPalette.windowText
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            text: level_to_text(viewModel.level_data_slow.level_rms)
        }

        Text {
            text: rmsCaption()
            font.family: fixedFont
            font.pixelSize: captionSize
            font.capitalization: Font.AllUppercase
            color: systemPalette.windowText
            opacity: 0.85
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        Text {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 48
            font.pixelSize: stereoValuePixelSize
            font.bold: true
            font.family: fixedFont
            color: systemPalette.windowText
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            text: level_to_text(viewModel.level_data_slow_2.level_rms)
        }
    }

    // Calibrate button — top-right corner overlay
    ToolButton {
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 4
        text: "CAL"
        font.pixelSize: 10
        opacity: 0.6
        ToolTip.text: "Calibrate global input level"
        ToolTip.visible: hovered
        onClicked: viewModel.calibrate_requested()
    }
}
