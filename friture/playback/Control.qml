import QtQuick 2.9
import QtQuick.Controls 2.15
import QtQuick.Window 2.2
import QtQuick.Layouts 1.15
import Friture 1.0

RowLayout {
    id: controlRow

    signal recordClicked()
    signal stopClicked()
    signal playClicked()
    signal positionChanged(real value)

    function showRecording() {
        record.enabled = false;
        record.down = true;
        stop.enabled = true;
        play.enabled = false;
        play.down = undefined;
        position.enabled = true;
    }

    function showStopped() {
        record.enabled = true;
        record.down = undefined;
        stop.enabled = false;
        play.enabled = true;
        play.down = undefined;
        position.enabled = true;
    }

    function showPlaying() {
        record.enabled = false;
        record.down = undefined;
        stop.enabled = true;
        play.enabled = false;
        play.down = true;
        position.enabled = false;
    }

    function setRecordingStartTime(time) {
        startTime.text = time.toFixed(1);
        position.from = time;
    }

    function setPlaybackPosition(time) {
        position.value = time;
        selectedTime.text = time.toFixed(1);
    }

    Button {
        id: record
        text: "Record"
        down: true
        enabled: false
        onClicked: {
            controlRow.showRecording();
            controlRow.recordClicked();
        }
    }

    Button {
        id: stop
        text: "Stop"
        onClicked: {
            controlRow.showStopped();
            controlRow.stopClicked();
        }
    }

    Button {
        id: play
        text: "Play"
        onClicked: {
            controlRow.showPlaying();
            controlRow.playClicked();
        }
    }

    FontMetrics {
        id: fontMetrics
    }

    Text {
        id: startTime
        text: "-5.0"
        // fixed width so the slider position doesn't change with this value
        width: fontMetrics.boundingRect("-000.0").width
        horizontalAlignment: Text.AlignRight
    }

    Slider {
        id: position
        from: -5.0
        to: 0.0
        value: 0.0
        stepSize: 0.1

        Layout.fillWidth: true

        onMoved: {
            selectedTime.text = position.value.toFixed(1);
            controlRow.positionChanged(position.value);
        }
    }

    Text {
        id: selectedTime
        text: "0.0"
        // fixed width so the slider position doesn't change with this value
        width: fontMetrics.boundingRect("-000.0").width
        horizontalAlignment: Text.AlignLeft
    }
}
