import socket
import threading
from ipaddress import IPv4Address, IPv4Network
import datetime
import time

import pandas as pd

# set display options
pd.options.display.max_columns = 40
pd.options.display.width = 120
pd.set_option("max_colwidth", 400)


# General information
def local_ip() -> IPv4Address:
    """Return local IPv4Address for the primary interface by way of attempting a socket connection.
    Unsuccessful socket attempt will return 127.0.0.1.

    :return: IP address for the primary interface
    :rtype: IPv4Address

    Note:
        This function attempts to forge a connection via the primary interface, in the event that multiple valid
        interfaces are online, the result may be undesirable.  Either disable other interfaces, or determine local ip
        via other means.

        If using a statically defined IP address (for instance, while connecting to an offline, unmanaged switch) it is
        highly recommended to supply an address, subnet, and gateway.  Omission of this information could prevent a
        valid socket attempt and default to the fallback interface depending on a few factors.
    """
    ip = "127.0.0.1"
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)

    try:
        # This connection does not need reach destination in order return interface IP Address
        s.connect(("10.254.254.254", 1))
        ip = s.getsockname()[0]

    # Fallback to loopback address, notify user
    except (PermissionError, ConnectionRefusedError, OSError):
        print("Unable to determine local address: defaulting to loopback interface")

    s.close()

    ip = IPv4Address(ip)
    return ip


# IP address lists
def generate_range_from_subnet(
    ip: str | IPv4Address, subnet: str | IPv4Address = 24
) -> list[IPv4Address]:
    """Return a list of IPv4 Address objects based on provided subnet information.
    Excludes network and broadcast addresses.

    :param ip: A valid IPv4 Address
    :type ip: str, IPv4Address
    :param subnet: (optional) CIDR notation integer value or subnet mask convention, 24 by default
    :type subnet: int, str

    :return: IPv4 Address objects based upon range of provided subnet, excluding network and broadcast addresses
    :rtype: list

    Note:
        If subnet is not referenced in either the ip or subnet params, function assumes 24 or (255.255.255.0).
        CIDR notation in ip param overrides subnet param.

        The following are examples of valid inputs:
            "10.0.0.1" <- assumption of 255.255.255.0 or 24 \n
            IPv4Address("192.168.10.10") <- assumption of 255.255.255.0 or 24 \n
            "192.168.5.1/20" <- overrides subnet parameter \n
            ("192.168.0.1", 24) \n
            ("10.10.2.0", "255.255.255.0") \n
    """
    # Convert both parameters to string for evaluation
    ip = str(ip)
    subnet = str(subnet)

    # CIDR notation overrides subnet param
    if "/" in ip:
        network_info = ip

    # Otherwise check what format the subnet info is provided in
    else:
        # Subnet mask form
        if "." in subnet:
            network_info = (ip, subnet)
        # As a last resort, the function will create CIDR notation from the subnet integer value
        else:
            network_info = ip + "/" + subnet

    # Not using strict for simplicity to allow for any IP address to pass
    network = IPv4Network(network_info, strict=False)
    network_hosts = [host for host in network.hosts()]

    return network_hosts


def generate_range_from_two_ips(
    first_ip: str | IPv4Address, second_ip: str | IPv4Address
) -> list[IPv4Address]:
    """Return a list of IPv4 Address objects between two provided IP addresses, including both provided addresses.

    :param first_ip: A valid IPv4 Address, example "10.10.10.132"
    :type first_ip: str, IPv4Address
    :param second_ip: A valid IPv4 Address, example IPv4Address("10.10.10.157")
    :type second_ip: str, IPv4Address

    :return: Both addresses along with every possible address in between them
    :rtype: list

    Note:
        The returned list will have complete disregard for any subnet boundaries, broadcast addresses, etc.

        Use some discretion as this function can generate a list with billions of values.
    """
    # Convert to IPv4 objects if not already
    first_ip = IPv4Address(first_ip)
    second_ip = IPv4Address(second_ip)

    starting_ip = first_ip
    ending_ip = second_ip
    # Ensure a proper range is created by starting with smaller IP address
    if first_ip > second_ip:
        starting_ip = second_ip
        ending_ip = first_ip

    # List will be inclusive of ending IP
    # Converting to integers allows for a comprehension as the addresses are translated to basic numbers
    ip_list = [IPv4Address(ip) for ip in range(int(starting_ip), int(ending_ip) + 1)]

    return ip_list


# TCP
def reachable_tcp_single_ip(
    host: str | IPv4Address,
    port: int,
    output: dict[IPv4Address, list[int]],
    timeout: int = 4,
) -> None:
    """Determine if a given host on a given port is reachable via TCP socket connection, add successful values to dictionary.

    :param host: A valid IPv4 Address, example "10.10.10.132"
    :type host: str, IPv4Address
    :param port: Port on which to attempt connection
    :type port: int
    :param output: Reachable hosts will be added to this
    :type output: dict
    :param timeout: (optional) Number of seconds to wait for a timeout failure, default 4
    :type timeout: int

    :return: Nothing, external dictionary will be updated
    :rtype: None

    Note:
        The dictionary will be updated in the following format: {IP4Address: [port], IPv4Address: [port1, port2], ...}

        If host is already present within the dictionary, the port will be appended to the existing list.
        However, if the port in question already exists within said list, it will not be added to avoid duplicates
    """
    # Define socket type, IPv4, TCP
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Timeout interval
    soc.settimeout(timeout)

    # If connection is successful, create entry for host/port or append port to list of ports if entry already exists
    try:
        soc.connect((str(host), int(port)))
        soc.shutdown(socket.SHUT_RDWR)
        if IPv4Address(host) in output.keys():
            # Prevent duplicate port listings in the event of multiple attempts
            if port not in output[IPv4Address(host)]:
                output[IPv4Address(host)].append(port)
        else:
            output[IPv4Address(host)] = [port]

    except (TimeoutError, ConnectionRefusedError, OSError):
        pass

    soc.close()


def tcp_ip_port_scanner(
    ip_list: list[str | IPv4Address], ports: int | list[int], df: bool = True, timeout: int = 4
) -> dict[IPv4Address, list[int]] | pd.DataFrame:
    """Determine which hosts from a given list are reachable via a port or list of ports, return dictionary or DataFrame
    of valid connections.

    :param ip_list: Containing either str ip "10.10.1.1" or IPv4Address("10.10.1.1") objects
    :type ip_list: list
    :param ports: Either a single int port or list of int ports
    :type ports: int, list
    :param df: (optional) This entry will determine what format is returned, True by default and therefore a DataFrame.
    :type df: bool
    :param timeout: (optional) Number of seconds to wait for a timeout failure, default 4
    :type timeout: int

    :return: Hosts with associated ports on which they responded
    :rtype: dict, pd.DataFrame

    Note:
        Dictionary formatted as: {IPv4Address("10.10.1.1"): [80, 443], ...}

        DataFrame columns: ip, ports
    """
    port_list = []

    # Determine if single port or multiple ports were provided, append/extend port_list accordingly

    if type(ports) is int:
        port_list.append(ports)
    elif type(ports) is list:
        port_list.extend(ports)

    threads_list = []
    output = {}

    # Create separate thread for each host to expedite the process
    # Most of the time in this function is consumed by waiting for a host response
    for ip in ip_list:
        for port in port_list:
            t = threading.Thread(
                target=reachable_tcp_single_ip, args=(ip, port, output, timeout)
            )
            threads_list.append(t)

    for number in range(len(threads_list)):
        threads_list[number].start()

    for number in range(len(threads_list)):
        threads_list[number].join()

    # Sort output to start with the lowest ip, sort each list of ports as well
    final_output = {ip: sorted(output[ip]) for ip in sorted(output.keys())}

    if df is True:
        pre_df_dictionary = {
            "ip": [host for host in final_output.keys()],
            "ports": [ports for ports in final_output.values()],
        }
        final_output = pd.DataFrame.from_dict(pre_df_dictionary)

    return final_output

def tcp_ip_port_monitor(
        ip_list: list[str | IPv4Address], ports: int | list[int], frequency: int = 10, duration: int|None = None, timeout: int = 4
) -> None:
    """Determine which hosts are reachable via a list of ports for a given duration (or indefinitely) at a given frequency and display the results

    :param ip_list: Containing either str ip "10.10.1.1" or IPv4Address("10.10.1.1") objects
    :type ip_list: list
    :param ports: Either a single int port or list of int ports
    :type ports: int, list
    :param frequency: (optional) Seconds to wait between batch scans, default 10
    :type frequency: int
    :param duration: (optional) Total seconds to run the monitor function (None by default for indefinitely)
    :type duration: int, None
    :param timeout: (optional) Seconds to wait for unresponsive host, default 2
    :type timeout: int

    :return: Nothing, print results to output
    :rtype: None
     """

    if duration is not None:
        print(f'Scanning every {frequency} second(s) for a duration of {duration} second(s):\n')
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=duration)
        while datetime.datetime.now() < end_time:
            responses = tcp_ip_port_scanner(ip_list, ports, timeout=timeout, df=False)
            print('Responding Hosts: [ports]\n')
            for host, ports in responses.items():
                print(host, ':', ports)
            print('\n')
            time.sleep(frequency)

    else:
        print(f'Scanning every {frequency} second(s), please use keyboard interrupt to exit\n')
        while True:
            responses = tcp_ip_port_scanner(ip_list, ports, timeout=timeout, df=False)
            print('Responding Hosts: [ports]\n')
            for host, ports in responses.items():
                print(host, ':', ports)
            print('\n')
            time.sleep(frequency)
