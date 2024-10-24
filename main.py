#!/usr/bin/env python3

try:
    import requests
    import xml.etree.ElementTree as ET
    from tcp_latency import measure_latency
    import socket
    import os
    from time import sleep
    from tabulate import tabulate
except ModuleNotFoundError:
    print("Couldn't Import Libraries")
    print("Kindly run:")
    print("\tpipenv install")
    print("Exiting...")
    exit(1)

current_dir = os.curdir
servers = []


# Get Servers List from https://c.speedtest.net/speedtest-servers-static.php
def get_xml():
    try:
        response = requests.get(
            "https://c.speedtest.net/speedtest-servers-static.php", timeout=10
        )
        response.raise_for_status()  # Raise an exception for bad responses
        print("Response 200, OK")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching server list: {e}")
        exit(1)


def write_xml_file(xml):
    print("\nWriting XML file...")
    file = open(f"{current_dir}/servers.xml", "w")
    file.write(xml)
    file.close()
    print(f"{current_dir}/servers.xml")
    print("\nWrote XML file to 'servers.xml'")


def parse_xml(filename):
    print(f"Parsing XML file '{filename}'")
    return ET.parse(filename).getroot()


def hostname_to_ip(hostname):
    try:
        return [socket.gethostbyname(hostname), 0]
    except socket.gaierror:
        print(f"Couldn't Resolve {hostname}")
        return ["", 1]


def my_ip():
    try:
        data = requests.get("http://ifconfig.me", timeout=5)
        return data.text
    except requests.exceptions.RequestException as e:
        print(f"Error getting public IP: {e}")
        return "Unavailable"


def xml_to_list(root):
    global servers
    for type_tag in root.findall("servers/server"):
        hostname = type_tag.get("host")
        hostname = hostname.replace(":8080", "")
        server_id = type_tag.get("id")
        server_name = type_tag.get("sponsor")
        server_city = type_tag.get("name")
        servers.append([hostname, server_id, server_name, server_city])


def test_latency(address):
    latency = measure_latency(host=address, port=8080, runs=3, timeout=2.5)
    return latency


def process_latency(latency):
    # Ensure latency has 3 values
    if latency and len(latency) >= 3:
        try:
            average = sum(latency[:3]) / 3  # Use sum() to calculate the average
            return average
        except TypeError as e:
            print(f"Error calculating latency: {e}")
            return None
    else:
        print("Latency test returned insufficient data")
        return None


def main():
    XML = get_xml()
    write_xml_file(XML)
    sleep(1.5)

    print(f"Your Public IP: {my_ip()}\n")

    root = parse_xml("servers.xml")
    xml_to_list(root)
    print(f"Found {len(servers)} Server(s)\n")
    print("Starting Latency Test")
    pings = []

    for server in servers:
        hostname = server[0]
        server_id = server[1]
        server_name = server[2]
        server_city = server[3]
        IP = hostname_to_ip(hostname)

        if IP[1] == 0:
            print(f"\n  Server: {server_name} - {server_city} (id = {server_id})")
            print(f"Hostname: {hostname}")
            print(f"      IP: {IP[0]}")
        else:
            continue

        latency = test_latency(hostname)
        if latency and len(latency) >= 3:
            average = process_latency(latency)
            if average is not None:
                print(
                    f" Latency: {latency[0]:.2f} ms, {latency[1]:.2f} ms, {latency[2]:.2f} ms, avg = {average:.2f} ms"
                )
                ping = [
                    hostname,
                    f"{latency[0]:.2f} ms",
                    f"{latency[1]:.2f} ms",
                    f"{latency[2]:.2f} ms",
                    f"{average:.2f} ms",
                ]
                pings.append(ping)
        else:
            print("Ping Test Failed or insufficient data")

    # Remove the XML file after processing
    if os.path.exists(f"{current_dir}/servers.xml"):
        os.remove(f"{current_dir}/servers.xml")

    # Display the summary using tabulate
    header = ["Hostname", "Ping #1", "Ping #2", "Ping #3", "Average"]
    print("\nSummary\n")
    print(tabulate(pings, headers=header))


if __name__ == "__main__":
    main()
