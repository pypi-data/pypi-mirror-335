import argparse
import json
import urllib.request

PARSER = argparse.ArgumentParser(description='Fetch metadata about a pip package')
PARSER.add_argument('package')


def main():
    args = PARSER.parse_args()
    # Fetch the package metadata: curl https://pypi.org/pypi/tensorflow/json
    # use urllib
    package = args.package
    url = f"https://pypi.org/pypi/{package}/json"
    with urllib.request.urlopen(url) as response:
        package_data = response.read().decode('utf-8')
        print(json.dumps(json.loads(package_data), indent=2))
