import QtQuick 2.15
import QtQuick.Shapes 1.15
import Friture 1.0

Item {
    required property Curve curve1
    required property Curve curve2

    width: childrenRect.width
    
    Column {
        padding: 4
        spacing: 4
        Row {
            spacing: 4
            Shape {
                width: 20
                height: 1
                anchors.verticalCenter: curve1legend.verticalCenter
                ShapePath {
                    strokeWidth: 1
                    strokeColor: "red"
                    fillColor: "transparent"
                    PathLine { x: 20; y: 0 }
                }
            }
            Text {
                id: curve1legend
                text: curve1.name
                width: contentWidth
                height: contentHeight
            }
        }
        
        Row {
            spacing: 4
            Shape {
                width: 20
                height: 1
                anchors.verticalCenter: curve2legend.verticalCenter
                ShapePath {
                    strokeWidth: 1
                    strokeColor: "blue"
                    fillColor: "transparent"
                    PathLine { x: 20; y: 0 }
                }
            }
            Text {    
                id: curve2legend
                text: curve2.name
                width: contentWidth
                height: contentHeight
            }
        }
    }
}