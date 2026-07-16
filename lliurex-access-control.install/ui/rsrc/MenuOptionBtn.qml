import QtQuick 2.15 
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15


Item {
    id: menuItem
    Layout.preferredWidth: 175
    Layout.preferredHeight: 35

    property string optionIcon: ""
    property alias optionText: control.text
    property alias optionEnabled:control.enabled

    signal menuOptionClicked()

    ItemDelegate {
        id: control
        anchors.fill: parent
        text: menuItem.optionText

        contentItem: RowLayout {
            spacing: 5
            anchors.fill: parent
            anchors.leftMargin: 8

            Image {
                Layout.preferredWidth: 24
                Layout.preferredHeight: 24
                Layout.alignment: Qt.AlignVCenter

                source: menuItem.optionIcon ? "file:///usr/share/icons/breeze/" + menuItem.optionIcon : ""

                sourceSize.width: 24
                sourceSize.height: 24

                fillMode: Image.PreserveAspectFit
                visible: menuItem.optionIcon !== ""
            }

            Text {
                text: control.text
                font: control.font
                color: !control.enabled ? "grey":
                       control.down?"white":"black"
                elide: Text.ElideRight
                verticalAlignment: Text.AlignVCenter
                Layout.fillWidth: true
            }
        }

        background: Rectangle {
            color: control.hovered ? "#add8e6" : "transparent"
        }

        onClicked: menuItem.menuOptionClicked()
    }
}
