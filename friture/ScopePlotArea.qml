import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Shapes 1.15
import Friture 1.0

Item {
    id: scopePlotArea

    required property Curve curve1
    required property Curve curve2
    required property bool two_channels
    required property Axis vertical_axis
    required property Axis horizontal_axis

    PlotBackground {
        anchors.fill: parent
    }
    
    PlotGrid {
        anchors.fill: parent

        vertical_scale_division: scopePlotArea.vertical_axis.scale_division
        horizontal_scale_division: scopePlotArea.horizontal_axis.scale_division
    }

    PlotCurve {
        anchors.fill: parent
        color: "red"
        curve: curve1
    }

    PlotCurve {
        visible: two_channels
        anchors.fill: parent
        color: "blue"
        curve: curve2
    }

    Rectangle {
        id: plotBorder
        anchors.fill: parent
        border.color: "gray"
        border.width: 1
        color: "transparent"
    }

    Item
    {
        id: crosshair
        visible: plotMouseArea.pressed
        anchors.fill: parent

        property double posX: Math.min(Math.max(plotMouseArea.mouseX, 0), scopePlotArea.width)
        property double posY: Math.min(Math.max(plotMouseArea.mouseY, 0), scopePlotArea.height)
        
        property double relativePosX: posX / scopePlotArea.width
        property double relativePosY: posY / scopePlotArea.height

        Rectangle
        {
            x: Math.min(crosshair.posX + 4, scopePlotArea.width - width)
            y: Math.max(crosshair.posY - mouseText.contentHeight - 4, 0)
            implicitWidth: mouseText.contentWidth
            implicitHeight: mouseText.contentHeight
            color: "white"

            Text {
                id: mouseText

                property double dataX: scopePlotArea.horizontal_axis.coordinate_transform.toPlot(crosshair.relativePosX)
                property double dataY: scopePlotArea.vertical_axis.coordinate_transform.toPlot(1. - crosshair.relativePosY)

                text: scopePlotArea.horizontal_axis.formatTracker(dataX)  + ", " + scopePlotArea.vertical_axis.formatTracker(dataY)
            }
        }

        Shape {
            ShapePath {
                strokeWidth: 1
                strokeColor: "lightgray"
                fillColor: "transparent"
                PathMove { x: crosshair.posX; y: 0 }
                PathLine { x: crosshair.posX; y: scopePlotArea.height }
                PathMove { x: 0; y: crosshair.posY }
                PathLine { x: scopePlotArea.width; y: crosshair.posY }
            }
        }
    }

    MouseArea {
        id: plotMouseArea
        anchors.fill: parent
        cursorShape: Qt.CrossCursor
    }
}
