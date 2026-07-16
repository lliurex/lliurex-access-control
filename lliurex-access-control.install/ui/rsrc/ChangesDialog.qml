import QtQuick 2.15      
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3
import org.kde.kirigami 2.16 as Kirigami


Dialog {
    id: customDialog
    property string dialogTitle:""
    property bool dialogVisible:false
    property string dialogMsg:""

    visible:dialogVisible
    title:customDialog.title
    modality:Qt.WindowModal

    contentItem: Rectangle {
        color: "#ebeced"
        implicitWidth: 460
        implicitHeight: 115

        RowLayout {
            id: contentLayout
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.margins: 0
            spacing: 15

            Kirigami.Icon {
                id: dialogIcon
                source: "dialog-warning"
                Layout.preferredWidth: 64
                Layout.preferredHeight: 64
                visible: status === Image.Ready
            }

            Text {
                id: dialogText
                text: customDialog.dialogMsg
                font.pointSize: 10
                Layout.fillWidth: true
                Layout.rightMargin:10
                wrapMode: Text.WordWrap
            }
        }

      
        DialogButtonBox {
            buttonLayout:DialogButtonBox.KdeLayout
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            anchors.margins: 10

            Button {
                id:dialogApplyBtn
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-ok"
                text: i18nd("lliurex-access-control","Apply")
                focus:true
                font.pointSize: 10
                DialogButtonBox.buttonRole: DialogButtonBox.ApplyRole
                Keys.onReturnPressed: dialogApplyBtn.clicked()
                Keys.onEnterPressed: dialogApplyBtn.clicked()
                onClicked: mainStackBridge.manageSettingsDialog("Accept")

            }

            Button {
                id:dialogDiscardBtn
                display:AbstractButton.TextBesideIcon
                icon.name:"delete"
                text: i18nd("lliurex-access-control","Discard")
                focus:true
                font.pointSize: 10
                DialogButtonBox.buttonRole: DialogButtonBox.DestructiveRole
                Keys.onReturnPressed: dialogDiscardBtn.clicked()
                Keys.onEnterPressed: dialogDiscardBtn.clicked()
                onClicked: mainStackBridge.manageSettingsDialog("Discard")


            }

            Button {
                id:dialogCancelBtn
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-cancel"
                text: i18nd("lliurex-access-control","Cancel")
                focus:true
                font.pointSize: 10
                DialogButtonBox.buttonRole:DialogButtonBox.RejectRole
                Keys.onReturnPressed: dialogCancelBtn.clicked()
                Keys.onEnterPressed: dialogCancelBtn.clicked()
                onClicked: mainStackBridge.manageSettingsDialog("Cancel")
        
            }
    
        }
    }
 }
