from flask import Flask, render_template, request, redirect, url_for
import subprocess

app = Flask(__name__)

COMMANDS = {
	"restart": ["sudo", "systemctl", "restart", "dreampi.service"],
	"status": ["sudo", "systemctl", "status", "dreampi.service"]
}

@app.route("/")
def index():

	# Service status
	try:
		# Mac test:
		#command = subprocess.run(["echo", "active"], capture_output=True, text=True, check=True, timeout=10)
		# On Raspberry Pi use:
		command = subprocess.run(["sudo", "systemctl", "is-active", "dreampi.service"], capture_output=True, text=True, check=True, timeout=10)
		status = command.stdout.strip().capitalize()
		status = f"<span class=\"badge rounded-pill text-bg-success p-2\">{status}</span>"
	except subprocess.CalledProcessError as e:
		status = f"<span class=\"badge rounded-pill text-bg-danger p-2\">Error</span>"
	except subprocess.TimeoutExpired as e:
		status = f"<span class=\"badge rounded-pill text-bg-warning p-2\">Unknown (timeout)</span>"
	
	# IP address
	try:
		command = subprocess.run(["hostname", "-I"], capture_output=True, text=True, check=True, timeout=10)
		ip_address = command.stdout.strip().split()[0]  # Get the first IP address
	except subprocess.CalledProcessError as e:
		ip_address = "Error"
	except subprocess.TimeoutExpired as e:
		ip_address = "Unknown (timeout)"

	return render_template("index.html", status=status, ip_address=ip_address)


@app.route("/configure")
def configure():
	return render_template("configure.html")

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

@app.route("/run", methods=["POST"])
def run():
	action = request.form.get("action", "")
	cmd = COMMANDS.get(action)

	if not cmd:
		return redirect(url_for("index"))

	try:
		command = subprocess.run(cmd, capture_output=True, text=True, check=True)
		result = command.stdout or command.stderr
	except subprocess.CalledProcessError as e:
		result = e.stderr or str(e)

	return render_template("index.html", result=result)

if __name__ == "__main__":
	from waitress import serve
	serve(app, host="0.0.0.0", port=80)