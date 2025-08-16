import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

RowLayout {
    id: controlBar
    objectName: "controlBar"
    spacing: 0

    SystemPalette { id: systemPalette; colorGroup: SystemPalette.Active }

    required property var viewModel

    ComboBox {
        id: widgetSelector
        model: [
            "Scope",
            "FFT Spectrum",
            "2D Spectrogram",
            "Octave Spectrum",
            "Generator",
            "Delay Estimator",
            "Long-time levels",
            "Pitch Tracker"
        ]
        currentIndex: viewModel.currentIndex
        onCurrentIndexChanged: viewModel.currentIndex = currentIndex
        ToolTip.text: "Select the type of audio widget"
        
        // replace with implicitContentWidthPolicy to either ComboBox.WidestText on Qt 6
        width: 130
        Layout.preferredWidth: width
        Layout.rightMargin: 5
    }

    ToolButton {
        id: settingsButton
        icon.source: "qrc:/images-src/dock-settings.svg"
        ToolTip.text: "Customize the audio widget"
        icon.color: systemPalette.windowText
        onClicked: viewModel.onSettingsClicked()
    }

    ToolButton {
        id: movePreviousButton
        icon.source: "qrc:/images-src/dock-move-previous.svg"
        ToolTip.text: "Move widget to previous slot"
        icon.color: systemPalette.windowText
        onClicked: viewModel.onMovePreviousClicked()
    }

    ToolButton {
        id: moveNextButton
        icon.source: "qrc:/images-src/dock-move-next.svg"
        ToolTip.text: "Move widget to next slot"
        icon.color: systemPalette.windowText
        onClicked: viewModel.onMoveNextClicked()
    }

    ToolButton {
        id: closeButton
        icon.source: "qrc:/images-src/dock-close.svg"
        ToolTip.text: "Close the audio widget"
        icon.color: systemPalette.windowText
        onClicked: viewModel.onCloseClicked()
    }

    Item {
        Layout.fillWidth: true
    }
}
