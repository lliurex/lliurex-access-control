import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQml.Models 2.8
import org.kde.kirigami 2.16 as Kirigami


ItemDelegate{
    id: listGroupItem
    
    property string groupId
    property bool isLocked
    property string description

    enabled:true
    height:50

    hoverEnabled:true

    leftPadding:15
    rightPadding:15
    topPadding:0
    bottomPadding:0

    background:Rectangle {
        anchors.fill:parent
        anchors.margins:5

        color: (listGroupItem.hovered) 
               ? Qt.hsla(Kirigami.Theme.highlightColor.hslHue, 
                 Kirigami.Theme.highlightColor.hslSaturation, 
                 Kirigami.Theme.highlightColor.hslLightness, 
                 0.15)
               :"transparent"
        radius:6
        border.width:1
        border.color:(listGroupItem.hovered)
                      ?Kirigami.Theme.highlightColor
                      :"transparent"

    }

    contentItem:RowLayout {
        
        anchors.fill:parent
        anchors.leftMargin:listGroupItem.leftPadding
        anchors.rightMargin:listGroupItem.rightPadding
        spacing:10

        CheckBox {
            id:groupCheck
            checked:isLocked
            Layout.alignment: Qt.AlignVCenter

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
