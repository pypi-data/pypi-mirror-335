import os.path as osp
import time

import paramiko

from pybsc import run_command


def return_true():
    return True


def create_tunnel_through_bastion(
        target_host, target_user,
        key_filepath=None,
        bastion_host=None, bastion_user=None):
    if key_filepath is None:
        key_filepath = osp.expanduser(osp.join('~', '.ssh', 'id_rsa'))
    target = paramiko.SSHClient()
    target.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    if bastion_host and bastion_user:
        bastion = paramiko.SSHClient()
        bastion.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        bastion.connect(bastion_host, username=bastion_user,
                        key_filename=key_filepath)

        bastion_transport = bastion.get_transport()
        dest_addr = (target_host, 22)  # Destination server IP and SSH port
        local_addr = ('127.0.0.1', 22)  # Local server IP and SSH port
        channel = bastion_transport.open_channel(
            "direct-tcpip", dest_addr, local_addr)

        target.connect(target_host, username=target_user,
                       key_filename=key_filepath, sock=channel)
    else:
        target.connect(target_host, username=target_user,
                       key_filename=key_filepath)
    return target


class SSHExecutor:

    def __init__(
            self, target_host, target_user,
            key_filepath=None,
            bastion_host=None, bastion_user=None):
        if key_filepath is None:
            key_filepath = osp.expanduser(osp.join('~', '.ssh', 'id_rsa'))
        self._target_host = target_host
        self._target_user = target_user
        self._key_filepath = key_filepath
        self._bastion_host = bastion_host
        self._bastion_user = bastion_user
        self._client = create_tunnel_through_bastion(
            target_host, target_user, key_filepath, bastion_host, bastion_user)

    def __del__(self):
        self._client.close()

    def execute_command(self, command):
        stdin, stdout, stderr = self._client.exec_command(command)
        output = stdout.read()
        return output

    def watch_dog(self, remote_file_path, poll_interval=5, condition=None):
        if condition is None:
            condition = return_true
        while condition():
            try:
                stdin, stdout, stderr = self._client.exec_command(
                    f"test -f {remote_file_path} && echo exists || echo not_exists")
                output = stdout.read().decode().strip()
                if "exists" == output:
                    print(f"File {remote_file_path} exists on remote server.")
                    break
                else:
                    print(f"Waiting for file {remote_file_path} to be created on remote server.")
                    time.sleep(poll_interval)
            except Exception as e:
                print(f"Error in watch_dog: {e}")
                break
        return condition()

    def execute_command_tmux(self, command, session_name):
        self.execute_command(f"tmux new-session -d -s {session_name}")
        tmux_command = f"tmux send-keys -t {session_name} '{command}' Enter"
        self.execute_command(tmux_command)

    def kill_tmux_session(self, session_name):
        self.execute_command(f'tmux kill-session -t {session_name}')

    def rsync(self, local_path, remote_path, is_upload=True):
        ssh_options = ["ssh", f"-i {self._key_filepath}",
                       '-o', 'StrictHostKeyChecking=no']

        if self._bastion_host is not None and self._bastion_user is not None:
            proxy_command = (
                f"-o ProxyCommand='ssh -o StrictHostKeyChecking=no -W %h:%p -i {self._key_filepath} "  # NOQA
                f"{self._bastion_user}@{self._bastion_host}'"
            )
            ssh_options.append(proxy_command)

        ssh_option_str = ' '.join(ssh_options)
        rsync_command = f"rsync -avz -e \"{ssh_option_str}\""

        if is_upload and osp.isdir(local_path):
            rsync_command += " -r"

        remote = f"{self._target_user}@{self._target_host}:{remote_path}"

        if is_upload:
            full_command = f"{rsync_command} \"{local_path}\" \"{remote}\""
        else:
            full_command = f"{rsync_command} \"{remote}\" \"{local_path}\""
        return run_command(full_command, shell=True)
