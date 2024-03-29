import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQml.Models 2.8
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
        height:visible?30:0
        CheckBox {
            id:groupCheck
            checked:isLocked
            onToggled:{
                groupStackBridge.manageGroupChecked([groupId,checked])
            }
            anchors.left:parent.left
            anchors.leftMargin:5
            anchors.verticalCenter:parent.verticalCenter
            ToolTip.delay: 1000
            ToolTip.timeout: 3000
            ToolTip.visible: hovered
            ToolTip.text:{
                if (groupCheck.checked){
                    i18nd("lliurex-access-control","Check to unlock access to this group")
                }else{
                    i18nd("lliurex-access-control","Check to lock access to this group")                   
                }
            }

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
