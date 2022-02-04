import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.kirigami 2.6 as Kirigami
import QtQuick 2.6
import QtQuick.Controls 2.6
import QtQuick.Layouts 1.12

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
        Layout.fillWidth: true
        anchors.left:parent.left

        Kirigami.InlineMessage {
            id: messageLabel
            visible:accessControlBridge.showSettingsUserMessage[0]
            text:getMessageText(accessControlBridge.showSettingsUserMessage[1])
            type:getMessageType(accessControlBridge.showSettingsUserMessage[2])
            Layout.minimumWidth:470
            Layout.maximumWidth:470
            Layout.topMargin: 40
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
                Layout.alignment:Qt.AlignLeft

                Text{
                    id:usersList
                    text:i18nd("lliurex-access-control","Users with restricted access:")
                    font.pointSize:10
                    Layout.leftMargin:80
                }
            }
            RowLayout {
                id:entryRow
                Layout.fillWidth: true
                Layout.alignment:Qt.AlignLeft
                visible:false

                TextField{
                    id:userEntry
                    placeholderText:i18nd("lliurex-acces-control","Username")
                    implicitWidth:310
                    font.pointSize:10

                }
                Button{
                   id:applyUserBtn
                   display:AbstractButton.IconOnly
                   icon.name:"dialog-ok.svg"
                   onClicked:{
                        accessControlBridge.addUser(userEntry.text)
                        entryRow.visible=false
                   }
                }

            }
            RowLayout{
                Layout.fillWidth: true
                Layout.alignment:Qt.AlignHCenter

                UserList{
                    id:userList
                    structModel:accessControlBridge.usersModel
                    structEnabled:userControlCb.checked
                }
                ColumnLayout{
                    Layout.leftMargin:10
                    Layout.alignment:Qt.AlignHCenter
                    Button{
                        id:addUserBtn
                        display:AbstractButton.TextBesideIcon
                        icon.name:"contact-new.svg"
                        text:i18nd("lliurex-access-control","Add user")
                        implicitWidth:110
                        enabled:userControlCb.checked
                        onClicked:{
                            entryRow.visible=true
                            userEntry.text=""
                        }
                    }    
                    Button{
                        id:removeListBtn
                        display:AbstractButton.TextBesideIcon
                        icon.name:"delete.svg"
                        text:i18nd("lliurex-access-control","Remove List")
                        implicitWidth:110
                        enabled:userControlCb.checked
                        onClicked:{
                            accessControlBridge.removeUserList()
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
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-ok.svg"
            text:i18nd("lliurex-access-control","Apply")
            Layout.preferredHeight:40
            enabled:accessControlBridge.settingsUserChanged
            onClicked:{
                synchronizePopup.open()
                synchronizePopup.popupMessage=i18nd("lliurex-access-control", "Apply changes. Wait a moment...")
                delay(1000, function() {
                    if (accessControlBridge.closePopUp){
                        synchronizePopup.close(),
                        timer.stop(),
                        userList.structModel=accessControlBridge.usersModel
                    }
                  })
                accessControlBridge.applyUserChanges()
            }
        }
        Button {
            id:cancelBtn
            visible:true
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-cancel.svg"
            text:i18nd("lliurex-access-control","Cancel")
            Layout.preferredHeight: 40
            enabled:accessControlBridge.settingsUserChanged
            onClicked:{
                synchronizePopup.open()
                synchronizePopup.popupMessage=i18nd("lliurex-access-control", "Restoring previous values. Wait a moment...")
                delay(1000, function() {
                    if (accessControlBridge.closePopUp){
                        synchronizePopup.close(),
                        timer.stop(),
                        userList.structModel=accessControlBridge.usersModel

                    }
                  })
                accessControlBridge.cancelChanges()
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
                msg=i18nd("lliurex-access-control","It is not possible to remove user list");
                break;
            case -40:
                msg=i18nd("lliurex-access-control","It is not possible to deactive access control by user");
                break;
            case -50:
                msg=i18nd("lliurex-access-control","Unable to update the list of groups with restricted access");
                break;
            case -60:
                msg=i18nd("lliurex-access-control","Unable to update the user list");
                break;                
            case -80:
                msg=i18nd("lliurex-access-control","No group selected");
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
        }

    }    
} 
