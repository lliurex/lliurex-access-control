import QtQuick 2.6
import QtQuick.Controls 2.6
import QtQml.Models 2.6
import org.kde.plasma.components 2.0 as Components
import org.kde.plasma.extras 2.0 as PlasmaExtras



Rectangle {
    property alias structModel:listUser.model
    property alias listCount:listUser.count
    property alias structEnabled:listUser.enabled

    id:userTable
    visible: true
    width: 345; height: 125
    color:"white"
    border.color: "#d3d3d3"

    ListModel{
        id: userModel
    } 
    PlasmaExtras.ScrollArea{
        implicitWidth:parent.width
        implicitHeight:130
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
                userId:model.userId
                isLocked:model.isLocked
            }

      } 
    }
}

