import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQml 2.15
import "./generators"

Rectangle {
    id: generatorRoot

    SystemPalette { id: systemPalette; colorGroup: SystemPalette.Active }
    color: systemPalette.window

    ColumnLayout {
        anchors.top: parent.top
        anchors.left: parent.left
        spacing: 12

        ComboBox {
            model: viewModel.generatorNames
            currentIndex: viewModel.generatorIndex
            onCurrentIndexChanged: viewModel.generatorIndex = currentIndex
        }

        Button {
            id: startStopButton
            text: viewModel.isPlaying ? qsTr("Stop") : qsTr("Start")
            checkable: true
            checked: viewModel.isPlaying
            onCheckedChanged: viewModel.isPlaying = checked
            icon.source: viewModel.isPlaying ? "qrc:/images-src/stop.svg" : "qrc:/images-src/start.svg"
        }

        SineSettings {
            Layout.fillWidth: true
            settingsViewModel: viewModel.sineGenerator
            visible: viewModel.generatorIndex === 0
        }

        WhiteSettings {
            Layout.fillWidth: true
            settingsViewModel: viewModel.whiteGenerator
            visible: viewModel.generatorIndex === 1
        }

        PinkSettings {
            Layout.fillWidth: true
            settingsViewModel: viewModel.pinkGenerator
            visible: viewModel.generatorIndex === 2
        }

        SweepSettings {
            Layout.fillWidth: true
            settingsViewModel: viewModel.sweepGenerator
            visible: viewModel.generatorIndex === 3
        }

        BurstSettings {
            Layout.fillWidth: true
            settingsViewModel: viewModel.burstGenerator
            visible: viewModel.generatorIndex === 4
        }
    }
}
