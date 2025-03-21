import getpass
import json
import locale
import os
import platform
import subprocess
import urllib.request

from openai import OpenAI
from rich import print as rprint
from rich.console import Console
from rich.markdown import Markdown


def get_ip_location():
    try:
        with urllib.request.urlopen("http://ip-api.com/json") as response:
            data = json.load(response)
            return {
                "country": data.get("country"),
                "regionName": data.get("regionName"),
                "city": data.get("city"),
                "zip": data.get("zip"),
                "isp": data.get("isp"),
            }
    except Exception as e:
        return {"error": str(e)}


def get_installed_software_windows():
    try:
        result = subprocess.run(["wmic", "product", "get", "name"], stdout=subprocess.PIPE, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error fetching installed software: {e}"


# Function to get installed software (macOS)
def get_installed_software_macos():
    try:
        result = subprocess.run(["ls", "/Applications"], stdout=subprocess.PIPE, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error fetching installed software: {e}"


# Determine OS and fetch installed software
def get_installed_software():
    if platform.system() == "Windows":
        return get_installed_software_windows()
    elif platform.system() == "Darwin":  # macOS
        return get_installed_software_macos()
    else:
        return "Installed software listing not supported on this OS."


# Collect hardware information
def get_hardware_info():
    try:
        if platform.system() == "Windows":
            result = subprocess.run(["wmic", "cpu", "get", "name"], stdout=subprocess.PIPE, text=True)
            cpu_info = result.stdout.strip()
            result = subprocess.run(["wmic", "computersystem", "get", "model"], stdout=subprocess.PIPE, text=True)
            model_info = result.stdout.strip()
        elif platform.system() == "Darwin":  # macOS
            result = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], stdout=subprocess.PIPE, text=True)
            cpu_info = result.stdout.strip()
            result = subprocess.run(["system_profiler", "SPHardwareDataType"], stdout=subprocess.PIPE, text=True)
            model_info = result.stdout.strip().split("\n")[4].split(":")[1].strip()
        else:
            cpu_info = "CPU information not supported on this OS."
            model_info = "Model information not supported on this OS."
    except Exception as e:
        cpu_info = f"Error fetching CPU information: {e}"
        model_info = f"Error fetching model information: {e}"

    return {"cpu": cpu_info, "model": model_info}


# Collect system information
def collect_system_info():
    system_info = {
        "python_version": platform.python_version(),
        "os_version": platform.platform(),
        "language": locale.getdefaultlocale(),
        "username": os.getlogin(),
        "installed_software": get_installed_software(),
        "ip_location": get_ip_location(),
        "hardware_info": get_hardware_info(),
    }
    return system_info


# Function to get OpenAI API key
def get_openai_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        api_key = getpass.getpass("Please enter your OpenAI API key: ")
    return api_key


# Main function to send information to GPT for roasting
def main():
    system_info = collect_system_info()
    print("System Information Collected:")
    print(json.dumps(system_info, indent=4))

    roast_request = "Here's my system info, roast me:\n" + json.dumps(system_info, indent=4)

    openai_api_key = get_openai_api_key()
    client = OpenAI(api_key=openai_api_key)

    console = Console()

    with console.status("[bold green]Roasting in progress...") as status:
        # Send request to OpenAI API
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a humorous AI who roasts system setups. Use markdown to format your response, add emojis, and make it short and fun!",
                    },
                    {"role": "user", "content": roast_request},
                ],
            )
        except Exception as e:
            print(f"Error communicating with OpenAI API: {e}")
            return

    rprint("\n[bold magenta]GPT-4o-mini's Roast :fire:[/bold magenta]")

    rprint(Markdown(response.choices[0].message.content))


if __name__ == "__main__":
    main()
