import QtQuick 2.15
import QtQuick.Window 2.2
import QtQuick.Layouts 1.15
import QtQuick.Shapes 1.15
import Friture 1.0

Plot {
    required property var viewModel
    required property string fixedFont

    scopedata: viewModel

    Repeater {
        model: scopedata.plot_items

        PlotFilledCurve {
            anchors.fill: parent
            curve: modelData
        }
    }    

    Item {
        visible: scopedata.bar_labels_x_distance * parent.width > fontMetrics.boundingRect("100").height
        anchors.fill: parent

        FontMetrics {
            id: fontMetrics
        }

        SystemPalette { id: systemPalette; colorGroup: SystemPalette.Active }
    
        Repeater {
            model: scopedata.barLabels

            Item {
                x: modelData.x * parent.width - barLabel.height / 2
                y: Math.max(4, Math.min(modelData.y * parent.height + 4, parent.height - barLabel.width - 4))

                // width vs. height: childrenRect doesn't take transformations into account.
                // https://bugreports.qt-project.org/browse/QTBUG-38953
                implicitWidth: barLabel.height
                implicitHeight: barLabel.width

                Text {
                    id: barLabel
                    text: modelData.unscaled_x
                    rotation: 270
                    transformOrigin: Item.Center
                    anchors.centerIn: parent
                    color: modelData.y * parent.parent.height + 4 > parent.parent.height - barLabel.width - 4 ? systemPalette.windowText : systemPalette.base
                }
            }               
        }
    }
}
