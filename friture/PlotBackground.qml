import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Shapes 1.15

Rectangle {
    id: background

    gradient: Gradient {
        GradientStop { position: 0.0; color: "#E0E0E0" }
        GradientStop { position: 0.5; color: "white" }
    }
}