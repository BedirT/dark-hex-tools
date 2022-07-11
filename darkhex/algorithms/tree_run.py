import gi
from darkhex.utils.util import load_file

gi.require_version("Gtk", "3.0")

import xdot
from gi.repository import Gtk

Gtk.init_check()


class TreeRun(xdot.DotWindow):

    def __init__(self, folder_path):
        xdot.DotWindow.__init__(self)
        self.dotwidget.connect("clicked", self.on_url_clicked)
        self.folder_path = folder_path

    def on_url_clicked(self, widget, url, event):
        dialog = Gtk.MessageDialog(parent=self,
                                   buttons=Gtk.ButtonsType.OK,
                                   message_format="clicked")
        dialog.connect("response", lambda dialog, response: dialog.destroy())
        dialog.run()
        return True

    def tree_run(self):
        dotcode = load_file(
            f"{self.folder_path}/tree.dot")

        dotcode = dotcode.encode("UTF-8")

        self.set_dotcode(dotcode)
        self.connect("delete-event", Gtk.main_quit)
        Gtk.main()
