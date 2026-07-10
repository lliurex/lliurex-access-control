import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    id: mainGrid
    spacing: 10

    Rectangle{
        id: sideBar
        width:175
        Layout.fillHeight:true
        border.color: palette.mid

        ColumnLayout {
            id: menuLayout
            Layout.fillWidth:true
            Layout.fillHeight: true
            spacing: 0

            MenuOptionBtn {
                id:groupItem
                optionText:i18nd("lliurex-access-control","Control by groups")
                optionIcon:"group"
                optionEnabled:true
                onMenuOptionClicked:mainStackBridge.manageTransitions(0)
            }

            MenuOptionBtn {
                id:userItem
                optionText:i18nd("lliurex-access-control","Control by users")
                optionIcon:"user"
                optionEnabled:userStackBridge.enableUserConfig
                onMenuOptionClicked:mainStackBridge.manageTransitions(1)
            }

            MenuOptionBtn {
                id:cdcItem
                optionText:i18nd("lliurex-access-control","Control by center")
                optionIcon:"view-institution"
                visible:cdcStackBridge.isCDCAccessControlAllowed
                onMenuOptionClicked:mainStackBridge.manageTransitions(2)
            }

            MenuOptionBtn {
                id:helpItem
                optionText:i18nd("lliurex-access-control","Help")
                optionIcon:"help-contents"
                onMenuOptionClicked:mainStackBridge.openHelp()
            }

            Item {
                    Layout.fillHeight:true

            }

        }
    }

    StackView{
        id: optionsView
        Layout.fillWidth:true
        Layout.fillHeight: true
        
        property int currentIndex:mainStackBridge.currentOptionsStack
       
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
            NumberAnimation {
                property: "opacity"
                from: 0
                to: 1
                duration: 60
            }
        }
        replaceExit: Transition {
            NumberAnimation {
                property: "opacity"
                from: 1
                to: 0
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

    CustomPopup{
        id:synchronizePopup
    }
}

