import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

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
                optionIcon:"actions/24/user-group-new.svg"
                optionEnabled:true
                onMenuOptionClicked:mainStackBridge.manageTransitions(0)
            }

            MenuOptionBtn {
                id:userItem
                optionText:i18nd("lliurex-access-control","Control by users")
                optionIcon:"actions/24/im-user.svg"
                optionEnabled:userStackBridge.enableUserConfig
                onMenuOptionClicked:mainStackBridge.manageTransitions(1)
            }

            MenuOptionBtn {
                id:cdcItem
                optionText:i18nd("lliurex-access-control","Control by center")
                optionIcon:"actions/24/view-institution.svg"
                visible:cdcStackBridge.isCDCAccessControlAllowed
                onMenuOptionClicked:mainStackBridge.manageTransitions(2)
            }

            MenuOptionBtn {
                id:helpItem
                optionText:i18nd("lliurex-access-control","Help")
                optionIcon:"actions/24/help-contents.svg"
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

