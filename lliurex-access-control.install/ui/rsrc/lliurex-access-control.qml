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
    Component.onCompleted: {
        x = Screen.width / 2 - width / 2
        y = Screen.height / 2 - height /2
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
        Layout.minimumWidth:670
        Layout.preferredWidth:670
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
            property int currentIndex:accessControlBridge.currentStack
            Layout.minimumWidth:670
            Layout.preferredWidth:670
            Layout.minimumHeight:370
            Layout.preferredHeight:370
            Layout.alignment:Qt.AlignHCenter|Qt.AlignVCenter
            Layout.leftMargin:0
            Layout.fillWidth:true
            Layout.fillHeight: true
            initialItem:loadingView

            onCurrentIndexChanged:{
                switch(currentIndex){
                    case 0:
                        mainView.replace(loadingView)
                        break;
                    case 1:
                        mainView.replace(loginView)
                        break;
                    case 2:
                        mainView.replace(applicationOptionsView)
                        break;
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
                id:loginView
                Login{
                    id:login
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
        id:timer
    }

    function delay(delayTime,cb){
        timer.interval=delayTime;
        timer.repeat=true;
        timer.triggered.connect(cb);
        timer.start()
    }


}

