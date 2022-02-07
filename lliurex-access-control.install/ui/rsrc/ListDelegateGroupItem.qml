import QtQuick 2.6
import QtQuick.Controls 2.6
import QtQml.Models 2.6
import org.kde.plasma.components 2.0 as Components


Components.ListItem{

    id: listGroupItem
    property string groupId
    property bool isLocked
    property string description

    enabled:true

    onContainsMouseChanged: {
        if (containsMouse) {
            listGroup.currentIndex = index
        } else {
            listGroup.currentIndex = -1
        }

    }

    Item{
        id: menuItem
        width: 470
        height:visible?30:0
        CheckBox {
            id:groupCheck
            checked:isLocked
            onToggled:{
                accessControlBridge.manageGroupChecked([groupId,checked])
            }
            anchors.left:parent.left
            anchors.leftMargin:5
            anchors.verticalCenter:parent.verticalCenter

        }

        Text{
            id: text
            text: description
            width:400
            clip: true
            anchors.left:groupCheck.right
            anchors.leftMargin:5
            anchors.verticalCenter:parent.verticalCenter
        }

    }
}
