import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3
import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.kirigami 2.16 as Kirigami

Rectangle{
    color:"transparent"
    
    ColumnLayout{
        id:generalLayout
        anchors.top:parent.top
        anchors.left:parent.left
        anchors.right:parent.right
        anchors.bottom:btnBox.top

        anchors.leftMargin:5
        anchors.rightMargin:15
        anchors.bottomMargin:25
        spacing: 10

        Text{ 
            text:i18nd("lliurex-access-control","Restrict access by user")
            font.pointSize: 16
        }

        Kirigami.InlineMessage {
            id: messageLabel
            visible:userStackBridge.showSettingsUserMessage.show
            text:getMessageText(userStackBridge.showSettingsUserMessage.msgCode)
            type:getMessageType(userStackBridge.showSettingsUserMessage.type)
            Layout.fillWidth:true
        }

        ColumnLayout {
            id: optionsGrid
            spacing: 5

            CheckBox {
                id: userControlCb
                text: i18nd("lliurex-access-control", "Activated access control by user on this computer")
                checked: userStackBridge.isUserAccessControlEnabled
                font.pointSize: 10
                focusPolicy: Qt.NoFocus
                Layout.alignment: Qt.AlignLeft

                onToggled: {
                    userStackBridge.manageUserAccessControl(checked)
                }
            }

            Text {
                id: usersList
                text: i18nd("lliurex-access-control", "Users with restricted access:")
                font.pointSize: 10
                Layout.alignment: Qt.AlignLeft
                Layout.topMargin:10

            }

            RowLayout {
                id: entryRow
                visible: false
                spacing: 5
                Layout.alignment: Qt.AlignLeft
                Layout.rightMargin:addUserBtn.width+25
                Layout.preferredWidth: usersList.implicitWidth

                TextField {
                    id: userEntry
                    placeholderText: i18nd("lliurex-access-control", "User names separated by space")
                    font.pointSize: 10
                    focus: true
                    Layout.fillWidth: true
                }

                Button {
                    id: applyUserBtn
                    display: AbstractButton.IconOnly
                    icon.name: "dialog-ok"
                    enabled: userEntry.text.trim().length > 0
                    focus: true
                    
                    ToolTip.delay: 1000
                    ToolTip.timeout: 3000
                    ToolTip.visible: hovered
                    ToolTip.text: i18nd("lliurex-access-control", "Click to add the users to list")
                    
                    Keys.onReturnPressed: applyUserBtn.clicked()
                    Keys.onEnterPressed: applyUserBtn.clicked()
                    
                    onClicked: {
                        userStackBridge.addUser(userEntry.text)
                        entryRow.visible = false
                        userEntry.text=""
                    }
                }

                Button{
                   id:cancelUserBtn
                   display:AbstractButton.IconOnly
                   icon.name:"dialog-close"
                   focus:true

                   ToolTip.delay: 1000
                   ToolTip.timeout: 3000
                   ToolTip.visible: hovered
                   ToolTip.text:i18nd("lliurex-access-control","Click to close")

                   Keys.onReturnPressed: cancelUserBtn.clicked()
                   Keys.onEnterPressed: cancelUserBtn.clicked()
                   
                   onClicked:{
                        entryRow.visible=false
                        userEntry.text=""
                   }
                }
            }

           RowLayout{
                Layout.alignment:Qt.AlignHCenter
                Layout.rightMargin:10

                UserList{
                    id:userList
                    structModel:userStackBridge.usersModel
                    structEnabled:userControlCb.checked
                    Layout.fillHeight:true
                    Layout.fillWidth:true

                }
                ColumnLayout{
                    id:userBtnLayout
                    Layout.leftMargin:10

                    Button{
                        id:addUserBtn
                        display:AbstractButton.TextBesideIcon
                        icon.name:"contact-new"
                        text:i18nd("lliurex-access-control","Add users")
                        enabled:userControlCb.checked && userEntry.text==""
                        implicitWidth:140
                        Keys.onReturnPressed: addUserBtn.clicked()
                        Keys.onEnterPressed: addUserBtn.clicked()
                        onClicked:{
                            entryRow.visible=true
                            userEntry.forceActiveFocus()
                        }
                    }    
                    Button{
                        id:removeListBtn
                        display:AbstractButton.TextBesideIcon
                        icon.name:"delete"
                        text:i18nd("lliurex-access-control","Remove List")
                        focus:true
                        enabled:(userList.listCount>0 && userEntry.text==="")?true:false
                        implicitWidth:140
                        Keys.onReturnPressed: removeListBtn.clicked()
                        Keys.onEnterPressed: removeListBtn.clicked()                    
                        onClicked:{
                           removeListDialog.open()
                        }
                    }

                }
            }
        }
    }

    Item{
        Layout.fillHeight:true
    }

    RowLayout{
        id:btnBox
        anchors.bottom: parent.bottom
        anchors.right:parent.right
        anchors.margins:15
        spacing:10

        Button {
            id:applyBtn
            visible:true
            focus:true
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-ok"
            text:i18nd("lliurex-access-control","Apply")
            enabled:userStackBridge.hasUserChanges
            Keys.onReturnPressed: applyBtn.clicked()
            Keys.onEnterPressed: applyBtn.clicked()                    
            onClicked:{
                closeTimer.stop()
                userStackBridge.applyUserChanges()
            }
        }

        Button {
            id:cancelBtn
            visible:true
            focus:true
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-cancel"
            text:i18nd("lliurex-access-control","Cancel")
            enabled:userStackBridge.hasUserChanges
            Keys.onReturnPressed: cancelBtn.clicked()
            Keys.onEnterPressed: cancelBtn.clicked()                    
            onClicked:{
                closeTimer.stop(),
                userStackBridge.cancelUserChanges()
            }
        }
    } 

    Dialog {
        id:localAdminDialog
        visible:userStackBridge.showLocalAdminDialog
        title:"Lliurex Access Control"+" - "+i18nd("lliurex-access-control","Control by users")
        modality:Qt.WindowModal

        contentItem: Rectangle {
            color: "#ebeced"
            implicitWidth: 550
            implicitHeight: 105

            RowLayout {
                id: localAdminLayout
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: 0
                spacing: 15

                Kirigami.Icon {
                    id: dialogIcon
                    source: "dialog-warning"
                    Layout.preferredWidth: 64
                    Layout.preferredHeight: 64
                    visible: status === Image.Ready
                }

                Text {
                    id: dialogText
                    text:i18nd("lliurex-access-control","Local administrators have been detected in the list of users to add.\nDo you want to include them in the list of users?")
                    font.pointSize: 10
                    Layout.fillWidth: true
                    Layout.rightMargin:10
                    wrapMode: Text.WordWrap
                }
            }
        
            DialogButtonBox {
                buttonLayout:DialogButtonBox.KdeLayout
                anchors.bottom:parent.bottom
                anchors.right:parent.right
                anchors.topMargin:10

                Button {
                    id:adminDialogApplyBtn
                    display:AbstractButton.TextBesideIcon
                    icon.name:"dialog-ok"
                    text: i18nd("lliurex-access-control","Yes")
                    focus:true
                    font.pointSize: 10
                    DialogButtonBox.buttonRole: DialogButtonBox.ApplyRole
                    Keys.onReturnPressed: adminDialogApplyBtn.clicked()
                    Keys.onEnterPressed: adminDialogApplyBtn.clicked()
                    onClicked: userStackBridge.manageLocalAdminDialog("Accept")                    

                }

                Button {
                    id:adminDialogCancelBtn
                    display:AbstractButton.TextBesideIcon
                    icon.name:"dialog-cancel"
                    text: i18nd("lliurex-access-control","No")
                    focus:true
                    font.pointSize: 10
                    DialogButtonBox.buttonRole:DialogButtonBox.RejectRole
                    Keys.onReturnPressed: adminDialogCancelBtn.clicked()
                    Keys.onEnterPressed: adminDialogCancelBtn.clicked()
                    onClicked: userStackBridge.manageLocalAdminDialog("Cancel")                  
       
                }
          
            }
        }
     }

    ChangesDialog{
        id:userChangesDialog
        dialogTitle:"Lliurex Access Control"+" - "+i18nd("lliurex-access-control","Control by users")
        dialogVisible:userStackBridge.showUserChangesDialog
        dialogMsg:i18nd("lliurex-access-control","The are pending changes to apply.\nDo you want apply the changes or discard them?")
        
    }

    Dialog{
        id:removeListDialog
        title:"Lliurex Access Control"+" - "+i18nd("lliurex-access-control","Control by users")
        visible:false
        modality:Qt.WindowModal

        contentItem: Rectangle {
            color: "#ebeced"
            implicitWidth: 480
            implicitHeight: 105

            RowLayout {
                id: removeLayout
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: 0
                spacing: 15

                Kirigami.Icon {
                    id: dialogRemoveIcon
                    source: "dialog-warning"
                    Layout.preferredWidth: 64
                    Layout.preferredHeight: 64
                    visible: status === Image.Ready
                }

                Text {
                    id: dialogRemoveText
                    text:i18nd("lliurex-access-control","The user list is going to be delete.Do you wish to continue?")
                    font.pointSize: 10
                    Layout.fillWidth: true
                    Layout.rightMargin:10
                    wrapMode: Text.WordWrap
                }
            }

            DialogButtonBox {
                buttonLayout:DialogButtonBox.KdeLayout
                anchors.bottom:parent.bottom
                anchors.right:parent.right
                anchors.topMargin:15

                Button {
                    id:removeListDialogApplyBtn
                    display:AbstractButton.TextBesideIcon
                    icon.name:"dialog-ok"
                    text: i18nd("lliurex-access-control","Accept")
                    focus:true
                    font.pointSize: 10
                    DialogButtonBox.buttonRole: DialogButtonBox.ApplyRole
                    Keys.onReturnPressed: removeListDialogApplyBtn.clicked()
                    Keys.onEnterPressed: removeListDialogApplyBtn.clicked()
                    onClicked:{
                        userStackBridge.removeUserList()
                        userList.structModel=userStackBridge.usersModel
                        removeListDialog.close()
                    }                    

                }

                Button {
                    id:removeListDialogCancelBtn
                    display:AbstractButton.TextBesideIcon
                    icon.name:"dialog-cancel"
                    text: i18nd("lliurex-access-control","Cancel")
                    focus:true
                    font.pointSize: 10
                    DialogButtonBox.buttonRole:DialogButtonBox.RejectRole
                    Keys.onReturnPressed: removeListDialogCancelBtn.clicked()
                    Keys.onEnterPressed: removeListDialogCancelBtn.clicked()
                    onClicked:removeListDialog.close()                    

                }

            }
        }
    }


    function getMessageText(code){

        switch (code){
            case 10:
                return i18nd("lliurex-access-control","Changes applied successfully")
            case -30:
                return i18nd("lliurex-access-control","It is not possible to deactive access control by user")
            case -40:
                return i18nd("lliurex-access-control","Unable to update the user list")           
            case -80:
                return i18nd("lliurex-access-control","There are no users selected to lock their access")
            case -90:
                return i18nd("lliurex-access-control","The indicated users already exist in the list")
            case -100:
                return i18nd("lliurex-access-control","It is not possible to lock the user with which you are configuring the access control")
            case -200:
				return i18nd("lliurex-access-control", "It is not possible to lock users from teacher or admins groups")
            default:
                return ""
        }

    }

    function getMessageType(type){

        switch (type) {
            case 0:
                return Kirigami.MessageType.Positive
            case 1:
                return Kirigami.MessageType.Error
            case 2:
                return Kirigami.MessageType.Warning
            case 3:
                return Kirigami.MessageType.Information
           default:
                return Kirigami.MessageType.Information
        }

    } 
   
} 
