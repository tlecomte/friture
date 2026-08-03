import QtQuick 2.15
import QtQuick.Window 2.2
import QtQuick.Layouts 1.15
import QtQuick.Shapes 1.15
import Friture 1.0

Plot {
    scopedata: viewModel

    Repeater {
        model: scopedata.plot_items

        SpectrogramItem {
            anchors.fill: parent
            curve: modelData
        }
    }
}