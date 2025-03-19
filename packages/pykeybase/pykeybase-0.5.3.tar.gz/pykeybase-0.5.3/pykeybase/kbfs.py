import io
import json
import re
import subprocess
import os
import platform

ansi_escape_re = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


class KeybaseFS:
    """KBFS Client"""

    def __init__(self):
        self.username = self._get_username()
        # Determine keybase location based on OS
        running_system = platform.system()
        if running_system == "Linux":
            self.base_dir = "/keybase"
        elif running_system == "Darwin":
            self.base_dir = "/Volumes/Keybase"
        elif running_system == "Windows":
            self.base_dir = "K:"

    def _write_file(self, filename: str, file_content: bytes):
        """Write file to the Keybase filesystem"""
        write_command = subprocess.Popen(
            ["keybase", "fs", "write", filename],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        write_command.stdin.write(file_content)
        _, stderr = write_command.communicate()
        if write_command.returncode != 0:
            if 'is not a file' in stderr.decode():
                raise IsADirectoryError(f'{filename} is a directory')
            else:
                raise Exception(stderr.decode())

    def _write_private_file(self, filename: str, file_content: bytes):
        """Write file to the user's private folder"""
        full_target_path = os.path.join(
            self.base_dir, "private", self.username, filename
        )
        self._write_file(full_target_path, file_content)

    def _write_team_file(self, filename: str, file_content: bytes, team: str):
        """Writes a file to a team folder"""
        full_target_path = os.path.join(
            self.base_dir, "team", team, filename
        )
        self._write_file(full_target_path, file_content)

    def _write_shared_file(self, filename: str, file_content: bytes, share_with: list):
        """Writes file to a shared directory."""
        share_string = self.username + "," + ",".join(share_with)
        full_target_path = os.path.join(self.base_dir, "private", share_string)
        self._write_file(full_target_path, file_content)

    def _write_public_file(self, filename: str, file_content: bytes):
        """Write file to the user's public folder"""
        full_target_path = os.path.join(
            self.base_dir, "public", self.username, filename
        )
        self._write_file(full_target_path, file_content)

    def _get_public_dir_contents(self, username: str = "") -> list:
        """List the public files of a user. The bot's files are listed by default"""
        if not username:
            username = self.username
        full_directory = os.path.join(self.base_dir, "public", username)
        ls_command = subprocess.check_output(
            ["keybase", "fs", "ls", "--rec", "-a", full_directory]
        ).decode().rstrip()
        file_list = ansi_escape_re.sub('', ls_command).split()
        return file_list

    def _get_private_dir_contents(self) -> list:
        """List the user's private files."""
        full_directory = os.path.join(self.base_dir, "private", self.username)
        ls_command = subprocess.check_output(
            ["keybase", "fs", "ls", "--rec", "-a", full_directory]
        ).decode().rstrip()
        file_list = ansi_escape_re.sub('', ls_command).split()
        return file_list

    def _get_shared_dir_contents(self, shared_with: list) -> list:
        """List the files shared between the user and a list of others"""
        share_string = self.username + ',' + ','.join(shared_with)
        full_directory = os.path.join(self.base_dir, "private", share_string)
        ls_command = subprocess.check_output(
            ["keybase", "fs", "ls", "--rec", "-a", full_directory]
        ).decode().rstrip()
        file_list = ansi_escape_re.sub('', ls_command).split()
        return file_list

    def _get_team_dir_contents(self, team: str) -> list:
        """List the files shared within a team"""
        full_directory = os.path.join(self.base_dir, "team", team)
        ls_command = subprocess.check_output(
            ["keybase", "fs", "ls", "--rec", "-a", full_directory]
        ).decode().rstrip()
        file_list = ansi_escape_re.sub('', ls_command).split()
        return file_list

    def _read_file_from_path(self, full_path: str) -> io.BytesIO:
        """Return a BytesIO object of the file as bytes"""
        file_as_bytes = None
        try:
            file_as_bytes = subprocess.check_output(['keybase', 'fs', 'read', full_path], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            error = exc.output.decode()
            if 'is not a file' in error:
                raise IsADirectoryError(f'{full_path} is a directory. Did you mean to get contents?') from exc
            elif 'file does not exist' in error:
                raise FileNotFoundError(f'{full_path} not found.') from exc
            else:
                raise exc
        return io.BytesIO(file_as_bytes)

    def _read_public_file(self, file_path: str, username: str = '') -> io.BytesIO:
        """Reads a public file to file-like object"""
        full_path = os.path.join(self.base_dir, 'public', username or self.username, file_path)
        return self._read_file_from_path(full_path)

    def _read_private_file(self, file_path: str) -> io.BytesIO:
        """Reads a file from the user's private dir"""
        full_path = os.path.join(self.base_dir, 'private', self.username, file_path)
        return self._read_file_from_path(full_path)

    def _read_shared_file(self, file_path: str, shared_with: list) -> io.BytesIO:
        """Reads a file from a shared directory"""
        share_string = self.username + ',' + ','.join(shared_with)
        full_path = os.path.join(self.base_dir, "private", share_string, file_path)
        return self._read_file_from_path(full_path)

    def _read_team_file(self, file_path: str, team: str) -> io.BytesIO:
        """Reads a file from a team directory"""
        full_path = os.path.join(self.base_dir, 'team', team, file_path)
        return self._read_file_from_path(full_path)

    def _make_dirs(self, base_path: str, new_dirs: list):
        """
        Iterates through a list of dirs to create in
        a base folder. Keybase FS API doesn't allow for
        mkdir when parents do not exist, but calling mkdir
        on a dir that does exist has no effect, so this just
        implements mkdir -p, essentially.
        """
        cur_path = base_path
        for new_dir in new_dirs:
            cur_path = os.path.join(cur_path, new_dir)
            subprocess.run(['keybase', 'fs', 'mkdir', cur_path])

    def _mkdir_private(self, dir: str) -> None:
        """
        Creates a new subdirectory in the user's private folder.
        """
        base_path = os.path.join(self.base_dir, 'private', self.username)
        self._make_dirs(base_path, dir.split(os.sep))

    def _mkdir_public(self, dir: str) -> None:
        """
        Creates a new subdirectory in the user's public
        folder.
        """
        base_path = os.path.join(self.base_dir, 'public', self.username)
        self._make_dirs(base_path, dir.split(os.sep))

    def _mkdir_shared(self, dir: str, shared_with: list) -> None:
        """
        Creates a new subdirectory in a folder shared between
        the logged-in user and the users listed in shared_with
        """
        share_string = self.username + ',' + ','.join(shared_with)
        base_path = os.path.join(self.base_dir, 'private', share_string)
        self._make_dirs(base_path, dir.split(os.sep))

    def _mkdir_team(self, dir: str, team_name: str) -> None:
        """
        Creates a new subdirectory in the given team
        folder.
        """
        base_path = os.path.join(self.base_dir, 'team', team_name)
        self._make_dirs(base_path, dir.split(os.sep))

    def _rm(self, paths: list, recursive: bool = False) -> None:
        """
        Removes all given paths.
        """
        command_list = ['keybase', 'fs', 'rm'] + (['-r'] if recursive else []) + paths
        subprocess.run(command_list)

    def _get_quota(self) -> dict:
        """
        Returns a dict of your usage, maximum,
        and available remaining storage.
        """
        command = subprocess.check_output(["keybase", "fs", "quota", "--json"])
        quota_status = json.loads(command.decode('utf-8'))
        results = {
            "total": self._byte_size(quota_status["QuotaBytes"]),
            "used": self._byte_size(quota_status["UsageBytes"]),
            "available": self._byte_size((quota_status["QuotaBytes"] - quota_status["UsageBytes"]))
        }
        return results

    def _get_team_quota(self, team_name: str) -> dict:
        """
        Returns a dict of a team's usage, maximum,
        and available remaining storage.
        """
        try:
            command = subprocess.check_output(["keybase", "fs", "quota", "--json", "--team", team_name], stderr=subprocess.STDOUT)
            quota_status = json.loads(command.decode('utf-8'))
            results = {
                "total": self._byte_size(quota_status["QuotaBytes"]),
                "used": self._byte_size(quota_status["UsageBytes"]),
                "available": self._byte_size((quota_status["QuotaBytes"] - quota_status["UsageBytes"]))
            }
        except subprocess.CalledProcessError as exc:
            error = exc.output.decode()
            if "does not exist" in error:
                raise AssertionError(f"The '{team_name}' team does not exist.") from exc
            elif "not a member" in error:
                raise AssertionError(f"You are not a member of the '{team_name}' team.") from exc
            else:
                raise exc
        return results

    def _get_username(self):
        """Return the username of the current user from the keybase CLI.
        TODO:
         * Check for errors if user is not logged in
        """
        command = subprocess.check_output(["keybase", "status", "-j"])
        keybase_status = json.loads(command.decode("utf-8"))
        return keybase_status.get("Username")

    def _byte_size(self, byte_count: int) -> str:
        """
        Return a byte count as a nice string
        of KB, MB, etc.
        """
        from math import floor, log, pow
        if byte_count == 0:
            return "0B"
        sizes = ("B", "KB", "MB", "GB")
        size_power = int(floor(log(byte_count, 1024)))
        size_base_int = pow(1024, size_power)
        size = round(byte_count / size_base_int, 2)
        return f"{size} {sizes[size_power]}"
