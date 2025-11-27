import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.plasma.components as PC


Popup {
    id: customDialog
    property alias dialogVisible:customDialog.visible
    property alias dialogMsg:dialogText.text
    signal dialogApplyClicked
    signal discardDialogClicked
    signal cancelDialogClicked

    modal:true
    closePolicy:Popup.NoAutoClose
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
      
        RowLayout {
            id:btnBox
            anchors.bottom:parent.bottom
            anchors.right:parent.right
            anchors.topMargin:15
            spacing:10

            PC.Button {
                id:dialogApplyBtn
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-ok.svg"
                text: i18nd("lliurex-access-control","Apply")
                focus:true
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                Keys.onReturnPressed: dialogApplyBtn.clicked()
                Keys.onEnterPressed: dialogApplyBtn.clicked()
                onClicked:{
                    dialogApplyClicked(),
                    mainStackBridge.manageSettingsDialog("Accept")

                }

            }

            PC.Button {
                id:dialogDiscardBtn
                display:AbstractButton.TextBesideIcon
                icon.name:"delete.svg"
                text: i18nd("lliurex-access-control","Discard")
                focus:true
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                Keys.onReturnPressed: dialogDiscardBtn.clicked()
                Keys.onEnterPressed: dialogDiscardBtn.clicked()
                onClicked:{
                    discardDialogClicked(),
                    mainStackBridge.manageSettingsDialog("Discard")

                }


            }

            PC.Button {
                id:dialogCancelBtn
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-cancel.svg"
                text: i18nd("lliurex-access-control","Cancel")
                focus:true
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                Keys.onReturnPressed: dialogCancelBtn.clicked()
                Keys.onEnterPressed: dialogCancelBtn.clicked()
                onClicked:{
                    cancelDialogClicked(),
                    mainStackBridge.manageSettingsDialog("Cancel")
                }
        
            }
        }
    }
 }
