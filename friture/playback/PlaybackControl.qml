import QtQuick 2.9
import QtQuick.Controls 2.15
import QtQuick.Window 2.2
import QtQuick.Layouts 1.15
import Friture 1.0

RowLayout {
    id: controlRow

    required property PlaybackControlViewModel viewModel

    SystemPalette { id: systemPalette; colorGroup: SystemPalette.Active }

    Button {
        id: record
        text: "Record"
        down: controlRow.viewModel.recording === true ? true : undefined
        enabled: controlRow.viewModel.playing === false && controlRow.viewModel.recording === false
        onClicked: {
            controlRow.viewModel.recording = true;
        }
    }

    Button {
        id: stop
        text: "Stop"
        down:  controlRow.viewModel.playing === false && controlRow.viewModel.recording === false ? true : undefined
        enabled: controlRow.viewModel.playing === true || controlRow.viewModel.recording === true
        onClicked: {
            controlRow.viewModel.playing = false;
            controlRow.viewModel.recording = false;
        }
    }

    Button {
        id: play
        text: "Play"
        down: controlRow.viewModel.playing === true ? true : undefined
        enabled: controlRow.viewModel.recording === false
        onClicked: {
            controlRow.viewModel.playing = true;
        }
    }

    FontMetrics {
        id: fontMetrics
    }

    Text {
        id: startTime
        text: controlRow.viewModel.recording_start_time.toFixed(1)
        color: systemPalette.text
        // fixed width so the slider position doesn't change with this value
        Layout.preferredWidth: fontMetrics.boundingRect("-000.0").width
        horizontalAlignment: Text.AlignRight
    }

    Slider {
        id: position
        from: controlRow.viewModel.recording_start_time
        to: 0.0
        value: controlRow.viewModel.position
        stepSize: 0.1

        enabled: controlRow.viewModel.playing === false

        Layout.fillWidth: true

        onMoved: {
            controlRow.viewModel.position = position.value;
        }
    }

    Text {
        id: selectedTime
        text: controlRow.viewModel.position.toFixed(1)
        color: systemPalette.text
        // fixed width so the slider position doesn't change with this value
        Layout.preferredWidth: fontMetrics.boundingRect("-000.0").width
        horizontalAlignment: Text.AlignLeft
    }
}
