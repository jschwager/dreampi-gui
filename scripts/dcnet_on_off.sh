#!/bin/bash
# Script name: DCNET ON/OFF Script for DreamPi
# Original author: scrivanidc
# Modified and maintained by: jschwager (onlycodered)

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
		# Need to add logging functionality
		#echo "dreampi_dcnet.py backup and dcnet.rpi does not exist. Downloading..."
		wget -q --show-progress -O dreampi_dcnet.py https://github.com/scrivanidc/dreampi_custom_scripts/raw/main/DCNET_V2/dreampi_dcnet.py
		wget -q --show-progress -O dcnet.rpi https://github.com/scrivanidc/dreampi_custom_scripts/raw/main/DCNET_V2/dcnet.rpi
		#wget -q --show-progress -O dcnet.rpi https://github.com/flyinghead/flycast/raw/refs/heads/dev/tools/dreampi/dcnet.rpi
		chmod +x dreampi_dcnet.py dcnet.rpi
	else
		# Need to add logging functionality
		#echo "dreampi_dcnet.py and dcnet.rpi exists. OK."
	fi
}

check_standard_backup() {
	if [ ! -f "dreampi_standard.py" ]; then
		# Need to add logging functionality
		#echo "dreampi_standard.py backup does not exist. Creating..."
		cp dreampi.py dreampi_standard.py
		cp dreampi.py dreampi_standard2.py
	else
		# Need to add logging functionality
		#echo "dreampi_standard.py backup exists. OK."
	fi
}

copy_dcnet_script() {
	cp dreampi_dcnet.py dreampi.py
	# Need to add logging functionality
	#echo "dreampi_dcnet.py copied to dreampi.py"
}

copy_standard_script() {
	cp dreampi_standard.py dreampi.py
	# Need to add logging functionality
	#echo "dreampi_standard.py copied to dreampi.py"
}

check_standard_backup
check_dcnet_files

if [ "$ACTION" = "enable" ]; then
	copy_dcnet_script
	echo "DCNET Enabled. If you experience issues, please restart the DreamPi service."
elif [ "$ACTION" = "disable" ]; then
	copy_standard_script
	echo "DCNET Disabled. If you experience issues, please restart the DreamPi service."
fi

if [ "$REBOOT" = true ]; then
	# Need to add logging functionality
	#echo "Restarting RaspberryPi, ready to dial soon"
	sleep 5
	sudo reboot &
else
	# Need to add logging functionality
	#echo "Reboot skipped (noreboot specified)."
fi