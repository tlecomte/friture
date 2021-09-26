import QtQuick 2.15
import QtQuick.Window 2.2
import QtQuick.Layouts 1.15
import QtQuick.Shapes 1.15
import Friture 1.0

Plot {
    property var stateId
    visible: stateId >= 0
    scopedata: stateId >= 0 ? Store.dock_states[stateId] : Qt.createQmlObject('import Friture 1.0; SpectrumData {}', this, "defaultSpectrumData");

    Repeater {
        model: scopedata.plot_items

        PlotFilledCurve {
            anchors.fill: parent
            curve: modelData
        }
    }

    FrequencyTracker {
        visible: scopedata.showFrequencyTracker
        anchors.fill: parent
        fmaxValue: scopedata.fmaxValue
        fmaxLogicalValue: scopedata.fmaxLogicalValue
    }
}