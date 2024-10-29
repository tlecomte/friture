import QtQuick 2.15
import QtQuick.Shapes 1.15
import Friture 1.0
import "plotItemColors.js" as PlotItemColors

Item {
    SystemPalette { id: systemPalette; colorGroup: SystemPalette.Active }

    required property ScopeData scopedata

    implicitWidth: childrenRect.width
    
    Column {
        padding: 4
        spacing: 4

        Repeater {
            model: scopedata.plot_items

            Row {
                spacing: 4
                Shape {
                    implicitWidth: 20
                    implicitHeight: 1
                    anchors.verticalCenter: curve1legend.verticalCenter
                    ShapePath {
                        strokeWidth: 1
                        strokeColor: PlotItemColors.color(index)
                        fillColor: "transparent"
                        PathLine { x: 20; y: 0 }
                    }
                }
                Text {
                    id: curve1legend
                    text: modelData.name
                    color: systemPalette.windowText
                }
            }
        }
    }
}