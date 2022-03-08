import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQml.Models 2.8
import org.kde.plasma.components 2.0 as Components



Rectangle {
    property alias structModel:listGroup.model
    property alias listCount:listGroup.count
    property alias structEnabled:listGroup.enabled

    id:groupTable
    visible: true
    width: 490; height: 125
    color:"white"
    border.color: "#d3d3d3"

    ListModel{
        id: folderModel
    }    
    ListView{
        id: listGroup
        anchors.fill:parent
        height: parent.height
        model:structModel
        enabled:structEnabled
        currentIndex:-1
        clip: true
        focus: true
        boundsBehavior: Flickable.StopAtBounds
        highlight: Rectangle { color: "#add8e6"; opacity:0.8;border.color:"#53a1c9" }
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

