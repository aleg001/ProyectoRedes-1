from abc import ABC
import slixmpp
import asyncio
from slixmpp.exceptions import IqError, IqTimeout
import base64
from Constants import *

# Standard library imports
import asyncio  # Asynchronous programming support
import os  # Operating system interfaces
import xml.etree.ElementTree as ET  # XML parsing and manipulation
import base64

# Third-party library imports
import xmpp  # XMPP (Jabber) library for instant messaging
import slixmpp  # Slixmpp library for XMPP client implementation
from slixmpp.plugins.xep_0234 import stanza  # XEP-0234: Jingle File Transfer
from slixmpp.exceptions import IqError, IqTimeout  # Slixmpp exceptions
from slixmpp.xmlstream.stanzabase import ET

# Third-party library imports with sub-modules
from aioconsole import ainput  # Asynchronous console input
from aioconsole.stream import aprint  # Asynchronous console output

import getpass  # password input


class Client(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        # Initialize the ClientXMPP class by calling its constructor
        super().__init__(jid, password)

        # Extract the username from the JID and store it as the client's name
        self.name = jid.split("@")[0]  # Splitting the JID to get the username

        # Initialize client attributes
        self.is_connected = False  # Flag to track the client's connection status
        self.chat = ""  # Store chat messages
        self.room_nickname = ""  # Store nickname for chat room
        self.chatroom = ""  # Store the chat room

        # Register plugins specified in PLUGIN_NAMES list
        for plugin_name in PLUGIN_NAMES:  # Assuming PLUGIN_NAMES is defined elsewhere
            self.register_plugin(plugin_name)

        # Attach event handlers to specific events
        self.add_event_handler(
            "session_start", self.start
        )  # Session start event handler
        self.add_event_handler("message", self.receiveMessage)  # Message event handler
        self.add_event_handler("groupchat_message", self.receiveChatRoomMessage)

    async def start(self, event):
        try:
            # Send presence to the server
            self.send_presence()

            # Get the roster (list of contacts) from the server
            await self.get_roster()

            # Set the connection status flag and print a successful connection message
            self.is_connected = True
            print("\n🌐 Connected to the server")

            # Create an asynchronous task (coroutine) to handle the menu interaction
            asyncio.create_task(self.menu())

        except IqError as err:
            # Handle IQ errors, which could occur during roster retrieval or presence sending
            self.is_connected = False
            print(f"❌ Error: {err.iq['error']['text']}")

            # Disconnect from the server
            self.disconnect()

        except IqTimeout:
            # Handle timeouts during communication with the server
            self.is_connected = False
            print("⏳ Error: The server is taking too long to respond")

            # Disconnect from the server
            self.disconnect()

    async def receiveChatRoomMessage(self, message=""):
        """
        Receive and process incoming messages in a chatroom.

        Args:
            message (dict): The incoming message in dictionary format.
        """
        # Get the name of the group user
        group_user = message["mucnick"]

        if group_user != self.boundjid.user:
            # Print the received message
            if self.room in str(message["from"]):
                print("{}: {}".format(group_user, message["body"]))
            else:
                print(
                    "New message from user {} in chat room {}: {}".format(
                        group_user, self.room.split("@")[0], message["body"]
                    )
                )

    # Asynchronous function to send and receive messages to/from a contact specified by their JID
    async def sendMessage(self):
        contact_jid = await ainput("Enter the JID of the contact to send a message: 📨")
        self.contact_chat = contact_jid

        contact_name = contact_jid.split("@")[0]
        await aprint(f"Message to: {contact_name} 👥")
        await aprint("To exit the chat, type: exit 🚪")

        while True:
            message = await ainput("Enter the message: ✏️")
            if message == "exit":
                self.chat = ""
                break
            else:
                self.send_message(mto=contact_jid, mbody=message, mtype="chat")
                print(f"Message sent: {message} 🚀")

    async def receiveMessage(self, message):
        # Extract the message type and contact email from the message
        msg_type = message["type"]
        contact_email = message["from"]
        contact_name = contact_email.split("@")[
            0
        ]  # Extract the contact name from the email
        contact_chat_name = self.contact_chat.split("@")[
            0
        ]  # Extract the contact chat name from the email

        if msg_type == "chat":  # Check if the message is a chat message
            if message["body"].startswith(
                "file://"
            ):  # Check if the message contains a file attachment
                try:
                    # Extract file extension and data from the message body
                    _, file_info = message["body"].split("://", 1)
                    file_extension, file_data = file_info.split("://", 1)
                    data_decoded = base64.b64decode(file_data)

                    # Create a filename for the received file
                    filename = f"file_received_from_{contact_name}.{file_extension}"
                    with open(filename, "wb") as file:
                        file.write(data_decoded)  # Write the decoded data to the file

                    print("📂 File received and downloaded")
                except Exception as err:
                    print("❌ Error decoding file information")
            else:  # If the message is not a file attachment
                if contact_name == contact_chat_name:
                    print(f"\n💬 Message from {contact_name}: {message['body']}")
                else:
                    print(
                        f"\n💬 Message from another conversation with {contact_name}: {message['body']}"
                    )

    def presenceMenu(self):
        """
        Display available presence statuses to the user and prompt them for their choice.

        Returns:
            tuple: A tuple containing the technical status value and its friendly message with emoji.
                If the user's input is invalid, it returns (None, None).
        """
        # Dictionary mapping of available options
        # This structure helps in easier management and scalability of statuses
        options = {
            1: ("", "Available 🟢"),
            2: ("away", "Away 🟠"),
            3: ("xa", "Not Available 🔴"),
            4: ("dnd", "Busy ⛔"),
        }

        print("Available statuses: 📋")
        for key, (_, message) in options.items():
            print(f"{key}) {message}")

        # Prompt user for their choice and handle potential exceptions
        try:
            option = int(input("Enter the status you want: "))
            print("Your status has been updated")
            print(f"Status: {options[option][1]}")
            # return options.get(option, (None, None))
            return options[option][0], options[option][1]
        except ValueError:
            return None, None

    # Asynchronous function to display contacts' presence and status information
    async def showContacts(self):
        contacts = list(self.client_roster.keys())

        if len(contacts) == 1 and contacts[0] == self.boundjid.bare:
            print("\nYou have no contacts 🚫")
            return

        print("\nList of users 📖")
        for user in contacts:
            if user != self.boundjid.bare:
                print(f"User: {user} 👥")
                user_presence_info = self.client_roster.presence(user)
                if user_presence_info != {}:
                    # Printing the status
                    for __, presence in user_presence_info.items():
                        match presence["show"]:
                            case "":
                                print("Status: Available 🟢")
                            case "away":
                                print("Status: Away 🟠")
                            case "dnd":
                                print("Status: Busy ⛔")
                            case "xa":
                                print("Status: Not Available 🔴")
                            case _:
                                print("Unknown Status ⚪")
                else:
                    print("Status: Disconnected 🌑")

    # Asynchronous function to add a contact by sending a presence subscription
    async def addContact(self):
        contact_jid = input("Enter the JID of the contact to add: 📩")

        try:
            self.send_presence_subscription(pto=contact_jid)
            print(f"Request sent successfully to {contact_jid} ✅")
            await self.get_roster()
        except IqError as error:
            print(f"Error sending the request: {error.iq['error']['text']} ❌")
        except IqTimeout:
            print("No response from the server ⌛")

    # Asynchronous function to show details of a specific contact using their JID
    async def showContact(self):
        contact_jid = input("Enter the JID of the contact to search: 🧐")

        if contact_jid not in self.client_roster:
            print("The user is not added as a contact 🚫")
        else:
            print(f"User: {contact_jid} 👥")
            user_presence_info = self.client_roster.presence(contact_jid)
            print(user_presence_info)
            if user_presence_info != {}:
                for __, presence in user_presence_info.items():
                    match presence["show"]:
                        case "":
                            print("Status: Available 🟢")
                        case "away":
                            print("Status: Away 🟠")
                        case "dnd":
                            print("Status: Busy ⛔")
                        case "xa":
                            print("Status: Not Available 🔴")
                        case _:
                            print("Unknown Status ⚪")
            else:
                print("Status: Disconnected 🌑")

    # Event handler to process incoming messages
    def message_callback(self, msg):
        if msg["type"] in ("chat", "normal"):
            print(f"\n{msg['from'].bare} said: {msg['body']}\n")

    # Asynchronous function to create a chat room with the specified name
    async def createChatRoom(self, name_room):
        try:
            domain_suffix = "@conference.alumchat.xyz"

            # Construct the full room name
            full_room_name = f"{name_room}{domain_suffix}"
            print(f"Creating room: {full_room_name} 🚧")

            # Join the Multi-User Chat (MUC) room
            self.plugin["xep_0045"].join_muc(full_room_name, self.boundjid.user)
            await asyncio.sleep(1)  # Wait to avoid creation errors

            # Room configuration
            form = self.plugin["xep_0004"].make_form(
                ftype="submit", title="ChatRoom Configuration"
            )
            form_fields = {
                "muc#roomconfig_roomname": full_room_name,
                "muc#roomconfig_roomdesc": "AlumChat user chat room",
                "muc#roomconfig_roomowners": [self.boundjid.user],
                "muc#roomconfig_maxusers": "50",
                "muc#roomconfig_publicroom": "1",
                "muc#roomconfig_persistentroom": "1",
                "muc#roomconfig_enablelogging": "1",
                "muc#roomconfig_changesubject": "1",
                "muc#roomconfig_membersonly": "0",
                "muc#roomconfig_allowinvites": "0",
                "muc#roomconfig_whois": "anyone",
            }
            for key, value in form_fields.items():
                form[key] = value

            # Set room configuration and send a welcome message
            await self.plugin["xep_0045"].set_room_config(full_room_name, config=form)
            print(f"Chat room created: {full_room_name} ✅")
            self.send_message(
                mto=full_room_name,
                mbody=f"Welcome to the room: {full_room_name} 🎉",
                mtype="groupchat",
            )

        except IqError:
            print("Error creating the chat room ❌")
        except IqTimeout:
            print("Maximum wait time for room creation ⏳")

    # Asynchronous function to join a chat room with the specified name and handle messages
    async def joinChatRoom(self, name_room):
        self.chatroom = name_room
        self.room_nickname = self.boundjid.user

        print("Messages from the room: 📜")

        try:
            await self.plugin["xep_0045"].join_muc(name_room, self.room_nickname)
        except IqError as err:
            print(f"Error while entering the chat room: {err.iq['error']['text']} ❌")
            return  # Return early if there's an error, so the following messages aren't printed
        except IqTimeout:
            print("No response from the server ⌛")
            return

        room_name = self.chatroom.split("@")[0]
        await aprint(f"Messages from Chat Room: {room_name} 🎉")
        await aprint("To exit the chat, type: exit chat 🚪")

        while True:
            message = await ainput("Enter the message: ✏️")
            if message == "exit chat":
                self.chat = ""
                self.exitChatRoom()
                break
            else:
                self.send_message(self.chatroom, message, mtype="groupchat")

    async def sendFiles(self):
        """
        Asynchronously sends a file to a specified contact.

        This method prompts the user for a JID (Jabber Identifier) and a file path.
        It then reads the file, encodes it in base64 format, and sends it as a message
        to the specified JID.


        """

        # Prompt user for the JID of the contact to send the file to
        contact_jid = await ainput("Enter the JID of the contact to send a file to: 📂")

        # Prompt user for the path of the file to send
        file_path = input("Add the path of the file: ")

        # Extract the file extension from the file path
        file_extension = file_path.split(".")[-1]

        # Read the file and store its data
        with open(file_path, "rb") as file:
            file_data = file.read()

        # Encode the file data in base64 format
        encoded_data = base64.b64encode(file_data).decode()

        # Create the message in a specific format, embedding the file data
        message = f"file://{file_extension}://{encoded_data}"

        # Send the message using a pre-defined method `self.send_message`
        self.send_message(mto=contact_jid, mbody=message, mtype="chat")

    # Function to exit the currently joined chat room and reset associated attributes
    def exitChatRoom(self):
        self["xep_0045"].leave_muc(self.chatroom, self.room_nickname)

        # Inform the user
        print(f"You have left the room: {self.chatroom} 🚪")

        # Reset chat attributes
        self.chatroom = ""
        self.room_nickname = ""

    # Asynchronous function to display available group chat options and handle user input
    async def groupchatMenu(self):
        menu_active = True
        while menu_active:
            print(
                "\n🌐 You have the following options available for group chat:\n"
                "1) Create a chat room\n"
                "2) Join a chat room\n"
                "3) Exit"
            )

            option = int(input("Enter the option you desire:"))

            # Use a match statement to execute the chosen option
            match option:
                case 1:
                    room_name = input("Enter the name for the chat room: ")
                    await self.createChatRoom(room_name)
                case 2:
                    room_name = input("Enter the name of the chat room: ")
                    await self.joinChatRoom()
                case 3:
                    menu_active = False

    # Asynchronous function to logout from the XMPP server
    async def logout(self):
        print("\nLogging out...\n")
        self.disconnect()
        print("\n\nLogged out successfully! 👋")

    # Asynchronous function to set the user's presence status
    async def setPresence(self):
        """
        Set the user's presence status based on their chosen option from the menu.

        This function first calls the presenceMenu to get the user's choice of presence status.
        It then sets the internal status and sends the presence to the server.
        Finally, it updates the user's roster.
        """
        # Get the user's chosen status from the menu
        status, status_message = self.presenceMenu()
        print(status, status_message)

        # If user provides an invalid choice, notify them and exit
        if not status and not status_message:
            print("Invalid choice! 🙁")
            return

        self.status = status
        self.status_message = status_message
        self.send_presence(pshow=self.status, pstatus=self.status_message)
        await self.get_roster()

    # Asynchronous menu function to display options and handle user input
    async def menu(self):
        """
        Displays the main menu options for the chat application.
        """
        while self.is_connected:
            print(
                "\n👋 Welcome to the chat! Let's Connect and Chat Away! 🌟📱\n"
                "\nReady to dive into the options? Here's what we've got: 🚀\n"
                "1) Show all contacts and their status 📋\n"
                "2) Add a user to contacts ➕\n"
                "3) Show contact details for a user 👤\n"
                "4) 1-to-1 communication with any user/contact 💬\n"
                "5) Participate in group conversations 👥🗨️\n"
                "6) Set presence message 📢\n"
                "8) Send/receive files 📁\n"
                "9) Log out and exit the chat 🚪🏃‍♂️💨\n"
            )
            option = int(input("Enter the option you desire:"))

            # Use a match statement to execute the chosen option
            match option:
                case 1:
                    await self.showContacts()
                case 2:
                    await self.addContact()
                case 3:
                    await self.showContact()
                case 4:
                    await self.sendMessage()
                case 5:
                    await self.groupchatMenu()
                case 6:
                    await self.setPresence()

                case 8:
                    await self.sendFiles()

                case 9:
                    await self.logout()
                    return
                case _:
                    print("Invalid option. Please enter a valid option.")


class Delete(slixmpp.ClientXMPP):
    """
    Delete is a subclass of slixmpp.ClientXMPP designed to unregister a user from an XMPP service.
    """

    def __init__(self, jid, password):
        """
        Initializes the Delete.

        :param jid: JID (Jabber ID) of the user.
        :param password: Password of the user.
        """
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.user = jid
        self.add_event_handler("session_start", self.start)

    async def start(self, event):
        """
        Handles the start of the session. Sends presence, retrieves the roster,
        unregisters the user, and then disconnects.

        :param event: The event triggering this function.
        """
        print("Sending presence...")
        self.send_presence()
        print("Getting roster...")
        await self.get_roster()
        print("Unregistering...")
        await self.unregister()
        print("Disconnecting...")
        self.disconnect()

    async def unregister(self):
        # Ensure that the client has a valid JID
        if not self.boundjid:
            print("❌ Invalid JID! Cannot unregister.")
            self.disconnect()
            return

        sRes = self.Iq()
        sRes["type"] = "set"
        sRes["from"] = self.boundjid.user
        fragment = ET.fromstring("<query xmlns='jabber:iq:register'><remove/></query>")
        sRes.append(fragment)

        try:
            await sRes.send()
            print(f"✅ Account removed: {self.boundjid.jid}")
        except IqError as err:
            error_text = (
                err.iq["error"]["text"]
                if err.iq and err.iq.get("error")
                else "Unknown error"
            )
            print(f"❌ Error removing account: {error_text}")
            self.disconnect()

        except IqTimeout:
            print("⏳ No response from server")
            self.disconnect()

        except Exception as e:
            print(f"❌ Unknown exception: {str(e)}")
            self.disconnect()


# Function to register a user with a specified username and password
def register_user(username, password):
    # Append the domain to the username
    user_jid = f"{username}@alumchat.xyz"

    # Create the JID
    jid = xmpp.JID(user_jid)

    # Create the client and connect
    user_account = xmpp.Client(jid.getDomain(), debug=[])
    user_account.connect()

    # Return the indication if registration was successful
    return xmpp.features.register(
        user_account, jid.getDomain(), {"username": jid.getNode(), "password": password}
    )
