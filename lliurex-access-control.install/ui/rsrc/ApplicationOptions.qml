import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15


GridLayout{
    id: optionsGrid
    columns: 2
    flow: GridLayout.LeftToRight
    columnSpacing:10

    Rectangle{
        width:160
        height:380
        border.color: "#d3d3d3"

        GridLayout{
            id: menuGrid
            rows:4 
            flow: GridLayout.TopToBottom
            rowSpacing:0

            MenuOptionBtn {
                id:groupItem
                optionText:i18nd("lliurex-access-control","Control by groups")
                optionIcon:"/usr/share/icons/breeze/actions/16/group.svg"
                Connections{
                    function onMenuOptionClicked(){
                        /*optionsLayout.currentIndex=0;*/
                        accessControlBridge.manageTransitions(0)
                    }
                }
            }

            MenuOptionBtn {
                id:userItem
                optionText:i18nd("lliurex-access-control","Control by users")
                optionIcon:"/usr/share/icons/breeze/actions/16/user.svg"
                Connections{
                    function onMenuOptionClicked(){
                        /*optionsLayout.currentIndex=1;*/
                        accessControlBridge.manageTransitions(1)
                   
                    }
                }
            }

            MenuOptionBtn {
                id:cdcItem
                optionText:i18nd("lliurex-access-control","Control by center")
                optionIcon:"/usr/share/icons/breeze/actions/16/view-institution.svg"
                Connections{
                    function onMenuOptionClicked(){
                        accessControlBridge.manageTransitions(2)
                   
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

        UsersSettings{
            id:userSettings
        }

        CdcSettings{
            id:cdcSettings
        }

    }
}

