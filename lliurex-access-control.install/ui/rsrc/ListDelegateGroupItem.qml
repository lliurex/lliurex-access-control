import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


ItemDelegate{
    id: listGroupItem
    
    property string groupId
    property bool isLocked
    property string description

    enabled:true
    height:45

    leftPadding:15
    rightPadding:15

    contentItem:RowLayout {
        
        spacing:10

        CheckBox {
            id:groupCheck
            checked:isLocked
            onToggled:{
                groupStackBridge.manageGroupChecked({"groupId":groupId,"isLocked":checked})
            }
           
            ToolTip.delay: 1000
            ToolTip.timeout: 3000
            ToolTip.visible: hovered
            ToolTip.text:{
                if (groupCheck.checked){
                    i18nd("lliurex-access-control","Check to unlock access to this group")
                }else{
                    i18nd("lliurex-access-control","Check to lock access to this group")                   
                }
            }

        }

        Text{
            id: text
            text: description
            Layout.fillWidth: true
            Layout.preferredWidth: 300
            verticalAlignment: Text.AlignVCenter
        }

    }
}
