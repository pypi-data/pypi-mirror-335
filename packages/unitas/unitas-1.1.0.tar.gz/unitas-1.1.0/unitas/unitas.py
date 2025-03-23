#!/bin/python
# pylint: disable=fixme, line-too-long, logging-fstring-interpolation, missing-function-docstring, missing-class-docstring
import glob
import threading
import http.server
import socketserver
import threading
import webbrowser
import tempfile
import shutil
import time
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError, Element
from typing import Dict, List, Optional, Tuple, Any, Set
import os
import concurrent.futures
import argparse
import re
import socket
from ipaddress import ip_address
import logging
from collections import defaultdict
from abc import ABC, abstractmethod
import time
import configparser
import shutil
from copy import deepcopy
from importlib.metadata import version, PackageNotFoundError
from hashlib import sha512
import json

try:
    import requests
    import urllib3

    REQUESTS_INSTALLED = True
except ImportError:
    REQUESTS_INSTALLED = False

try:
    from importlib.metadata import version, PackageNotFoundError

    try:
        __version__ = version("unitas")
    except PackageNotFoundError:
        __version__ = "dev-version"
except ImportError:
    __version__ = "dev-version"  # Fallback for older Python versions


def start_http_server(json_content, port=8000):
    """Start an HTTP server to serve the HTML viewer and JSON data."""
    # Create a temporary directory to serve files from
    temp_dir = tempfile.mkdtemp()
    try:
        # Find the HTML file
        html_file = None
        # Try to find the packaged HTML file
        try:
            import pkg_resources

            html_file = pkg_resources.resource_filename("unitas.resources", "view.html")
        except (ImportError, pkg_resources.DistributionNotFound):
            # Fall back to looking in the script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            potential_html = os.path.join(script_dir, "view.html")
            if os.path.exists(potential_html):
                html_file = potential_html

        if not html_file or not os.path.exists(html_file):
            logging.error("Could not find the HTML viewer file (view.html)")
            return False

        # Copy the HTML file to the temp directory
        shutil.copy(html_file, os.path.join(temp_dir, "index.html"))

        # Write the JSON data to the temp directory
        with open(os.path.join(temp_dir, "data.json"), "w", encoding="utf-8") as f:
            f.write(json_content)

        # Create a minimal JavaScript file to auto-load the data
        auto_loader_js = """
        document.addEventListener('DOMContentLoaded', function() {
            // Auto-load the JSON data
            fetch('data.json')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    // Access the internal handleFile function
                    // Simulate file selection
                    scanData = data;
                    
                    // Hide the initial screen and show data view directly
                    document.getElementById('initial-screen').classList.add('hidden');
                    document.getElementById('data-view').classList.remove('hidden');
                    document.getElementById('error-message').classList.add('hidden');
                    
                    // Call the validation and display functions
                    validateAndDisplayData(data);
                })
                .catch(error => {
                    console.error('Error loading data:', error);
                    const errorMsg = document.getElementById('error-message');
                    if (errorMsg) {
                        errorMsg.textContent = "Error loading data automatically. Please try uploading manually.";
                        errorMsg.classList.remove('hidden');
                    }
                });
        });
        """

        with open(os.path.join(temp_dir, "auto-loader.js"), "w", encoding="utf-8") as f:
            f.write(auto_loader_js)

        # Modify the index.html to include the auto-loader script
        with open(os.path.join(temp_dir, "index.html"), "r", encoding="utf-8") as f:
            html_content = f.read()

        # Add the auto-loader script right before the closing </head> tag
        html_content = html_content.replace(
            "</head>", '<script src="auto-loader.js"></script></head>'
        )

        with open(os.path.join(temp_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_content)

        # Save the current directory
        original_dir = os.getcwd()

        # Change to the temp directory
        os.chdir(temp_dir)

        # Create a custom HTTP handler to add CORS headers
        class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
            def end_headers(self):
                self.send_header("Access-Control-Allow-Origin", "*")
                super().end_headers()

        # Create a simple HTTP server
        httpd = socketserver.TCPServer(("", port), CustomHTTPRequestHandler)

        # Start server in a new thread
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        logging.info(f"Started HTTP server at http://localhost:{port}")
        logging.info("The web interface is now available")
        logging.info("Press Ctrl+C to stop the server")

        # Open web browser
        webbrowser.open(f"http://localhost:{port}/index.html")

        # Keep the main thread running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("\nStopping HTTP server")

        # Shutdown the server
        httpd.shutdown()
        server_thread.join()

        # Return to the original directory
        os.chdir(original_dir)

        return True

    except Exception as e:
        logging.error(f"Error starting HTTP server: {e}")
        return False
    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)


class UnitasConfig:
    def __init__(self, config_file: str = "~/.unitas"):
        self.config_file = os.path.expanduser(config_file)
        self.config = configparser.ConfigParser()

        if not os.path.exists(self.config_file):
            logging.error(f"Config file {config_file} was not found creating default")
            self.create_template_config()
        else:
            self.config.read(self.config_file)

    def create_template_config(self):
        self.config["nessus"] = {
            "secret_key": "",
            "access_key": "",
            "url": "https://127.0.0.1:8834",
        }
        with open(self.config_file, "w") as file:
            self.config.write(file)
        logging.info(
            f"Template config file created at {self.config_file}. Please update the settings."
        )

    def get_secret_key(self):
        return self.config.get("nessus", "secret_key")

    def get_access_key(self):
        return self.config.get("nessus", "access_key")

    def get_url(self):
        return self.config.get("nessus", "url")


class PortDetails:
    def __init__(
        self,
        port: str,
        protocol: str,
        state: str,
        service: str = "unknown?",
        comment: str = "",
    ):
        if not PortDetails.is_valid_port(port):
            raise ValueError(f'Port "{port}" is not valid!')
        self.port = port
        self.protocol = protocol
        self.state = state
        self.service = service
        self.comment = comment

    def __str__(self) -> str:
        return f"{self.port}/{self.protocol}({self.service})"

    def to_dict(self) -> Dict[str, str]:
        return {
            "port": self.port,
            "protocol": self.protocol,
            "state": self.state,
            "service": self.service,
            "comment": self.comment,
        }

    def __eq__(self, other):
        if not isinstance(other, PortDetails):
            return NotImplemented
        return self.to_dict() == other.to_dict()

    def __repr__(self) -> str:
        return f"PortDetails({self.port}/{self.protocol} {self.state} {self.service} {self.comment})"

    def update(self, other: "PortDetails"):
        # check if service should be overwritten
        update_service = False
        if other.service != "unknown?" and self.service == "unknown?":
            update_service = True
        if (
            not "unknown" in other.service and not "?" in other.service
        ) and self.service == "unknown":
            update_service = True
        # without the question mark, it was a service scan
        elif "?" not in other.service and "?" in self.service:
            update_service = True
        # if the tag is longer e.g. http/tls instead of http, take it
        elif "?" not in other.service and len(other.service) > len(self.service):
            update_service = True

        if update_service:
            logging.debug(f"Updating service from {self.service} -> {other.service}")
            self.service = other.service
        # update the comments if comment is set
        if not self.comment and other.comment:
            logging.debug(f"Updating comment from {self.comment} -> {other.comment}")
            self.comment = other.comment

        if not self.state and other.state:
            logging.debug(f"Updating state from {self.state} -> {other.state}")
            self.state = other.state

    @staticmethod
    def is_valid_port(port: str) -> bool:
        try:
            port_num = int(port)
            return 1 <= port_num <= 65535
        except ValueError:
            return False

    SERVICE_MAPPING: Dict[str, str] = {
        "www": "http",
        "microsoft-ds": "smb",
        "cifs": "smb",
        "ms-wbt-server": "rdp",
        "ms-msql-s": "mssql",
    }

    @staticmethod
    def get_service_name(service: str, port: str):
        # some times nmap shows smb as netbios, but only overwrite this for port 445
        if port == "445" and "netbios" in service:
            return "smb"
        if service in PortDetails.SERVICE_MAPPING:
            return PortDetails.SERVICE_MAPPING[service]
        return service

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "PortDetails":
        return cls(data["port"], data["protocol"], data["state"], data["service"])


class ThreadSafeServiceLookup:
    def __init__(self):
        self._lock = threading.Lock()
        self._cache: Dict[str, str] = {}

    def get_service_name_for_port(
        self, port: str, protocol: str = "tcp", default_service: str = "unknown?"
    ):
        if PortDetails.is_valid_port(port):
            cache_id = port + protocol
            if cache_id in self._cache:
                return self._cache[cache_id]
            with self._lock:
                if cache_id in self._cache:
                    return self._cache[cache_id]
                try:
                    service = socket.getservbyport(int(port), protocol)
                    if service is None:
                        service = default_service
                except (socket.error, ValueError, TypeError):
                    logging.debug(f"Lookup for {port} and {protocol} failed!")
                    service = default_service
                service = PortDetails.get_service_name(service, port)
                self._cache[cache_id] = service
                return service
        else:
            raise ValueError(f'Port "{port}" is not valid!')


service_lookup = ThreadSafeServiceLookup()
hostup_dict = defaultdict(dict)
config = UnitasConfig()


class HostScanData:
    def __init__(self, ip: str):
        if not HostScanData.is_valid_ip(ip):
            raise ValueError(f"'{ip}' is not a valid ip!")
        self.ip = ip
        self.hostname: str = ""
        self.ports: List[PortDetails] = []

    @staticmethod
    def is_valid_ip(address: str) -> bool:
        try:
            ip_address(address)
            return True
        except ValueError:
            return False

    def add_port_details(self, new_port: PortDetails):
        if new_port is None:  # skip if new_port is None
            return

        for p in self.ports:
            if p.port == new_port.port and p.protocol == new_port.protocol:
                p.update(new_port)
                return
        # if the port did not exist, just add it
        self.ports.append(new_port)

    def add_port(
        self,
        port: str,
        protocol: str,
        state: str = "TBD",
        service: str = "unknown?",
        comment: str = "",
    ) -> None:
        new_port = PortDetails(port, protocol, state, service, comment)
        self.add_port_details(new_port)

    def set_hostname(self, hostname: str) -> None:
        self.hostname = hostname

    def get_sorted_ports(self) -> List[PortDetails]:
        return sorted(self.ports, key=lambda p: (p.protocol, int(p.port)))

    def __str__(self) -> str:
        ports_str = ", ".join(str(port) for port in self.ports)
        return f"{self.ip} ({self.hostname}): {ports_str}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ip": self.ip,
            "hostname": self.hostname,
            "ports": [port.to_dict() for port in self.ports],
        }

    def to_markdown_rows(self) -> List[str]:
        return [
            f"|{self.ip}|{str(x)}|       |       |" for x in self.get_sorted_ports()
        ]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HostScanData":
        host = cls(data["ip"])
        host.hostname = data["hostname"]
        for port_data in data["ports"]:
            host.ports.append(PortDetails.from_dict(port_data))
        return host


class Convert(ABC):
    def __init__(self, global_state: Dict[str, HostScanData] = None):
        self.global_state = Convert.sort_global_state_by_ip(global_state or {})

    @abstractmethod
    def convert(self) -> str:
        pass

    @abstractmethod
    def parse(self, content: str) -> Dict[str, HostScanData]:
        pass

    @staticmethod
    def sort_global_state_by_ip(
        global_state: Dict[str, HostScanData],
    ) -> Dict[str, HostScanData]:
        sorted_ips = sorted(global_state.keys(), key=ip_address)
        return {ip: global_state[ip] for ip in sorted_ips}


class GrepConverter(Convert):

    def convert_with_up(self, hostup_dict: dict) -> str:
        output = []
        for ip, reason in hostup_dict.items():
            output.append(f"{ip}|host-up({reason})")
        return "\n".join(output) + "\n" + self.convert()

    def convert(self):
        output = []
        for host in self.global_state.values():
            services = ""
            for port in host.get_sorted_ports():
                services += f"{port.port}/{port.protocol}({port.service}) "
            output.append(f"{host.ip}|{services}")
        return "\n".join(output) + "\n"

    def parse(self, content: str) -> Dict[str, HostScanData]:
        raise ValueError("not implemented")


class MarkdownConvert(Convert):
    def convert(self, formatted: bool = False) -> str:
        output = ["|IP|Hostname|Port|Status|Comment|"]
        output.append("|--|--|--|--|---|")

        max_ip_len = max_hostname_len = max_port_len = max_status_len = (
            max_comment_len
        ) = 0

        if formatted:
            # Find the maximum length of each column
            for host in self.global_state.values():
                max_ip_len = max(max_ip_len, len(host.ip))
                max_hostname_len = max(max_hostname_len, len(host.hostname))
                for port in host.get_sorted_ports():
                    port_info = f"{port.port}/{port.protocol}({port.service})"
                    max_port_len = max(max_port_len, len(port_info))
                    max_status_len = max(max_status_len, len(port.state))
                    max_comment_len = max(max_comment_len, len(port.comment))

        for host in self.global_state.values():
            for port in host.get_sorted_ports():
                service = f"{port.port}/{port.protocol}({port.service})"
                output.append(
                    f"|{host.ip.ljust(max_ip_len)}|{host.hostname.ljust(max_hostname_len)}|{service.ljust(max_port_len)}|{port.state.ljust(max_status_len)}|{port.comment.ljust(max_comment_len)}|"
                )
        return "\n".join(output) + "\n"

    def parse(self, content: str) -> Dict[str, HostScanData]:
        lines = content.strip().split("\n")
        if len(lines) < 2:
            logging.error(
                f"Could not load markdown, markdown was only {len(lines)} lines. are you missing the two line header?"
            )
            return {}
        lines = lines[2:]  # Skip header and separator
        result = {}
        counter = 1
        for line in lines:
            counter += 1
            match = re.match(
                r"\s*\|([^|]+)\|\s*([^|]*)\s*\|\s*([^|/]+)/([^|(]+)\(([^)]+)\)\s*\|\s*([^|]*)\s*\|\s*([^|]*)\s*\|",
                line.strip(),
            )
            if match:
                ip, hostname, port, protocol, service, status, comment = match.groups()
                ip = ip.strip()
                if ip not in result:
                    result[ip] = HostScanData(ip)
                    if hostname.strip():
                        result[ip].set_hostname(hostname.strip())
                result[ip].add_port(
                    port.strip(),
                    protocol.strip(),
                    status.strip() or "TBD",
                    service.strip(),
                    comment.strip(),
                )
            else:
                logging.error(
                    f"Markdown error: Failed to parse line nr {counter}: {line}"
                )

        return result


class ScanParser(ABC):
    def __init__(self, file_path: str):
        self.file_path: str = file_path
        self.tree: ET.ElementTree = ET.parse(file_path)
        self.root: ET.Element = self.tree.getroot()
        self.data: Dict[str, HostScanData] = {}

    @abstractmethod
    def parse(self) -> Dict[str, HostScanData]:
        pass

    @staticmethod
    @abstractmethod
    def get_extensions() -> List[str]:
        pass

    @classmethod
    def load_file(cls, directory: str) -> List["ScanParser"]:
        files = []
        for ext in cls.get_extensions():
            logging.debug(
                f'Looking in folder "{directory}" for "{ext}" files for parser {cls.__name__}'
            )
            for f in glob.glob(f"{directory}/**/*.{ext}", recursive=True):
                logging.debug(f"Adding file {f} for parser {cls.__name__}")
                try:
                    files.append(cls(f))
                except ParseError:
                    logging.error(f"Could not load XML from file {f}")
        return files


class NessusParser(ScanParser):

    @staticmethod
    def get_extensions() -> List[str]:
        return ["nessus"]

    def parse(self) -> Dict[str, HostScanData]:
        for block in self.root.findall(".//ReportHost"):
            name: str = block.attrib.get("name", "")
            hostname: Optional[str] = None

            if HostScanData.is_valid_ip(name):
                ip = name
                host_blk = block.find(".//tag[@name='host-fqdn']")
                if host_blk is not None and host_blk.text:
                    hostname = host_blk.text
            else:
                ip_blk = block.find(".//tag[@name='host-ip']")
                hostname = name
                if ip_blk is not None and ip_blk.text:
                    ip = ip_blk.text
                else:
                    raise ValueError(f"Could not find IP for host {hostname}")

            host = HostScanData(ip)
            if hostname:
                host.set_hostname(hostname)
            plugin_found = (
                self._parse_service_detection(block, host) > 0
                or self._parse_port_scanners(block, host) > 0
            )
            # the idea here is if the host has some version or port scan, it must be up
            # sofar i have not seen a nessus file w
            if plugin_found and len(host.ports) == 0:
                if not ip in hostup_dict:
                    hostup_dict[ip] = "nessus plugin seen"

            if len(host.ports) == 0:
                continue

            self.data[ip] = host
        return self.data

    def _parse_service_item(self, item: ET.Element) -> PortDetails:
        if not all(
            attr in item.attrib
            for attr in ["port", "protocol", "svc_name", "pluginName"]
        ):
            logging.error(f"Failed to parse nessus service scan: {ET.tostring(item)}")
            return None
        port: str = item.attrib.get("port")
        if port == "0":  # host scans return port zero, skip
            return None
        protocol: str = item.attrib.get("protocol")
        service: str = item.attrib.get("svc_name")
        service = PortDetails.get_service_name(service, port)
        comment: str = ""
        if "TLS" in item.attrib.get("pluginName") or "SSL" in item.attrib.get(
            "pluginName", ""
        ):
            if service == "http":
                service = "https"
            comment = "TLS"
        state: str = "TBD"
        return PortDetails(
            port=port, service=service, comment=comment, state=state, protocol=protocol
        )

    def _parse_service_detection(self, block: ET.Element, host: HostScanData) -> int:
        counter = 0
        # xml module has only limited xpath support
        for item in [
            b
            for b in block.findall(".//ReportItem")
            if b.attrib.get("pluginFamily", "Port Scanner")
            not in ["Port Scanner", "Settings"]
        ]:
            counter += 1
            host.add_port_details(self._parse_service_item(item))
        return counter

    def _parse_port_item(self, item: ET.Element) -> PortDetails:
        if not all(attr in item.attrib for attr in ["port", "protocol", "svc_name"]):
            logging.error(f"Failed to parse nessus port scan: {ET.tostring(item)}")
            return None
        port: str = item.attrib.get("port")
        if port == "0":  # host scans return port zero, skip
            return None
        protocol: str = item.attrib.get("protocol")
        service: str = item.attrib.get("svc_name")
        if "?" not in service:  # append a ? for just port scans
            service = service_lookup.get_service_name_for_port(port, protocol, service)
            service += "?"
        else:
            service = PortDetails.get_service_name(service, port)
        state: str = "TBD"
        return PortDetails(port=port, service=service, state=state, protocol=protocol)

    def _parse_port_scanners(self, block: ET.Element, host: HostScanData) -> int:
        counter = 0
        for item in block.findall(".//ReportItem[@pluginFamily='Port scanners']"):
            counter += 1
            host.add_port_details(self._parse_port_item(item))
        return counter


class NmapParser(ScanParser):

    @staticmethod
    def get_extensions() -> List[str]:
        return ["xml"]

    def parse(self) -> Dict[str, HostScanData]:
        for host in self.root.findall(".//host"):
            status = host.find(".//status")
            if status is not None and status.attrib.get("state") == "up":
                address = host.find(".//address")
                if address is not None:  # explicit None check is needed
                    host_ip: str = address.attrib.get("addr", "")
                    h = HostScanData(ip=host_ip)

                    self._parse_ports(host, h)
                    if len(h.ports) == 0:  # do not parse host that have no IP
                        if not host_ip in hostup_dict:
                            reason = status.attrib.get("reason", "")
                            if reason and not reason == "user-set":
                                hostup_dict[host_ip] = reason
                        continue

                    self.data[host_ip] = h

                    hostnames = host.find(".//hostnames")
                    if hostnames is not None:
                        for x in hostnames:
                            if "name" in x.attrib:
                                h.set_hostname(x.attrib.get("name"))
                                # prefer the user given hostname instead of the PTR
                                if x.attrib.get("type", "") == "user":
                                    break
        return self.data

    def _parse_port_item(self, port: ET.Element) -> PortDetails:
        if not all(attr in port.attrib for attr in ["portid", "protocol"]):
            logging.error(f"Failed to parse nmap scan: {ET.tostring(port)}")
            return None
        protocol: str = port.attrib.get("protocol")
        portid: str = port.attrib.get("portid")
        service_element = port.find(".//service")
        comment: str = ""
        tls_found: bool = False

        if service_element is not None:
            service: str = service_element.attrib.get("name")
            # need or service will not be overwritten by other services
            if service == "tcpwrapped":
                service = "unknown?"
            elif service_element.attrib.get("method") == "table":
                service = service_lookup.get_service_name_for_port(
                    portid, protocol, service
                )
                service += "?"
            else:
                service = PortDetails.get_service_name(service, portid)
                product = service_element.attrib.get("product", "")
                if product:
                    comment += product
                version = service_element.attrib.get("version", "")
                if version:
                    comment += " " + version

            if service_element.attrib.get("tunnel", "none") == "ssl":
                # nmap is not is not consistent with http/tls and https
                tls_found = True
        else:
            service = service_lookup.get_service_name_for_port(
                portid, protocol, "unknown"
            )
            service += "?"

        if not tls_found:
            for script in port.findall(".//script"):
                # some services have TLS but nmap does not mark it via the tunnel e.g. FTP
                if script.attrib.get("id", "") == "ssl-cert":
                    tls_found = True
                    break

        if tls_found:
            if service == "http":
                service = "https"
            if comment:
                comment += ";"

            comment += "TLS"

        return PortDetails(
            port=portid,
            protocol=protocol,
            state="TBD",
            comment=comment,
            service=service,
        )

    def _parse_ports(self, host: ET.Element, h: HostScanData) -> None:
        for port in host.findall(".//port[state]"):
            # for some reason, doing a single xpath query fails with invalid attribute#
            # only allow open ports
            if port.find("state[@state='open']") is not None:
                h.add_port_details(self._parse_port_item(port))


class NessusExporter:

    report_name = "Merged Report"

    def __init__(self):
        access_key, secret_key, url = (
            config.get_access_key(),
            config.get_secret_key(),
            config.get_url(),
        )
        if not access_key or not secret_key:
            raise ValueError("Secret or access key was empty!")
        self.access_key = access_key
        self.secret_key = secret_key
        self.url = url

        self.ses = requests.Session()
        self.ses.headers.update(
            {"X-ApiKeys": f"accessKey={self.access_key}; secretKey={self.secret_key}"}
        )
        self.ses.verify = False  # yeah i know :D

        def error_handler(r, *args, **kwargs):
            if not r.ok:
                logging.error(f"Problem with nessus API: {r.text}")
            r.raise_for_status()

        self.ses.hooks = {"response": error_handler}
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _initiate_export(self, scan_id):
        logging.info(f"Initiating export for scan ID: {scan_id}")
        return self.ses.post(
            f"{self.url}/scans/{scan_id}/export",
            json={"format": "nessus", "chapters": ""},
        ).json()["file"]

    def _check_export_status(self, scan_id, file_id):
        logging.debug(
            f"Checking export status for scan ID: {scan_id}, file ID: {file_id}"
        )
        while True:
            status = self.ses.get(
                f"{self.url}/scans/{scan_id}/export/{file_id}/status"
            ).json()["status"]
            if status == "ready":
                logging.debug(f"Export is ready for download for scan ID: {scan_id}")
                break
            logging.debug("Export is not ready yet, waiting 5 seconds...")
            time.sleep(5)

    def _list_scans(self) -> List[Dict]:
        logging.debug("Listing nessus scans")
        scans = self.ses.get(f"{self.url}/scans").json()["scans"]
        if not scans:
            return []
        export_scans = []
        for x in scans:
            if x["status"] in ["cancled", "running"]:
                logging.warning(
                    f"Skipping scan \"{x['name']}\" because status is {x['status']}"
                )
            else:
                export_scans.append(x)
        return export_scans

    def _sanitize_name(self, scan: dict) -> str:
        return scan["name"].replace(" ", "_").replace("/", "_").replace("\\", "_")

    def _generate_file_name(self, target_dir: str, scan: dict) -> str:
        scan_id = scan["id"]
        scan_name = self._sanitize_name(scan)
        filename = os.path.join(target_dir, f"{scan_name}_{scan_id}.nessus")
        return filename

    def _download_export(self, scan: dict, file_id: str, target_dir: str):
        scan_id = scan["id"]
        filename = self._generate_file_name(target_dir, scan)
        if os.path.exists(filename):
            logging.error(f"Export file {filename} already exists. Skipping download.")
            return
        logging.info(f"Downloading export for scan ID: {scan_id} to {filename}")
        response = self.ses.get(
            f"{self.url}/scans/{scan_id}/export/{file_id}/download", stream=True
        )
        response.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logging.info(f"Download completed successfully for {filename}")

    def export(self, target_dir: str):
        scans = self._list_scans()

        if not scans:
            logging.error("No scans found!")
            return

        for scan in scans:
            scan_id = scan["id"]
            scan_name = scan["name"]
            if scan_name.lower() == "merged":
                logging.info("Skipping export for scan named 'merged'")
                continue

            nessus_filename = self._generate_file_name(target_dir, scan)
            if not os.path.exists(nessus_filename):
                nessus_file_id = self._initiate_export(scan_id)
                self._check_export_status(scan_id, nessus_file_id)
                self._download_export(scan, nessus_file_id, target_dir)
            else:
                logging.info(
                    f"Skipping export for {nessus_filename} as it already exists."
                )


class JsonExport(Convert):
    """
    Export scan results as a structured JSON file that can be loaded
    by the standalone HTML viewer or used for other data analysis.
    """

    def __init__(
        self,
        global_state: Dict[str, HostScanData] = None,
        hostup_dict: Dict[str, str] = None,
    ):
        super().__init__(global_state)
        self.hostup_dict = hostup_dict or {}

    def convert(self) -> str:
        """Convert the scan data to a JSON string."""
        # Prepare hosts data
        hosts_data = []
        for ip, host in self.global_state.items():
            host_entry = {
                "ip": ip,
                "hostname": host.hostname,
                "ports": [],
                "hasOpenPorts": len(host.ports) > 0,
            }
            for port in host.ports:
                host_entry["ports"].append(
                    {
                        "port": port.port,
                        "protocol": port.protocol,
                        "service": port.service,
                        "state": port.state,
                        "comment": port.comment,
                        "uncertain": "?" in port.service,
                        "tls": "TLS" in port.comment,
                    }
                )
            hosts_data.append(host_entry)

        # Prepare hosts-up data
        hostup_data = []
        for ip, reason in self.hostup_dict.items():
            hostup_data.append({"ip": ip, "reason": reason})

        # Build complete data structure
        data = {
            "metadata": {
                "version": __version__,
                "timestamp": time.time(),
                "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
                "stats": {
                    "totalHosts": len(hosts_data),
                    "totalPorts": sum(len(host["ports"]) for host in hosts_data),
                    "hostsUp": len(hostup_data),
                },
            },
            "hosts": hosts_data,
            "hostsUp": hostup_data,
        }

        # Return pretty-printed JSON
        return json.dumps(data, indent=2)

    def parse(self, content: str) -> Dict[str, HostScanData]:
        """
        Parse a JSON string back into a Unitas state structure.
        This allows importing previously exported JSON data.
        """
        try:
            data = json.loads(content)
            result = {}

            # Parse hosts
            for host_entry in data.get("hosts", []):
                ip = host_entry.get("ip")
                if not ip or not HostScanData.is_valid_ip(ip):
                    logging.warning(f"Invalid IP in JSON data: {ip}")
                    continue

                host = HostScanData(ip)
                host.set_hostname(host_entry.get("hostname", ""))

                for port_entry in host_entry.get("ports", []):
                    try:
                        host.add_port(
                            port_entry.get("port", ""),
                            port_entry.get("protocol", "tcp"),
                            port_entry.get("state", "TBD"),
                            port_entry.get("service", "unknown?"),
                            port_entry.get("comment", ""),
                        )
                    except ValueError as e:
                        logging.warning(f"Error adding port: {e}")

                result[ip] = host

            return result

        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON data: {e}")
            return {}
        except Exception as e:
            logging.error(f"Error importing JSON data: {e}")
            return {}


class ScanMerger(ABC):
    def __init__(self, directory: str, output_directory: str):
        self.directory = directory
        self.output_directory = output_directory
        self.output_file: str = None
        self.filter: str = None

    def search(self, wildcard: str) -> List[str]:
        files = []
        for file in glob.glob(
            os.path.join(self.directory, "**", wildcard), recursive=True
        ):
            # Skip if it's a directory
            if os.path.isdir(file):
                continue

            # Skip output directory files
            if os.path.abspath(self.output_directory) in os.path.abspath(file):
                logging.warning(
                    f"Skipping file {file} to prevent merging a merged scan!"
                )
            else:
                files.append(file)

        return files

    def parse(self):
        pass


class NmapHost:

    def __init__(self, ip: str, host: Element):
        self.ip = ip
        self.host: Element = host
        self.hostnames: List[Element] = []
        self.ports: Dict[str, ET.Element] = {}
        self.hostscripts: Dict[str, ET.Element] = {}
        self.os_e: Element = None
        self.reason: str = None

    def elements_equal(self, e1: Element, e2: Element):
        if e1.tag != e2.tag:
            return False
        if e1.text != e2.text:
            return False
        if e1.tail != e2.tail:
            return False
        if e1.attrib != e2.attrib:
            return False
        if len(e1) != len(e2):
            return False
        return all(self.elements_equal(c1, c2) for c1, c2 in zip(e1, e2))

    def find_port(self, protocol: str, portid: str) -> Element:
        for p in self.ports:
            if p.get("protocol") == protocol and p.get("portid") == portid:
                return p
        return None

    def add_port(self, port: ET.Element):
        key = self._get_port_key(port)

        if key in self.ports:
            self._merge_port_info(self.ports[key], port)
        else:
            self.ports[key] = deepcopy(port)

    def _get_port_key(self, port: ET.Element) -> str:
        key = f"{port.get('protocol')}_{port.get('portid')}"
        state = port.find("state")
        if state is not None:
            key += f"_{state.get('state')}"
        return key

    def _merge_port_info(self, existing_port: ET.Element, new_port: ET.Element):
        # Merge service information
        existing_service = existing_port.find("service")
        new_service = new_port.find("service")
        if existing_service is not None and new_service is not None:
            self._merge_service_info(existing_service, new_service)
        elif new_service is not None:
            existing_port.append(deepcopy(new_service))

        # Merge script results
        existing_scripts = {
            script.get("id"): script for script in existing_port.findall("script")
        }
        for new_script in new_port.findall("script"):
            script_id = new_script.get("id")
            if script_id not in existing_scripts:
                existing_port.append(deepcopy(new_script))

    def _merge_service_info(
        self, existing_service: ET.Element, new_service: ET.Element
    ):
        for attr, value in new_service.attrib.items():
            if attr not in existing_service.attrib or existing_service.get(attr) == "":
                existing_service.set(attr, value)

    def add_hostname(self, hostname: Element):
        if not any(self.elements_equal(e, hostname) for e in self.hostnames):
            self.hostnames.append(hostname)

    def _merge_script_info(self, existing_script: ET.Element, new_script: ET.Element):
        # Update output if it's different
        if existing_script.get("output") != new_script.get("output"):
            existing_script.set("output", new_script.get("output"))

        # Merge or update table elements
        existing_tables = {
            table.get("key"): table for table in existing_script.findall("table")
        }
        for new_table in new_script.findall("table"):
            table_key = new_table.get("key")
            if table_key not in existing_tables:
                existing_script.append(deepcopy(new_table))
            else:
                self._merge_table_info(existing_tables[table_key], new_table)

    def _merge_table_info(self, existing_table: ET.Element, new_table: ET.Element):
        existing_elems = {
            elem.get("key"): elem for elem in existing_table.findall("elem")
        }
        for new_elem in new_table.findall("elem"):
            elem_key = new_elem.get("key")
            if elem_key not in existing_elems:
                existing_table.append(deepcopy(new_elem))
            elif existing_elems[elem_key].text != new_elem.text:
                existing_elems[elem_key].text = new_elem.text

    def add_hostscript(self, hostscript: ET.Element):
        script_id = hostscript.get("id")
        if script_id not in self.hostscripts:
            self.hostscripts[script_id] = deepcopy(hostscript)
        else:
            self._merge_script_info(self.hostscripts[script_id], hostscript)


class NmapMerger(ScanMerger):

    def __init__(self, directory: str, output_directory: str):
        super().__init__(directory, output_directory)
        self.output_file: str = "merged_nmap.xml"
        self.filter: str = "*.xml"
        self.template: str = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE nmaprun>
<?xml-stylesheet href="file:///usr/bin/../share/nmap/nmap.xsl" type="text/xsl"?>
<!-- Merge scan generated -->
<nmaprun scanner="nmap" args="non merged" start="1695570860" startstr="Sun Sep 24 17:54:20 2023" version="7.94" xmloutputversion="1.05">
<scaninfo type="syn" protocol="tcp" numservices="1000" services="1-1000"/>
<verbose level="0"/>
<debugging level="0"/>
{{host}}
<runstats>
<finished time="1315618434" timestr="Fri Sep  9 18:33:54 2011" elapsed="13.66" summary="Nmap done at Fri Sep  9 18:33:54 2011; 1 IP address (1 host up) scanned in 13.66 seconds" exit="success"/>
<hosts up="1" down="0" total="1"/>
</runstats>
</nmaprun>
        """

    def parse(self):
        hosts: Dict[str, NmapHost] = {}
        for file_path in self.search(self.filter):
            logging.info(f"Trying to parse {file_path}")
            try:
                root = ET.parse(file_path)
                for host in root.findall(".//host"):
                    status = host.find(".//status")
                    if status is not None and status.attrib.get("state") == "up":
                        address = host.find(".//address")
                        if address is not None:  # explicit None check is needed
                            host_ip: str = address.attrib.get("addr", "")
                            if not host_ip in hosts:
                                nhost = NmapHost(host_ip, host)
                                hosts[host_ip] = nhost
                            else:
                                nhost = hosts[host_ip]

                            nhost.reason = status.attrib.get("reason", "user-set")
                            ports = host.find("ports")
                            if ports is not None:
                                for x in ports.findall("extraports"):
                                    ports.remove(x)

                                for port in ports.findall("port[state]"):
                                    state = port.find("state")
                                    if (
                                        port.attrib.get("protocol", "udp") == "udp"
                                        and state.attrib.get("state", "open|filtered")
                                        == "open|filtered"
                                        and state.attrib.get("reason", "no-response")
                                        == "no-response"
                                    ):
                                        pass
                                    else:
                                        nhost.add_port(port)
                                    ports.remove(port)

                            hostnames = host.find("hostnames")
                            if hostnames is not None:
                                for x in hostnames:
                                    hostnames.remove(x)
                                    nhost.add_hostname(x)

                            for x in host.findall(".//hostscript"):
                                host.remove(x)
                                nhost.add_hostscript(x)

                            os_e = host.find(".//os")
                            if os_e is not None:
                                host.remove(os_e)
                                nhost.os_e = os_e
            except IsADirectoryError:
                logging.error("Seems like we tried to open a dir")
                continue
            except ParseError:
                logging.error("Failed to parse nmap xml")
                continue
        if hosts:
            self._render_template(hosts)
        else:
            logging.error("No hosts found, could not generate merged nmap scan!")

    def _render_template(self, hosts: Dict[str, NmapHost]) -> str:
        payload: str = ""
        for ip, nhost in hosts.items():
            host = nhost.host
            ports = host.find("ports")

            # odd case where the host is up, but not port was found
            if nhost.reason == "user-set" and len(nhost.ports) == 0:
                continue

            # if the first scan had no ports, we need to add the element again
            if ports is None:

                ports = ET.fromstring("<ports></ports>")
                host.append(ports)

            for _, p in nhost.ports.items():
                ports.append(p)
            # clear all child elements
            # add all of them
            hostnames = host.find("hostnames")
            for p in nhost.hostnames:
                hostnames.append(p)

            hostscripts = host.find("hostscripts")
            if not hostscripts:
                hostscripts = ET.fromstring("<hostscripts></hostscripts>")
                host.append(hostscripts)
            for _, p in nhost.hostscripts.items():
                hostscripts.append(p)

            payload += ET.tostring(host).decode()
        data = self.template.replace("{{host}}", payload)

        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

        output_file = os.path.join(self.output_directory, self.output_file)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(data)

        logging.info(f"Saving merged scan to {output_file}")
        if shutil.which("xsltproc") is None:
            logging.error(
                "xsltproc is not installed and nmap html report will not generated!"
            )
        else:
            os.system(f"xsltproc {output_file} -o {output_file}.html")

        return output_file

    def save_report(self) -> str:
        pass
        # TBD add code to convert HTML


class NessusMerger(ScanMerger):

    def __init__(self, directory: str, output_directory: str, report_title: str = None):
        super().__init__(directory, output_directory)
        self.tree: ET.ElementTree = None
        self.root: ET.Element = None
        self.output_file: str = "merged_report.nessus"
        self.filter: str = "*.nessus"
        self.report_title: str = report_title or NessusExporter.report_name

    def parse(self):
        first_file_parsed = True
        for file_path in self.search(self.filter):
            logging.info(f"Parsing - {file_path}")
            try:
                if first_file_parsed:
                    self.tree = ET.parse(file_path)
                    self.report = self.tree.find("Report")
                    self.report.attrib["name"] = self.report_title
                    first_file_parsed = False
                else:
                    tree = ET.parse(file_path)
                    self._merge_hosts(tree)
            except IsADirectoryError:
                logging.error("Seems like we tried to open a dir")
            except ParseError:
                logging.error("Failed to parse")

    def _merge_hosts(self, tree):
        for host in tree.findall(".//ReportHost"):
            existing_host = self.report.find(
                f".//ReportHost[@name='{host.attrib['name']}']"
            )
            if not existing_host:
                logging.debug(f"Adding host: {host.attrib['name']}")
                self.report.append(host)
            else:
                self._merge_report_items(host, existing_host)

    def _merge_report_items(self, host, existing_host):
        for item in host.findall("ReportItem"):
            if not existing_host.find(
                f"ReportItem[@port='{item.attrib['port']}'][@pluginID='{item.attrib['pluginID']}']"
            ):
                logging.debug(
                    f"Adding finding: {item.attrib['port']}:{item.attrib['pluginID']}"
                )
                existing_host.append(item)

    def save_report(self) -> str:
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
        output_file = os.path.join(self.output_directory, self.output_file)
        if self.tree is None:
            logging.error("Generated Nessus was empty")
            return
        self.tree.write(output_file, encoding="utf-8", xml_declaration=True)
        logging.info(f"Saving merged scan to {output_file}")
        return output_file


class CustomFormatter(logging.Formatter):
    """
    Custom logging formatter to add tags for different log levels.
    """

    def format(self, record):
        level_tags = {
            logging.DEBUG: "[d]",
            logging.INFO: "[+]",
            logging.WARNING: "[!]",
            logging.ERROR: "[e]",
            logging.CRITICAL: "[c]",
        }
        record.leveltag = level_tags.get(record.levelno, "[?]")
        return super().format(record)


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO

    formatter = CustomFormatter("%(leveltag)s %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(handler)


def load_markdown_state(filename: str) -> Dict[str, HostScanData]:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        # Strip empty lines
        content = "\n".join(line for line in content.split("\n") if line.strip())
        converter = MarkdownConvert()
        return converter.parse(content)
    except FileNotFoundError:
        logging.warning(f"File {filename} not found. Starting with empty state.")
        return {}
    except Exception as e:
        logging.error(f"Error loading {filename}: {str(e)}")
        return {}


def merge_states(
    old_state: Dict[str, HostScanData], new_state: Dict[str, HostScanData]
) -> Dict[str, HostScanData]:
    merged_state = old_state.copy()
    for ip, new_host_data in new_state.items():
        if ip not in merged_state:
            logging.debug(f"Added host {ip}")
            merged_state[ip] = new_host_data
        else:
            existing_ports = {(p.port, p.protocol): p for p in merged_state[ip].ports}
            for new_port in new_host_data.ports:
                key = (new_port.port, new_port.protocol)
                if key in existing_ports:
                    if not existing_ports[key] == new_port:
                        existing_ports[key].update(new_port)
                else:
                    logging.debug(f"Added port {new_port}")
                    existing_ports[key] = new_port

            merged_state[ip].ports = list(existing_ports.values())
    return merged_state


def search_port_or_service(
    global_state: Dict[str, HostScanData],
    search_terms: List[str],
    with_url: bool,
    hide_ports: bool,
) -> List[str]:
    matching_ips = set()
    for ip, host_data in global_state.items():
        for port in host_data.ports:
            for term in search_terms:
                if term.lower().strip() == port.port.lower() or (
                    term.lower().strip() == port.service.lower()
                    or term.lower().strip() + "?" == port.service.lower()
                ):
                    port_nr = port.port
                    service = port.service.replace("?", "")
                    url: str = ip
                    if with_url:
                        url = service + "://" + url

                    if port == 139:
                        pass

                    # show ports if the port is not the default port for the service
                    # if multiple terms are used, do not do this e.g. http and https, which leads to the same host without any context which is which
                    if hide_ports:
                        pass  # no need to do anything

                    elif (
                        not service_lookup.get_service_name_for_port(port_nr) == service
                        or len(search_terms) > 1
                    ):
                        url += ":" + port_nr

                    matching_ips.add(url)

    return sorted(list(matching_ips))


def parse_file(parser: ScanParser) -> Tuple[str, Dict[str, HostScanData]]:
    try:
        return parser.file_path, parser.parse()
    except ParseError:
        logging.error(f"Could not load {parser.file_path}, invalid XML")
        return parser.file_path, {}


def parse_files_concurrently(
    parsers: List[ScanParser], max_workers: int = 1
) -> Dict[str, HostScanData]:
    global_state: Dict[str, HostScanData] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_parser = {
            executor.submit(parse_file, parser): parser for parser in parsers
        }
        for future in concurrent.futures.as_completed(future_to_parser):
            parser = future_to_parser[future]
            try:
                _, scan_results = future.result()
                global_state = merge_states(global_state, scan_results)

            except Exception as exc:
                logging.error(f"{parser.file_path} generated an exception: {exc}")
    return global_state


def generate_nmap_scan_command(global_state: Dict[str, HostScanData]) -> str:
    scan_types: Set[str] = set()
    tcp_ports: Set[str] = set()
    udp_ports: Set[str] = set()
    targets: Set[str] = set()
    for ip, host_data in global_state.items():
        for port in host_data.ports:
            if "?" in port.service:
                if port.protocol == "tcp":
                    tcp_ports.add(port.port)
                    scan_types.add("S")
                elif port.protocol == "udp":
                    udp_ports.add(port.port)
                    scan_types.add("U")
                targets.add(ip)

    if not tcp_ports and not udp_ports:
        return "no ports found for re-scanning"
    ports = "-p"
    if tcp_ports:
        ports += "T:" + ",".join(tcp_ports)
    if udp_ports:
        if tcp_ports:
            ports += ","
        ports += "U:" + ",".join(udp_ports)
    targets_str = " ".join(targets)
    # -Pn: we know that the host is up and skip pre scan
    return f"sudo nmap -n -r --reason -Pn -s{''.join(scan_types)} -sV -v {ports} {targets_str} -oA service_scan_{sha512(targets_str.encode()).hexdigest()[:5]}"


def filter_uncertain_services(
    global_state: Dict[str, HostScanData],
) -> Dict[str, HostScanData]:
    certain_services = {}
    for ip, host_data in global_state.items():
        service_ports = [port for port in host_data.ports if not "?" in port.service]
        if service_ports:
            new_host_data = HostScanData(ip)
            new_host_data.hostname = host_data.hostname
            new_host_data.ports = service_ports
            certain_services[ip] = new_host_data
    return certain_services


BANNER = """              __________               
____  ___________(_)_  /______ ________
_  / / /_  __ \_  /_  __/  __ `/_  ___/
/ /_/ /_  / / /  / / /_ / /_/ /_(__  ) 
\__,_/ /_/ /_//_/  \__/ \__,_/ /____/  
                                       """


def main() -> None:
    parser = argparse.ArgumentParser(
        description=f"Unitas v{__version__}: A network scan parser and analyzer",
        epilog="Example usage: python unitas.py /path/to/scan/folder -v --search 'smb'",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("scan_folder", help="Folder containing scan files")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose output (sets log level to DEBUG)",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the version number and exit",
    )
    parser.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="Update existing markdown from state.md or stdin",
    )
    parser.add_argument(
        "-s",
        "--search",
        help="Search for specific port numbers or service names (comma-separated)",
    )
    parser.add_argument(
        "-U",
        "--url",
        action="store_true",
        default=False,
        help="Adds the protocol of the port as URL prefix",
    )
    parser.add_argument(
        "-S",
        "--service",
        action="store_true",
        default=False,
        help="Show only service scanned ports",
    )

    parser.add_argument(
        "-p",
        "--hide-ports",
        action="store_true",
        default=False,
        help="Hide ports from search",
    )

    parser.add_argument(
        "-r",
        "--rescan",
        action="store_true",
        default=False,
        help="Print a nmap command to re-scan the ports not service scanned",
    )

    parser.add_argument(
        "-e",
        "--export",
        action="store_true",
        default=False,
        help="Export all scans from nessus",
    )

    parser.add_argument(
        "-m",
        "--merge",
        action="store_true",
        default=False,
        help="Merge scans in the folder",
    )

    parser.add_argument(
        "-g",
        "--grep",
        action="store_true",
        default=False,
        help="Output the scan results in grepable format (including hosts that are up, but have no port open e.g. via ICMP)",
    )

    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        default=False,
        help="Export scan results as a JSON file that can be loaded by the HTML viewer",
    )

    parser.add_argument(
        "-T",
        "--report-title",
        help="Specify a custom title for the merged Nessus report",
        default=None,
    )
    parser.add_argument(
        "-H",
        "--http-server",
        action="store_true",
        default=False,
        help="Start an HTTP server to visualize scan results in a web browser",
    )
    parser.add_argument(
        "-P",
        "--port",
        type=int,
        default=8000,
        help="Port to use for HTTP server (default: 8000)",
    )

    args = parser.parse_args()

    if args.update:
        existing_state = load_markdown_state("state.md")
    else:
        existing_state = {}

    setup_logging(args.verbose)

    logging.info(f"Unitas v{__version__} starting up.")
    logging.info(BANNER)

    if not os.path.exists(args.scan_folder):
        folder = os.path.abspath(args.scan_folder)
        logging.error(f"Source folder {folder} was not found!")
        return

    if args.export:
        if not REQUESTS_INSTALLED:
            logging.error(
                "requests was not installed, please install it via pip to use the exporter!"
            )
            return
        logging.info(f"Starting nessus export to {os.path.abspath(args.scan_folder)}")
        NessusExporter().export(args.scan_folder)
        return

    if args.merge:
        logging.info("Starting to merge scans!")

        merger = NmapMerger(args.scan_folder, os.path.join(args.scan_folder, "merged"))
        merger.parse()

        merger = NessusMerger(
            args.scan_folder,
            os.path.join(args.scan_folder, "merged"),
            args.report_title,
        )
        merger.parse()
        merger.save_report()
        # upload does not work on Nessus pro. because tenable disabled API support.
        return

    parsers = NessusParser.load_file(args.scan_folder) + NmapParser.load_file(
        args.scan_folder
    )
    if not parsers:
        logging.error("Could not load any kind of scan files")
        return

    global_state = parse_files_concurrently(parsers)

    for p in parsers:
        try:
            scan_results = p.parse()
            new_hosts = merge_states(global_state, scan_results)
            if new_hosts:
                logging.debug(
                    "New hosts added: %s", ", ".join(str(host) for host in new_hosts)
                )
        except ParseError:
            logging.error("Could not load %s, invalid XML", p.file_path)
        except ValueError as e:
            logging.error(f"Failed to parse {p.file_path}: {e}")

    final_state = merge_states(existing_state, global_state)

    if hostup_dict:
        # check if the host is up in the final state
        for ip in final_state.keys():
            if ip in hostup_dict:
                del hostup_dict[ip]

        logging.info(
            f"Found {len(hostup_dict)} hosts that are up, but have no open ports"
        )
        up_file: str = "/tmp/up.txt"
        with open(up_file, "w", encoding="utf-8") as f:
            for ip, reason in hostup_dict.items():
                logging.info(f"UP:{ip}:{reason}")
                f.write(f"{ip}\n")
            logging.info(f"Wrote list of host without open ports to {up_file}")

    if not final_state:
        logging.error("Did not find any open ports!")
        return

    if args.rescan:
        logging.info("nmap command to re-scan all non service scanned ports")
        logging.info(generate_nmap_scan_command(final_state))
        return

    if args.grep:
        grep_conv = GrepConverter(final_state)
        logging.info("Scan Results (grep):")
        print()
        print(grep_conv.convert_with_up(hostup_dict))
        return

    if args.http_server:
        logging.info("Starting HTTP server to visualize scan results")

        # Generate JSON data
        json_exporter = JsonExport(final_state, hostup_dict)
        json_content = json_exporter.convert()

        # Start the HTTP server
        start_http_server(json_content, args.port)
        return

    if args.json:
        json_exporter = JsonExport(final_state, hostup_dict)
        json_content = json_exporter.convert()
        output_file = f"unitas.json"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(json_content)
        logging.info(f"Exported JSON data to {os.path.abspath(output_file)}")
        return

    if args.service:
        logging.info("Filtering non-service scanned ports")
        final_state = filter_uncertain_services(final_state)

    if args.search:
        hide_ports = args.hide_ports
        search_terms = [term.strip().lower() for term in args.search.split(",")]
        matching_ips = search_port_or_service(
            final_state, search_terms, args.url, hide_ports
        )
        if matching_ips:
            logging.info(
                f"Systems with ports/services matching '{', '.join(search_terms)}':"
            )
            for ip in matching_ips:
                print(ip)
        else:
            logging.info(f"No systems found with port/service '{args.search}'")
    else:
        md_converter = MarkdownConvert(final_state)
        md_content = md_converter.convert(True)

        logging.info("Updated state saved to state.md")
        with open("state.md", "w", encoding="utf-8") as f:
            f.write(md_content)

        logging.info("Scan Results (Markdown):")
        print()
        print(md_content)


if __name__ == "__main__":
    main()
