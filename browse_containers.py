
import subprocess
import time


def get_container_ids():
    result = subprocess.run(["docker", "ps", "-q"], capture_output=True, text=True)
    return result.stdout.strip().splitlines()


def get_container_name(cid: str):
    result = subprocess.run(["docker", "inspect", "--format={{.Name}}", cid], capture_output=True, text=True)
    return result.stdout.strip().lstrip('/')


def stream_logs(cid: str):
    return subprocess.Popen(["docker", "logs", "-f", cid])


def open_shell(cid: str):
    subprocess.run(["make", "shell"])


if __name__ == "__main__":
    while True:
        container_ids = get_container_ids()
        print(container_ids)
        exit()
        for container_id in container_ids:
            name = get_container_name(container_id)
            print(f"\n=== Logs for {name} ===")
            log_proc = stream_logs(container_id)
            try:
                input(f"Press [Enter] to open shell in {name}, or [Ctrl+C] to skip...\n")
                log_proc.terminate()
                open_shell(container_id)
            except KeyboardInterrupt:
                log_proc.terminate()
                print("Skipping shell...")
            print("Returning to log loop...")
            time.sleep(1)
        print("\nLooping through containers again...\n")
        time.sleep(2)
