import QtQuick 2.9
import QtQuick.Controls 1.4
import QtQuick.Window 2.2
import QtQuick.Layouts 1.15
import Friture 1.0

RowLayout {
    id: controlRow

    signal paused()
    signal played()

    Button {
        text: "Pause"
        onClicked: controlRow.paused()
    }

    Button {
        text: "Play"
        onClicked: controlRow.played()
    }
}
