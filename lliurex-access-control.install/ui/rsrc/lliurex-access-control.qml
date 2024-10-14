import org.kde.plasma.core as PlasmaCore
import org.kde.kirigami as Kirigami
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

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
    Component.onCompleted: {
        x = Screen.width / 2 - width / 2
        y = Screen.height / 2 - height /2
    }

    
    onClosing:(close)=>{
        close.accepted=closing;
        mainStackBridge.closeApplication()
        delay(100, function() {
            if (mainStackBridge.closeGui){
                closing=true,
                closeTimer.stop(),           
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
        Layout.minimumWidth:675
        Layout.preferredWidth:675
        Layout.minimumHeight:500

        RowLayout {
            id: bannerBox
            Layout.alignment:Qt.AlignTop
            Rectangle{
                color: "#0049ac"
                Layout.minimumWidth:mainLayout.width
                Layout.preferredWidth:mainLayout.width
                Layout.fillWidth:true
                Layout.minimumHeight:120
                Layout.maximumHeight:120
                Image{
                    id:banner
                    source: "/usr/share/lliurex-access-control/rsrc/banner.png"
                    anchors.centerIn:parent
                }
            }
        }

        StackView {
            id: mainView
            property int currentIndex:mainStackBridge.currentStack
            Layout.minimumWidth:675
            Layout.preferredWidth:675
            Layout.minimumHeight:370
            Layout.preferredHeight:370
            Layout.alignment:Qt.AlignHCenter|Qt.AlignVCenter
            Layout.leftMargin:0
            Layout.fillWidth:true
            Layout.fillHeight: true
            initialItem:loadingView

            onCurrentIndexChanged:{
                switch (currentIndex){
                    case 0:
                        mainView.replace(loadingView)
                        break;
                    case 1:
                        mainView.replace(applicationOptionsView)
                }
            }

            replaceEnter: Transition {
                PropertyAnimation {
                    property: "opacity"
                    from: 0
                    to:1
                    duration: 600
                }
            }
            replaceExit: Transition {
                PropertyAnimation {
                    property: "opacity"
                    from: 1
                    to:0
                    duration: 600
                }
            }

            Component{
                id:loadingView
                Loading{
                    id:loading
                }
            }
            Component{
                id:applicationOptionsView
                ApplicationOptions{
                    id:applicationOptions
                }
            }

        }

    }

    Timer{
        id:closeTimer
    }

    function delay(delayTime,cb){
        closeTimer.interval=delayTime;
        closeTimer.repeat=true;
        closeTimer.triggered.connect(cb);
        closeTimer.start()
    }


}

