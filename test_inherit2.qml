import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Control {
    width: 400; height: 300
    
    // Set palette on the root item
    palette.window: isDark ? "#353535" : "#f0f0f0"
    palette.windowText: isDark ? "#ffffff" : "#1a1a1a"
    palette.base: isDark ? "#191919" : "#ffffff"
    palette.text: isDark ? "#ffffff" : "#1a1a1a"
    palette.button: isDark ? "#353535" : "#f0f0f0"
    palette.buttonText: isDark ? "#ffffff" : "#1a1a1a"

    property bool isDark: true

    contentItem: ColumnLayout {
        anchors.fill: parent
        
        ToolBar {
            Layout.fillWidth: true
            RowLayout {
                ToolButton { text: "Button" }
                ComboBox { model: ["Item 1", "Item 2"] }
            }
        }
        
        Rectangle {
            Layout.fillWidth: true; Layout.fillHeight: true
            color: palette.window
            Text { text: "Content"; color: palette.windowText; anchors.centerIn: parent }
        }
        
        Button {
            text: "Toggle Theme"
            onClicked: parent.isDark = !parent.isDark
        }
    }
}
