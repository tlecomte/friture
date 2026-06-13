import QtQuick 2.9
import QtQuick.Window 2.2
import QtQuick.Layouts 1.15
import Friture 1.0

Rectangle {
    SystemPalette { id: systemPalette; colorGroup: SystemPalette.Active }
    color: systemPalette.window

    required property LevelViewModel level_view_model

    readonly property bool ready: level_view_model !== null

    RowLayout
    {
        id: metersLayout
        anchors.fill: parent
        spacing: 0
        visible: ready

        readonly property int topOffset: height/20

        SingleMeter {
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignLeft
            levelMax: ready ? level_view_model.level_data.level_max : -150
            levelRms: ready ? level_view_model.level_data.level_rms : -150
            topOffset: metersLayout.topOffset
            levelIECMaxBallistic: ready ? level_view_model.level_data_ballistic.peak_iec : 0
        }

        MeterScale {
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignLeft
            topOffset: metersLayout.topOffset
            twoChannels: ready && level_view_model.two_channels
        }

        SingleMeter {
            visible: ready && level_view_model.two_channels
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignLeft
            levelMax: ready ? level_view_model.level_data_2.level_max : -150
            levelRms: ready ? level_view_model.level_data_2.level_rms : -150
            topOffset: metersLayout.topOffset
            levelIECMaxBallistic: ready ? level_view_model.level_data_ballistic_2.peak_iec : 0
        }

        Item {
            Layout.fillWidth: true
        }
    }
}