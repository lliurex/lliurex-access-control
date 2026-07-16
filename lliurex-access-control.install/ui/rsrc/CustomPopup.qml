import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15


Popup {
    id: popUpWaiting
    width: 570
    height: 100
    anchors.centerIn: Overlay.overlay
    modal: true
    focus: true
    visible: mainStackBridge.showPopUp.show
    closePolicy: Popup.NoAutoClose

    background: Rectangle {
        color: palette.window
        border.color: palette.mid
        radius: 4
    }

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 10

        Image{
            id:spinnerImage
            source: "loading.png"
            Layout.preferredWidth: 24
            Layout.preferredHeight: 24
            Layout.alignment: Qt.AlignHCenter
            fillMode: Image.PreserveAspectFit
            smooth:false
            antialiasing:false
                rotation:0
        }
            
        Timer{
            id:rotationTimer
            running:(spinnerImage!==null && popUpWaiting!==null) && spinnerImage.visible && popUpWaiting.visible
            repeat:true
            interval:100

            onTriggered:{
                if (spinnerImage && typeof spinnerImage.rotation!="undefined"){
                    var nextRotation= spinnerImage.rotation-30
                    if (nextRotation<0){
                        nextRotation=330
                    }
                    spinnerImage.rotation=nextRotation
                 }else{
                    stop()
                 }   

            }
        }
        
        Text {
            id: popupText
            text:getMessage(mainStackBridge.showPopUp.msgCode)
            font.pointSize: 10
            color: palette.windowText
            Layout.alignment: Qt.AlignHCenter
            horizontalAlignment: Text.AlignHCenter
        }
    }

    function getMessage(code){

        switch (code){
            case 30:
                return i18nd("lliurex-access-control", "Apply changes. Wait a moment...")
            case 31:
                return i18nd("lliurex-access-control", "Restoring previous values. Wait a moment...")
            default:
                return ""
        }
    }
}
