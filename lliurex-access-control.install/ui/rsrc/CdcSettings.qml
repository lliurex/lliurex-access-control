import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.plasma.core as PlasmaCore
import org.kde.kirigami as Kirigami

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
            text:i18nd("lliurex-access-control","Restrict access by center")
            font.pointSize: 16
        }


        Kirigami.InlineMessage {
            id: messageLabel
            visible:cdcStackBridge.showSettingsCDCMessage.show
            text:getMessageText(cdcStackBridge.showSettingsCDCMessage.msgCode)
            type:getMessageType(cdcStackBridge.showSettingsCDCMessage.type)
            Layout.fillWidth:true

        }

        ColumnLayout{
            id: optionsGrid
            spacing: 5

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
            enabled:cdcStackBridge.settingsCDCChanged
            Keys.onReturnPressed: applyBtn.clicked()
            Keys.onEnterPressed: applyBtn.clicked()
            onClicked:{
                closeTimer.stop()
                cdcStackBridge.applyCDCChanges()
            }
        }
        Button {
            id:cancelBtn
            visible:true
            focus:true
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-cancel"
            text:i18nd("lliurex-access-control","Cancel")
            enabled:cdcStackBridge.settingsCDCChanged
            Keys.onReturnPressed: cancelBtn.clicked()
            Keys.onEnterPressed: cancelBtn.clicked()
            onClicked:{
                closeTimer.stop()
                cdcStackBridge.cancelCDCChanges()
            }
        }
    } 

    ChangesDialog{
        id:cdcChangesDialog
        dialogVisible:cdcStackBridge.showCDCChangesDialog
        dialogMsg:i18nd("lliurex-access-control","The are pending changes to apply.\nDo you want apply the changes or discard them?")

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
    
} 
