import QtQuick 2.9
import QtQuick.Window 2.2
import QtQuick.Layouts 1.15

Rectangle {
    SystemPalette { id: myPalette; colorGroup: SystemPalette.Active }
    color: myPalette.window

    RowLayout
    {
        id: metersLayout
        anchors.fill: parent
        spacing: 0

        readonly property int topOffset: height/20

        SingleMeter {
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignLeft
            levelMax: level_data.level_max
            levelRms: level_data.level_rms
            topOffset: metersLayout.topOffset
            levelIECMaxBallistic: level_data_ballistic.peak_iec
        }

        MeterScale {
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignLeft
            topOffset: metersLayout.topOffset
            twoChannels: level_settings.two_channels
        }

        SingleMeter {
            visible: level_settings.two_channels
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignLeft
            levelMax: level_data_2.level_max
            levelRms: level_data_2.level_rms
            topOffset: metersLayout.topOffset
            levelIECMaxBallistic: level_data_ballistic_2.peak_iec
        }

        Item {
            Layout.fillWidth: true
        }
    }
}