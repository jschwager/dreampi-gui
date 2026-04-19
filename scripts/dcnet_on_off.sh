#!/bin/bash
# Script name: DCNET ON/OFF Script for DreamPi
# Original author: scrivanidc
# Updated and maintained by: jschwager (onlycodered)

# Updated 2025-09-15
ACTION="${1:-}"
REBOOT=true

show_help() {
  echo "Usage: $0 <enable|disable> [noreboot]"
  echo ""
  echo "Examples:"
  echo "  $0 enable"
  echo "  $0 disable"
  echo "  $0 enable noreboot"
}

case "$ACTION" in
  enable|disable)
    ;;
  *)
    show_help
    exit 1
    ;;
esac

if [ "${2:-}" = "noreboot" ]; then
  REBOOT=false
elif [ -n "${2:-}" ]; then
  echo "Invalid second argument: $2"
  show_help
  exit 1
fi

cd /home/pi/dreampi/
echo ""
check_dcnet_files() {
  if [ ! -f "dreampi_dcnet.py" ]; then
    echo "dreampi_dcnet.py backup and dcnet.rpi does not exist. Downloading..."
    echo ">>"
    wget -q --show-progress -O dreampi_dcnet.py https://github.com/scrivanidc/dreampi_custom_scripts/raw/main/DCNET_V2/dreampi_dcnet.py
    wget -q --show-progress -O dcnet.rpi https://github.com/scrivanidc/dreampi_custom_scripts/raw/main/DCNET_V2/dcnet.rpi
    #wget -q --show-progress -O dcnet.rpi https://github.com/flyinghead/flycast/raw/refs/heads/dev/tools/dreampi/dcnet.rpi
    chmod +x dreampi_dcnet.py dcnet.rpi
  else
    echo "dreampi_dcnet.py and dcnet.rpi exists. OK."
    echo ">>"
  fi
}

check_standard_backup() {
  if [ ! -f "dreampi_standard.py" ]; then
    echo "dreampi_standard.py backup does not exist. Creating..."
    cp dreampi.py dreampi_standard.py
    cp dreampi.py dreampi_standard2.py
  else
    echo "dreampi_standard.py backup exists. OK."
    echo ">>"
  fi
}

copy_dcnet_script() {
  cp dreampi_dcnet.py dreampi.py
  echo "dreampi_dcnet.py copied to dreampi.py"
  echo ">>"
}

copy_standard_script() {
  cp dreampi_standard.py dreampi.py
  echo "dreampi_standard.py copied to dreampi.py"
  echo ">>"
}

check_standard_backup
check_dcnet_files

if [ "$ACTION" = "enable" ]; then
  copy_dcnet_script
  echo "Done. DCNET Script ON (Standard DreamPi Script disabled)"
elif [ "$ACTION" = "disable" ]; then
  copy_standard_script
  echo "Done. DCNET Script OFF (Standard DreamPi Script enabled)"
fi

if [ "$REBOOT" = true ]; then
  echo ">>"
  echo "Restarting RaspberryPi, ready to dial soon"
  sleep 5
  sudo reboot &
else
  echo ">>"
  echo "Reboot skipped (noreboot specified)."
fi