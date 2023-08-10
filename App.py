from client_xmpp import *
from xmpp_utils import *
import tkinter as tk

# Start an infinite loop to keep the application running until explicitly exited
while True:
    # Print the main menu with options
    print(
        "\n👋 Welcome to the chat! Let's Connect and Chat Away! 🌟📱\n"
        "\nReady to dive into the options? Here's what we've got: 🚀\n"
        "1) Set up a new account 🎉\n"
        "2) Log in to your chat world 🔑\n"
        "3) Bid farewell and delete your account 🙁👋\n"
        "4) Take a breather and exit for now 🏃‍♂️💨"
    )

    # Prompt the user to input their choice
    opcion = int(input("Just type the number of your choice and hit Enter: "))

    if opcion == 1:  # User chose to set up a new account
        print("\nCreating a new account 🌟")
        print("Please enter your desired username.")
        print("Note: You don't need to include the domain '@alumchat.xyz'.")
        username = input("Username: ")
        password = input("Password: ")

        # Call a function 'register_user' to register the new user
        if register_user(username, password):
            print("Registration completed! 🎉")
        else:
            print("Registration could not be completed 😔")

    elif opcion == 2:  # User chose to log in
        print("\nLogging in to your chat world 🚪🔐")
        print("Please enter your username.")
        print("Remember, no need to type the domain '@alumchat.xyz'.")
        username = input("Username: ")
        password = input("Password: ")

        # Add the domain to the username
        user_jid = f"{username}@alumchat.xyz"

        # Create a client instance and connect to the server
        client = Client(user_jid, password)
        client.connect(disable_starttls=True, use_ssl=False)
        client.process(forever=False)  # Process client events, then exit

    # Handle user's menu choice
    if opcion == 3:  # User chose to delete their account
        print("\n🚫 Deleting account from the server")

    elif opcion == 4:  # User chose to exit the application
        print("\n👋 Exiting the chat")
        break  # Exit the loop and end the program
