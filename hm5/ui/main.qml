import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    width: 600
    height: 500
    title: "Поиск рецептиков"

    Text {
        anchors {
            top: parent.top
            left: parent.left
            leftMargin: 16
        }
        text: "Найди рецепт:"
        font.pixelSize: 22
    }

     TextField {
            id: editText
            width: parent.width

            anchors {
             top: parent.top
             topMargin: 32
             left: parent.left
             leftMargin: 16
             right: searchButton.left
             rightMargin: 16
        }
     }

        Button {
            id: searchButton
            height: 40
            text: qsTr("Поиск")

             anchors {
             top: parent.top
             topMargin: 32
             right: parent.right
             rightMargin: 16
             }

             onClicked: {
                searcher.search(editText.text)
            }
        }

        ListView {
            width: 200; height: 250
            model: linksModel
            anchors {
             top: editText.bottom
             topMargin: 16
             left: parent.left
             leftMargin: 16
             }
            delegate: Item {
                id: linkListItem
                width: ListView.view.width
                height: 40
                Column {
                    Text {
                        text: display.path
                        onLinkActivated: Qt.openUrlExternally(link)
                     }
                }
            }
        }
}