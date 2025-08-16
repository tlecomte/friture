import QtQuick 2.15
import QtQuick.Window 2.2
import QtQuick.Layouts 1.15
import QtQuick.Shapes 1.15
import Friture 1.0

Item {
    id: container
    property var stateId

    // delay the load of the Plot until stateId has been set
    Loader {
        id: loader
        anchors.fill: parent
    }

    onStateIdChanged: {
        console.log("stateId changed: " + stateId)
        loader.sourceComponent = plotComponent
    }

    Component {
        id: plotComponent
        Plot {
            scopedata: Store.dock_states[container.stateId]

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
    }
}
