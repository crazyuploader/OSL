#!/usr/bin/env python3

try:
    from requests import get
    import xml.etree.ElementTree as ET
    from tcp_latency import measure_latency
    import socket
    import os
    import subprocess
    from time import sleep
    from tabulate import tabulate
except ModuleNotFoundError:
    print("Couldn't Import Libraries")
    print("Kindly run:")
    print("")
    print("\tpip install -r requirements.txt")
    print("")
    print("Exiting...")
    exit(1)


current_dir = os.curdir
servers = []


# Function to Clear Console
def clear():
    # For Windows
    if os.name == "nt":
        pass
    # For anything else (Linux, etc)
    else:
        _ = subprocess.call("/usr/bin/clear")


# Get Servers List from https://c.speedtest.net/speedtest-servers-static.php
def get_xml():
    data = get("https://c.speedtest.net/speedtest-servers-static.php")
    if data.status_code == 200:
        print("Response 200, OK")
    else:
        exit(1)
    return data.text


def write_xml_file(xml):
    print("")
    print("Writing XML file...")
    file = open("{}/servers.xml".format(current_dir), "w")
    file.write(xml)
    file.close()
    print("{}/servers.xml".format(current_dir))
    print("")
    print("Wrote XML file to 'servers.xml'")


def parse_xml(filename):
    print("Parsing XML file '{}'".format(filename))
    return ET.parse(filename).getroot()


def hostname_to_ip(hostname):
    try:
        return [socket.gethostbyname(hostname), 0]
    except socket.gaierror:
        print("Couldn't Resolve {}".format(hostname))
        return ["", 1]


def my_ip():
    data = get("http://ifconfig.me")
    return data.text


def xml_to_list(root):
    global servers
    for type_tag in root.findall('servers/server'):
        hostname = type_tag.get('host')
        hostname = hostname.replace(":8080", "")
        server_id = type_tag.get('id')
        server_name = type_tag.get('sponsor')
        server_city = type_tag.get('name')
        servers.append([hostname, server_id, server_name, server_city])


def test_latency(address):
    return measure_latency(host=address, port=8080, runs=3, timeout=2.5)


def main():
    XML = get_xml()
    write_xml_file(XML)
    sleep(1.5)
    clear()
    print("Your Public IP: {}".format(my_ip()))
    print("")
    root = parse_xml("servers.xml")
    xml_to_list(root)
    print("Found {} Server(s)".format(len(servers)))
    print("")
    print("Starting Latency Test")
    pings = []
    for server in servers:
        hostname = server[0]
        server_id = server[1]
        server_name = server[2]
        server_city = server[3]
        IP = hostname_to_ip(hostname)
        if IP[1] == 0:
            print("")
            print("\t  Server: {} - {} (id = {})".format(server_name, server_city, server_id))
            print("\tHostname: {}".format(hostname))
            print("\t      IP: {}".format(IP[0]))
        else:
            print("")
            continue
        latency = test_latency(hostname)
        if latency is not None:
            try:
                average = (latency[0] + latency[1] + latency[2]) / 3
                print("\t Latency: {:.2f} ms, {:.2f} ms, {:.2f} ms, avg = {:.2f} ms".format(latency[0], latency[1], latency[2], average))
                ping = [hostname]
                ping.append("{:.2f} ms".format(latency[0]))
                ping.append("{:.2f} ms".format(latency[1]))
                ping.append("{:.2f} ms".format(latency[2]))
                ping.append("{:.2f} ms".format(average))
                pings.append(ping)
            except TypeError:
                print("Server Did Not Respond")
        else:
            print("Ping Test Failed")
        print("")
    if os.path.exists("{}/servers.xml".format(current_dir)):
        os.remove("servers.xml")
    header = ["Hostname", "Ping #1", "Ping #2", "Ping #3", "Average"]
    clear()
    print("Summary")
    print("")
    print(tabulate(pings, headers=header))


if __name__ == "__main__":
    main()
