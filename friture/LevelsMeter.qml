import QtQuick 2.9
import QtQuick.Window 2.2
import QtQuick.Layouts 1.15
import Friture 1.0

Rectangle {
    SystemPalette { id: myPalette; colorGroup: SystemPalette.Active }
    color: myPalette.window

    required property LevelViewModel level_view_model

    RowLayout
    {
        id: metersLayout
        anchors.fill: parent
        spacing: 0

        readonly property int topOffset: height/20

        SingleMeter {
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignLeft
            levelMax: level_view_model.level_data.level_max
            levelRms: level_view_model.level_data.level_rms
            topOffset: metersLayout.topOffset
            levelIECMaxBallistic: level_view_model.level_data_ballistic.peak_iec
        }

        MeterScale {
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignLeft
            topOffset: metersLayout.topOffset
            twoChannels: level_view_model.two_channels
        }

        SingleMeter {
            visible: level_view_model.two_channels
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignLeft
            levelMax: level_view_model.level_data_2.level_max
            levelRms: level_view_model.level_data_2.level_rms
            topOffset: metersLayout.topOffset
            levelIECMaxBallistic: level_view_model.level_data_ballistic_2.peak_iec
        }

        Item {
            Layout.fillWidth: true
        }
    }
}