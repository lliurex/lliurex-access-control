import QtQuick 2.6
import QtQuick.Controls 2.6
import QtQml.Models 2.6


Rectangle {
    property alias structModel:listGroup.model
    property alias listCount:listGroup.count
    property alias structEnabled:listGroup.enabled

    id:groupTable
    visible: true
    width: 470; height: 125
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
        delegate: listdelegate
        clip: true
        boundsBehavior: Flickable.StopAtBounds
     }         

    Component{
        id: listdelegate
        Rectangle{
            id: menuItem
            width: 470
            height:visible?30:0
            color:"transparent"

            CheckBox {
                id:groupCheck
                checked:isChecked
                onToggled:{
                    accessControlBridge.manageGroupChecked([id,checked])
                }
                anchors.left:parent.left
                anchors.leftMargin:5
                anchors.verticalCenter:parent.verticalCenter

            }

            Text{
                id: text
                text: description
                width:400
                clip: true
                anchors.left:groupCheck.right
                anchors.leftMargin:5
                anchors.verticalCenter:parent.verticalCenter
            }
        }
    }
}

