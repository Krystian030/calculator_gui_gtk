import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GObject, Gdk, Pango  
from calculator import calculate_expression

class CalculatorWindow(Gtk.Window):
    
    def __init__(self, menu_bar, history_box):
        Gtk.Window.__init__(self, title="Kalkulator")
        self.set_default_size(310, 400)
        self.set_resizable(False) 
        self.history_box = history_box

        self.set_name("calculator-window")
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path("styles.css")

        context = Gtk.StyleContext()
        screen = Gdk.Screen.get_default()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.expression = ""
        self.menu_bar = menu_bar

        self.connect("destroy", self.on_window_destroy)  

        grid = Gtk.Grid()
        self.add(grid)
        
        grid.attach(self.menu_bar, 0, 0, 1, 1)
        self.create_display_panel(grid)
        self.create_button_panel(grid)
        self.create_operators_panel(grid)

    def create_operators_panel(self, parent_grid):
        operators_panel = Gtk.Grid()
        operators_panel.set_name("operators-panel")
        parent_grid.attach(operators_panel, 0, 2, 1, 1)
        operators_panel.set_size_request(156, 270)

        # Operators
        operators = ['+', '-', '*', '/', '=', '←']
        for i, label in enumerate(operators):
            button = Gtk.Button(label=label)
            button.connect("clicked", self.on_button_clicked)
            button.set_size_request(64, 88)
            button.get_style_context().add_class("button")
            operators_panel.attach(button, i % 2, i // 2, 1, 1)

    def create_button_panel(self, parent_grid):
        button_panel = Gtk.Grid()
        button_panel.set_name("button-panel")
        parent_grid.attach(button_panel, 0, 2, 1, 1)

        button_panel.set_hexpand(True)
        button_panel.set_size_request(244, 270)

        # Buttons 1 to 9
        buttons = ['7', '8', '9', '4', '5', '6', '1', '2', '3']
        for i, label in enumerate(buttons):
            button = Gtk.Button(label=label)
            button.connect("clicked", self.on_button_clicked)
            button.set_size_request(64, 60)
            button.get_style_context().add_class("button")
            button_panel.attach(button, i % 3, i // 3, 1, 1)

        # Button "0"
        button_0 = Gtk.Button(label="0")
        button_0.connect("clicked", self.on_button_clicked)
        button_0.set_size_request(141, 60)
        button_0.get_style_context().add_class("button")
        button_panel.attach(button_0, 0, 3, 2, 1)

        # Button "."
        button_dot = Gtk.Button(label=".")
        button_dot.connect("clicked", self.on_button_clicked)
        button_dot.set_size_request(64, 60)
        button_dot.get_style_context().add_class("button")
        button_panel.attach(button_dot, 2, 3, 1, 1)
        
    def create_display_panel(self, parent_grid):
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER) 
        parent_grid.attach(scrolled_window, 0, 1, 1, 1)
        
        display_panel = Gtk.Grid()
        display_panel.set_column_homogeneous(True)
        display_panel.set_row_homogeneous(True)
        display_panel.set_name("display-panel")  
        scrolled_window.add(display_panel)
        
        display_panel.set_hexpand(True)
        display_panel.set_size_request(310, 112)
        
        self.expression_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.expression_box.set_name("expression-box")
        display_panel.attach(self.expression_box, 0, 0, 1, 1)

        self.result_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.result_box.set_name("result-box")
        display_panel.attach(self.result_box, 0, 1, 1, 1)
        
        self.expression_entry = Gtk.Label()  
        self.expression_entry.set_name("expression-label")
        self.expression_entry.set_property("xalign", 1) # text-align to right
        self.expression_box.pack_end(self.expression_entry, True, True, 0)

        self.result_entry = Gtk.Label()
        self.result_entry.set_name("result-label")
        self.result_entry.set_property("xalign", 1) # text-align to right
        self.result_box.pack_end(self.result_entry, True, True, 0)
    
    def on_button_clicked(self, button):
        label = button.get_label()
        
        # Clean the result if the previous expression has been calculated
        if self.expression == "" and self.result_entry.get_text() != "":
            self.result_entry.set_text("")
            
        if label == '=':
            try:
                result = calculate_expression(self.expression)
                self.result_entry.set_text("=" + str(result))
                self.history_box.add_to_history(f"{self.expression}={result}")  
                self.expression = ""
            except Exception as e:
                self.show_error_dialog(str(e))
                self.result_entry.set_text("")  
                self.expression = ""
                self.expression_entry.set_text(self.expression)
        else:
            if label == '←':
                self.expression = self.expression[:-1]
                self.expression_entry.set_text(self.expression)
                if self.expression == "":
                    self.result_entry.set_text("")
            else:
                self.expression += label
    
            self.expression_entry.set_text(self.expression)
    
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

    def on_dialog_response(self, dialog, _):
        dialog.destroy()
        
    def on_window_destroy(self, window):
        window.destroy()


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

class HistoryWindow(Gtk.Window):
    def __init__(self, menu_bar, history_box):
        Gtk.Window.__init__(self, title="Historia Obliczeń")
        
        self.set_default_size(370, 400)
        self.set_resizable(False) 
        self.set_name("history-window")  

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path("styles.css")
        context = Gtk.StyleContext()
        screen = Gdk.Screen.get_default()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.history_box = history_box
        self.menu_bar = menu_bar
        self.connect("destroy", self.on_window_destroy) 
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)
        vbox.set_name("history-box")

        vbox.pack_start(self.menu_bar, False, False, 0)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        vbox.pack_start(scrolled_window, True, True, 0)
        
        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)
        self.textview.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(23/255, 24/255, 26/255, 1))
        self.textview.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1, 1, 1, 1))
        self.textview.set_name("history-text")
        scrolled_window.add(self.textview)
        
        self.history_box.connect('history-updated', self.update_history_list)
        self.update_history_list()

        clear_button = Gtk.Button(label="Wyczyść historię")
        clear_button.set_name("clear-history-button")
        clear_button.connect("clicked", self.on_clear_button_clicked)
        clear_button.set_name("clear-history-button")
        vbox.pack_end(clear_button, False, False, 0)
    
    def update_history_list(self, *_):
        history_text = "\n".join(self.history_box.get_history())
        buffer = self.textview.get_buffer()
        buffer.set_text(history_text)
    
    def on_window_destroy(self, window):
        window.destroy()

    def on_clear_button_clicked(self, button):
        self.history_box.history_of_calculations = []
        self.history_box.emit('history-updated')

class AboutWindow(Gtk.Window):
    def __init__(self, menu_bar):
        Gtk.Window.__init__(self, title="O programie")
        self.set_default_size(400, 200)
        self.set_resizable(False) 
        self.set_name("about-window")  

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path("styles.css")
        context = Gtk.StyleContext()
        screen = Gdk.Screen.get_default()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.menu_bar = menu_bar
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)
        vbox.set_name("about-box")

        vbox.pack_start(self.menu_bar, False, False, 0)

        label = Gtk.Label()
        label.set_markup("<span size='large'><b>Autor:</b></span> Krystian Jandy s184589\n\n<span size='large'><b>Wersja aplikacji:</b></span> 1.0\n\n<span size='large'><b>Opis:</b></span>\nAplikacja kalkulatora jest narzędziem umożliwiającym wygodne wykonywanie podstawowych operacji matematycznych, takich jak dodawanie, odejmowanie, mnożenie i dzielenie, za pomocą prostego i intuicyjnego interfejsu graficznego użytkownika. Oprócz podstawowych funkcji matematycznych, aplikacja umożliwia również przeglądanie historii wykonanych działań, pozwalając użytkownikowi śledzić i analizować poprzednie obliczenia.")
        label.set_line_wrap(True)
        label.set_padding(20, 20)
        label.set_max_width_chars(50)  # Ograniczenie szerokości labela
        vbox.pack_start(label, True, True, 0)

        close_button = Gtk.Button(label="Zamknij")
        close_button.connect("clicked", self.on_close_button_clicked)
        close_button.set_name("close-button")
        vbox.pack_end(close_button, False, False, 0)
    
    def on_close_button_clicked(self, button):
        self.destroy()


class CalculatorApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.calculator", flags=Gio.ApplicationFlags.FLAGS_NONE)
        
        self.history_box = HistoryBox()
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path("styles.css")
        context = Gtk.StyleContext()
        screen = Gdk.Screen.get_default()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.connect("activate", self.on_activate)
        
    def on_activate(self, _):
        win = CalculatorWindow(self.build_menu_bar(), self.history_box)
        win.show_all()

        
    def build_menu_bar(self):
        menu_bar = Gtk.MenuBar()
        menu_bar.set_name("menu-bar")  # Dodanie identyfikatora dla menu

        # Sekcja Aplikacja
        menu_application = Gtk.Menu()
        application_menu_item = Gtk.MenuItem(label="Aplikacja")
        application_menu_item.set_submenu(menu_application)
        application_menu_item.set_name("menu-item")  

        # Kalkulator w sekcji Aplikacja
        calculator_item = Gtk.MenuItem(label="Kalkulator")
        calculator_item.connect("activate", self.on_calculator_clicked)
        calculator_item.set_name("menu-item")  
        menu_application.append(calculator_item)

        history_item = Gtk.MenuItem(label="Historia")
        history_item.connect("activate", self.on_history_clicked)
        history_item.set_name("menu-item")  
        menu_application.append(history_item)
        
        # Dodanie kreski oddzielającej
        separator = Gtk.SeparatorMenuItem()
        menu_application.append(separator)

        # Dodanie opcji "Wyjście" w sekcji "Aplikacja"
        quit_item = Gtk.MenuItem(label="Wyjście")
        quit_item.connect("activate", self.on_quit_activate)
        quit_item.set_name("menu-item")  
        menu_application.append(quit_item)

        menu_bar.append(application_menu_item)

        # Sekcja About
        about_menu_item = Gtk.MenuItem(label="O programie")
        about_menu_item.connect("activate", self.on_about_program_clicked)
        about_menu_item.set_name("menu-item")  
        
        menu_bar.append(about_menu_item)
        
        return menu_bar
    
    def on_calculator_clicked(self, _):
        calculator_window = CalculatorWindow(self.build_menu_bar(), self.history_box)
        calculator_window.show_all()

    def on_history_clicked(self, _):
        history_window = HistoryWindow(self.build_menu_bar(), self.history_box)
        history_window.show_all()
    
    def on_about_program_clicked(self, x):
        about_menu = AboutWindow(self.build_menu_bar())
        about_menu.show_all()

    def on_quit_activate(self, _):
        Gtk.main_quit()


    
if __name__ == "__main__":
    app = CalculatorApplication()
    app.run(None)
    Gtk.main()
