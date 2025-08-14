import QtQuick 2.15
import QtQuick.Controls 2.15
import Friture 1.0

Row {
    id: root
    required property Burst_Generator_Settings_View_Model viewModel
    spacing: 8

    SystemPalette { id: systemPalette; colorGroup: SystemPalette.Active }

    Text {
        text: "Period:"
        color: systemPalette.text
        anchors.verticalCenter: parent.verticalCenter
    }
    DecimalSpinBox {   
        binding: root.viewModel.period
        onDecimalValueModified: root.viewModel.period = decimalValue
        suffix: " s"
        decimalFrom: 0.01
        decimalTo: 60
    }
}