import QtQuick 2.15
import QtQuick.Controls 2.15
import Friture 1.0

Row {
    id: sineSettingsRoot
    spacing: 8
    required property Sine_Generator_Settings_View_Model viewModel

    SystemPalette { id: systemPalette; colorGroup: SystemPalette.Active }

    Text {
        text: "Frequency:"
        color: systemPalette.text
        anchors.verticalCenter: parent.verticalCenter
    }

    DecimalSpinBox {   
        binding: sineSettingsRoot.viewModel.frequency
        onDecimalValueModified: sineSettingsRoot.viewModel.frequency = decimalValue
    }
}