#!/bin/bash

echo "200:"
curl -X POST -d "hostname=hello&ip_addr=8.8.8.8&mac_addr=3D:F2:C9:A6:B3:4F" localhost:8000/register
echo
echo "400:"
curl -X POST -d "hostname=hello&ip_addr=8.8.8.333&mac_addr=3D:F2:C9:A6:B3:4F" localhost:8000/register
