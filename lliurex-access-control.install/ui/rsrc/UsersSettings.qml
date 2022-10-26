import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.kirigami 2.16 as Kirigami
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3

Rectangle{
    color:"transparent"
    Text{ 
        text:i18nd("lliurex-access-control","Restrict access by user")
        font.family: "Quattrocento Sans Bold"
        font.pointSize: 16
    }

    GridLayout{
        id:generalLayout
        rows:2
        flow: GridLayout.TopToBottom
        rowSpacing:10
        width:parent.width
        height:parent.height-90
        anchors.left:parent.left

        Kirigami.InlineMessage {
            id: messageLabel
            visible:accessControlBridge.showSettingsUserMessage[0]
            text:getMessageText(accessControlBridge.showSettingsUserMessage[1])
            type:getMessageType(accessControlBridge.showSettingsUserMessage[2])
            Layout.minimumWidth:490
            Layout.fillWidth:true
            Layout.topMargin: 40
            Layout.rightMargin:10
        }

        GridLayout{
            id: optionsGrid
            rows: 4
            flow: GridLayout.TopToBottom
            rowSpacing:5
            Layout.topMargin: messageLabel.visible?0:50

            CheckBox {
                id:userControlCb
                text:i18nd("lliurex-access-control","Activated access control by user on this computer")
                checked:accessControlBridge.isAccessDenyUserEnabled
                font.pointSize: 10
                focusPolicy: Qt.NoFocus
                onToggled:{
                   accessControlBridge.manageUserAccessControl(checked)
                }

                Layout.alignment:Qt.AlignLeft
                Layout.bottomMargin:15
            }
            RowLayout {
                Layout.fillWidth: true
                Layout.alignment:Qt.AlignCenter
                Layout.rightMargin:addUserBtn.width+25

                Text{
                    id:usersList
                    text:i18nd("lliurex-access-control","Users with restricted access:")
                    font.pointSize:10
                    width:userEntry.width
                }
            }
            RowLayout {
                id:entryRow
                Layout.alignment:Qt.AlignLeft
                visible:false
                Layout.rightMargin:addUserBtn.width+25
                
                TextField{
                    id:userEntry
                    placeholderText:i18nd("lliurex-access-control","Username")
                    font.pointSize:10
                    width:263
                    Layout.fillWidth:true
                    focus:true

                }
                Button{
                   id:applyUserBtn
                   display:AbstractButton.IconOnly
                   icon.name:"dialog-ok.svg"
                   enabled:userEntry.text.trim().length>0?true:false
                   focus:true
                   ToolTip.delay: 1000
                   ToolTip.timeout: 3000
                   ToolTip.visible: hovered
                   ToolTip.text:i18nd("lliurex-access-control","Click to add the user to list")
                   Keys.onReturnPressed: applyUserBtn.clicked()
                   Keys.onEnterPressed: applyUserBtn.clicked()
                   onClicked:{
                        synchronizePopup.open()
                        synchronizePopup.popupMessage=i18nd("lliurex-access-control", "Validating data. Wait a moment...")
                        delay(500, function() {
                            if (accessControlBridge.closePopUp){
                                synchronizePopup.close(),
                                timer.stop

                            }
                        })
                        accessControlBridge.addUser(userEntry.text)
                        entryRow.visible=false
                        userEntry.text=""

                   }
                }
                Button{
                   id:cancelUserBtn
                   display:AbstractButton.IconOnly
                   icon.name:"dialog-close.svg"
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
                    structModel:accessControlBridge.usersModel
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
                        icon.name:"contact-new.svg"
                        text:i18nd("lliurex-access-control","Add user")
                        implicitWidth:140
                        enabled:userControlCb.checked && userEntry.text==""
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
                        icon.name:"delete.svg"
                        text:i18nd("lliurex-access-control","Remove List")
                        implicitWidth:140
                        focus:true
                        enabled:{
                            if ((userList.listCount>0)&&(userEntry.text=="")){
                                true
                            }else{
                                false
                            }
                        }
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
    RowLayout{
        id:btnBox
        anchors.bottom: parent.bottom
        anchors.right:parent.right
        anchors.bottomMargin:15
        anchors.rightMargin:10
        spacing:10

        Button {
            id:applyBtn
            visible:true
            focus:true
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-ok.svg"
            text:i18nd("lliurex-access-control","Apply")
            Layout.preferredHeight:40
            enabled:accessControlBridge.settingsUserChanged
            Keys.onReturnPressed: applyBtn.clicked()
            Keys.onEnterPressed: applyBtn.clicked()                    
            onClicked:{
                applyChanges(),
                accessControlBridge.applyUserChanges()
            }
        }
        Button {
            id:cancelBtn
            visible:true
            focus:true
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-cancel.svg"
            text:i18nd("lliurex-access-control","Cancel")
            Layout.preferredHeight: 40
            enabled:accessControlBridge.settingsUserChanged
            Keys.onReturnPressed: cancelBtn.clicked()
            Keys.onEnterPressed: cancelBtn.clicked()                    
            onClicked:{
                discardChanges(),
                accessControlBridge.cancelUserChanges()
            }
        }
    } 

    Dialog {
        id:localAdminDialog
        visible:accessControlBridge.showLocalAdminDialog
        title:"Lliurex Access Control"+" - "+i18nd("lliurex-access-control","Control by users")
        modality:Qt.WindowModal

        contentItem: Rectangle {
            color: "#ebeced"
            implicitWidth: 480
            implicitHeight: 105
            anchors.topMargin:5
            anchors.leftMargin:5

            Image{
                id:adminDialogIcon
                source:"/usr/share/icons/breeze/status/64/dialog-warning.svg"

            }
            Text {
                id:adminDialogText
                text:i18nd("lliurex-access-control","The user you want to add is a local administrator of the computer.\nDo you wish to continue?")
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                anchors.left:adminDialogIcon.right
                anchors.verticalCenter:adminDialogIcon.verticalCenter
                anchors.leftMargin:10
            
            }
             DialogButtonBox {
                buttonLayout:DialogButtonBox.KdeLayout
                anchors.bottom:parent.bottom
                anchors.right:parent.right
                anchors.topMargin:15

                Button {
                    id:adminDialogApplyBtn
                    display:AbstractButton.TextBesideIcon
                    icon.name:"dialog-ok.svg"
                    text: i18nd("lliurex-access-control","Accept")
                    focus:true
                    font.family: "Quattrocento Sans Bold"
                    font.pointSize: 10
                    DialogButtonBox.buttonRole: DialogButtonBox.ApplyRole
                    Keys.onReturnPressed: adminDialogApplyBtn.clicked()
                    Keys.onEnterPressed: adminDialogApplyBtn.clicked()                    

                }

                Button {
                    id:adminDialogCancelBtn
                    display:AbstractButton.TextBesideIcon
                    icon.name:"dialog-cancel.svg"
                    text: i18nd("lliurex-access-control","Cancel")
                    focus:true
                    font.family: "Quattrocento Sans Bold"
                    font.pointSize: 10
                    DialogButtonBox.buttonRole:DialogButtonBox.RejectRole
                    Keys.onReturnPressed: adminDialogCancelBtn.clicked()
                    Keys.onEnterPressed: adminDialogCancelBtn.clicked()                    
       
                }

                onApplied:{
                    accessControlBridge.manageLocalAdminDialog("Accept")
                }

                onRejected:{
                    accessControlBridge.manageLocalAdminDialog("Cancel")

                }
            }
        }
     }

    ChangesDialog{
        id:userChangesDialog
        dialogTitle:"Lliurex Access Control"+" - "+i18nd("lliurex-access-control","Control by users")
        dialogVisible:accessControlBridge.showUserChangesDialog
        dialogMsg:i18nd("lliurex-access-control","The are pending changes to apply.\nDo you want apply the changes or discard them?")
        Connections{
            target:userChangesDialog
            function onDialogApplyClicked(){
                applyChanges()
                
            }
            function onDiscardDialogClicked(){
                discardChanges()
            }

        }
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
            anchors.topMargin:5
            anchors.leftMargin:5

            Image{
                id:removeListDialogIcon
                source:"/usr/share/icons/breeze/status/64/dialog-warning.svg"
            }

            Text {
                id:removeListDialogText
                text:i18nd("lliurex-access-control","The user list is going to be delete.Do you wish to continue?")
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                anchors.left:removeListDialogIcon.right
                anchors.verticalCenter:removeListDialogIcon.verticalCenter
                anchors.leftMargin:10
            }
           
           DialogButtonBox {
                buttonLayout:DialogButtonBox.KdeLayout
                anchors.bottom:parent.bottom
                anchors.right:parent.right
                anchors.topMargin:15

                Button {
                    id:removeListDialogApplyBtn
                    display:AbstractButton.TextBesideIcon
                    icon.name:"dialog-ok.svg"
                    text: i18nd("lliurex-access-control","Accept")
                    focus:true
                    font.family: "Quattrocento Sans Bold"
                    font.pointSize: 10
                    DialogButtonBox.buttonRole: DialogButtonBox.ApplyRole
                    Keys.onReturnPressed: removeListDialogApplyBtn.clicked()
                    Keys.onEnterPressed: removeListDialogApplyBtn.clicked()                    

                }

                Button {
                    id:removeListDialogCancelBtn
                    display:AbstractButton.TextBesideIcon
                    icon.name:"dialog-cancel.svg"
                    text: i18nd("lliurex-access-control","Cancel")
                    focus:true
                    font.family: "Quattrocento Sans Bold"
                    font.pointSize: 10
                    DialogButtonBox.buttonRole:DialogButtonBox.RejectRole
                    Keys.onReturnPressed: removeListDialogCancelBtn.clicked()
                    Keys.onEnterPressed: removeListDialogCancelBtn.clicked()                    

                }

                onApplied:{
                    accessControlBridge.removeUserList()
                    userList.structModel=accessControlBridge.usersModel
                    removeListDialog.close()
                }

                onRejected:{
                    accessControlBridge.manageLocalAdminDialog("Cancel")
                    removeListDialog.close()

                }
            }
        }
    }

    CustomPopup{
        id:synchronizePopup
     }

    Timer{
        id:timer
    }

    function delay(delayTime,cb){
        timer.interval=delayTime;
        timer.repeat=true;
        timer.triggered.connect(cb);
        timer.start()
    }


    function getMessageText(code){

        var msg="";
        switch (code){
            case 10:
                msg=i18nd("lliurex-access-control","Changes applied successfully");
                break;
            case -30:
                msg=i18nd("lliurex-access-control","It is not possible to deactive access control by user");
                break;
            case -40:
                msg=i18nd("lliurex-access-control","Unable to update the user list");
                break;                
            case -80:
                msg=i18nd("lliurex-access-control","There are no users selected to lock their access");
                break;
            case -90:
                msg=i18nd("lliurex-access-control","The user already exists in the list");
                break;
            case -100:
                msg=i18nd("lliurex-access-control","It is not possible to lock the user with which you are configuring the access control");
                break;
		break;
            default:
                break;
        }
        return msg;

    }

    function getMessageType(type){

        switch (type){
            case "Info":
                return Kirigami.MessageType.Information
            case "Success":
                return Kirigami.MessageType.Positive
            case "Error":
                return Kirigami.MessageType.Error
            case "Warning":
                return Kirigami.MessageType.Warning

        }

    } 

    function applyChanges(){
        synchronizePopup.open()
        synchronizePopup.popupMessage=i18nd("lliurex-access-control", "Apply changes. Wait a moment...")
        delay(500, function() {
            if (accessControlBridge.closePopUp){
                synchronizePopup.close(),
                timer.stop()
            }
          })
    } 

    function discardChanges(){
        synchronizePopup.open()
        synchronizePopup.popupMessage=i18nd("lliurex-access-control", "Restoring previous values. Wait a moment...")
        delay(1000, function() {
            if (accessControlBridge.closePopUp){
                synchronizePopup.close(),
                timer.stop()
            }
          })
    }      
} 
