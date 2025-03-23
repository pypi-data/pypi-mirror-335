import requests
import configparser
import os

# Disable SSL warnings (useful for self-signed certificates)
requests.packages.urllib3.disable_warnings()


class CiscoISE:
    def __init__(self, config_file="nati.ini"):
        self.config = self._load_config(config_file)
        self.host = self.config.get("ise", "ise_url")
        self.username = self.config.get("ise", "ise_uid")
        self.password = self.config.get("ise", "ise_pwd")
        self.proxies = self._load_proxies()

        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        self.session.auth = (self.username, self.password)

    def _load_config(self, config_file):
        """Loads configuration from an ini file."""
        config = configparser.ConfigParser()
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file {config_file} not found.")
        config.read(config_file)
        return config

    def _load_proxies(self):
        """Loads proxy settings if available in the configuration file."""
        if self.config.has_section("proxy"):
            return {
                "http": self.config.get("proxy", "http", fallback=None),
                "https": self.config.get("proxy", "https", fallback=None),
            }
        return None  # No proxy configured

    def _handle_response(self, response):
        """Handles HTTP responses and raises errors if necessary."""
        if response.status_code in [200, 201, 204]:
            return response.json() if response.text else {}
        else:
            response.raise_for_status()

    def get(self, endpoint: str):
        """Performs a GET request to the Cisco ISE ERS API."""
        if not endpoint:
            raise ValueError("Endpoint must be provided for the GET request.")

        url = f"{self.host}/ers/{endpoint}"
        try:
            response = self.session.get(url, verify=False,
                                        proxies=self.proxies)  # Set verify=True if using a trusted cert
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            print(f"Error making GET request to {url}: {e}")
            return None

    def get_all(self, endpoint: str):
        """Retrieves all results from Cisco ISE API, handling pagination failures gracefully."""
        if not endpoint:
            raise ValueError("Endpoint must be provided for the GET request.")

        results = []
        url = f"{self.host}/ers/{endpoint}"

        try:
            while url:
                try:
                    response = self.session.get(url, verify=False, proxies=self.proxies)
                    data = self._handle_response(response)

                    if not data or "SearchResult" not in data:
                        print(f"Unexpected response format at {url}. Skipping this page.")
                        break  # Stop if we get an unexpected format

                    # Append results
                    if "resources" in data["SearchResult"]:
                        results.extend(data["SearchResult"]["resources"])

                    # Move to next page if available
                    next_page = data["SearchResult"].get("nextPage", {}).get("href")
                    if next_page:
                        print(f"Fetching next page: {next_page}")
                        url = next_page  # Update for next iteration
                    else:
                        url = None  # Stop looping if no more pages

                except requests.exceptions.RequestException as e:
                    print(f"Error fetching page {url}: {e}. Skipping and continuing.")
                    url = None  # Stop pagination but return collected results

            return results

        except requests.exceptions.RequestException as e:
            print(f"Error fetching initial data from {endpoint}: {e}")
            return None

    def post(self, endpoint: str, data: dict):
        """Performs a POST request to the Cisco ISE ERS API."""
        if not endpoint:
            raise ValueError("Endpoint must be provided for the POST request.")

        url = f"{self.host}/ers/{endpoint}"
        try:
            response = self.session.post(url, json=data, verify=False,
                                         proxies=self.proxies)  # Set verify=True if using a trusted cert
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            print(f"Error making POST request to {url}: {e}")
            return None

    def test_connection(self):
        """Tests the API connection by fetching ISE system node information."""
        return self.get("config/node")


if __name__ == "__main__":
    ise = CiscoISE()
    print("Testing Cisco ISE Connection...")
    response = ise.test_connection()
    print(response if response else "Failed to connect to Cisco ISE.")
