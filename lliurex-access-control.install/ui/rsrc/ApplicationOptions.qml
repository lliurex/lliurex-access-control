import QtQuick 2.6
import QtQuick.Controls 2.6
import QtQuick.Layouts 1.12


GridLayout{
    id: optionsGrid
    columns: 2
    flow: GridLayout.LeftToRight
    columnSpacing:10

    Rectangle{
        width:150
        height:380
        border.color: "#d3d3d3"

        GridLayout{
            id: menuGrid
            rows:2 
            flow: GridLayout.TopToBottom
            rowSpacing:0

            MenuOptionBtn {
                id:groupItem
                optionText:i18nd("lliurex-access-control","Control by groups")
                optionIcon:"/usr/share/icons/breeze/actions/16/group.svg"
                Connections{
                    function onMenuOptionClicked(){
                        optionsLayout.currentIndex=0;
                    }
                }
            }

            MenuOptionBtn {
                id:helpItem
                optionText:i18nd("lliurex-access-control","Help")
                optionIcon:"/usr/share/icons/breeze/actions/16/help-contents.svg"
                Connections{
                    function onMenuOptionClicked(){
                        accessControlBridge.openHelp();
                    }
                }
            }
        }
    }

    StackLayout {
        id: optionsLayout
        currentIndex:accessControlBridge.currentOptionsStack
        implicitHeight: 380
        Layout.alignment:Qt.AlignHCenter

        GroupsSettings{
            id:groupsSettings
        }

    }
}

