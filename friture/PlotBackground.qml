import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Shapes 1.15

Rectangle {
    id: background

    SystemPalette { id: systemPalette; colorGroup: SystemPalette.Active }

    gradient: Gradient {
        GradientStop { position: -0.5; color: systemPalette.window }
        GradientStop { position: 0.5; color: systemPalette.base }
    }
}