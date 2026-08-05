import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.2
import Friture 1.0

// eventually move from Control to ApplicationWindow.
// Meanwhile, needs to be Control rather than Item or Rectangle
// so that it has a `palette` property
Control {
    id: mainWindow
    anchors.fill: parent
    // title: qsTr("Friture") // ApplicationWindow
    // icon.source: "qrc:/images-src/window-icon.svg" // ApplicationWindow

    SystemPalette { id: systemPalette; colorGroup: SystemPalette.Active }

    // apply the palette changes from the system palette (controlled from ThemeManager)
    // to the whole QtQuick application
    palette.window: systemPalette.window
    palette.windowText: systemPalette.windowText
    palette.base: systemPalette.base
    palette.alternateBase: systemPalette.alternateBase
    palette.text: systemPalette.text
    palette.button: systemPalette.button
    palette.buttonText: systemPalette.buttonText
    palette.light: systemPalette.light
    palette.midlight: systemPalette.midlight
    palette.mid: systemPalette.mid
    palette.dark: systemPalette.dark
    palette.shadow: systemPalette.shadow
    palette.highlight: systemPalette.highlight
    palette.highlightedText: systemPalette.highlightedText
    palette.toolTipBase: systemPalette.toolTipBase
    palette.toolTipText: systemPalette.toolTipText

    property string fixedFont

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
                    checked: main_window_view_model.toolbar_view_model.recording
                    icon.source: startButton.checked ? "qrc:/images-src/stop.svg" : "qrc:/images-src/start.svg"
                    text: startButton.checked ? qsTr("Stop") : qsTr("Start")
                    ToolTip.text: qsTr("Start/Stop")
                    icon.height: 32
                    icon.width: 32
                    Shortcut {
                        context: Qt.ApplicationShortcut
                        sequences: ["Space"]
                        onActivated: startButton.clicked()
                    }
                    onClicked: {
                        main_window_view_model.toolbar_view_model.recording_toggle()
                    }
                }
                ToolButton {
                    id: newDockButton
                    icon.source: "qrc:/images-src/new-dock.svg"
                    text: qsTr("New dock")
                    ToolTip.text: qsTr("Add a new dock to Friture window")
                    icon.height: 32
                    icon.width: 32
                    onClicked: {
                        main_window_view_model.toolbar_view_model.new_dock()
                    }
                }
                ToolButton {
                    id: settingsButton
                    icon.source: "qrc:/images-src/tools.svg"
                    text: qsTr("Settings")
                    ToolTip.text: qsTr("Display settings dialog")
                    icon.height: 32
                    icon.width: 32
                    onClicked: {
                        main_window_view_model.toolbar_view_model.settings()
                    }
                }
                ToolButton {
                    id: aboutButton
                    icon.source: "qrc:/images-src/window-icon.svg"
                    text: qsTr("About Friture")
                    icon.height: 32
                    icon.width: 32
                    onClicked: {
                        main_window_view_model.toolbar_view_model.about()
                    }
                }
            }
        }

        MainWindow {
            id: centralWidget
            Layout.fillWidth: true
            Layout.fillHeight: true
            fixedFont: mainWindow.fixedFont
        }
    }
}
