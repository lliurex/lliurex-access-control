import QtQuick 2.6
import QtQuick.Controls 2.6
import QtQml.Models 2.6
import org.kde.plasma.components 2.0 as Components


Components.ListItem{

    id: listUserItem
    property string userId
    property bool isLocked

    enabled:true

    onContainsMouseChanged: {
        if (containsMouse) {
            listUser.currentIndex = index
        } else {
            listUser.currentIndex = -1
        }

    }

    Item{
        id: menuItem
        width: 320
        height:visible?30:0
        CheckBox {
            id:userCheck
            checked:isLocked
            onToggled:{
                accessControlBridge.manageUserChecked([userId,checked])
            }
            anchors.left:parent.left
            anchors.leftMargin:5
            anchors.verticalCenter:parent.verticalCenter

        }

        Text{
            id: userName
            text: userId
            width:250
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
            visible:listUserItem.ListView.isCurrentItem
            onClicked:{
                console.log(index)
                accessControlBridge.removeUser(index)
                entryRow.visible=false
            }
        }

    }
}
