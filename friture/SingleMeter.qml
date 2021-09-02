import QtQuick 2.9
import QtQuick.Layouts 1.15
import QtQuick.Shapes 1.15
import "iec.js" as IECFunctions

Rectangle {
    color: "black"
    width: 16
    Layout.minimumWidth: 16
    Layout.preferredWidth: 16
    Layout.maximumWidth: 16

    required property double levelMax
    required property double levelRms
    required property double levelIECMaxBallistic
    required property int topOffset

    Gradient {
        id: maxGradient
        GradientStop { position: 0.2; color: "#F00014" }
        GradientStop { position: 0.3; color: "#F0A014" }
        GradientStop { position: 0.4; color: "#DCDC14" }
        GradientStop { position: 0.6; color: "#A0DC14" }
        GradientStop { position: 0.8; color: "#28A028" }
    }

    Gradient {
        id: rmsGradient
        GradientStop { position: 0.0; color: "#E6E6FF" }
        GradientStop { position: 0.7; color: "#0000FF" }
        GradientStop { position: 1.0; color: "#000096" }
    }

    Item {
        width: parent.width
        height: IECFunctions.dB_to_IEC(levelMax) * (parent.height - topOffset)
        anchors.bottom: parent.bottom
        clip: true

        Rectangle {
            width: parent.width
            height: parent.parent.height
            anchors.bottom: parent.bottom

            // this item must be static so that the gradient is not permanently redrawn
            gradient: maxGradient
        }
    }

    Item {
        width: parent.width
        height: IECFunctions.dB_to_IEC(levelRms) * (parent.height - topOffset)
        anchors.bottom: parent.bottom
        clip: true

        Rectangle {
            width: parent.width
            height: parent.parent.height
            anchors.bottom: parent.bottom

            // this item must be static so that the gradient is not permanently redrawn
            gradient: rmsGradient
        }
    }

    Shape {
        width: parent.width
        x: 0
        y: topOffset

        ShapePath {
            strokeWidth: 1
            strokeColor: "gray"
            startX: 0; startY: 0
            PathLine { x: 16; y: 0 }
        }
    }

    Shape {
        width: parent.width
        x: 0
        y: pathY(levelIECMaxBallistic)

        ShapePath {
            strokeWidth: 1
            strokeColor: iec_to_color(levelIECMaxBallistic)
            startX: 0; startY: 0
            PathLine { x: 16; y: 0 }

            function iec_to_color(iec) {
                if (iec > 0.8) {
                    return "#F00014"
                } else if (iec > 0.7) {
                    return "#F0A014"
                } else if (iec > 0.6) {
                    return "#DCDC14"
                } else if (iec > 0.4) {
                    return "#A0DC14"
                } else if (iec > 0.2) {
                    return "#28A028"
                } else {
                    return "#20B0020"
                }
            }
        }

        function pathY(iec) {
            return Math.round((parent.height - topOffset) * (1. - iec) + topOffset)
        }
    }
}