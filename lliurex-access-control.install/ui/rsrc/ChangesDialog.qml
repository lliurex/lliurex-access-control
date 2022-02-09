import QtQuick 2.6
import QtQuick.Controls 2.6
import QtQuick.Layouts 1.12
import QtQuick.Dialogs 1.3


Dialog {
    id: customDialog
    property alias dialogTitle:customDialog.title
    property alias dialogVisible:customDialog.visible
    property alias dialogMsg:dialogText.text
    signal dialogApplyClicked
    signal discardDialogClicked

    visible:dialogVisible
    title:dialogTitle
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
            text:dialogMsg
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
                dialogApplyClicked()
                accessControlBridge.manageSettingsDialog("Accept")

            }

            onDiscarded:{
                discardDialogClicked(),
                accessControlBridge.manageSettingsDialog("Discard")

            }

            onRejected:{
                accessControlBridge.manageSettingsDialog("Cancel")

            }
        }
    }
 }