import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami


Popup {
    id: customDialog
    property bool dialogVisible: false
    visible: dialogVisible

    property alias dialogMsg: dialogText.text

    modal:true
    closePolicy:Popup.NoAutoClose
    anchors.centerIn:Overlay.overlay

    background:Rectangle{
        color:"#ebeced"
        border.color:"#b8b9ba"
        border.width:1
        radius:5.0
    }

    contentItem: Item {
        implicitWidth: 400
        implicitHeight: 105

        RowLayout {
            id: contentRow
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            spacing: 15

            Kirigami.Icon {
                id: iconInternal
                source:"dialog-warning"
                Layout.preferredWidth: Kirigami.Units.iconSizes.huge
                Layout.preferredHeight: Kirigami.Units.iconSizes.huge
            }
            
            Text {
                id: dialogText
                font.pointSize: 10
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                verticalAlignment: Text.AlignVCenter
                color: "#31363b"
            }
        }
      
        RowLayout {
            id:btnBox
            anchors.bottom:parent.bottom
            anchors.right:parent.right
            anchors.topMargin:10
            spacing:10

            Button {
                id:dialogApplyBtn
                icon.name:"dialog-ok"
                text: i18nd("lliurex-access-control","Apply")
                focus:true
                Keys.onReturnPressed: dialogApplyBtn.clicked()
                Keys.onEnterPressed: dialogApplyBtn.clicked()
                onClicked:{
                    mainStackBridge.manageSettingsDialog("Accept")

                }

            }

            Button {
                id:dialogDiscardBtn
                display:AbstractButton.TextBesideIcon
                icon.name:"delete"
                text: i18nd("lliurex-access-control","Discard")
                focus:true
                Keys.onReturnPressed: dialogDiscardBtn.clicked()
                Keys.onEnterPressed: dialogDiscardBtn.clicked()
                onClicked:{
                    mainStackBridge.manageSettingsDialog("Discard")

                }


            }

            Button {
                id:dialogCancelBtn
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-cancel"
                text: i18nd("lliurex-access-control","Cancel")
                focus:true
                Keys.onReturnPressed: dialogCancelBtn.clicked()
                Keys.onEnterPressed: dialogCancelBtn.clicked()
                onClicked:{
                    mainStackBridge.manageSettingsDialog("Cancel")
                }
        
            }
        }
    }
 }
