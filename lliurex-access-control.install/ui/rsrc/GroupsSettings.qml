import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.kirigami 2.6 as Kirigami
import QtQuick 2.6
import QtQuick.Controls 2.6
import QtQuick.Layouts 1.12
import QtQuick.Dialogs 1.3

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
            visible:accessControlBridge.showSettingsGroupMessage[0]
            text:getMessageText(accessControlBridge.showSettingsGroupMessage[1])
            type:getMessageType(accessControlBridge.showSettingsGroupMessage[2])
            Layout.minimumWidth:470
            Layout.maximumWidth:470
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
                structModel:accessControlBridge.groupsModel
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
            enabled:accessControlBridge.settingsGroupChanged
            onClicked:{
                applyChanges()
                accessControlBridge.applyGroupChanges()
            }
        }
        Button {
            id:cancelBtn
            visible:true
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-cancel.svg"
            text:i18nd("lliurex-access-control","Cancel")
            Layout.preferredHeight: 40
            enabled:accessControlBridge.settingsGroupChanged
            onClicked:{
                discardChanges()
                accessControlBridge.cancelGroupChanges()
            }
        }
    } 


    Dialog {
        id: customGroupDialog
        visible:accessControlBridge.showGroupChangesDialog
        title:"Lliurex Access Control"+" - "+i18nd("lliurex-access-control","Control by groups")
        modality:Qt.WindowModal

        contentItem: Rectangle {
            color: "#ebeced"
            implicitWidth: 400
            implicitHeight: 105
            anchors.topMargin:5
            anchors.leftMargin:5

            Image{
                id:dialogIcon
                source:"/usr/share/icons/breeze/status/64/dialog-warning.svg"

            }
            
            Text {
                id:dialogText
                text:i18nd("lliurex-access-control","The are pending changes to apply.\nDo you want apply the changes or discard them?")
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                anchors.left:dialogIcon.right
                anchors.verticalCenter:dialogIcon.verticalCenter
                anchors.leftMargin:10
            
            }
          
            DialogButtonBox {
                buttonLayout:DialogButtonBox.KdeLayout
                anchors.bottom:parent.bottom
                anchors.right:parent.right
                anchors.topMargin:15

                Button {
                    id:dialogApplyBtn
                    display:AbstractButton.TextBesideIcon
                    icon.name:"dialog-ok.svg"
                    text: i18nd("lliurex-access-control","Apply")
                    font.family: "Quattrocento Sans Bold"
                    font.pointSize: 10
                    DialogButtonBox.buttonRole: DialogButtonBox.ApplyRole
                }

                Button {
                    id:dialogDiscardBtn
                    display:AbstractButton.TextBesideIcon
                    icon.name:"delete.svg"
                    text: i18nd("lliurex-access-control","Discard")
                    font.family: "Quattrocento Sans Bold"
                    font.pointSize: 10
                    DialogButtonBox.buttonRole: DialogButtonBox.DestructiveRole

                }

                Button {
                    id:dialogCancelBtn
                    display:AbstractButton.TextBesideIcon
                    icon.name:"dialog-cancel.svg"
                    text: i18nd("lliurex-access-control","Cancel")
                    font.family: "Quattrocento Sans Bold"
                    font.pointSize: 10
                    DialogButtonBox.buttonRole:DialogButtonBox.RejectRole
                }

                onApplied:{
                    applyChanges()
                    accessControlBridge.manageSettingsDialog("Accept")
                
                }

                onDiscarded:{
                    discardChanges()
                    accessControlBridge.manageSettingsDialog("Discard")

                }

                onRejected:{
                    accessControlBridge.manageSettingsDialog("Cancel")

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
            case -10:
                msg=i18nd("lliurex-access-control","It is not possible to deactive access control by group");
                break;
            case -20:
                msg=i18nd("lliurex-access-control","Unable to update the list of groups with restricted access");
                break;
            case -70:
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

    function applyChanges(){
        synchronizePopup.open()
        synchronizePopup.popupMessage=i18nd("lliurex-access-control", "Apply changes. Wait a moment...")
        delay(1000, function() {
            if (accessControlBridge.closePopUp){
                synchronizePopup.close(),
                timer.stop(),
                groupList.structModel=accessControlBridge.groupsModel
            }
          })
    } 

    function discardChanges(){
        synchronizePopup.open()
        synchronizePopup.popupMessage=i18nd("lliurex-access-control", "Restoring previous values. Wait a moment...")
        delay(1000, function() {
            if (accessControlBridge.closePopUp){
                synchronizePopup.close(),
                timer.stop(),
                groupList.structModel=accessControlBridge.groupsModel

            }
          })
    }  
} 
