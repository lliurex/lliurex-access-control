import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.kirigami 2.6 as Kirigami
import QtQuick 2.6
import QtQuick.Controls 2.6
import QtQuick.Layouts 1.12
import QtQuick.Window 2.2
import QtQuick.Dialogs 1.3

ApplicationWindow {

    property bool closing: false
    id:mainWindow
    visible: true
    title: "LliureX Access Control"
    property int margin: 1
    width: mainLayout.implicitWidth + 2 * margin
    height: mainLayout.implicitHeight + 2 * margin
    minimumWidth: mainLayout.Layout.minimumWidth + 2 * margin
    minimumHeight: mainLayout.Layout.minimumHeight + 2 * margin
    maximumWidth: mainLayout.Layout.maximumWidth + 2 * margin
    maximumHeight: mainLayout.Layout.maximumHeight + 2 * margin
    Component.onCompleted: {
        x = Screen.width / 2 - width / 2
        y = Screen.height / 2 - height / 2
    }

    
    onClosing: {
        close.accepted=closing;
        accessControlBridge.closeApplication()
        delay(100, function() {
            if (accessControlBridge.closeGui){
                closing=true,
                timer.stop(),           
                mainWindow.close();

            }else{
                closing=false;
            }
        })
        
    }
    
    ColumnLayout {
        id: mainLayout
        anchors.fill: parent
        anchors.margins: margin
        Layout.minimumWidth:650
        Layout.maximumWidth:650
        Layout.minimumHeight:500
        Layout.maximumHeight:500

        RowLayout {
            id: bannerBox
            Layout.alignment:Qt.AlignTop
            Layout.minimumHeight:120
            Layout.maximumHeight:120

            Image{
                id:banner
                source: "/usr/share/lliurex-access-control/rsrc/banner.png"
            }
        }

        StackLayout {
            id: stackLayout
            currentIndex:accessControlBridge.currentStack
            implicitWidth: 650
            Layout.alignment:Qt.AlignHCenter
            Layout.leftMargin:0
            Layout.fillWidth:true
            Layout.fillHeight: true

            Loading{
                id:loading
            }

            ApplicationOptions{
                id:applicationOptions
            }

        }

        Dialog {
            id: customDialog
            visible:accessControlBridge.showChangesDialog
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
                        accessControlBridge.manageSettingsDialog("Accept")
                    
                    }

                    onDiscarded:{
                        accessControlBridge.manageSettingsDialog("Discard")

                    }

                    onRejected:{
                        accessControlBridge.manageSettingsDialog("Cancel")

                    }
                }
            }
         }

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


}

