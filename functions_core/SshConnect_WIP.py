import fabric2, logging, tempfile, time, threading

class SshConnect():

    active_sessions = []
    global_lock = threading.Lock()

    @staticmethod 
    def manage_sessions(session_key: list):
        timestamp_now = time.time()
        keep_sessions = []
        valid_session = []
        logging.debug(f"Managing sessions for session keys: {session_key} and active_sessions: {SshConnect.active_sessions}")

        if SshConnect.active_sessions:
            for value in SshConnect.active_sessions:
                try:
                    if not hasattr(value[4], 'ssh') or not getattr(value[4].ssh, 'is_connected', False):
                        logging.debug(f"Session {value[4]} is not connected or missing 'ssh'")
                        continue
                except Exception as msgerror:
                    logging.error(f"Failed to check session connection for {value} with msg: {msgerror}")
                    continue

                if abs(timestamp_now - value[5]) <= 55:
                    logging.debug(f"Valid session under 55s and connected: {value}")
                    keep_sessions.append(value)
                    if session_key and value[:4] == session_key[:4]:
                        logging.debug(f"This is the instance to be reused: {value[4]}")
                        valid_session = value[4]
                else:
                    logging.debug(f"Session no longer valid, closing: {value}")
                    invalid_session = value[4]
                    if hasattr(invalid_session, 'ssh_bastion'):
                        invalid_session.ssh_bastion.close()
                        del invalid_session.ssh_bastion
                        logging.debug("Closed bastion session")
                    if hasattr(invalid_session, 'ssh'):
                        invalid_session.ssh.close()
                        del invalid_session.ssh
                        logging.debug("Closed ssh session")
            SshConnect.active_sessions = keep_sessions
            return valid_session if valid_session else None
        else:
            logging.debug("No active sessions found")
            return None

    def __init__(self, param_ip, bastion, user, host_keys):
        session_key = [param_ip, bastion, user, host_keys, self, time.time()]

        with SshConnect.global_lock:
            ret_value = SshConnect.manage_sessions(session_key)
            if ret_value:
                self.ssh = ret_value.ssh
                if hasattr(ret_value, 'ssh_bastion'):
                    self.ssh_bastion = ret_value.ssh_bastion
                return  # Return early if we re-used session

            # No active session found, create new connection
            self.bastion = bastion
            if bastion:
                # Connect to bastion
                try:
                    self.ssh_bastion = fabric2.Connection(
                        host=str(bastion), 
                        user=user, 
                        port=22, 
                        connect_timeout=12, 
                        connect_kwargs={
                            "key_filename": host_keys, 
                            "banner_timeout": 12, 
                            "auth_timeout": 12, 
                            "channel_timeout": 12,
                        }
                    )
                    self.ssh_bastion.open()
                    logging.debug("Opened bastion connection")
                except Exception as e:
                    logging.error(f"Failed to connect to bastion: {e}")
                    self.cleanup()
                    raise Exception(f"Failed the connection to bastion: {e}")

                # Retrieve private key from bastion
                try:
                    pkey_bastion = self.ssh_bastion.run("cat $HOME/.ssh/id_rsa", hide=True).stdout.strip()
                    logging.debug(f"Received private key (truncated): {pkey_bastion[:50]}")
                except Exception as e:
                    logging.error(f"Failed to retrieve private key from bastion: {e}")
                    self.cleanup()
                    raise Exception(f"Failed to retrieve PKEY from bastion: {e}")

                # Write private key to temporary file
                with tempfile.NamedTemporaryFile(delete=False) as f:
                    f.write(pkey_bastion.encode())
                    private_key_file = f.name

                # Connect to target host through bastion
                try:
                    self.ssh = fabric2.Connection(
                        host=str(param_ip),
                        user=user,
                        port=22,
                        connect_timeout=12,
                        connect_kwargs={
                            "key_filename": private_key_file,
                            "banner_timeout": 12,
                            "auth_timeout": 12,
                            "channel_timeout": 12,
                        },
                        gateway=self.ssh_bastion
                    )
                    self.ssh.open()
                    logging.debug("SSH connection through bastion opened successfully")
                except Exception as e:
                    logging.error(f"Failed to connect to host through bastion: {e}")
                    self.cleanup()
                    raise Exception(f"Failed to connect through bastion: {e}")

                if hasattr(self, 'ssh') and getattr(self.ssh, 'is_connected', False):
                    SshConnect.active_sessions.append(session_key)

            else:
                # No bastion, direct connection
                try:
                    self.ssh = fabric2.Connection(
                        host=param_ip, 
                        user=user, 
                        port=22, 
                        connect_timeout=12, 
                        connect_kwargs={
                            "key_filename": host_keys,
                            "banner_timeout": 12,
                            "auth_timeout": 12,
                            "channel_timeout": 12,
                        }
                    )
                    self.ssh.open()
                    logging.debug("SSH direct connection opened successfully")
                except Exception as e:
                    logging.error(f"Failed direct SSH connection: {e}")
                    self.cleanup()
                    raise Exception(f"Failed direct connection: {e}")

                if hasattr(self, 'ssh') and getattr(self.ssh, 'is_connected', False):
                    SshConnect.active_sessions.append(session_key)

    def run(self, cmd):
        with SshConnect.global_lock:
            try:
                logging.debug(f"Executing command on session: {self}")
                return self.ssh.run(cmd, hide=True, timeout=30, warn=True)
            except Exception as e:
                logging.error(f"Failed to execute command: {e}")
                self.cleanup()
                raise Exception(f"Command execution failed: {e}")

    def rm(self):
        with SshConnect.global_lock:
            SshConnect.manage_sessions(None)

    def cleanup(self):
        if hasattr(self, 'ssh'):
            try:
                self.ssh.close()
            except:
                pass
            del self.ssh
        if hasattr(self, 'ssh_bastion'):
            try:
                self.ssh_bastion.close()
            except:
                pass
            del self.ssh_bastion
