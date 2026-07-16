import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQml.Models 2.8
import org.kde.plasma.components 2.0 as Components
import org.kde.plasma.components 3.0 as PC3
import org.kde.kirigami 2.16 as Kirigami



Rectangle {
    property alias structModel:listUser.model
    property alias listCount:listUser.count
    property alias structEnabled:listUser.enabled

    id:userTable
    visible: true
    Layout.fillWidth:true
    Layout.fillHeight:true
    color:"white"
    border.color: "#d3d3d3"
    border.width: 1

    ListModel{
        id: userModel
    } 

    PC3.ScrollView{
        id:mainScroll
        anchors.fill:parent
   
        ListView{
            id: listUser
            model:structModel
            enabled:true
            currentIndex:-1
            clip: true
            focus: true
            boundsBehavior: Flickable.StopAtBounds
           
            highlightFollowsCurrentItem:true
            highlightMoveDuration: 0
            highlightResizeDuration: 0
            
            delegate: ListDelegateUserItem{
                width:userTable.width-(mainScroll.ScrollBar.vertical.visible ? mainScroll.ScrollBar.vertical.width : 0)
                userId:model.userId
                isLocked:model.isLocked
            }

            Kirigami.PlaceholderMessage { 
                id: emptyUserHint
                anchors.centerIn: parent
                width: parent.width - (Kirigami.Units.largeSpacing * 4)
                visible:listUser.count>0?false:true
                text: i18nd("lliurex-access-control","The user list is empty")
                icon.name:"lliurex-access-control"
            }
      } 
    }
}

