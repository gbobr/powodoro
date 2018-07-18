import gi
gi.require_version('Wnck', '3.0')

from gi.repository import Wnck, GLib
from threading import Timer

class FocusTracker:

    def track_pid(self, pid, focus_time, on_lost, on_focus):
        print("Begin FocusTracker on pid %d" % pid)
        self.focus_time = focus_time
        self.unfocused_time = 0
        self.focused = True
        self.pid = pid
        self.on_focus = on_focus
        self.on_lost = on_lost
        self.check_focus()

    def _gtk_check(self):
        s = Wnck.Screen.get_default()
        s.force_update()
        window = s.get_active_window()

        if window.get_pid() != self.pid:
            self.unfocused_time = self.unfocused_time + 1
            print("Loosing focus, %d seconds" % self.unfocused_time)
            if self.focused == True and self.unfocused_time > self.focus_time:
                print("Lost focus, pid: %s" % window.get_pid())
                self.focused = False
                self.on_lost()
        else:
            self.unfocused_time = 0
            if self.focused == False:
                print("Regained focus, pid: %s" % window.get_pid())
                self.focused = True
                self.on_focus()

    def check_focus(self):
        GLib.idle_add(self._gtk_check)
        self.timer = Timer(1, self.check_focus)
        self.timer.start()

    def stop(self):
        self.timer.cancel()