import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.2
import Friture 1.0

Rectangle { // eventually move to ApplicationWindow
    id: mainWindow
    anchors.fill: parent
    // title: qsTr("Friture") // ApplicationWindow
    // icon.source: "qrc:/images-src/window-icon.svg" // ApplicationWindow

    required property MainWindowViewModel main_window_view_model
    required property string fixedFont

    ColumnLayout { // remove once we use ApplicationWindow
        anchors.fill: parent
        spacing: 0

        ToolBar {
            id: toolBar
            Layout.fillWidth: true // remove once we use ApplicationWindow

            RowLayout {
                spacing: 0

                ToolButton {
                    id: startButton
                    checkable: true
                    checked: mainWindow.main_window_view_model.toolbar_view_model.recording
                    icon.source: startButton.checked ? "qrc:/images-src/stop.svg" : "qrc:/images-src/start.svg"
                    icon.color: undefined
                    text: startButton.checked ? qsTr("Stop") : qsTr("Start")
                    ToolTip.text: qsTr("Start/Stop")
                    icon.height: 32
                    icon.width: 32
                    //shortcut: "Space"
                    onClicked: {
                        mainWindow.main_window_view_model.toolbar_view_model.recording_toggle()
                    }
                }
                ToolButton {
                    id: newDockButton
                    icon.source: "qrc:/images-src/new-dock.svg"
                    icon.color: undefined
                    text: qsTr("New dock")
                    ToolTip.text: qsTr("Add a new dock to Friture window")
                    icon.height: 32
                    icon.width: 32
                    onClicked: {
                        mainWindow.main_window_view_model.toolbar_view_model.new_dock()
                    }
                }
                ToolButton {
                    id: settingsButton
                    icon.source: "qrc:/images-src/tools.svg"
                    icon.color: undefined
                    text: qsTr("Settings")
                    ToolTip.text: qsTr("Display settings dialog")
                    icon.height: 32
                    icon.width: 32
                    onClicked: {
                        mainWindow.main_window_view_model.toolbar_view_model.settings()
                    }
                }
                ToolButton {
                    id: aboutButton
                    icon.source: "qrc:/images-src/window-icon.svg"
                    icon.color: undefined
                    text: qsTr("About Friture")
                    icon.height: 32
                    icon.width: 32
                    onClicked: {
                        mainWindow.main_window_view_model.toolbar_view_model.about()
                    }
                }
            }
        }

        MainWindow {
            id: centralWidget
            Layout.fillWidth: true
            Layout.fillHeight: true
            fixedFont: mainWindow.fixedFont
            main_window_view_model: mainWindow.main_window_view_model
        }
    }
}
