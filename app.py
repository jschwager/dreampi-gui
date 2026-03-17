from flask import Flask, render_template, request, redirect, url_for
import subprocess

app = Flask(__name__)

COMMANDS = {
	"restart": ["sudo", "systemctl", "restart", "dreampi.service"],
	"status": ["sudo", "systemctl", "status", "dreampi.service"]
}

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/logs")
def logs():
	try:
		completed = subprocess.run(["sudo", "journalctl", "-u", "dreampi.service", "-n", "100", "--no-pager"], capture_output=True, text=True, check=True)
		logs = completed.stdout
	except subprocess.CalledProcessError as e:
		logs = e.stderr or str(e)

	return render_template("logs.html", logs=logs)

@app.route("/run", methods=["POST"])
def run():
	action = request.form.get("action", "")
	cmd = COMMANDS.get(action)

	if not cmd:
		return redirect(url_for("index"))

	try:
		completed = subprocess.run(cmd, capture_output=True, text=True, check=True)
		result = completed.stdout or completed.stderr
	except subprocess.CalledProcessError as e:
		result = e.stderr or str(e)

	return render_template("index.html", result=result)

if __name__ == "__main__":
	from waitress import serve
	serve(app, host="0.0.0.0", port=5001)