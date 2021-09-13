import QtQuick 2.15
import QtQuick.Window 2.2
import QtQuick.Layouts 1.15
import QtQuick.Shapes 1.15
import Friture 1.0

Item {
    id: xscaleColumn

    implicitHeight: childrenRect.height

    required property ScaleDivision scale_division

    property int majorTickLength: 8
    property int minorTickLength: 4

    property double rightOverflow: getRightOverflow(scale_division.logicalMajorTicks, xscaleColumn.width)

    function getRightOverflow(majorTicks, totalWidth) {
        if (majorTicks.length == 0) {
            return 0.
        }

        var lastMajorTick = majorTicks[majorTicks.length - 1]
        var textWidth = fontMetrics.boundingRect(lastMajorTick.value).width;
        var tickPos = lastMajorTick.logicalValue * totalWidth
        var rightPos = tickPos + textWidth / 2
        var rightOverflow = Math.max(0., rightPos - totalWidth)
        return rightOverflow
    }

    FontMetrics {
        id: fontMetrics
    }

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
        model: xscaleColumn.scale_division.logicalMajorTicks

        Item {
            x: modelData.logicalValue * xscaleColumn.width
            y: 0
            implicitHeight: childrenRect.height

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
            }
        }
    }

    // QML docs discourage the use of multiple Shape objects. But the Repeater cannot be used inside Shape.
    Repeater {
        model: xscaleColumn.scale_division.logicalMinorTicks

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