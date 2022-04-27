import QtQuick 2.15 
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15


Item {
	id:menuItem
	Layout.preferredWidth: 160
	Layout.preferredHeight: 35

	property alias optionIcon:menuOptionIcon.source
	property alias optionText:menuOptionText.text
  property alias optionEnabled:menuOption.enabled
	signal menuOptionClicked()

	Rectangle{
		id:menuOption
		width:160
		height:35
		color:"transparent"
		border.color:"transparent"
    enabled:optionEnabled

		Row{
			spacing:5
			anchors.verticalCenter:menuOption.verticalCenter
			leftPadding:5
            
      Image{
        id:menuOptionIcon
        source:optionIcon
      }

      Text {
        id:menuOptionText
        text:optionText
        anchors.verticalCenter:menuOptionIcon.verticalCenter
      }  
    }

    MouseArea {
    	id: mouseAreaOption
      	anchors.fill: parent
        hoverEnabled:true

        onEntered: {
          menuOption.color="#add8e6"
        }
        onExited: {
          menuOption.color="transparent"
        }
        onClicked: {
        	menuOptionClicked()
        }
    }   
  }
}


