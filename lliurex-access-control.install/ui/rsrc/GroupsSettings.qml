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
            text:i18nd("lliurex-access-control","Restrict access by group")
            font.pointSize: 16
        }

    
        Kirigami.InlineMessage {
            id: messageLabel
            visible:groupStackBridge.showSettingsGroupMessage.show
            text:getMessageText(groupStackBridge.showSettingsGroupMessage.msgCode)
            type:getMessageType(groupStackBridge.showSettingsGroupMessage.type)
            Layout.fillWidth:true
        }

        ColumnLayout{
            id: optionsGrid
            spacing:5

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
            }

            Text{
                id:groupsList
                text:i18nd("lliurex-access-control","Groups with restricted access:")
                font.pointSize:10
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
        anchors.margins:15
        spacing:10

        Button {
            id:applyBtn
            visible:true
            focus:true
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-ok"
            text:i18nd("lliurex-access-control","Apply")
            enabled:groupStackBridge.hasGroupChanges
            Keys.onReturnPressed: applyBtn.clicked()
            Keys.onEnterPressed: applyBtn.clicked()
            onClicked:{
                closeTimer.stop()
                groupStackBridge.applyGroupChanges()
            }
        }

        Button {
            id:cancelBtn
            visible:true
            focus:true
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-cancel"
            text:i18nd("lliurex-access-control","Cancel")
            enabled:groupStackBridge.hasGroupChanges
            Keys.onReturnPressed: cancelBtn.clicked()
            Keys.onEnterPressed: cancelBtn.clicked()
            onClicked:{
                closeTimer.stop()
                groupStackBridge.cancelGroupChanges()
            }
        }
    } 

    ChangesDialog{
        id:groupChangesDialog
        dialogVisible:groupStackBridge.showGroupChangesDialog
        dialogMsg:i18nd("lliurex-access-control","The are pending changes to apply.\nDo you want apply the changes or discard them?")
        
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
   
} 
