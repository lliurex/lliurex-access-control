import QtQuick
import QtQuick.Controls
import QtQml.Models
import org.kde.plasma.components as PC
import org.kde.kirigami as Kirigami



Rectangle {
    property alias structModel:listUser.model
    property alias listCount:listUser.count
    property alias structEnabled:listUser.enabled

    id:userTable
    visible: true
    width: 335; height: 125
    color:"white"
    border.color: "#d3d3d3"

    ListModel{
        id: userModel
    } 
    PC.ScrollView{
        implicitWidth:parent.width
        implicitHeight:parent.height
        anchors.leftMargin:10
   
        ListView{
            id: listUser
            anchors.fill:parent
            height: parent.height
            model:structModel
            enabled:true
            currentIndex:-1
            clip: true
            focus: true
            boundsBehavior: Flickable.StopAtBounds
            highlight: Rectangle { color: "#add8e6"; opacity:0.8;border.color:"#53a1c9" }
            highlightMoveDuration: 0
            highlightResizeDuration: 0
            delegate: ListDelegateUserItem{
                width:userTable.width
                userId:model.userId
                isLocked:model.isLocked
            }
            Kirigami.PlaceholderMessage { 
                id: emptyUserHint
                anchors.centerIn: parent
                width: parent.width - (Kirigami.Units.largeSpacing * 4)
                visible:listUser.count>0?false:true
                text: i18nd("lliurex-access-control","The user list is empty")
            }
      } 
    }
}

