import QtQuick 2.15

import Edupals.N4D.Agent 1.0 as N4DAgent


Rectangle {
    width:  childrenRect.width
    height:  childrenRect.height
    anchors.centerIn: parent
    color: "#e9e9e9"

    N4DAgent.Login
    {
        showAddress:false
        address:'localhost'
        showCancel: false
        inGroups:["sudo","admins"]
        
        /*anchors.centerIn: parent*/
        
        onLogged: {
            tunnel.onTicket(ticket),
            showAddress=true;

        }
    }
}
