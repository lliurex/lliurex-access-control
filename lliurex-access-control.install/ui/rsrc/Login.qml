import QtQuick 2.6
import QtQuick.Controls 2.6
import QtQuick.Layouts 1.12
import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.kirigami 2.6 as Kirigami

Rectangle{
    visible: true
    Layout.fillWidth:true
    Layout.fillHeight: true
    color:"transparent"

    GridLayout {
        id: loginGrid
        rows: 6
        flow: GridLayout.TopToBottom
        Layout.topMargin: 10
        Layout.bottomMargin: 10
        anchors.centerIn:parent
        rowSpacing:10

        Item {
          	Layout.fillWidth: true
            Layout.topMargin:(mainLayout.Layout.minimumHeight-bannerBox.Layout.minimumHeight)/2-loginGrid.rows*30
        }
        RowLayout {
            Layout.fillWidth: true
            Layout.alignment:Qt.AlignHCenter
            Image{
              	id:imgUsername
              	source: "images/username.svg"
            }
            TextField {
                id:userEntry
                placeholderText:i18nd("lliurex-access-control","User")
                implicitWidth:280
                font.family: "Quattrocento Sans Bold"
          		  font.pointSize: 10
                Layout.alignment:Qt.AlignCenter
              }
          
        }
        RowLayout {
            Layout.fillWidth: true
            Layout.alignment:Qt.AlignHCenter
            Image{
              	id:imgPassword
              	source: "images/password.svg"
        	  }
            TextField {
                id:passwordEntry
                placeholderText:i18nd("lliurex-access-control","Password")
                echoMode:TextInput.Password
                implicitWidth: 280
                font.family: "Quattrocento Sans Bold"
          		font.pointSize: 10
                Layout.alignment:Qt.AlignCenter
            }
        }

      	RowLayout {
            Layout.fillWidth: true
            Layout.alignment:Qt.AlignHCenter
            
            Button {
                id:loginButton
                text: i18nd("lliurex-access-control","Login")
                focus:true
                Keys.onReturnPressed: loginButton.clicked()
                Keys.onEnterPressed: loginButton.clicked()

                onClicked: {
                    loginLabel.text=i18nd("lliurex-access-control","Validating user...")
                    loginLabel.color="black"
                    loginGrid.enabled=false
                    delay(100, function() {
                        if (!accessControlBridge.runningLogin){
                            loginLabel.text=""
                            loginGrid.enabled=true
                            timer.stop()
                        }
                    })
                    accessControlBridge.validate([userEntry.text,passwordEntry.text])
                }
            }
      
        }
         Kirigami.InlineMessage {
            id: messageLabel
            visible:accessControlBridge.showLoginMessage[0]
            text:i18nd("lliurex-access-control","Invalid user")
            type:Kirigami.MessageType.Error
            Layout.fillWidth: true
            Layout.minimumHeight:40
            Layout.leftMargin:10
            Layout.rightMargin:10
        }
        RowLayout{
            Layout.fillWidth: true
            Layout.alignment:Qt.AlignHCenter

            Text {
                id:loginLabel
                text: ""
                visible:true
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                color:"black"
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