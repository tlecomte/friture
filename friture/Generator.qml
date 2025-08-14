import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3
import QtQml 2.15
import "./generators"

Rectangle {
    id: generatorRoot
    required property var viewModel
    required property string fixedFont

    SystemPalette { id: systemPalette; colorGroup: SystemPalette.Active }
    color: systemPalette.window
    anchors.fill: parent

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
            viewModel: generatorRoot.viewModel.sineGenerator
            visible: generatorRoot.viewModel.generatorIndex === 0
        }

        WhiteSettings {
            viewModel: generatorRoot.viewModel.whiteGenerator
            visible: generatorRoot.viewModel.generatorIndex === 1
        }

        PinkSettings {
            viewModel: generatorRoot.viewModel.pinkGenerator
            visible: generatorRoot.viewModel.generatorIndex === 2
        }

        SweepSettings {
            viewModel: generatorRoot.viewModel.sweepGenerator
            visible: generatorRoot.viewModel.generatorIndex === 3
        }

        BurstSettings {
            viewModel: generatorRoot.viewModel.burstGenerator
            visible: generatorRoot.viewModel.generatorIndex === 4
        }
    }
}
