import org.kde.plasma.core as PlasmaCore
import org.kde.kirigami as Kirigami
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

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
        anchors.left:parent.left
        width:parent.width-10
        height:parent.height-90
        enabled:true
        Kirigami.InlineMessage {
            id: messageLabel
            visible:groupStackBridge.showSettingsGroupMessage.show
            text:getMessageText(groupStackBridge.showSettingsGroupMessage.msgCode)
            type:getMessageType(groupStackBridge.showSettingsGroupMessage.type)
            Layout.minimumWidth:490
            Layout.fillWidth:true
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
                checked:groupStackBridge.isGroupAccessControlEnabled
                font.pointSize: 10
                focusPolicy: Qt.NoFocus
                Keys.onReturnPressed: groupControlCb.toggled()
                Keys.onEnterPressed: groupControlCb.toggled()
                onToggled:{
                   groupStackBridge.manageGroupAccessControl(checked)
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
                structModel:groupStackBridge.groupsModel
                structEnabled:groupControlCb.checked
                Layout.fillHeight:true
                Layout.fillWidth:true
 
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
            enabled:groupStackBridge.hasGroupChanges
            Keys.onReturnPressed: applyBtn.clicked()
            Keys.onEnterPressed: applyBtn.clicked()
            onClicked:{
                applyChanges()
                closeTimer.stop()
                groupStackBridge.applyGroupChanges()
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
            enabled:groupStackBridge.hasGroupChanges
            Keys.onReturnPressed: cancelBtn.clicked()
            Keys.onEnterPressed: cancelBtn.clicked()
            onClicked:{
                discardChanges()
                closeTimer.stop()
                groupStackBridge.cancelGroupChanges()
            }
        }
    } 

    ChangesDialog{
        id:groupChangesDialog
        dialogVisible:groupStackBridge.showGroupChangesDialog
        dialogMsg:i18nd("lliurex-access-control","The are pending changes to apply.\nDo you want apply the changes or discard them?")
        Connections{
            target:groupChangesDialog
            function onDialogApplyClicked(){
                applyChanges()
                
            }
            function onDiscardDialogClicked(){
                discardChanges()
            }
            function onCancelDialogClicked(){
                closeTimer.stop()
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

        switch (code){
            case 10:
                return i18nd("lliurex-access-control","Changes applied successfully")
            case -10:
                return i18nd("lliurex-access-control","It is not possible to deactive access control by group")
            case -20:
                return i18nd("lliurex-access-control","Unable to update the list of groups with restricted access")
            case -70:
                return i18nd("lliurex-access-control","There are no groups selected to lock their access")
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

    function applyChanges(){
        synchronizePopup.open()
        synchronizePopup.popupMessage=i18nd("lliurex-access-control", "Apply changes. Wait a moment...")
        delay(500, function() {
            if (mainStackBridge.closePopUp){
                synchronizePopup.close(),
                timer.stop()
            }
          })
    } 

    function discardChanges(){
        synchronizePopup.open()
        synchronizePopup.popupMessage=i18nd("lliurex-access-control", "Restoring previous values. Wait a moment...")
        delay(1000, function() {
            if (mainStackBridge.closePopUp){
                synchronizePopup.close(),
                timer.stop()

            }
          })
    }  
} 
