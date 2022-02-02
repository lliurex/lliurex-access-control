import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.kirigami 2.6 as Kirigami
import QtQuick 2.6
import QtQuick.Controls 2.6
import QtQuick.Layouts 1.12

Rectangle{
    color:"transparent"
    Text{ 
        text:i18nd("lliurex-access-control","Restrict access by group")
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
            visible:accessControlBridge.showSettingsMessage[0]
            text:getMessageText(accessControlBridge.showSettingsMessage[1])
            type:getMessageType(accessControlBridge.showSettingsMessage[2])
            Layout.minimumWidth:430
            Layout.maximumWidth:430
            Layout.topMargin: 40
        }

        GridLayout{
            id: optionsGrid
            rows: 3
            flow: GridLayout.TopToBottom
            rowSpacing:5
            Layout.topMargin: messageLabel.visible?0:50

            CheckBox {
                id:groupControlCb
                text:i18nd("lliurex-access-control","Activated access control by group on this computer")
                checked:accessControlBridge.isAccessDenyGroupEnabled
                font.pointSize: 10
                focusPolicy: Qt.NoFocus
                onToggled:{
                   accessControlBridge.manageGroupAccessControl(checked)
                }

                Layout.alignment:Qt.AlignLeft
                Layout.bottomMargin:15
            }
            RowLayout {
                Layout.fillWidth: true
                Layout.alignment:Qt.AlignHCenter

                Text{
                    id:groupsList
                    text:i18nd("lliurex-access-control","Groups with restricted access:")
                    font.pointSize:10

                }
            }
            GroupList{
                id:groupList
                structModel:accessControlBridge.model
                structEnabled:groupControlCb.checked
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
            enabled:accessControlBridge.settingsChanged
            onClicked:{
                synchronizePopup.open()
                synchronizePopup.popupMessage=i18nd("lliurex-access-control", "Apply changes. Wait a moment...")
                delay(1000, function() {
                    if (accessControlBridge.closePopUp){
                        synchronizePopup.close(),
                        timer.stop(),
                        groupList.structModel=accessControlBridge.model
                    }
                  })
                accessControlBridge.applyChanges()
            }
        }
        Button {
            id:cancelBtn
            visible:true
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-cancel.svg"
            text:i18nd("lliurex-access-control","Cancel")
            Layout.preferredHeight: 40
            enabled:accessControlBridge.settingsChanged
            onClicked:{
                synchronizePopup.open()
                synchronizePopup.popupMessage=i18nd("lliurex-access-control", "Restoring previous values. Wait a moment...")
                delay(1000, function() {
                    if (accessControlBridge.closePopUp){
                        synchronizePopup.close(),
                        timer.stop(),
                        groupList.structModel=accessControlBridge.model

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
                msg=i18nd("lliurex-acccess-control","Changes applied successfully");
                break;
            case -10:
                msg=i18nd("lliurex-access-control","It is not possible to deactive access control by group");
                break;
            case -20:
                msg=i18nd("lliurex-access-control","Unable to update the list of groups with restricted access");
                break;
            case -30:
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