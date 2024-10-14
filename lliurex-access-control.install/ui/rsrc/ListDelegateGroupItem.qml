import QtQuick
import QtQuick.Controls
import QtQml.Models
import org.kde.plasma.components as Components


Components.ItemDelegate{

    id: listGroupItem
    property string groupId
    property bool isLocked
    property string description

    enabled:true
    height:45

    Item{
        id: menuItem
        height:visible?30:0
	width:parent.width
	anchors.verticalCenter:parent.verticalCenter


        MouseArea {
            id: mouseAreaOption
            anchors.fill: parent
            hoverEnabled:true
            propagateComposedEvents:true

            onEntered: {
                listGroup.currentIndex=index
            }
        }

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
