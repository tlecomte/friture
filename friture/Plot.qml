import QtQuick 2.15
import QtQuick.Window 2.2
import QtQuick.Layouts 1.15
import QtQuick.Shapes 1.15
import Friture 1.0

Rectangle {
    id: plot
    anchors.fill: parent

    SystemPalette { id: myPalette; colorGroup: SystemPalette.Active }
    color: myPalette.window

    required property ScopeData scopedata
    default property alias content: plotItemPlaceholder.children

    GridLayout {
        anchors.fill: parent
        rowSpacing: 2
        columnSpacing: 2

        Item {
            Layout.row: 0
            Layout.column: 2

            // spacer so that the labels of the vertical scale are not clipped
            implicitHeight: verticalScale.topOverflow
            Layout.maximumHeight: implicitHeight
        }

        Item {
            Layout.row: 1
            Layout.column: 0

            // width vs. height: childrenRect doesn't take transformations into account.
            // https://bugreports.qt-project.org/browse/QTBUG-38953
            implicitWidth: verticalAxisLabel.height
            implicitHeight: verticalAxisLabel.width

            Text {
                id: verticalAxisLabel
                text: scopedata.vertical_axis.name
                transformOrigin: Item.Center
                rotation: -90
                anchors.centerIn: parent
            }
        }

        VerticalScale {
            id: verticalScale
            Layout.row: 1
            Layout.column: 1
            Layout.fillHeight: true

            scale_division: scopedata.vertical_axis.scale_division
        }

        PlotArea {
            Layout.row: 1
            Layout.column: 2
            Layout.fillHeight: true
            Layout.fillWidth: true

            vertical_axis: scopedata.vertical_axis
            horizontal_axis: scopedata.horizontal_axis

            Item {
                id: plotItemPlaceholder
                anchors.fill: parent
            }
        }

        Item {
            Layout.row: 1
            Layout.column: 3

            // spacer so that the last label of the horizontal scale is not clipped
            Layout.maximumWidth: implicitWidth
            implicitWidth: Math.max(0., horizontalScale.rightOverflow - (legend.visible ? legend.width : 0.))
        }

        Legend {
            id: legend
            Layout.row: 1
            Layout.column: 4
            Layout.alignment: Qt.AlignTop | Qt.AlignLeft
            visible: scopedata.plot_items.length > 1

            scopedata: plot.scopedata
        }

        HorizontalScale {
            id: horizontalScale
            Layout.row: 2
            Layout.column: 2
            Layout.fillWidth: true

            scale_division: scopedata.horizontal_axis.scale_division
        }

        Text {
            Layout.row: 3
            Layout.column: 2
            text: scopedata.horizontal_axis.name
            horizontalAlignment: Text.AlignHCenter
            Layout.fillWidth: true
        }
    }
}