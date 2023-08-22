# Import necessary modules
import time
from client_xmpp import *  # Importing modules for XMPP client functionality
import getpass  # password input


class ChatProject:
    def __init__(self):
        self.exit_program = False  # Set the initial condition to enter the loop

    # Function to display the main menu options
    def display_main_menu(self):
        """
        Displays the main menu options for the chat application.
        """
        print(
            "\n👋 Welcome to the chat! Let's Connect and Chat Away! 🌟📱\n"
            "\nReady to dive into the options? Here's what we've got: 🚀\n"
            "1) Set up a new account 🎉\n"
            "2) Log in to your chat world 🔑\n"
            "3) Bid farewell and delete your account 🙁👋\n"
            "4) Take a breather and exit for now 🏃‍♂️💨"
        )

    # Function to handle creating a new account
    def handle_create_account(self):
        """
        Handles the process of creating a new chat account for the user.
        """
        print("\nCreating a new account 🌟")
        print("Please enter your desired username.")
        print("Note: You don't need to include the domain '@alumchat.xyz'.")

        while True:
            username = input("Username: ")
            if not username:
                print("Username cannot be empty. Please try again.")
            else:
                break

        while True:
            # password = input("Password: ")
            password = getpass.getpass("Password: ")
            if not password:
                print("Password cannot be empty. Please try again.")
            else:
                break

        # Call the 'register_user' function to register the new user
        if register_user(username, password):
            print("Registration completed! 🎉")
        else:
            print("Registration could not be completed 😔")

    # Function to handle logging in
    def handle_log_in(self):
        """
        Handles the process of logging in to the user's chat account.
        """
        print("\nLogging in to your chat world 🚪🔐")
        print("Please enter your username.")
        print("Remember, no need to type the domain '@alumchat.xyz'.")
        username = input("Username: ")
        # password = input("Password: ")

        password = getpass.getpass("Password: ")
        # Form the user's JID and create a client instance
        user_jid = f"{username}@alumchat.xyz"
        client = Client(user_jid, password)

        # Connect to the server and process client events
        client.connect(disable_starttls=True, use_ssl=False)
        client.process(forever=False)

    # Function to handle deleting an account
    def handle_delete_account(self):
        """
        Handles the process of deleting the user's chat account.
        """
        user_jid = input("\n🗑️ Please enter your username: ")
        password = getpass.getpass("🔒 Please enter your password: ")

        # Create an instance of the Delete class
        client = Delete(user_jid, password)
        print("\n🚫 Deleting your account...")

        # Connect to the XMPP server and start the deletion process
        client.connect(disable_starttls=True, use_ssl=False)
        print("🚫 Connected to the XMPP server. Deleting your account...")
        time.sleep(5)
        # client.close()
        # client.process(forever=False, timeout=10)  # Process client events, then exit
        # client.close()

    def run(self):
        while not self.exit_program:  # Loop until exit_program becomes True
            self.display_main_menu()
            option = int(input("Just type the number of your choice and hit Enter: "))

            match option:
                case 1:
                    self.handle_create_account()
                case 2:
                    self.handle_log_in()
                case 3:
                    self.handle_delete_account()
                case 4:
                    print("\n👋 Exiting the chat")
                    self.exit_program = True  # Set the condition to exit the loop
                    break
                case _:
                    print("Invalid choice. Please select a valid option.")


if __name__ == "__main__":
    app = ChatProject()
    app.run()
