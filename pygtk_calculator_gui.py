import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GObject
from calculator import calculate_expression

class HistoryBox(GObject.GObject):    
    __gsignals__ = {
        'history-updated': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self):
        GObject.GObject.__init__(self)
        self.history_of_calculations = []

    def add_to_history(self, calculation):
        self.history_of_calculations.append(calculation)
        self.emit('history-updated')

    def get_history(self):
        return self.history_of_calculations
    

class CalculatorWindow(Gtk.Window):
    def __init__(self, history_box):
        Gtk.Window.__init__(self, title="Kalkulator")

        self.expression = ""
        self.history_box = history_box

        grid = Gtk.Grid()
        self.set_child(grid)

        self.entry = Gtk.Entry()
        self.entry.set_text("0")
        grid.attach(self.entry, 0, 0, 1, 1)

        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+',
            '←'  # Backspace button
        ]

        button_grid = Gtk.Grid()
        grid.attach(button_grid, 0, 1, 1, 1)

        row = 0
        col = 0
        for label in buttons:
            button = Gtk.Button()
            button.set_label(label)
            button.connect("clicked", self.on_button_clicked)
            button_grid.attach(button, col, row, 1, 1)
            col += 1
            if col > 3:
                col = 0
                row += 1

    def on_button_clicked(self, button):
        label = button.get_label()
        if label == '=':
            try:
                result = calculate_expression(self.expression)
                self.entry.set_text(str(result))
                self.history_box.add_to_history(f"{self.expression} = {result}")
                self.expression = str(result)
            except Exception as e:
                self.show_error_dialog(str(e))
        else:
            if label == 'C':
                self.expression = ""
            elif label == '←':
                self.expression = self.expression[:-1]
                self.entry.set_text(self.expression)
            else:
                self.expression += label
            self.entry.set_text(self.expression)

    def show_error_dialog(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.connect("response", self.on_dialog_response)
        dialog.present()

    def on_dialog_response(self, dialog, response_id):
        dialog.destroy()
        
class HistoryWindow(Gtk.Window):
    def __init__(self, history_box):
        Gtk.Window.__init__(self, title="Historia Obliczeń")

        self.history_box = history_box
        
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.set_child(scrolled_window)

        self.textview = Gtk.TextView()
        self.textview.set_editable(False)  
        self.textview.set_cursor_visible(False)  
        scrolled_window.set_child(self.textview)
        
        self.history_box.connect('history-updated', self.update_history_list)
        self.update_history_list()

    def update_history_list(self, *_):
        history_text = "\n".join(self.history_box.get_history())
        buffer = self.textview.get_buffer()
        buffer.set_text(history_text)
            
class AboutWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="O Programie")

        grid = Gtk.Grid()
        self.set_child(grid)

        label = Gtk.Label(label="Aplikacja Kalkulator v1.0\nAutor: Twój Autor")
        grid.attach(label, 0, 0, 1, 1)


class MenuWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Menu")

        self.history_box = HistoryBox()

        self.grid = Gtk.Grid()
        self.set_child(self.grid)
    
        button_calculator = Gtk.Button(label="Kalkulator")
        button_calculator.connect("clicked", self.on_calculator_clicked)
        self.grid.attach(button_calculator, 0, 0, 1, 1)

        button_history = Gtk.Button(label="Historia Obliczeń")
        button_history.connect("clicked", self.on_history_clicked)
        self.grid.attach(button_history, 0, 1, 1, 1)

        button_about = Gtk.Button(label="O Programie")
        button_about.connect("clicked", self.on_about_clicked)
        self.grid.attach(button_about, 0, 2, 1, 1)
        
    def on_calculator_clicked(self, button):
        calculator_window = CalculatorWindow(self.history_box)
        calculator_window.present()

    def on_history_clicked(self, button):
        history_window = HistoryWindow(self.history_box)
        history_window.present()

    def on_about_clicked(self, button):
        about_window = AboutWindow()
        about_window.present()

        
class CalculatorApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.calculator", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        win = MenuWindow(app)
        win.present()


if __name__ == "__main__":
    app = CalculatorApplication()
    app.run()
