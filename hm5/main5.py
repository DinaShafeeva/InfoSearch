import sys

from PyQt5.QtCore import QAbstractListModel, QModelIndex, Qt, QObject, pyqtProperty, pyqtSlot
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine


class Searcher(QObject):
    def __init__(self):
        QObject.__init__(self)

    @pyqtSlot(str)
    def search(self, arg1):
        links.addLink(LinkListItem(arg1))
        engine.rootContext().setContextProperty('linksModel', links)


class LinkListItem(QObject):
    def __init__(self, link: str, parent=None):
        super().__init__(parent)
        self.link = link

    @pyqtProperty('QString')
    def path(self):
        return self.link


class LinkList(QAbstractListModel):
    def __init__(self, links: list, parent=None):
        super().__init__(parent)
        self.links = links

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.links)

    def data(self, index: QModelIndex, role=None):
        if role == Qt.DisplayRole:
            return self.links[index.row()]

    def addLink(self, link):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.links.append(link)
        self.endInsertRows()


links = LinkList([])
if __name__ == '__main__':
    app = QGuiApplication(sys.argv)

    links.addLink(LinkListItem('AbcЫ'))
    links.addLink(LinkListItem('Def'))
    links.addLink(LinkListItem('Ghi'))

    searcher = Searcher()
    engine = QQmlApplicationEngine()
    engine.quit.connect(app.quit)
    engine.rootContext().setContextProperty("searcher", searcher)
    engine.load('./ui/main.qml')

    engine.rootContext().setContextProperty('linksModel', links)
    sys.exit(app.exec())
