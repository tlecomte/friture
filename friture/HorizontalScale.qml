import QtQuick 2.15
import QtQuick.Window 2.2
import QtQuick.Layouts 1.15
import QtQuick.Shapes 1.15
import Friture 1.0

Item {
    id: xscaleColumn

    height: childrenRect.height

    required property ScaleDivision horizontal_scale_division

    property int majorTickLength: 8
    property int minorTickLength: 4

    Shape {
        anchors.left: parent.left
        anchors.right: parent.right

        ShapePath {
            strokeWidth: 1
            strokeColor: "black"
            fillColor: "transparent"

            PathMove { x: 0; y: 0 }
            PathLine { x: xscaleColumn.width; y: 0 }
        }
    }

    // QML docs discourage the use of multiple Shape objects. But the Repeater cannot be used inside Shape.
    Repeater {
        model: xscaleColumn.horizontal_scale_division.logicalMajorTicks

        Item {
            x: modelData.logicalValue * xscaleColumn.width
            y: 0
            height: childrenRect.height

            Shape {
                ShapePath {
                    strokeWidth: 1
                    strokeColor: "black"
                    fillColor: "transparent"

                    PathMove { x: 0; y: 0 }
                    PathLine { x: 0; y: majorTickLength }
                }
            }

            Text {
                id: tickLabel
                text: modelData.value
                anchors.horizontalCenter: parent.horizontalCenter
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignTop
                y: majorTickLength + 1
                height: contentHeight
            }
        }
    }

    // QML docs discourage the use of multiple Shape objects. But the Repeater cannot be used inside Shape.
    Repeater {
        model: xscaleColumn.horizontal_scale_division.logicalMinorTicks

        Item {
            x: modelData.logicalValue * xscaleColumn.width
            y: 0

            Shape {
                ShapePath {
                    strokeWidth: 1
                    strokeColor: "black"
                    fillColor: "transparent"

                    PathMove { x: 0; y: 0 }
                    PathLine { x: 0; y: minorTickLength }
                }
            }
        }
    }
}