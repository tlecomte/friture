import QtQuick 2.9
import QtQuick.Layouts 1.15
import QtQuick.Shapes 1.15
import "iec.js" as IECFunctions

Item {
    id: meterScale
    implicitWidth: 16
    SystemPalette { id: systemPalette; colorGroup: SystemPalette.Active }

    required property int topOffset
    required property bool twoChannels
    required property string unitLabel

    readonly property var scaleDbValues: IECFunctions.meterScaleTicks(unitLabel)

    Repeater {
        model: scaleDbValues

        Item {
            implicitWidth: 16
            x: 0
            y: pathY(modelData)

            Shape {
                ShapePath {
                    strokeWidth: 1
                    strokeColor: systemPalette.windowText
                    startX: 0
                    startY: 0
                    PathLine { x: 2; y: 0 }
                }   
            }

            Text {
                text: Math.abs(modelData)
                font.pointSize: 6
                x: 0
                width: 16
                y: -5
                height: 10
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                color: systemPalette.windowText
            }

            Shape {
                visible: twoChannels

                ShapePath {
                    strokeWidth: 1
                    strokeColor: systemPalette.windowText
                    startX: 14
                    startY: 0
                    PathLine { x: 16; y: 0 }
                }   
            }

            function pathY(dB) {
                var fraction = IECFunctions.level_db_to_meter_fraction(dB, unitLabel);
                return Math.round((metersLayout.height - meterScale.topOffset) * (1. - fraction) + meterScale.topOffset)
            }
        }
    }
}