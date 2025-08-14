import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root
    required property var viewModel
    required property string fixedFont

    SystemPalette { id: systemPalette; colorGroup: SystemPalette.Active }
    color: systemPalette.window
    anchors.fill: parent

    Column {
        spacing: 8
        anchors.fill: parent
        anchors.margins: 12

        Row {
            spacing: 8
            Label {
                text: qsTr("Delay:")
                font.pointSize: 14
                color: systemPalette.windowText
            }
            Label {
                text: viewModel.delay
                font.pointSize: 14
                font.bold: true
                color: systemPalette.windowText
            }
        }
        Row {
            spacing: 8
            Label {
                text: qsTr("Confidence:")
                color: systemPalette.windowText
            }
            Label {
                id: correlationLabel
                text: viewModel.correlation
                color: systemPalette.windowText
            }
        }
        Row {
            spacing: 8
            Label {
                text: qsTr("Polarity:")
                color: systemPalette.windowText
            }
            Label {
                text: viewModel.polarity
                font.pointSize: 14
                font.bold: true
                color: systemPalette.windowText
            }
        }
        Label {
            text: viewModel.channel_info
            wrapMode: Text.WordWrap
            color: systemPalette.windowText
        }
    }
}
