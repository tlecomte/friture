import QtQuick 2.15
import QtQuick.Window 2.2
import QtQuick.Layouts 1.15
import QtQuick.Shapes 1.15
import Friture 1.0

Rectangle {
    anchors.fill: parent

    SystemPalette { id: myPalette; colorGroup: SystemPalette.Active }
    color: myPalette.window

    property var stateId
    property ScopeData scopedata: stateId >= 0 ? Store.dock_states[stateId] : defaultScopeData

    ScopeData {
        id: defaultScopeData
    }

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

        ScopePlotArea {
            Layout.row: 1
            Layout.column: 2
            Layout.fillHeight: true
            Layout.fillWidth: true

            vertical_scale_division: scopedata.vertical_axis.scale_division
            horizontal_scale_division: scopedata.horizontal_axis.scale_division
            vertical_coordinate_transform: scopedata.vertical_axis.coordinate_transform
            horizontal_coordinate_transform: scopedata.horizontal_axis.coordinate_transform
            curve1: scopedata.curve
            curve2: scopedata.curve_2
            two_channels: scopedata.two_channels
            vertical_axis: scopedata.vertical_axis
            horizontal_axis: scopedata.horizontal_axis
        }

        Item {
            Layout.row: 1
            Layout.column: 3

            // spacer so that the last label of the horizontal scale is not clipped
            Layout.maximumWidth: implicitWidth
            implicitWidth: Math.max(0., horizontalScale.rightOverflow - (scopedata.two_channels ? legend.width : 0.))
        }

        Legend {
            id: legend
            Layout.row: 1
            Layout.column: 4
            Layout.alignment: Qt.AlignTop | Qt.AlignLeft
            visible: scopedata.two_channels

            curve1: scopedata.curve
            curve2: scopedata.curve_2
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