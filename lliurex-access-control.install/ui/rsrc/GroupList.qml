import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQml.Models 2.8
import org.kde.plasma.components 2.0 as Components



Rectangle {
    property alias structModel:listGroup.model
    property alias listCount:listGroup.count
    property alias structEnabled:listGroup.enabled

    id:groupTable
    visible: true
    Layout.fillWidth:true
    Layout.fillHeight:true
    color:"white"
    border.color: "#d3d3d3"

    ListModel{
        id: folderModel
    }    
    ListView{
        id: listGroup
        model:structModel
        enabled:structEnabled
        anchors.fill:parent
        currentIndex:-1
        clip: true
        focus: true
        boundsBehavior: Flickable.StopAtBounds
        highlightFollowsCurrentItem:true
        highlightMoveDuration: 0
        highlightResizeDuration: 0
        delegate: ListDelegateGroupItem{
            width:groupTable.width
            groupId:model.groupId
            isLocked:model.isLocked
            description:model.description
        }

     } 

}

