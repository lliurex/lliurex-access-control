import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


GridLayout{
    id: optionsGrid
    columns: 2
    flow: GridLayout.LeftToRight
    columnSpacing:10

    Rectangle{
        width:165
        Layout.fillHeight:true
        border.color: "#d3d3d3"

        GridLayout{
            id: menuGrid
            rows:4 
            flow: GridLayout.TopToBottom
            rowSpacing:0

            MenuOptionBtn {
                id:groupItem
                optionText:i18nd("lliurex-access-control","Control by groups")
                optionIcon:"/usr/share/icons/breeze/actions/22/group.svg"
                optionEnabled:true
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.manageTransitions(0)
                    }
                }
            }

            MenuOptionBtn {
                id:userItem
                optionText:i18nd("lliurex-access-control","Control by users")
                optionIcon:"/usr/share/icons/breeze/actions/22/user.svg"
                optionEnabled:userStackBridge.enableUserConfig
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.manageTransitions(1)
                   
                    }
                }
            }

            MenuOptionBtn {
                id:cdcItem
                optionText:i18nd("lliurex-access-control","Control by center")
                optionIcon:"/usr/share/icons/breeze/actions/22/view-institution.svg"
                optionEnabled:cdcStackBridge.isCDCAccessControlAllowed
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.manageTransitions(2)
                   
                    }
                }
            }

            MenuOptionBtn {
                id:helpItem
                optionText:i18nd("lliurex-access-control","Help")
                optionIcon:"/usr/share/icons/breeze/actions/22/help-contents.svg"
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.openHelp();
                    }
                }
            }
        }
    }

    StackView{
        id: optionsView
        property int currentIndex:mainStackBridge.currentOptionsStack
        Layout.fillWidth:true
        Layout.fillHeight: true
        Layout.alignment:Qt.AlignHCenter
       
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
                duration:60
            }
        }
        replaceExit: Transition {
            PropertyAnimation {
                property: "opacity"
                from: 1
                to:0
                duration: 60
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

