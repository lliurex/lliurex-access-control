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
                optionEnabled:true
                Connections{
                    function onMenuOptionClicked(){
                        accessControlBridge.manageTransitions(0)
                    }
                }
            }

            MenuOptionBtn {
                id:userItem
                optionText:i18nd("lliurex-access-control","Control by users")
                optionIcon:"/usr/share/icons/breeze/actions/16/user.svg"
                optionEnabled:true
                Connections{
                    function onMenuOptionClicked(){
                        accessControlBridge.manageTransitions(1)
                   
                    }
                }
            }

            MenuOptionBtn {
                id:cdcItem
                optionText:i18nd("lliurex-access-control","Control by center")
                optionIcon:"/usr/share/icons/breeze/actions/16/view-institution.svg"
                optionEnabled:accessControlBridge.isCDCAccessControlAllowed
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

    StackView{
        id: optionsView
        property int currentIndex:accessControlBridge.currentOptionsStack
        implicitHeight: 380
        Layout.fillWidth:true
        Layout.fillHeight: true
        
        initialItem:groupsView

        onCurrentIndexChanged:{
            switch (currentIndex){
                case 0:
                    optionsView.replace(groupsView)
                    break;
                case 1:
                    optionsView.replace(usersView)
                    break;
                case 2:
                    optionsView.replace(cdcView)
                    break;
            }
        }

        replaceEnter: Transition {
            PropertyAnimation {
                property: "opacity"
                from: 0
                to:1
                duration: 600
            }
        }
        replaceExit: Transition {
            PropertyAnimation {
                property: "opacity"
                from: 1
                to:0
                duration: 600
            }
        }

        Component{
            id:groupsView
            GroupsSettings{
                id:groupsSettings
            }
        }
        Component{
            id:usersView
            UsersSettings{
                id:userSettings
            }
        }
        Component{
            id:cdcView
            CdcSettings{
                id:cdcSettings
            }
        }

    }
}

