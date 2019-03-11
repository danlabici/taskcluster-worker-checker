from twc_modules import twc_mouse, main_menu


def conf_menu():
    print("This function will help you configure user_settings.json\n"
          "Choose one of the following options:")
    print("1. Fresh Configuration (First time users)\n"
          "2. Configure only Click Locations\n"
          "3. Configure only Wait Times\n"
          "0. Go Back.")
    try:
        choice = int(input())
    except ValueError:
        print("\n\nInvalid Choice!\n")
        conf_menu()

    if choice == 1:
        twc_mouse.mouse_listener("test")

    if choice == 2:
        pass

    if choice == 3:
        pass

    if choice == 0:
        main_menu.run_menu()

conf_menu()