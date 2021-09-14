import QtQuick 2.15
import QtQuick.Window 2.2
import QtQuick.Layouts 1.15
import QtQuick.Shapes 1.15
import Friture 1.0
import "plotItemColors.js" as PlotItemColors

Plot {
    property var stateId
    visible: stateId >= 0
    scopedata: stateId >= 0 ? Store.dock_states[stateId] : Qt.createQmlObject('import Friture 1.0; ScopeData {}', this, "defaultScopeData");

    Repeater {
        model: scopedata.plot_items

        PlotCurve {
            anchors.fill: parent
            color: PlotItemColors.color(index)
            curve: modelData
        }
    }
}