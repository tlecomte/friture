import QtQuick 2.9
import QtQuick.Window 2.2
import QtQuick.Layouts 1.15
import Friture 1.0

Rectangle {
    id: pitch
    SystemPalette { id: systemPalette; colorGroup: SystemPalette.Active }
    color: systemPalette.window

    implicitWidth: pitchCol.implicitWidth
    implicitHeight: parent ? parent.height : 0

    property var pitch_view_model

    ColumnLayout {
        id: pitchCol
        spacing: 0

        FontMetrics {
            id: fontMetrics
            font.pointSize: 14
            font.bold: true
        }

        Text {
            id: note
            text: pitch_view_model.note
            textFormat: Text.PlainText
            font.pointSize: 14
            font.bold: true
            rightPadding: 6
            horizontalAlignment: Text.AlignRight
            Layout.alignment: Qt.AlignTop | Qt.AlignRight
            color: systemPalette.windowText
        }

        Text {
            id: pitchHz
            text: pitch_view_model.pitch
            textFormat: Text.PlainText
            font.pointSize: 14
            font.bold: true
            rightPadding: 6
            horizontalAlignment: Text.AlignRight
            Layout.preferredWidth: fontMetrics.boundingRect("000.0").width
            Layout.alignment: Qt.AlignTop | Qt.AlignRight
            color: systemPalette.windowText
        }

        Text {
            id: pitchUnit
            text: pitch_view_model.pitch_unit
            textFormat: Text.PlainText
            rightPadding: 6
            horizontalAlignment: Text.AlignRight
            Layout.alignment: Qt.AlignTop | Qt.AlignRight
            color: systemPalette.windowText
        }
    }
}
