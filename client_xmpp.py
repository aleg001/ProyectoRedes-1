from abc import ABC
import slixmpp
import asyncio
from slixmpp.exceptions import IqError, IqTimeout
import base64
from xmpp_utils import *
from Constants import *


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
            asyncio.create_task(menu(self))

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
