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
            result = calculate_expression(self.expression)
            self.entry.set_text(str(result))
            self.history_box.add_to_history(f"{self.expression} = {result}")
            self.expression = str(result)
        else:
            if label == 'C':
                self.expression = ""
            elif label == '←':
                self.expression = self.expression[:-1]
                self.entry.set_text(self.expression)
            else:
                self.expression += label
            self.entry.set_text(self.expression)


class HistoryWindow(Gtk.Window):
    def __init__(self, history_box):
        Gtk.Window.__init__(self, title="Historia Obliczeń")

        self.history_box = history_box
        self.listbox = Gtk.ListBox() 
        grid = Gtk.Grid()
        self.set_child(grid)
        grid.attach(self.listbox, 0, 0, 1, 1)
        self.connect("destroy", self.on_destroy)

        self.history_box.connect('history-updated', self.update_history_list)
        self.update_history_list()

    def update_history_list(self, *args):
        listbox = Gtk.ListBox()
        self.set_child(listbox)
        for calculation in self.history_box.get_history():
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label=calculation)
            row.set_child(label)
            listbox.append(row)
            
    def on_destroy(self, widget):
        # When the window is closed, hide it instead of destroying it
        widget.hide()

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
        self.set_child(self.grid)  # Używamy set_child zamiast add

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
