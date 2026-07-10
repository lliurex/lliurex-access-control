import org.kde.plasma.core as PlasmaCore
import org.kde.kirigami as Kirigami
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle{
    color:"transparent"
    Text{ 
        text:i18nd("lliurex-access-control","Restrict access by center")
        font.family: "Quattrocento Sans Bold"
        font.pointSize: 16
    }

    GridLayout{
        id:generalLayout
        rows:2
        flow: GridLayout.TopToBottom
        rowSpacing:10
        width:parent.width-10
        anchors.left:parent.left

        Kirigami.InlineMessage {
            id: messageLabel
            visible:cdcStackBridge.showSettingsCDCMessage.show
            text:getMessageText(cdcStackBridge.showSettingsCDCMessage.msgCode)
            type:getMessageType(cdcStackBridge.showSettingsCDCMessage.type)
            Layout.minimumWidth:490
            Layout.fillWidth:true
            Layout.topMargin: 40
        }

        GridLayout{
            id: optionsGrid
            rows: 2
            flow: GridLayout.TopToBottom
            rowSpacing:5
            Layout.topMargin: messageLabel.visible?0:50

            CheckBox {
                id:cdcControlCb
                text:i18nd("lliurex-access-control","Activated access control by center on this computer")
                checked:cdcStackBridge.isAccessDenyCDCEnabled
                font.pointSize: 10
                focusPolicy: Qt.NoFocus
                Keys.onReturnPressed: cdcControlCb.toggled()
                Keys.onEnterPressed: cdcControlCb.toggled()
                onToggled:{
                   cdcStackBridge.manageCDCAccessControl(checked)
                }

                Layout.alignment:Qt.AlignLeft
                Layout.bottomMargin:15
            }
            RowLayout {
                Layout.fillWidth: true
                Layout.alignment:Qt.AlignLeft

                Text{
                    id:cdcLabel
                    text:i18nd("lliurex-access-control","Lock access to users who do not belong to the center:")
                    font.pointSize:10

                }
                TextField{
                    id:cdcEntry
                    text:cdcStackBridge.cdcCode
                    enabled:cdcControlCb.checked
                    maximumLength:8
                    font.pointSize:10
                    horizontalAlignment:TextInput.AlignLeft
                    focus:true
                    implicitWidth:75
                    onTextEdited:{
                        if ((cdcEntry.text=="")||(cdcEntry.text.length==8)){
                            wait(1000, function() {
                                waitTimer.stop()
                                cdcStackBridge.manageCDCCodeChange(cdcEntry.text)
                            })
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
            enabled:cdcStackBridge.settingsCDCChanged
            Keys.onReturnPressed: applyBtn.clicked()
            Keys.onEnterPressed: applyBtn.clicked()
            onClicked:{
                applyChanges()
                closeTimer.stop()
                cdcStackBridge.applyCDCChanges()
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
            enabled:cdcStackBridge.settingsCDCChanged
            Keys.onReturnPressed: cancelBtn.clicked()
            Keys.onEnterPressed: cancelBtn.clicked()
            onClicked:{
                discardChanges()
                closeTimer.stop()
                cdcStackBridge.cancelCDCChanges()
            }
        }
    } 

    ChangesDialog{
        id:cdcChangesDialog
        dialogVisible:cdcStackBridge.showCDCChangesDialog
        dialogMsg:i18nd("lliurex-access-control","The are pending changes to apply.\nDo you want apply the changes or discard them?")
        Connections{
            target:cdcChangesDialog
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
        id:delayTimer
    }

    function delay(delayTime,cb){
        delayTimer.interval=delayTime;
        delayTimer.repeat=true;
        delayTimer.triggered.connect(cb);
        delayTimer.start()
    }

    Timer{
        id:waitTimer
    }

    function wait(delayTime,cb){
        waitTimer.interval=delayTime;
        waitTimer.repeat=true;
        waitTimer.triggered.connect(cb);
        waitTimer.start()
    }


    function getMessageText(code){

        switch (code){
            case 10:
                return i18nd("lliurex-access-control","Changes applied successfully")
            case -50:
                return i18nd("lliurex-access-control","It is not possible to deactive access control by center")
            case -60:
                return i18nd("lliurex-access-control","Unable to update the center code")
            case -90:
                return i18nd("lliurex-access-control","No center code has been indicated")
            case -101:
                 return i18nd("lliurex-access-control","Center code is not valid")           
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
        delayTimer.stop()
        delay(500, function() {
            if (mainStackBridge.closePopUp){
                synchronizePopup.close(),
                delayTimer.stop()
            }
        })
    } 

    function discardChanges(){
        synchronizePopup.open()
        synchronizePopup.popupMessage=i18nd("lliurex-access-control", "Restoring previous values. Wait a moment...")
        delayTimer.stop()
        delay(1000, function() {
            if (mainStackBridge.closePopUp){
                synchronizePopup.close(),
                delayTimer.stop()

            }
        })
    }  
} 
