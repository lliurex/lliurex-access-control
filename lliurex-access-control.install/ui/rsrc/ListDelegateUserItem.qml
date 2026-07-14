import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami


ItemDelegate{

    id: listUserItem
    property string userId
    property bool isLocked

    enabled:true
    height:45
    width: listUserItem.ListView.view?listUserItem.ListView.view.width -10 : 0
    hoverEnabled:true

    leftPadding:15
    rightPadding:15

    onHoveredChanged:{
        if (listUserItem.ListView.view){
            if (hovered){
                listUserItem.ListView.view.currentIndex=index
            }
        }else if (!hovered && !optionsMenu.opened && listUserItem.ListView.view===index){
            listUserItem.ListView.view.currentIndex=-1
        }
    }

    background:Rectangle {
        x:5
        y:5
        width:parent.width-10
        height:parent.height-5 
        color: (listUserItem.hovered) 
               ?Qt.alpha(Kirigami.Theme.highlightColor,0.15)
               :"transparent"
        radius:6
        border.width:1
        border.color:(listUserItem.hovered)
                      ?Kirigami.Theme.highlightColor
                      :"transparent"

    }
    
    contentItem:RowLayout {

        spacing: 10


        CheckBox {
            id:userCheck
            checked:isLocked
            onToggled:{
                userStackBridge.manageUserChecked({"userId":userId,"isLocked":checked})
            }

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
            Layout.fillWidth: true
            Layout.preferredWidth:0 
            elide: Text.ElideMiddle
            Layout.alignment: Qt.AlignVCenter
        }

        Button{
            id:removeUserBtn
            display:AbstractButton.IconOnly
            icon.name:"delete"
            visible: listUserItem.hovered
            Layout.preferredWidth: visible ? implicitWidth : 0
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
