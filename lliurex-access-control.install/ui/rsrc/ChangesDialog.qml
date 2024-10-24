import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


Dialog {
    id: customDialog
    property alias dialogTitle:customDialog.title
    property alias dialogVisible:customDialog.visible
    property alias dialogMsg:dialogText.text
    signal dialogApplyClicked
    signal discardDialogClicked
    signal cancelDialogClicked

    visible:dialogVisible
    title:dialogTitle
    modal:true
    anchors.centerIn:Overlay.overlay
    background:Rectangle{
        color:"#ebeced"
        border.color:"#b8b9ba"
        border.width:1
        radius:5.0
    }

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
                focus:true
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                DialogButtonBox.buttonRole: DialogButtonBox.ApplyRole
                Keys.onReturnPressed: dialogApplyBtn.clicked()
                Keys.onEnterPressed: dialogApplyBtn.clicked()

            }

            Button {
                id:dialogDiscardBtn
                display:AbstractButton.TextBesideIcon
                icon.name:"delete.svg"
                text: i18nd("lliurex-access-control","Discard")
                focus:true
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                DialogButtonBox.buttonRole: DialogButtonBox.DestructiveRole
                Keys.onReturnPressed: dialogDiscardBtn.clicked()
                Keys.onEnterPressed: dialogDiscardBtn.clicked()


            }

            Button {
                id:dialogCancelBtn
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-cancel.svg"
                text: i18nd("lliurex-access-control","Cancel")
                focus:true
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                DialogButtonBox.buttonRole:DialogButtonBox.RejectRole
                Keys.onReturnPressed: dialogCancelBtn.clicked()
                Keys.onEnterPressed: dialogCancelBtn.clicked()
        
            }

            onApplied:{
                dialogApplyClicked()
                mainStackBridge.manageSettingsDialog("Accept")

            }

            onDiscarded:{
                discardDialogClicked(),
                mainStackBridge.manageSettingsDialog("Discard")

            }

            onRejected:{
                cancelDialogClicked(),
                mainStackBridge.manageSettingsDialog("Cancel")

            }
        }
    }
 }
