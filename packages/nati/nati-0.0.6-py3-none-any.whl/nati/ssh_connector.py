from netmiko import ConnectHandler

def get_device_info(hostname, username, password, device_type="cisco_ios"):
    device = {
        "device_type": device_type,
        "host": hostname,
        "username": username,
        "password": password,
    }

    try:
        with ConnectHandler(**device) as conn:
            hostname = conn.send_command("show running-config | include hostname")
            version = conn.send_command("show version | include Version")
            return {"hostname": hostname.strip(), "version": version.strip()}
    except Exception as e:
        return {"error": str(e)}
