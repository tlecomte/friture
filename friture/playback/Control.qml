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

    function showRecording() {
        record.enabled = false;
        record.down = true;
        stop.enabled = true;
        play.enabled = false;
        play.down = undefined;
    }

    function showStopped() {
        record.enabled = true;
        record.down = undefined;
        stop.enabled = false;
        play.enabled = true;
        play.down = undefined;
    }

    function showPlaying() {
        record.enabled = false;
        record.down = undefined;
        stop.enabled = true;
        play.enabled = false;
        play.down = true;
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
}
