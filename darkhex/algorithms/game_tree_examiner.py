import gi
import darkhex.utils.util as util

gi.require_version("Gtk", "3.0")

import xdot
from gi.repository import Gtk

Gtk.init_check()


class GameTreeRunner(xdot.DotWindow):

    def __init__(self, tree_name):
        """
        Initializes the GameTreeRunner.

        Args:
            tree_name (str): The name of the tree to be run. The tree
            should be included in data/game_trees.
        """
        xdot.DotWindow.__init__(self)
        self.dotwidget.connect("clicked", self.on_url_clicked)
        self.tree_name = tree_name

    def on_url_clicked(self, widget, url, event):
        dialog = Gtk.MessageDialog(parent=self,
                                   buttons=Gtk.ButtonsType.OK,
                                   message_format="clicked")
        dialog.connect("response", lambda dialog, response: dialog.destroy())
        dialog.run()
        return True

    def tree_run(self):
        dotcode = util.load_file(
            f"{util.PathVars.game_trees}{self.tree_name}/tree.dot")

        dotcode = dotcode.encode("UTF-8")

        self.set_dotcode(dotcode)
        self.connect("delete-event", Gtk.main_quit)
        Gtk.main()
