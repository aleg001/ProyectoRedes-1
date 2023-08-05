"""
Plugin Documentation

Welcome to the documentation for the plugins available in this system. These plugins are designed to enhance the functionality and features of your Python application. Below, you'll find a detailed list of the available plugins along with their descriptions and usage guidelines.

Available Plugins:

1. xep_0030 - Service Discovery
   - Description: This plugin allows your application to discover services provided by other entities on the network. It's a fundamental component for building a dynamic and adaptable network environment.
   - Usage: Use this plugin to query and announce available services within the network.

2. xep_0199 - Ping
   - Description: The Ping plugin enables the ability to send and respond to pings. It's a simple yet effective way to check the connectivity and responsiveness of entities on the network.
   - Usage: Integrate this plugin to monitor the availability and latency of network participants.

3. xep_0045 - Multi-User Chat (MUC)
   - Description: The Multi-User Chat plugin empowers users to participate in group conversations. It's ideal for creating chat rooms and fostering collaborative discussions.
   - Usage: Incorporate this plugin to enable multi-user chat functionality within your application.

4. xep_0085 - Chat State Notifications
   - Description: This plugin provides real-time notifications about the state of a user's chat, such as typing, paused, active, and inactive. It enhances the user experience by conveying presence information.
   - Usage: Implement this plugin to display user activity and engagement in your chat interface.

5. xep_0004 - Data Forms
   - Description: The Data Forms plugin offers a structured way to gather and exchange data. It's useful for configuring settings, preferences, and other structured information.
   - Usage: Use this plugin to create interactive forms for users to provide data in a standardized format.

6. xep_0060 - Publish-Subscribe (PubSub)
   - Description: Publish-Subscribe enables the distribution of messages to multiple subscribers. It's valuable for broadcasting updates, news, and other content to interested parties.
   - Usage: Integrate this plugin to establish a publish-subscribe pattern for information dissemination.

7. xep_0066 - Out of Band Data
   - Description: Out of Band Data plugin facilitates the sharing of data that is not directly part of a conversation. It's useful for sending files, images, and other content alongside messages.
   - Usage: Incorporate this plugin to enable users to share files and additional information within conversations.

8. xep_0363 - HTTP File Upload
   - Description: The HTTP File Upload plugin allows users to upload files and share them through URLs. It's a convenient way to exchange files without the need for direct peer-to-peer transfers.
   - Usage: Implement this plugin to enable seamless file sharing via URLs in your application.


"""

PLUGIN_NAMES = [
    "xep_0030",  # Service Discovery
    "xep_0199",  # Ping
    "xep_0045",  # Multi-User Chat (MUC)
    "xep_0085",  # Chat State Notifications
    "xep_0004",  # Data Forms
    "xep_0060",  # Publish-Subscribe (PubSub)
    "xep_0066",  # Out of Band Data
    "xep_0363",  # HTTP File Upload
]
