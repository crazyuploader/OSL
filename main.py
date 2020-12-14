#!/usr/bin/env python3

from requests import get
import xml.etree.ElementTree as ET
from tcp_latency import measure_latency
import socket
from os import name
import subprocess
from time import sleep


# Function to Clear Console
def clear():
    # For Windows
    if name == "nt":
        _ = subprocess.call("cls")

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
    file = open("servers.xml", "w")
    file.write(xml)
    file.close
    print("")
    print("Wrote XML file to 'servers.xml'")


def parse_xml(filename):
    print("Parsing XML file '{}'".format(filename))
    return ET.parse(filename).getroot()


def hostname_to_ip(hostname):
    return socket.gethostbyname(hostname)


def my_ip():
    data = get("http://ifconfig.me")
    return data.text


if __name__ == "__main__":
    XML = get_xml()
    write_xml_file(XML)
    sleep(1.5)
    clear()
    print("Your IP: {}".format(my_ip()))
    print("")
    root = parse_xml("servers.xml")
    print("")
    print("Starting Latency Test")
    for type_tag in root.findall('servers/server'):
        value = type_tag.get('host')
        value = value.replace(":8080", "")
        IP = hostname_to_ip(value)
        print("Checking Ping for {} ({})".format(value, IP))
        latency = measure_latency(host=value, port=8080, runs=3, timeout=2.5)
        print("Ping for {} is = {:.2f} ms, {:.2f} ms, {:.2f} ms".format(IP, latency[0], latency[1], latency[2]))
        print("")
    print("Done!")
