import subprocess


def get_version(command):
    try:
        # Run the command, capture the output, decode to string, and strip whitespace
        version_output = (
            subprocess.check_output(command, stderr=subprocess.STDOUT).decode().strip()
        )
        return version_output
    except FileNotFoundError:
        # This error occurs if the command is not found (e.g., node or npm not installed)
        return None
    except subprocess.CalledProcessError as e:
        # If command fails, you can inspect e.output or return None
        print("FAILED TO GET VERSION, ERR: ", e)
        return None
