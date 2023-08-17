import xmpp
from aioconsole import ainput
from aioconsole.stream import aprint
from slixmpp.exceptions import IqError, IqTimeout
import asyncio
import os
from slixmpp.plugins.xep_0234 import stanza
import xmpp
from aioconsole import ainput
from aioconsole.stream import aprint
from slixmpp.exceptions import IqError, IqTimeout
import asyncio

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
            print(user_presence_info)
            for _, presence_data in user_presence_info.items():
                if presence_data["status"]:
                    print(f"Status: {presence_data['status']} 📝")


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
        for _, presence_data in user_presence_info.items():
            print(presence_data)
            if presence_data["status"]:
                print(f"Status: {presence_data['status']} 📝")


# Event handler to process incoming messages
def message_callback(self, msg):
    if msg["type"] in ("chat", "normal"):
        print(f"\n{msg['from'].bare} said: {msg['body']}\n")


# Asynchronous function to send and receive messages to/from a contact specified by their JID
async def sendMessage(self):
    contact_jid = await ainput("Enter the JID of the contact to send a message: 📨")
    self.contact_chat = contact_jid

    contact_name = contact_jid.split("@")[0]
    await aprint(f"Message to: {contact_name} 👥")
    await aprint("To exit the chat, type: exit chat 🚪")

    # Add the event handler for incoming messages
    self.add_event_handler("message", message_callback)

    while True:
        message = await ainput("Enter the message: ✏️")
        if message == "exit chat":
            self.chat = ""
            exitChatRoom(self)
            # Remove the event handler when exiting the chat
            self.del_event_handler("message", message_callback)
            break
        else:
            self.send_message(mto=contact_jid, mbody=message, mtype="chat")
            print(f"Message sent: {message} 🚀")


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
            exitChatRoom(self)
            break
        else:
            self.send_message(self.chatroom, message, mtype="groupchat")


async def sendFiles(self):
    contact_jid = await ainput("Enter the JID of the contact to send a file to: 📂")

    # Check if the receiver supports Jingle file transfer
    if not self["xep_0030"].supports(contact_jid, "urn:xmpp:jingle:1"):
        print("The contact does not support Jingle file transfer.")
        return

    filepath = await ainput("Enter the path of the file you want to send: 📎")

    if not os.path.exists(filepath):
        print("The specified file does not exist.")
        return

    filesize = os.path.getsize(filepath)
    file_name = os.path.basename(filepath)

    session = self["xep_0234"].new_session(receiver_jid=contact_jid)

    file_info = {
        "name": file_name,
        "size": filesize,
        "date": os.path.getctime(filepath),
    }

    # Create the offer with file info
    session["offer"] = stanza.Offer(file_info)
    session["offer"]["desc_type"] = "file"
    session["offer"]["transport_method"] = "ibb"

    try:
        with open(filepath, "rb") as file:
            # Send the file
            await self["xep_0234"].send_file(session, file, block_size=4096)
            print(f"File {file_name} sent successfully! 🚀")
    except Exception as e:
        print(f"Error sending the file: {str(e)} ❌")


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
                await createChatRoom(self, room_name)
            case 2:
                room_name = input("Enter the name of the chat room: ")
                await joinChatRoom(self)
            case 3:
                menu_active = False


# Asynchronous function to logout from the XMPP server
async def logout(self):
    print("Logging out...")
    self.disconnect()
    print("Logged out successfully! 👋")


# Asynchronous menu function to display options and handle user input
async def menu(self):
    while self.is_connected:
        print(
            "\n📋 You have the following options available to use in the chat:\n"
            "1) Show all contacts and their status\n"
            "2) Add a user to contacts\n"
            "3) Show contact details for a user\n"
            "4) 1-to-1 communication with any user/contact\n"
            "5) Participate in group conversations\n"
            "6) Set presence message\n"
            "7) Send/receive notifications\n"
            "8) Send/receive files"
        )

        option = int(input("Enter the option you desire:"))

        # Use a match statement to execute the chosen option
        match option:
            case 1:
                await showContacts(self)
            case 2:
                await addContact(self)
            case 3:
                await showContact(self)
            case 4:
                await sendMessage(self)
            case 5:
                await groupchatMenu(self)
            case 6:
                await sendMessage(self)

            case 7:
                await sendNotificacion(self)
            case 8:
                await sendFiles(self)

            case 9:
                await logout(self)
                return
            case _:
                print("Invalid option. Please enter a valid option.")
