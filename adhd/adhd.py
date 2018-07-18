import gi
import screeninfo

from adhd.gui.tracker import FocusTracker

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Wnck', '3.0')

from gi.repository import Gtk, Gdk, Wnck, GObject


class WndReminder(Gtk.Window):

    def __init__(self, app, monitor):
        self.app = app;
        self.monitor = monitor;
        w = monitor.width
        Gtk.Window.__init__(self, title="PyADHD", decorated=False)
        self.move(monitor.x,0)
        self.set_default_size(w, 50)
        # Box
        self.box = Gtk.Box()
        self.add(self.box)
        # Button
        self.button = Gtk.Button(label="Snooze")
        self.button.connect("clicked", self.on_button_clicked)
        self.box.add(self.button)
        self.label = Gtk.Label(label="Go back to {task}!")
        self.box.add(self.label)
        self.set_keep_above(True)
        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1.0,0.5,0.5,1.0))

    def on_button_clicked(self, widget):
        self.app.hide_notifications()

class WndSelector(Gtk.Dialog):
    def __init__(self, app, parent):
        Gtk.Dialog.__init__(self, "Select window to track",parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)

        s = Wnck.Screen.get_default()
        s.force_update()

        name_store = Gtk.ListStore(int, str)

        for w in s.get_windows():
            name_store.append([w.get_pid(), w.get_name()])

        select = Gtk.ComboBox.new_with_model_and_entry(name_store)
        select.set_entry_text_column(1)
        select.connect("changed", self.on_combo_changed)

        box = self.get_content_area()
        box.add(select)
        self.show_all()

    def on_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            row_id, name = model[tree_iter][:2]
            print("Selected: ID=%d, name=%s" % (row_id, name))
            self.track_pid = row_id
        else:
            entry = combo.get_child()
            print("Entered: %s" % entry.get_text())


class AdhdApp:
    notification_windows = []

    def __init__(self):
        for m in screeninfo.get_monitors():
            w = WndReminder(self, m)
            self.notification_windows.append(w);

    def show_notifications(self):
        print("Showing notifications")
        for w in self.notification_windows:
            w.show_all()

    def hide_notifications(self):
        print("Hiding notifications")
        for w in self.notification_windows:
            w.hide()

    def track(self, pid):
        self.track_pid = pid
        print("Tracking PID %d" % self.track_pid)
        tracker = FocusTracker()
        tracker.track_pid(self.track_pid, 5, self.show_notifications, self.hide_notifications)

    def run(self):
        def selector_done(window, result):
            window.hide()
            self.track(window.track_pid)

        self.selector = WndSelector(self, None)
        self.selector.connect("response",selector_done)
        self.selector.show_all()


def app_main():
    app = AdhdApp()
    app.run()
    GObject.threads_init()
    Gtk.main()
