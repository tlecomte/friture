import QtQuick 2.15
import QtQuick.Shapes 1.15
import Friture 1.0

Item {
    id: frequencyTracker

    required property string fmaxValue
    required property string fmaxLogicalValue

    property double posX: fmaxLogicalValue * width
    visible: fmaxLogicalValue >= 0. && fmaxLogicalValue <= 1.
    
    width: column.width
    height: column.height

    Column {
        id: column
        x: frequencyTracker.posX - frequencyTrackerText.contentWidth/2
        spacing: 0

        Rectangle
        {
            id: background
            width: frequencyTrackerText.contentWidth
            height: frequencyTrackerText.contentHeight
            color: "white"

            Text {
                id: frequencyTrackerText
                text: frequencyTracker.fmaxValue
            }
        }

        Shape {
            width: background.width
            height: outline.triangleSize

            ShapePath {
                strokeWidth: 0
                fillColor: "white"

                // draw a small downward-pointing triangle to indicate the frequency
                PathMove { x: background.width / 2 - outline.triangleSize; y: 0 }
                PathLine { x: background.width / 2; y: outline.triangleSize }
                PathLine { x: background.width / 2 + outline.triangleSize; y: 0 }
            }

            ShapePath {
                id: outline
                strokeWidth: 1
                strokeColor: "black"
                fillColor: "white"

                property int triangleSize: 4

                // draw a small downward-pointing triangle to indicate the frequency
                PathMove { x: 0; y: 0 }
                PathLine { x: background.width / 2 - outline.triangleSize; y: 0 }
                PathLine { x: background.width / 2; y: outline.triangleSize }
                PathLine { x: background.width / 2 + outline.triangleSize; y: 0 }
                PathLine { x: background.width; y: 0 }
            }
        }
    }
}