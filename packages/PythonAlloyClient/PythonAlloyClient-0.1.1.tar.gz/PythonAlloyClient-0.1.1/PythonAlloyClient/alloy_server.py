import socket
import subprocess
import json
from typing import Optional
import random
import threading
import os
import re
from .syntax_status import SyntaxStatus

# get path to internal Alloy jar
internal_jar_path = os.path.join(
    os.path.dirname(__file__), "resources", "org.alloytools.alloy.dist.jar"
)


class AlloyServer:
    def __init__(self, alloy_jar_path: str = internal_jar_path, quiet: bool = True):
        self.alloy_jar_path = alloy_jar_path
        self.port = self._find_available_port()
        self.process: Optional[subprocess.Popen] = None
        self.socket: Optional[socket.socket] = None
        self.server_socket: Optional[socket.socket] = None
        self.client_socket: Optional[socket.socket] = None

        self.quiet = quiet

    def _find_available_port(self) -> int:
        """Find an available port between 49152 and 65534"""
        while True:
            port = random.randint(49152, 65534)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(("localhost", port))
                sock.close()
                return port
            except OSError:
                sock.close()
                continue

    def print(self, *args, **kwargs):
        if not self.quiet:
            print(*args, **kwargs)

    def _log_subprocess_output(self, stream, prefix):
        """Log subprocess output with prefix"""
        for line in stream:
            if isinstance(line, bytes):
                line = line.decode()
            self.print(f"{prefix}: {line.rstrip()}")

    def start(self):
        """Start the Alloy language server"""
        try:
            # Create and bind server socket first
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(("localhost", self.port))
            self.server_socket.listen(1)

            # Launch Alloy server process with output handling
            self.print(
                f"Starting Alloy language server: java -jar {self.alloy_jar_path} ls {self.port}"
            )
            self.process = subprocess.Popen(
                ["java", "-jar", self.alloy_jar_path, "ls", str(self.port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )

            # Start threads to monitor subprocess output
            threading.Thread(
                target=self._log_subprocess_output,
                args=(self.process.stdout, "Alloy[stdout]"),
                daemon=True,
            ).start()
            threading.Thread(
                target=self._log_subprocess_output,
                args=(self.process.stderr, "Alloy[stderr]"),
                daemon=True,
            ).start()

            # Accept client connection from language server
            self.print(
                f"Waiting for Alloy language server to connect on port {self.port}..."
            )
            self.client_socket, _ = self.server_socket.accept()
            self.print("Alloy language server connected!")

        except Exception as e:
            self.stop()
            raise RuntimeError(f"Failed to start Alloy server: {e}")

    def stop(self):
        """Stop the Alloy language server"""
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
        if self.process:
            self.process.terminate()
            self.process = None

    def _send_lsp_message(self, message: dict):
        """Send a message following LSP protocol"""
        content = json.dumps(message)
        content_bytes = content.encode("utf-8")
        header = f"Content-Length: {len(content_bytes)}\r\n\r\n"

        self.print(f"Sending message:\nHeader: {header.strip()}\nContent: {content}")

        self.client_socket.sendall(header.encode("ascii"))
        self.client_socket.sendall(content_bytes)

    def _read_lsp_message(self) -> dict:
        """Read a message following LSP protocol"""
        # Read header
        header = ""
        while not header.endswith("\r\n\r\n"):
            next_char = self.client_socket.recv(1).decode("ascii")
            if not next_char:
                raise RuntimeError("Connection closed while reading header")
            header += next_char

        self.print(f"Received header: {header.strip()}")

        # Parse Content-Length
        if not header.startswith("Content-Length: "):
            raise RuntimeError(f"Invalid header: {header}")
        content_length = int(header.split(":")[1].strip().split("\r\n")[0])

        # Read content
        content_bytes = b""
        while len(content_bytes) < content_length:
            chunk = self.client_socket.recv(content_length - len(content_bytes))
            if not chunk:
                raise RuntimeError("Connection closed while reading content")
            content_bytes += chunk

        content = content_bytes.decode("utf-8")
        self.print(f"Received content: {content}")
        return json.loads(content)

    def check_syntax(self, alloy_code: str) -> SyntaxStatus:
        """
        Check Alloy code syntax by sending to language server.
        Returns a SyntaxStatus object containing the syntax check result.
        """
        if not self.client_socket:
            raise RuntimeError("Server not connected")

        try:
            # Save code to temporary file
            tmp_file = "temp_check.als"
            tmp_file_uri = f"file:///{tmp_file}"

            with open(tmp_file, "w") as f:
                f.write(alloy_code)

            # First notify server about the document
            # by simulating a didOpen request
            didopen_request = {
                "jsonrpc": "2.0",
                "method": "textDocument/didOpen",
                "params": {
                    "textDocument": {
                        "uri": tmp_file_uri,
                        "languageId": "alloy",
                        "version": 1,
                        "text": alloy_code,
                    }
                },
            }
            self._send_lsp_message(didopen_request)

            # Now execute the command
            execute_request = {
                "jsonrpc": "2.0",
                "method": "ExecuteAlloyCommand",
                "params": [
                    tmp_file_uri,
                    -1,  # command index (-1 for syntax check only)
                    0,  # line
                    0,  # char
                ],
                "id": 1,
            }

            self.print("\nSending execute command...")
            self._send_lsp_message(execute_request)

            self.print("\nWaiting for response...")
            response = self._read_lsp_message()

            # Cleanup temp file
            os.remove(tmp_file)

            if "error" in response:
                traceback = response["error"]["data"]
                traceback_lines = traceback.splitlines()

                # look at the last "Caused by: " line and
                # select all lines until indentation begins
                error_message = ""
                for line in reversed(traceback_lines):
                    if line.startswith("Caused by: "):
                        line = line[11:]
                        error_message = line + "\n" + error_message
                        break

                    if line[0].strip() == "":
                        continue  # skip indented lines

                    error_message = line + "\n" + error_message

                error_message = error_message.strip()
                
                # get the first line of the error message with error info
                error_info_line = error_message.split("\n")[0]
                
                # now parse the error info line
                error_type = error_info_line.split("at")[0].strip()
                
                # search for the line and column number in the error info line
                # as "line \d+" and "column \d+"
                line_number = int(re.search(r"line \d+", error_info_line).group(0).split()[1])
                column_number = int(re.search(r"column \d+", error_info_line).group(0).split()[1])                
                
                # get the remaining lines of the error message
                narrowed_error_message = ("\n".join(error_message.split("\n")[1:])).strip()

                error_dict = {
                    "full_error_message": error_message,
                    "error_type": error_type,
                    "line_number": line_number,
                    "column_number": column_number,
                    "error_message": narrowed_error_message
                }
                return SyntaxStatus(False, error_dict)

            return SyntaxStatus(True)

        except Exception as e:
            if os.path.exists(tmp_file):
                os.remove(tmp_file)
            return SyntaxStatus(False, str(e))
