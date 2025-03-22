import subprocess
import psutil
import time

CLI_COMMAND = ["python", "-m", "live_translation.cli"]


def test_cli_help():
    """Test if `live_translation.cli` runs with --help."""
    result = subprocess.run(CLI_COMMAND + ["--help"], capture_output=True, text=True)

    assert result.returncode == 0, "CLI command failed."
    assert "usage:" in result.stdout.lower(), "CLI command help not found."


def test_cli_invalid_argument():
    """Test invalid CLI argument handling."""
    result = subprocess.run(CLI_COMMAND + ["--invalid"], capture_output=True, text=True)

    assert result.returncode != 0, "CLI command should fail."
    assert "unrecognized arguments" in result.stderr.lower(), (
        "Invalid argument error not found."
    )


def test_cli_real_execution():
    """Test CLI execution."""
    process = subprocess.Popen(
        CLI_COMMAND, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    time.sleep(10)

    parent = psutil.Process(process.pid)
    for child in parent.children(recursive=True):
        child.terminate()

    process.terminate()
    process.wait(timeout=5)

    stdout, _ = process.communicate()

    assert process.returncode is not None, "CLI command should exit."
    assert "🚀 Starting the pipeline..." in stdout, "CLI didn't start properly"
