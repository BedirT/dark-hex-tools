import gi
import sys
sys.path.append('../../')

from Projects.SVerify.util import choose_strategy, load_file
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

import xdot


class MyDotWindow(xdot.DotWindow):

    def __init__(self):
        xdot.DotWindow.__init__(self)
        self.dotwidget.connect('clicked', self.on_url_clicked)

    def on_url_clicked(self, widget, url, event):
        dialog = Gtk.MessageDialog(
            parent=self,
            buttons=Gtk.ButtonsType.OK,
            message_format="clicked")
        dialog.connect('response', lambda dialog, response: dialog.destroy())
        dialog.run()
        return True


def main():
    _, filename = choose_strategy()
    dotcode = load_file(f'Data/{filename}/tree.dot')

    dotcode = dotcode.encode('UTF-8')

    window = MyDotWindow()
    window.set_dotcode(dotcode)
    window.connect('delete-event', Gtk.main_quit)
    Gtk.main()


if __name__ == '__main__':
    main()