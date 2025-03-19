import json
import re
import subprocess
import sys
import shlex


class KeybaseTeam:
    """Keybase Chat Client"""
    def __init__(self):
        self.base_cmd ='keybase team'

    def _send_team_api(self, api_command):
        """Send a JSON formatted request to the team api.

        This takes a dictionary and sends it as a JSON request to the Keybase
        team api. You can get a full list of supported API commands by running
        the following command in the terminal:
            keybase team api --help

        Args:
            api_command (dict): API command to send.

        Returns:
            dict: Response from API
        """
        command = "%s api -m '%s'" % (
            self.base_cmd,
            json.JSONEncoder().encode(api_command)
        )
        try:
            response = subprocess.check_output(shlex.split(command))
        except subprocess.CalledProcessError as err:
            raise

        return json.loads(response.decode('utf-8'))

    def _send_team_cmd(self, cmd):
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

    def create_team(self, team):
        """
        {
            "method": "create-team",
            "params": {
                "options": {
                    "team": "phoenix"
                }
            }
        }
        """
        cmd = {
            "method": "create-team",
            "params": {
                "options": {
                    "team": team
                }
            }
        }

        return self._send_team_api(cmd)

    def rename_subteam(self, team, new_team):
        """
        {
            "method": "rename-subteam",
            "params": {
                "options": {
                    "team": "phoenix.bots",
                    "new-team-name": "phoenix.humans"
                }
            }
        }
        """
        cmd = {
            "method": "rename-subteam",
            "params": {
                "options": {
                    "team": team,
                    "new-team-name": new_team
                }
            }
        }

        return self._send_team_api(cmd)

    def team_requests(self, team):
        """
        {
            "method": "list-requests",
            "params": {
                "options": {
                    "team": "phoenix"
                }
            }
        }
        """
        cmd = {
            "method": "list-requests",
            "params": {
                "options": {
                    "team": team
                }
            }
        }

        return self._send_team_api(cmd)

    def add_members(self, team, usernames: list=None, emails: list=None) -> dict:
        """
        {
            "method": "add-members",
            "params": {
                "options": {
                    "team": "phoenix", 
                    "emails": [
                        {
                            "email": "alice@keybase.io", 
                            "role": "writer"
                        },
                        ...
                    ],
                    "usernames": [
                        {
                            "username": "frank",
                            "role": "reader"
                        },
                        {
                            "username": "keybaseio@twitter",
                            "role": "writer"
                        }
                    ]
                }
            }
        }
        """
        cmd = {
            "method": "add-members",
            "params": {
                "options": {
                    "team": team
                }
            }
        }
        if emails:
            cmd['params']['options']['email'] = emails
        if usernames:
            cmd['params']['options']['usernames'] = usernames

        return self._send_team_api(cmd)

    def change_membership(self, team, username, role):
        """
        {
            "method": "edit-member",
            "params": {
                "options": {
                    "team": "phoenix",
                    "username": "frank",
                    "role": "writer"
                }
            }
        }
        """
        cmd = {
            "method": "edit-member",
            "params": {
                "options": {
                    "team": team,
                    "username": username,
                    "role": role
                }
            }
        }

        return self._send_team_api(cmd)        

    def remove_member(self, team, username: str) -> dict:
        """
        {
            "method": "remove-member",
            "params": {
                "options": {
                "team": "phoenix",
                "username": "frank"
                }
            }
        }
        """
        cmd = {
            "method": "remove-member",
            "params": {
                "options": {
                    "team": team,
                    "username": username
                }
            }
        }

        return self._send_team_api(cmd)

    def list_memberships(self, team):
        """
        {
            "method": "list-team-memberships",
            "params": {
                "options": {
                    "team": "phoenix"
                    }
                }
        }
        """
        cmd = {
            "method": "list-team-memberships",
            "params": {
                "options": {
                    "team": team
                }
            }
        }

        return self._send_team_api(cmd)

    def list_memberships_self(self, team):
        """
        {
            "method": "list-self-memberships",
        }
        """
        cmd = {
            "method": "list-self-memberships"
        }

        return self._send_team_api(cmd)

    def list_memberships_user(self, username):
        """
        {
            "method": "list-user-memberships",
            "params": {
                "options": {
                    "username": "cleo"
                    }
                }
        }
        """
        cmd = {
            "method": "list-user-memberships",
            "params": {
                "options": {
                    "username": username
                }
            }
        }

        return self._send_team_api(cmd)

    def leave_team(self, team):
        """
        {
            "method": "leave-team",
            "params": {
                "options": {
                    "team": "phoenix",
                    "permanent": "true"
                }
            }
        }
        """
        cmd = {
            "method": "leave-team",
            "params": {
                "options": {
                    "team": team,
                    "permanent": true
                }
            }
        }

        return self._send_team_api(cmd)
