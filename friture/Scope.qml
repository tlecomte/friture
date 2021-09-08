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
    property ScopeData scopedata: Store.dock_states[stateId]  

    GridLayout {
        anchors.fill: parent
        rowSpacing: 2
        columnSpacing: 2

        FontMetrics {
            id: fontMetrics
        }

        Item {
            Layout.row: 0
            Layout.column: 2

            // spacer so that the labels of the vertical scale are not clipped
            height: fontMetrics.ascent
        }

        Item {
            Layout.row: 1
            Layout.column: 0

            // width vs. height: childrenRect doesn't take transformations into account.
            // https://bugreports.qt-project.org/browse/QTBUG-38953
            width: childrenRect.height
            height: childrenRect.width

            Text {
                
                text: "Signal"
                transformOrigin: Item.Bottom
                rotation: -90
            }
        }

        VerticalScale {
            Layout.row: 1
            Layout.column: 1
            Layout.fillHeight: true

            vertical_scale_division: scopedata.vertical_scale_division
        }

        ScopePlotArea {
            Layout.row: 1
            Layout.column: 2
            Layout.fillHeight: true
            Layout.fillWidth: true

            vertical_scale_division: scopedata.vertical_scale_division
            horizontal_scale_division: scopedata.horizontal_scale_division
            vertical_coordinate_transform: scopedata.vertical_coordinate_transform
            horizontal_coordinate_transform: scopedata.horizontal_coordinate_transform
            curve1: scopedata.curve
            curve2: scopedata.curve_2
            two_channels: scopedata.two_channels
        }

        Legend {
            Layout.row: 1
            Layout.column: 3
            Layout.alignment: Qt.AlignTop | Qt.AlignLeft
            visible: scopedata.two_channels

            curve1: scopedata.curve
            curve2: scopedata.curve_2
        }

        HorizontalScale {
            Layout.row: 2
            Layout.column: 2
            Layout.fillWidth: true

            horizontal_scale_division: scopedata.horizontal_scale_division
        }

        Text {
            Layout.row: 3
            Layout.column: 2
            text: "Time (ms)"
            horizontalAlignment: Text.AlignHCenter
            Layout.fillWidth: true
        }
    }
}