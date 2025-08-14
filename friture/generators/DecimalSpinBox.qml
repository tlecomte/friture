import QtQuick 2.15
import QtQuick.Controls 2.15

// a SpinBox that allows decimal values with a suffix
SpinBox {     
    property var binding
    property string suffix: " Hz"
    property int decimals: 2
    property real decimalValue: value / decimalFactor
    property real decimalFrom: 20
    property real decimalTo: 22000
    readonly property real decimalFactor: Math.pow(10, decimals)

    signal decimalValueModified()

    id: spinbox
    from: decimalFrom * decimalFactor
    value: binding * decimalFactor
    to: decimalTo * decimalFactor
    stepSize: decimalFactor
    editable: true

    onValueModified: spinbox.decimalValueModified()

    validator: DoubleValidator {
        bottom: Math.min(spinbox.from, spinbox.to)
        top:  Math.max(spinbox.from, spinbox.to)
        decimals: spinbox.decimals
        notation: DoubleValidator.StandardNotation
    }

    textFromValue: function(value, locale) {
        return Number(value / decimalFactor).toLocaleString(locale, 'f', spinbox.decimals) + suffix
    }

    valueFromText: function(text, locale) {
        if (text.endsWith(suffix)) {
            text = text.slice(0, -suffix.length).trim();
        }

        return Number.fromLocaleString(locale, text) * decimalFactor
    }
}