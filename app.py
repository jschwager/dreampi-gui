from flask import Flask, render_template, request, redirect, url_for, flash
import subprocess
from pathlib import Path

app = Flask(__name__)
app.secret_key = "2fq398j7q34987q34t9"  # Replace with a secure random key in production

BASE_DIR = Path(__file__).resolve().parent

COMMANDS = {
    "restart": ["sudo", "systemctl", "restart", "dreampi.service"],
    "status": ["sudo", "systemctl", "status", "dreampi.service"],
    "dcnet-on": [str(BASE_DIR / "scripts" / "dcnet_on_off.sh"), "enable", "noreboot"],
    "dcnet-off": [str(BASE_DIR / "scripts" / "dcnet_on_off.sh"), "disable", "noreboot"],
}

# FUNCTION: Status styling helper
def style_helper(color, status):
	if color == "green":
		return f"<i class=\"bi bi-check-circle-fill\" style=\"color: green;\"></i> {status}"
	elif color == "red":
		return f"<i class=\"bi bi-dash-circle-fill\" style=\"color: red;\"></i> {status}"
	elif color == "yellow":
		return f"<i class=\"bi bi-exclamation-circle-fill\" style=\"color: orange;\"></i> {status}"

# ROUTE: Home
@app.route("/")
def index():

	# Service status
	try:
		command = subprocess.run(["sudo", "systemctl", "is-active", "dreampi.service"], capture_output=True, text=True, check=True, timeout=5)
		service_status = command.stdout.strip().capitalize()
		service_status = style_helper("green", service_status)
	except subprocess.CalledProcessError as e:
		service_status = style_helper("red", "Error / Inactive")
	except subprocess.TimeoutExpired as e:
		service_status = style_helper("yellow", "Unknown (timeout)")
	
	# DCNET button status
	try:
		dcnet_status_command = subprocess.run(["grep", "-q", "dcnet", "../dreampi/dreampi.py"], capture_output=True, text=True, check=True, timeout=5)
		dcnet_button_text = "Disable DCNET"
		dcnet_button_action = "dcnet-off"
	except subprocess.CalledProcessError as e:
		dcnet_button_text = "Enable DCNET"
		dcnet_button_action = "dcnet-on"
	except subprocess.TimeoutExpired as e:
		dcnet_button_text = "DCNET Unknown"

	# IP Address

	# DreamPi IP address
	try:
		ip_address_command = subprocess.run(["hostname", "-I"], capture_output=True, text=True, check=True, timeout=5)
		ip_address = ip_address_command.stdout.strip().split()[0]  # Get the first IP address
	except subprocess.CalledProcessError as e:
		ip_address = style_helper("red", "Error")
	except subprocess.TimeoutExpired as e:
		ip_address = style_helper("yellow", "Unknown (timeout)")
	
	# Dreamcast IP address
	try:
		dc_ip_address_command = subprocess.run(
			"sudo journalctl -u dreampi.service | grep 'Created alias interface' | grep -oE '[0-9]+\\.[0-9]+\\.[0-9]+\\.(98|99)' | tail -n 1",
			capture_output=True,
			text=True,
			check=True,
			timeout=5,
			shell=True
		)
		dc_ip_address = dc_ip_address_command.stdout.strip() or style_helper("yellow", "No IP found in logs")
	except subprocess.CalledProcessError as e:
		dc_ip_address = style_helper("red", "Error")
	except subprocess.TimeoutExpired as e:
		dc_ip_address = style_helper("yellow", "Unknown (timeout)")

	# System Overview

	# Hostname
	try:
		hostname_command = subprocess.run(["hostname"], capture_output=True, text=True, check=True, timeout=5)
		hostname = hostname_command.stdout.strip()
	except subprocess.CalledProcessError as e:
		hostname = style_helper("red", "Error")
	except subprocess.TimeoutExpired as e:
		hostname = style_helper("yellow", "Unknown (timeout)")

	# Uptime
	try:
		uptime_command = subprocess.run(["uptime", "-p"], capture_output=True, text=True, check=True, timeout=5)
		uptime = uptime_command.stdout.strip()
	except subprocess.CalledProcessError as e:
		uptime = style_helper("red", "Error")
	except subprocess.TimeoutExpired as e:
		uptime = style_helper("yellow", "Unknown (timeout)")
	
	# Modem detection
	try:
		modem_command = subprocess.run(
			"lsusb | grep -E '(Modem|Conexant)' | awk -F' ID [0-9a-fA-F]*:[0-9a-fA-F]* ' '{print $2}'",
			capture_output=True,
			text=True,
			shell=True,
			timeout=5
		)
		modem_name = style_helper("green", modem_command.stdout.strip()) or style_helper("red", "Error / Not Detected")
	except subprocess.CalledProcessError as e:
		modem_name = style_helper("red", "Error / Not Detected")
	except subprocess.TimeoutExpired as e:
		modem_name = style_helper("yellow", "Unknown (timeout)")

	return render_template("index.html", service_status=service_status, dcnet_button_text=dcnet_button_text, dcnet_button_action=dcnet_button_action, ip_address=ip_address, dc_ip_address=dc_ip_address, hostname=hostname, uptime=uptime, modem_name=modem_name)

# ROUTE: Logs
@app.route("/logs")
def logs():
	try:
		command = subprocess.run(["sudo", "journalctl", "-u", "dreampi.service", "-n", "100", "--no-pager"], capture_output=True, text=True, check=True, timeout=10)
		logs = command.stdout
	except subprocess.CalledProcessError as e:
		logs = e.stderr or str(e)
	except subprocess.TimeoutExpired as e:
		logs = "The command timed out."
	return render_template("logs.html", logs=logs)

# ROUTE: Run command
@app.route("/run", methods=["POST"])
def run():
    action = request.form.get("action", "")
    cmd = COMMANDS.get(action)
    if not cmd:
        flash("Invalid action.", "danger")
        return redirect(url_for("index"))

    try:
        command = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
        result = (command.stdout or command.stderr or "Command completed with no output.").strip()
        flash(result, "success")
    except subprocess.CalledProcessError as e:
        flash((e.stderr or str(e)).strip(), "danger")
    except Exception as e:
        flash(str(e), "danger")

    return redirect(url_for("index"))

if __name__ == "__main__":
	from waitress import serve
	serve(app, host="0.0.0.0", port=8080)