import io
import json
import re
import subprocess
import sys
import shlex


class KeybaseChat:
    """Keybase Chat Client"""
    def __init__(self):
        self.base_cmd = 'keybase chat'
        self.username = self._get_username()

    def __repr__(self):
        return 'KeybaseChat()'

    def _send_chat_api(self, api_command):
        """Send a JSON formatted request to the chat api.

        This takes a dictionary and sends it as a JSON request to the Keybase
        chat api. You can get a full list of supported API commands by running
        the following command in the terminal:
            keybase chat api --help

        Args:
            api_command (dict): API command to send.

        Returns:
            dict: Response from API
        """
        command = "keybase chat api -m '{}'".format(
            json.JSONEncoder().encode(api_command).replace("'", "'\"'\"'")
        )
        response = subprocess.check_output(shlex.split(command))
        return json.loads(response.decode('utf-8'))

    def _send_chat_cmd(self, cmd):
        """added for future use if a api is not exposed"""
        command = '%s %s' % (self.base_cmd, cmd)
        with subprocess.Popen(
            shlex.split(command),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        ) as process:
            response = process.stdout.readlines()
        return response

    def _get_username(self):
        """Return the username of the current user from the keybase CLI.
           TODO:
            * Check for errors if user is not logged in
        """
        command = subprocess.check_output(['keybase', 'status', '-j'])
        keybase_status = json.loads(command.decode('utf-8'))
        return keybase_status.get('Username')

    @staticmethod
    def api_listener() -> dict:
        """api_listener() generator function around the api listener"""

        command = 'keybase chat api-listen'
        with subprocess.Popen(
            shlex.split(command),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        ) as process:
            while True:
                yield process.stdout.readline().decode('utf-8').strip()

    def list_inbox(self):
        """Return a dictionary with the users inbox
        """
        api_command = {
            "method": "list"
        }
        return self._send_chat_api(api_command)

    def get_conversations(self):
        """Return a dictionary with all active conversations.

        This method will return a dictionary containing all active
        conversations. The dictionary will be formatted as follows:

        {
            "teams": {
                "team1": {
                    "channel1": {
                        "conversation_id": <conversation_id>
                        "unread": True
                    },
                    "channel2": {
                        "conversation_id": <conversation_id>
                        "unread": False
                    }
                },
                "team2": {
                    "channel1": {
                        "conversation_id": <conversation_id>
                        "unread": False
                    },
                    "channel2": {
                        "conversation_id": <conversation_id>
                        "unread": True
                    }
                }
            },
            "individuals": {
                "individual1": {
                    "conversation_id": <conversation_id>
                    "unread": True
                },
                "individual2": {
                    "conversation_id": <conversation_id>
                    "unread": False
                }
            }
        }
        """
        api_command = {
            "method": "list",
            "params": {
                "options": {
                    "topic_type": "CHAT"
                }
            }
        }
        conversations_dict = self._send_chat_api(api_command)
        result = {
            "teams": {},
            "individuals": {},
        }
        for conversation in conversations_dict['result']['conversations']:
            conversation_id = conversation['id']
            unread = conversation['unread']
            if conversation['channel']['members_type'] == 'team':
                team_name = conversation['channel']['name']
                topic_name = conversation['channel']['topic_name']
                try:
                    result['teams'][team_name][topic_name] = {}
                except KeyError:
                    result['teams'][team_name] = {}
                    result['teams'][team_name][topic_name] = {}
                finally:
                    result['teams'][team_name]['conversation_id'] = conversation_id
                    result['teams'][team_name][topic_name]['unread'] = unread
            else:
                whole_name = conversation['channel']['name']
                name = whole_name.replace(self.username, '').replace(',', '')
                result['individuals'][name]['conversation_id'] = conversation_id
                result['individuals'][name] = {}
                result['individuals'][name]['unread'] = unread
        return result.copy()

    def send_team_message(self, team, message, channel='general', nonblock=False):
        """Send message to a team channel.

        Args:
            team (str): Team name
            message (str): Message to send to the channel

        Optional Args:
            channel (str): Channel name within the team

        Returns:
            dict: Response from API as follows:

        {
            "result": {
                "message": "message sent",
                "id": 516,
                "ratelimits": [{
                    "tank": "chat",
                    "capacity": 9000,
                    "reset": 899,
                    "gas":8999
                }]
            }
        }
        """
        api_command = {
            "method": "send",
            "params": {
                "options": {
                    "channel": {
                        "name": team,
                        "members_type": "team",
                        "topic_name": channel
                    },
                    "message": {
                        "body": message
                    },
                    "nonblock": nonblock
                }
            }
        }
        return self._send_chat_api(api_command)

    def send_user_message(self, user, message, nonblock=False):
        """Send message to a single user.

        Args:
            user (str): User's username
            message (str): Message to send to the user

        Returns:
            dict: Response from API as follows:

        {
            "result": {
                "message": "message sent",
                "id": 7,
                "ratelimits": [{
                    "tank": "chat",
                    "capacity": 9000,
                    "reset": 215,
                    "gas": 8986
                }]
            }
        }
        """
        api_command = {
            "method": "send",
            "params": {
                "options": {
                    "channel": {
                        "name": "{},{}".format(self.username, user)
                    },
                    "message": {
                        "body": message
                    },
                    "nonblock": nonblock
                }
            }
        }
        return self._send_chat_api(api_command)

    def send_conversationID_message(self, conversation_id, message, nonblock=False):
        """Send message to a conversation_id.

        Args:
            conversation_id (str): ConversationID to send the message to
            message (str): Message to send to the user

        Returns:
            dict: Response from API as follows:

        {
            "result": {
                "message": "message sent",
                "id": 7,
                "ratelimits": [{
                    "tank": "chat",
                    "capacity": 9000,
                    "reset": 215,
                    "gas": 8986
                }]
            }
        }
        """
        api_command = {
            "method": "send",
            "params": {
                "options": {
                    "conversation_id": conversation_id,
                    "message": {
                        "body": message
                    },
                    "nonblock": nonblock
                }
            }
        }
        return self._send_chat_api(api_command)

    def edit_team_message(self, team, message_id, message, channel='general', nonblock=False):
        """Edit message sent to a team channel.

        Args:
            team (str): Team name
            message_id (int): id of message to edit
            message (str): Edited message to replace existing message with

        Optional Args:
            channel (str): Channel name within the team

        Returns:
            dict: Response from API as follows:

        {
            "result": {
                "message": "message edited",
                "id": 517,
                "ratelimits": [{
                    "tank": "chat",
                    "capacity": 9000,
                    "reset": 842,
                    "gas": 8998
                }]
            }
        }
        """
        api_command = {
            "method": "edit",
            "params": {
                "options": {
                    "channel": {
                        "name": team,
                        "members_type": "team",
                        "topic_name": channel
                    },
                    "message_id": message_id,
                    "message": {
                        "body": message
                    },
                    "nonblock": nonblock
                }
            }
        }
        return self._send_chat_api(api_command)

    def edit_user_message(self, user, message_id, message, nonblock=False):
        """Edit sent message to a single user.

        Args:
            user (str): User's username
            message_id (int): id of message to edit
            message (str): Edited message to replace existing message with

        Returns:
            dict: Response from API as follows:

        {
            "result": {
                "message": "message edited",
                "id": 8,
                "ratelimits": [{
                    "tank": "chat",
                    "capacity": 9000,
                    "reset": 899,
                    "gas": 8999
                }]
            }
        }
        """
        api_command = {
            "method": "edit",
            "params": {
                "options": {
                    "channel": {
                        "name": "{},{}".format(self.username, user)
                    },
                    "message_id": message_id,
                    "message": {
                        "body": message
                    },
                    "nonblock": nonblock
                }
            }
        }
        return self._send_chat_api(api_command)

    def edit_conversationID_message(self, conversation_id, message_id, message, nonblock=False):
        """Edit sent message to a conversation_id.

        Args:
            conversation_id (str): ConversationID to edit the message from
            message_id (int): id of message to edit
            message (str): Edited message to replace existing message with

        Returns:
            dict: Response from API as follows:

        {
            "result": {
                "message": "message edited",
                "id": 8,
                "ratelimits": [{
                    "tank": "chat",
                    "capacity": 9000,
                    "reset": 899,
                    "gas": 8999
                }]
            }
        }
        """
        api_command = {
            "method": "edit",
            "params": {
                "options": {
                    "conversation_id": conversation_id,
                    "message_id": message_id,
                    "message": {
                        "body": message
                    },
                    "nonblock": nonblock
                }
            }
        }
        return self._send_chat_api(api_command)

    def reaction_team_message(self, team, message_id, message, channel='general', nonblock=False):
        """Add reaction to a message sent to a team channel.

        Args:
            team (str): Team name
            message_id (int): id of message to add reaction to
            message (str): Content of reaction, can be emoji or text
                e.g. ":+1:" or "<reaction-message>"

        Optional Args:
            channel (str): Channel name within the team

        Returns:
            dict: Response from API as follows:

        {
            "result": {
                "message": "message reacted to",
                "id": 518,
                "ratelimits": [{
                    "tank": "chat",
                    "capacity": 9000,
                    "reset":555,
                    "gas":8997
                }]
            }
        }
        """
        api_command = {
            "method": "reaction",
            "params": {
                "options": {
                    "channel": {
                        "name": team,
                        "members_type": "team",
                        "topic_name": channel
                    },
                    "message_id": message_id,
                    "message": {
                        "body": message
                    },
                    "nonblock": nonblock
                }
            }
        }
        return self._send_chat_api(api_command)

    def reaction_user_message(self, user, message_id, message, nonblock=False):
        """Add reaction to a message sent to a single user.

        Args:
            user (str): User's username
            message_id (int): id of message to add reaction to
            message (str): Content of reaction, can be emoji or text
                e.g. ":+1:" or "<reaction_message>"

        Returns:
            dict: Response from API as follows:

        {
            "result": {
                "message": "message reacted to",
                "id": 10,
                "ratelimits": [{
                    "tank": "chat",
                    "capacity": 9000,
                    "reset": 170,
                    "gas": 8997
                }]
            }
        }
        """
        api_command = {
            "method": "reaction",
            "params": {
                "options": {
                    "channel": {
                        "name": "{},{}".format(self.username, user)
                    },
                    "message_id": message_id,
                    "message": {
                        "body": message
                    },
                    "nonblock": nonblock
                }
            }
        }
        return self._send_chat_api(api_command)

    def reaction_conversationID_message(self, conversation_id, message_id, message, nonblock=False):
        """Add reaction to a message sent to a conversation_id.

        Args:
            conversation_id (str): ConversationID to react to a message from
            message_id (int): id of message to add reaction to
            message (str): Content of reaction, can be emoji or text
                e.g. ":+1:" or "<reaction_message>"

        Returns:
            dict: Response from API as follows:

        {
            "result": {
                "message": "message reacted to",
                "id": 10,
                "ratelimits": [{
                    "tank": "chat",
                    "capacity": 9000,
                    "reset": 170,
                    "gas": 8997
                }]
            }
        }
        """
        api_command = {
            "method": "reaction",
            "params": {
                "options": {
                    "conversation_id": conversation_id,
                    "message_id": message_id,
                    "message": {
                        "body": message
                    },
                    "nonblock": nonblock
                }
            }
        }
        return self._send_chat_api(api_command)

    def delete_team_message(self, team, message_id, channel='general', nonblock=False):
        """Delete a message sent to a team channel.

        Args:
            team (str): Team name
            message_id (int): id of message to delete

        Optional Args:
            channel (str): Channel name within the team

        Returns:
            dict: Response from API as follows:

        {
            "result": {
                "message": "message deleted",
                "id": 521,
                "ratelimits": [{
                    "tank": "chat",
                    "capacity": 9000,
                    "reset": 624,
                    "gas": 8993
                }]
            }
        }
        """
        api_command = {
            "method": "delete",
            "params": {
                "options": {
                    "channel": {
                        "name": team,
                        "members_type": "team",
                        "topic_name": channel
                    },
                    "message_id": message_id,
                    "nonblock": nonblock
                }
            }
        }
        return self._send_chat_api(api_command)

    def delete_user_message(self, user, message_id, nonblock=False):
        """Delete a message sent to a single user.

        Args:
            user (str): User's username
            message_id (int): id of message to delete

        Returns:
            dict: Response from API as follows:

        {
            "result": {
                "message": "message deleted",
                "id": 16,
                "ratelimits": [{
                    "tank": "chat",
                    "capacity": 9000,
                    "reset": 851,
                    "gas": 8998
                }]
            }
        }
        """
        api_command = {
            "method": "delete",
            "params": {
                "options": {
                    "channel": {
                        "name": "{},{}".format(self.username, user)
                    },
                    "message_id": message_id,
                    "nonblock": nonblock
                }
            }
        }
        return self._send_chat_api(api_command)

    def delete_conversationID_message(self, conversation_id, message_id, nonblock=False):
        """Delete a message sent to a conversation_id.

        Args:
            conversation_id (str): ConversationID to delete a message from
            message_id (int): id of message to delete

        Returns:
            dict: Response from API as follows:

        {
            "result": {
                "message": "message deleted",
                "id": 16,
                "ratelimits": [{
                    "tank": "chat",
                    "capacity": 9000,
                    "reset": 851,
                    "gas": 8998
                }]
            }
        }
        """
        api_command = {
            "method": "delete",
            "params": {
                "options": {
                    "conversation_id": conversation_id,
                    "message_id": message_id,
                    "nonblock": nonblock
                }
            }
        }
        return self._send_chat_api(api_command)

    def get_team_messages(self, team, channel='general'):
        """Return new messages from team channel.

        Args:
            team (str): Team name

        Optional Args:
            channel (str): Channel name within the team

        Returns dict formatted as follows:

        {
            "63": {
                "sender": "username2",
                "body": "message 3"
            },
            "62": {
                "sender": "username2",
                "body": "message 2"
            },
            "61": {
                "sender": "username1",
                "body": "message 1",
            }
        }
        """
        api_command = {
            "method": "read",
            "params": {
                "options": {
                    "channel": {
                        "name": team,
                        "members_type": "team",
                        "topic_name": channel
                    }
                }
            }
        }
        response = {}
        messages = self._send_chat_api(api_command)['result']['messages']
        for message in messages:
            if message['msg']['unread']:
                if message['msg']['content']['type'] == 'text':
                    message_id = str(message['msg']['id'])
                    sender = message['msg']['sender']['username']
                    body = message['msg']['content']['text']['body']
                    response[message_id] = {}
                    response[message_id]['sender'] = sender
                    response[message_id]['body'] = body
        return response

    def get_user_messages(self, user):
        """Return new messages from user.

        Args:
            user (str): User's username

        Returns dict formatted as follows:

        {
            "63": {
                "sender": "username",
                "body": "message 3"
            },
            "62": {
                "sender": "username",
                "body": "message 2"
            },
            "61": {
                "sender": "username",
                "body": "message 1",
            }
        }
        """
        api_command = {
            "method": "read",
            "params": {
                "options": {
                    "channel": {
                        "name": "{},{}".format(self.username, user),
                    }
                }
            }
        }
        response = {}
        for message in self._send_chat_api(api_command)['result']['messages']:
            if message['msg']['unread']:
                if message['msg']['content']['type'] == 'text':
                    message_id = message['msg']['id']
                    sender = message['msg']['sender']['username']
                    body = message['msg']['content']['text']['body']
                    response[message_id] = {}
                    response[message_id]['sender'] = sender
                    response[message_id]['body'] = body
        return response

    def get_conversationID_messages(self, conversation_id):
        """Return new messages from a conversation_id.

        Args:
            conversation_id (str): ConversationID to get messages from

        Returns dict formatted as follows:

        {
            "63": {
                "sender": "username",
                "body": "message 3"
            },
            "62": {
                "sender": "username",
                "body": "message 2"
            },
            "61": {
                "sender": "username",
                "body": "message 1",
            }
        }
        """
        api_command = {
            "method": "read",
            "params": {
                "options": {
                    "channel": {
                        "name": "{},{}".format(self.username, user),
                    }
                }
            }
        }
        response = {}
        for message in self._send_chat_api(api_command)['result']['messages']:
            if message['msg']['unread']:
                if message['msg']['content']['type'] == 'text':
                    message_id = message['msg']['id']
                    sender = message['msg']['sender']['username']
                    body = message['msg']['content']['text']['body']
                    response[message_id] = {}
                    response[message_id]['sender'] = sender
                    response[message_id]['body'] = body
        return response

