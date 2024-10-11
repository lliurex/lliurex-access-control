import QtQuick
import QtQuick.Controls
import QtQml.Models
import org.kde.plasma.components as Components


Components.ItemDelegate{

    id: listUserItem
    property string userId
    property bool isLocked

    enabled:true
    height:45

    Item{
        id: menuItem
        height:visible?30:0
        width:parent.width-removeUserBtn.width
	anchors.verticalCenter:parent.verticalCenter

        MouseArea {
            id: mouseAreaOption
            anchors.fill: parent
            hoverEnabled:true
            propagateComposedEvents:true

            onEntered: {
                listUser.currentIndex=index
            }
	    onExited:{
		listUser.currentIndex=-1
	    }
        }
        CheckBox {
            id:userCheck
            checked:isLocked
            onToggled:{
                userStackBridge.manageUserChecked([userId,checked])
            }
            anchors.left:parent.left
            anchors.leftMargin:5
            anchors.verticalCenter:parent.verticalCenter
            ToolTip.delay: 1000
            ToolTip.timeout: 3000
            ToolTip.visible: hovered
            ToolTip.text:{
                if (userCheck.checked){
                    i18nd("lliurex-access-control","Check to unlock access to this user")
                }else{
                     i18nd("lliurex-access-control","Check to lock access to this user")                   
                }
            }
        }

        Text{
            id: userName
            text: userId
            width: parent.width-removeUserBtn.width-20
            clip: true
            anchors.left:userCheck.right
            anchors.leftMargin:5
            anchors.verticalCenter:parent.verticalCenter
        }
        Button{
            id:removeUserBtn
            display:AbstractButton.IconOnly
            icon.name:"delete.svg"
            anchors.left:userName.right
	    anchors.verticalCenter:parent.verticalCenter
            visible:listUserItem.ListView.isCurrentItem
            onClicked:{
                userStackBridge.removeUser(index)
                entryRow.visible=false
            }
            ToolTip.delay: 1000
            ToolTip.timeout: 3000
            ToolTip.visible: hovered
            ToolTip.text:i18nd("lliurex-access-control","Clic to remove this user from the list")
        }

    }
}
