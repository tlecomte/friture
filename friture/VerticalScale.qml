import QtQuick 2.15
import QtQuick.Window 2.2
import QtQuick.Layouts 1.15
import QtQuick.Shapes 1.15
import Friture 1.0

Item {
    id: yscaleColumn

    required property ScaleDivision vertical_scale_division

    width: tickLabelMaxWidth + 1 + majorTickLength

    property int majorTickLength: 8
    property int minorTickLength: 4

    property int tickLabelMaxWidth: maxTextWidth(vertical_scale_division.logicalMajorTicks)

    function maxTextWidth(majorTicks) {
        var maxWidth = 0
        for (var i = 0; i < majorTicks.length; i++) {
            var textWidth = fontMetrics.boundingRect(majorTicks[i].value.toFixed(1)).width;
            if (textWidth > maxWidth) {
                maxWidth = textWidth;
            }
        }
        return Math.ceil(maxWidth)
    }

    FontMetrics {
        id: fontMetrics
    }

    Shape {
        anchors.right: yscaleColumn.right

        ShapePath {
            strokeWidth: 1
            strokeColor: "black"
            fillColor: "transparent"

            PathMove { x: 0; y: 0 }
            PathLine { x: 0; y: yscaleColumn.height }
        }
    }

    // QML docs discourage the use of multiple Shape objects. But the Repeater cannot be used inside Shape.
    Repeater {
        model: vertical_scale_division.logicalMajorTicks

        Item {
            anchors.right: yscaleColumn.right
            width: 1 + majorTickLength

            y: (1. - modelData.logicalValue) * yscaleColumn.height

            Shape {
                anchors.right: parent.right

                ShapePath {
                    strokeWidth: 1
                    strokeColor: "black"
                    fillColor: "transparent"

                    PathMove { x: 0; y: 0 }
                    PathLine { x: -majorTickLength; y: 0 }
                }
            }
        }
    }

    Item {
        id: tickLabels

        // QML docs discourage the use of multiple Shape objects. But the Repeater cannot be used inside Shape.
        Repeater {
            model: vertical_scale_division.logicalMajorTicks

            Item {
                width: tickLabelMaxWidth
                y: (1. - modelData.logicalValue) * yscaleColumn.height

                Text {
                    id: tickLabel
                    text: modelData.value.toFixed(1)
                    anchors.verticalCenter: parent.verticalCenter
                    verticalAlignment: Text.AlignVCenter

                    width: tickLabelMaxWidth
                    horizontalAlignment: Text.AlignRight
                }
            }
        }
    }

    // QML docs discourage the use of multiple Shape objects. But the Repeater cannot be used inside Shape.
    Repeater {
        model: vertical_scale_division.logicalMinorTicks

        Item {
            y: (1. - modelData.logicalValue) * yscaleColumn.height
            anchors.right: parent.right
        
            Shape {
                anchors.right: parent.right

                ShapePath {
                    strokeWidth: 1
                    strokeColor: "black"
                    fillColor: "transparent"

                    PathMove { x: 0; y: 0 }
                    PathLine { x: -minorTickLength; y: 0 }
                }
            }
        }
    }
}