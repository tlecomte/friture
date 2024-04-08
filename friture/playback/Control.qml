import QtQuick 2.9
import QtQuick.Controls 1.4
import QtQuick.Window 2.2
import QtQuick.Layouts 1.15
import Friture 1.0

RowLayout {
    id: controlRow

    signal paused()

    Button {
        text: "Pause"
        onClicked: controlRow.paused()
    }
}
