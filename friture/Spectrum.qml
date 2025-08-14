import QtQuick 2.15
import QtQuick.Window 2.2
import QtQuick.Layouts 1.15
import QtQuick.Shapes 1.15
import Friture 1.0

Plot {
    required property var viewModel
    required property string fixedFont

    scopedata: viewModel

    Repeater {
        model: scopedata.plot_items

        PlotFilledCurve {
            anchors.fill: parent
            curve: modelData
        }
    }

    Column {
        anchors.fill: parent
        spacing: 0
        FrequencyTracker {
            visible: scopedata.showFrequencyTracker
            anchors.left: parent.left
            anchors.right: parent.right
            fmaxValue: scopedata.fmaxValue
            fmaxLogicalValue: scopedata.fmaxLogicalValue
        }

        FrequencyTracker {
            visible: scopedata.showPitchTracker
            anchors.left: parent.left
            anchors.right: parent.right
            fmaxValue: scopedata.fpitchDisplayText
            fmaxLogicalValue: scopedata.fpitchValue
        }
    }
}
