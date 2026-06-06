import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.2
import Friture 1.0

Rectangle {
    required property MainWindowViewModel main_window_view_model

    color: main_window_view_model.window_color

    property string fixedFont

    ColumnLayout {
        id: root
        anchors.fill: parent

        Item {
            id: control_bar_container
            objectName: "control_bar_container"
            Layout.fillWidth: true
            Layout.preferredHeight: 40
        }

        Item {
            id: audio_widget_container
            objectName: "audio_widget_container"
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: 5
        }
    }
}
