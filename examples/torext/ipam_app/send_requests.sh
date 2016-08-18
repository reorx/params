#!/bin/bash

function mycurl() {
    curl -w ' %{http_code}' $@
    echo
}

echo "POST /register 200:"
mycurl -X POST -d "hostname=hello.com&ip_addr=8.8.8.8&mac_addr=3D:F2:C9:A6:B3:4F&ts=1471510216" localhost:8000/register
echo
echo "POST /register 400:"
mycurl -X POST -d "hostname=hello.com&ip_addr=8.8.8.333&mac_addr=3D:F2:C9:A6:B3:4F&ts=1471510216" localhost:8000/register
echo
echo "POST /resolves 200:"
mycurl -X POST -d "hostname=hello.com&ip_addr=10.10.10.1" localhost:8000/resolves
echo
echo "POST /resolves 400:"
mycurl -X POST -d "hostname=10.10.10.10&ip_addr=10.10.10.1" localhost:8000/resolves
echo
echo "GET /macs/3D:F2:C9:A6:B3:4F 200:"
mycurl "localhost:8000/macs/3D:F2:C9:A6:B3:4F"
echo
echo "GET /macs/3D:F2:C9:A6:B3:4F 400:"
mycurl "localhost:8000/macs/3D:F2:C9"
