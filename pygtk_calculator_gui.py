import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GObject, Gdk
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
    def __init__(self, history_box, menu_bar):
        Gtk.Window.__init__(self, title="Kalkulator")
        self.set_default_size(400, 426)

        self.set_name("calculator-window")
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path("styles.css")

        context = Gtk.StyleContext()
        screen = Gdk.Screen.get_default()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.expression = ""
        self.history_box = history_box
        self.menu_bar = menu_bar

        self.connect("destroy", self.on_window_destroy)  

        grid = Gtk.Grid()
        self.add(grid)
        
        grid.attach(self.menu_bar, 0, 0, 1, 1)

        self.entry = Gtk.Entry()
        self.entry.set_text("0")
        grid.attach(self.entry, 0, 1, 1, 1)

        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+',
            '←' 
        ]

        button_grid = Gtk.Grid()
        grid.attach(button_grid, 0, 2, 1, 1)

        row = 0
        col = 0
        for label in buttons:
            button = Gtk.Button(label=label)
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
        dialog.run()
        dialog.destroy()

    def on_dialog_response(self, dialog, response_id):
        dialog.destroy()
        
    def on_window_destroy(self, window):
        window.destroy()
        
class HistoryWindow(Gtk.Window):
    def __init__(self, history_box, menu_bar):
        Gtk.Window.__init__(self, title="Historia Obliczeń")

        self.history_box = history_box
        self.menu_bar = menu_bar
        self.connect("destroy", self.on_window_destroy) 
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        vbox.pack_start(self.menu_bar, False, False, 0)  # Dodajemy menu bar

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        vbox.pack_start(scrolled_window, True, True, 0)
        
        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)
        scrolled_window.add(self.textview)
        
        self.history_box.connect('history-updated', self.update_history_list)
        self.update_history_list()

    def update_history_list(self, *_):
        history_text = "\n".join(self.history_box.get_history())
        buffer = self.textview.get_buffer()
        buffer.set_text(history_text)
    
    def on_window_destroy(self, window):
        window.destroy()
        
class AboutWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="O Programie")
        self.connect("destroy", self.on_window_destroy) 
        
        grid = Gtk.Grid()
        self.add(grid)

        label = Gtk.Label(label="Aplikacja Kalkulator v1.0\nAutor: Twój Autor")
        grid.attach(label, 0, 0, 1, 1)

    def on_window_destroy(self, window):
        window.destroy()

 
class CalculatorApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.calculator", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect("activate", self.on_activate)
        self.history_box = HistoryBox()
        self.windows = []  # Lista przechowująca otwarte okna

        
    def on_activate(self, app):
        win = CalculatorWindow(self.history_box, self.build_menu_bar())
        # win = HistoryWindow(self.history_box, self.menu_bar)
        self.windows.append(win)  # Dodaj otwarte okno do listy
        win.show_all()

        
    def build_menu_bar(self):
        menu_bar = Gtk.MenuBar()

        # Tworzenie sekcji "Application"
        menu_application = Gtk.Menu()
        application_menu_item = Gtk.MenuItem(label="Aplikacja")
        application_menu_item.set_submenu(menu_application)

        # Tworzenie podopcji "Kalkulator" w sekcji "Application"
        calculator_item = Gtk.MenuItem(label="Kalkulator")
        calculator_item.connect("activate", self.on_calculator_clicked)
        menu_application.append(calculator_item)

        # Tworzenie podopcji "Historia" w sekcji "Application"
        history_item = Gtk.MenuItem(label="Historia")
        history_item.connect("activate", self.on_history_clicked)
        menu_application.append(history_item)

        # Dodanie kreski oddzielającej
        separator = Gtk.SeparatorMenuItem()
        menu_application.append(separator)

        # Dodanie opcji "Wyjście" w sekcji "Application"
        quit_item = Gtk.MenuItem(label="Wyjście")
        quit_item.connect("activate", self.on_quit_activate)
        menu_application.append(quit_item)

        menu_bar.append(application_menu_item)

        # Tworzenie sekcji "About"
        menu_about = Gtk.Menu()
        about_menu_item = Gtk.MenuItem(label="O programie")
        about_menu_item.set_submenu(menu_about)

        # Tworzenie podopcji "Opis programu" w sekcji "About"
        program_description_item = Gtk.MenuItem(label="Opis programu")
        program_description_item.connect("activate", self.on_program_description_clicked)
        menu_about.append(program_description_item)

        # Tworzenie podopcji "Autor" w sekcji "About"
        author_item = Gtk.MenuItem(label="Autor")
        author_item.connect("activate", self.on_author_clicked)
        menu_about.append(author_item)

        menu_bar.append(about_menu_item)
        return menu_bar
    
    def on_calculator_clicked(self, button):
        calculator_window = CalculatorWindow(self.history_box, self.build_menu_bar())
        self.windows.append(calculator_window)  # Dodaj otwarte okno do listy
        # calculator_window.connect("destroy", self.on_window_closed)  # Dodaj obsługę zamknięcia okna
        calculator_window.show_all()

    def on_history_clicked(self, button):
        history_window = HistoryWindow(self.history_box, self.build_menu_bar())
        self.add_window(history_window)
        history_window.show_all()

    def on_quit_activate(self, button):
        Gtk.main_quit()

    def on_program_description_clicked(self, button):
        pass

    def on_author_clicked(self, button):
        pass
    
if __name__ == "__main__":
    app = CalculatorApplication()
    app.run(None)
    Gtk.main()
