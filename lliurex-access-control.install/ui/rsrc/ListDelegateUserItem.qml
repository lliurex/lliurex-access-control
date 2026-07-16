import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQml.Models 2.8
import org.kde.kirigami 2.16 as Kirigami


ItemDelegate{

    id: listUserItem
    property string userId
    property bool isLocked

    enabled:true
    height:50
    width: listUserItem.ListView.view?listUserItem.ListView.view.width -10 : 0
    hoverEnabled:true

    leftPadding:15
    rightPadding:15
    topPadding:0
    bottomPadding:0

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
        anchors.fill:parent
        anchors.margins:5

        color: (listUserItem.hovered) 
               ? Qt.hsla(Kirigami.Theme.highlightColor.hslHue, 
                 Kirigami.Theme.highlightColor.hslSaturation, 
                 Kirigami.Theme.highlightColor.hslLightness, 
                 0.15)
               :"transparent"
        radius:6
        border.width:1
        border.color:(listUserItem.hovered)
                      ?Kirigami.Theme.highlightColor
                      :"transparent"

    }
    
    contentItem:RowLayout {

        anchors.fill:parent
        anchors.leftMargin:listUserItem.leftPadding
        anchors.rightMargin:listUserItem.rightPadding
        spacing:10

        CheckBox {
            id:userCheck
            checked:isLocked
            Layout.alignment: Qt.AlignVCenter

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
            Layout.alignment: Qt.AlignVCenter

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
