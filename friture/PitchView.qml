import QtQuick 2.15
import QtQuick.Window 2.2
import QtQuick.Layouts 1.15
import QtQuick.Shapes 1.15
import Friture 1.0
import "plotItemColors.js" as PlotItemColors

Item {
    id: container
    property var stateId

    // delay the load of the Plot until stateId has been set
    Loader {
        id: loader
        anchors.fill: parent
    }

    onStateIdChanged: {
        console.log("stateId changed: " + stateId)
        loader.sourceComponent = plotComponent
    }

    Component {
        id: plotComponent

        Item {
            Plot {
                id: plot
                scopedata: Store.dock_states[container.stateId]

                anchors.fill: null // override 'fill: parent' in Plot.qml
                anchors.left: parent.left
                anchors.right: pitchItem.left                
                anchors.top: parent.top
                anchors.bottom: parent.bottom

                Repeater {
                    model: plot.scopedata.plot_items

                    PlotCurve {
                        anchors.fill: parent
                        color: PlotItemColors.color(index)
                        curve: modelData
                    }
                }
            }

            Rectangle {
                id: pitchItem

                implicitWidth: pitchCol.implicitWidth
                implicitHeight: parent ? parent.height : 0

                anchors.right: parent.right

                SystemPalette { id: systemPalette; colorGroup: SystemPalette.Active }
                color: systemPalette.window

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
                        text: plot.scopedata.note
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
                        text: plot.scopedata.pitch
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
                        text: plot.scopedata.pitch_unit
                        textFormat: Text.PlainText
                        rightPadding: 6
                        horizontalAlignment: Text.AlignRight
                        Layout.alignment: Qt.AlignTop | Qt.AlignRight
                        color: systemPalette.windowText
                    }
                }
            }
        }
    }
}
