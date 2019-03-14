from twc_modules import main_menu
from twc_modules.user_conf_manager import UserConfigurator
from pynput.mouse import Listener


class MouseListener():
    def __init__(self):
        self.cursor_x = None
        self.cursor_y = None

    def _on_click(self, x, y, button, pressed):
        self.cursor_x = x
        self.cursor_y = y
        if not pressed:
            return False
        return False

    def listen_mouse(self):
        with Listener(on_click=self._on_click)as listener:
            listener.join()


class WizardMenu(UserConfigurator, MouseListener):
    def __init__(self):
        UserConfigurator.__init__(self)
        MouseListener.__init__(self)
        self.user_choice = int()
        self.invalid_choice = "Invalid choice."
        self.cursor_current_x = int()
        self.cursor_current_y = int()
        self.steps_to_run = list()

    def welcome_menu(self):
        print("Welcome to TWC User Settings Wizard. \n"
              "This functionality will help you configure TWC to work on your own PC. \n"
              "The process will be pretty straight forward and if you encounter any issue, \n"
              "you can always rebuild user_settings.json back to it's default values.")
        print("=" * 40)
        print("1. Configure All Settings - First time users.\n"
              "2. Configure ONLY click locations\n"
              "3. Configure ONLY sleep timers\n"
              "4. [NOT IMPLEMENTED YET] Reset user_settings.json back to default values.\n"
              "0. Exit Configuration Wizard.")

        self.ask_for_choice()

    def ask_for_choice(self):
        self.user_choice = input("\nMenu choice:")
        self.check_if_int()
        return self.user_choice

    def check_if_int(self):
        try:
            self.user_choice = int(self.user_choice)
            self.run_steps()
        except ValueError:
            print(self.invalid_choice)
            self.ask_for_choice()

    # All settings
    def run_steps(self):
        if self.user_choice == 1:
            self.ilo_data()
            self.click_menu()
            self.timer_menu()

        elif self.user_choice == 2:
            self.click_menu()

        elif self.user_choice == 3:
            self.timer_menu()

        elif self.user_choice == 4:
            print("Not implemented yet.")
            self.welcome_menu()

        elif self.user_choice == 0:
            main_menu.run_menu()

        else:
            print(self.invalid_choice)
            self.ask_for_choice()

    # Password and iLO location.
    def ilo_data(self):
        print("In this step we will configure the iLO Installation path and the iLO Password")

        def ilo_path_configuration():
            print("Please enter the path of iLO installation, usually:\n"
                  "C:\Program Files (x86)\Hewlett-Packard\HP iLO Integrated Remote Console\HPLOCONS.exe")

            path = input("Path:")
            print("You have selected the following path: {} \n"
                  "Is that right? (Y/N)".format(path))

            save_choice = input().lower()
            if "y" in save_choice:
                self.save_ilo_path(path)
            else:
                path = None
                ilo_path_configuration()

        ilo_path_configuration()

        def ilo_password_configuration():
            print("Please enter iLO password:\n"
                  "Found in ~/secrets/passwords/oob-passwords.txt.gpg")

            inp = input("Path:")
            print("You have selected the following password: {} \n"
                  "Is that right? (Y/N)".format(inp))

            save_choice = input().lower()
            if "y" in save_choice:
                self.save_ilo_password(inp)
            else:
                inp = None
                ilo_password_configuration()

        ilo_password_configuration()

    # Get current cursor X position, we only need this to know which display we are on.
    def current_cursor_x_position(self):
        try:
            import pyautogui
            self.cursor_current_x, self.cursor_current_y = pyautogui.position()
            return int(self.cursor_current_x)
        except ImportError:
            print("You are running this script on Linux or OSX. Please run from Windows.")
            exit(0)

    # Only Click Locations
    def click_menu(self):
        print("In this step we will configure the automated click locations for the tool. \n"
              "Those locations are used for the TWC to know where to click. \n"
              "Until all 5 steps are done __KEEP IT ON THE SAME SCREEN__\n"
              "The Wizard __WILL TELL YOU__ when to swap the screens, if needed.\n"
              "If you use __TWO SCREENS__ you will need to run this menu twice! \n"
              "Once for each screen!")
        self.ilo_iphost_textfield()

    def ilo_iphost_textfield(self):
        print("Please Launch iLO on your PC and click on the\n"
              "'Network Address' text field.")
        self.listen_mouse()
        print("You have clicked at: {}, {}".format(self.cursor_x,self.cursor_y))
        print("Do you want to save? (Y/N)")

        save_choice = input().lower()
        if "y" in save_choice:
            self.save_click_cords(display=self.which_display(self.current_cursor_x_position()),
                                  key="ilo",
                                  value=[self.cursor_x, self.cursor_y])
        else:
            self.cursor_x, self.cursor_y = 0, 0
            self.ilo_iphost_textfield()

        self.ilo_password_textfield()

    def ilo_password_textfield(self):
        print("Please click on the\n"
              "'Password' text field.")
        self.listen_mouse()
        print("You have clicked at: {}, {}".format(self.cursor_x, self.cursor_y))
        print("Do you want to save? (Y/N)")

        save_choice = input().lower()
        if "y" in save_choice:
            self.save_click_cords(display=self.which_display(self.current_cursor_x_position()),
                                  key="password",
                                  value=[self.cursor_x, self.cursor_y])
        else:
            self.cursor_x, self.cursor_y = 0, 0
            self.ilo_password_textfield()

        self.ilo_connect_button()

    def ilo_connect_button(self):
        print("Please click on the\n"
              "'Connect' button.")
        self.listen_mouse()
        print("You have clicked at: {}, {}".format(self.cursor_x, self.cursor_y))
        print("Do you want to save? (Y/N)")

        save_choice = input().lower()
        if "y" in save_choice:
            self.save_click_cords(display=self.which_display(self.current_cursor_x_position()),
                                  key="connect_btn",
                                  value=[self.cursor_x, self.cursor_y])
        else:
            self.cursor_x, self.cursor_y = 0, 0
            self.ilo_connect_button()

        self.ilo_power_dropdown()

    def ilo_power_dropdown(self):
        print("Please click on \n"
              "'Power Switch' dropdown menu.")
        self.listen_mouse()
        print("You have clicked at: {}, {}".format(self.cursor_x, self.cursor_y))
        print("Do you want to save? (Y/N)")

        save_choice = input().lower()
        if "y" in save_choice:
            self.save_click_cords(display=self.which_display(self.current_cursor_x_position()),
                                  key="power_dropdown",
                                  value=[self.cursor_x, self.cursor_y])
        else:
            self.cursor_x, self.cursor_y = 0, 0
            self.ilo_power_dropdown()

        self.ilo_cold_boot()

    def ilo_cold_boot(self):
        print("Please click on \n"
              "'Cold Boot' text field.")
        self.listen_mouse()
        print("You have clicked at: {}, {}".format(self.cursor_x, self.cursor_y))
        print("Do you want to save? (Y/N)")

        save_choice = input().lower()
        if "y" in save_choice:
            self.save_click_cords(display=self.which_display(self.current_cursor_x_position()),
                                  key="cold_boot",
                                  value=[self.cursor_x, self.cursor_y])
        else:
            self.cursor_x, self.cursor_y = 0, 0
            self.ilo_cold_boot()

    # Only Timer Locations
    def timer_menu(self):
        keys_to_update = [("launch_ilo", "Delay in seconds before taking the first action.\n"
                                         "Default: 1 second"),
                          ("ip_port", "Delay in seconds before typing the ILO:Port\n"
                                      "Default: 0 seconds"),
                          ("password", "Delay in seconds before typing the Password\n"
                                       "Default: 0 seconds"),
                          ("click_connect", "Delay in seconds before clicking on Connect button\n"
                                            "Default: 0 seconds"),
                          ("power_dropdown", "Delay in seconds before click on Power Switch dropdown\n"
                                             "Default: 7 seconds"),
                          ("cold_reboot", "Delay in seconds before clicking on Cold Boot \n"
                                          "Default: 1 second"),
                          ("close_ilo", "Delay in seconds before closing the iLO session\n"
                                        "Default: 10")]

        for key, description in keys_to_update:
            self.set_timers(key, description)

    def set_timers(self, key, description):
        print(description)
        value = input()
        if value == "0" or int(value):
            self.save_sleep_timer(key, value)
        else:
            print("Not an int! Restarting this step!")
            self.set_timers(key, description)

    # Change user_setting.json back to Default Values
    def default_settings(self):
        print("Menu not implemented yet.")
        self.welcome_menu()

    # Exit menu
    def wizard_exit(self):
        pass
