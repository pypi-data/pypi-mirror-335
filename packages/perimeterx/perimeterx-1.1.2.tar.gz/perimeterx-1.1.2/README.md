# PerimeterX Solver

This Python module allows you to generate and solve PerimeterX challenges. It utilizes tls_client to spoof JA3 fingerprint and reversed fingerprinting techniques to obtain a HQ cookie from the PerimeterX collector.

## Installation

You can install the module from PyPI using pip:

```bash
pip install perimeterx
```

## Quick Start

A quick example of how to use the `PX` class to solve a PerimeterX challenge:

```python
from perimeterx import PX

if __name__ == "__main__":
    token = PX(
        app_id="PX943r4Fb8",
        ft=330,
        collector_uri="https://collector-px943r4fb8.px-cloud.net/api/v2/collector",
        host="https://arcteryx.com/",
        sid="0396fb2e-5f0f-11ef-ae7c-f857124857d2󠄱󠄷󠄲󠄴󠄱󠄷󠄰󠄳󠄷󠄹󠄹󠄵󠄶",
        vid="0bc41189-5ec3-11ef-ba8c-eaab7bc900b7",
        cts="0c3f5439-5ec3-11ef-83dc-88da46c325fa",
        proxy="http://user:pass@ip:port"
    ).solve()
    
    print(f"Solved PX: {token}")
```

### Parameters

- `app_id` (str): The website's PerimeterX application ID.
- `ft` (int): The website's PerimeterX application ft.
- `collector_uri` (str): The URL of the PerimeterX collector.
- `host` (str): The host URL for the target website.
- `sid` (str): PerimeterX Session ID.
- `vid` (str): PerimeterX Visitor ID.
- `cts` (str): PerimeterX client token string.
- `pxhd` (str, optional): Optional header for stricter sites.
- `proxy` (str, optional): Proxy settings in the format `http://user:pass@ip:port`.

## Dependencies

- `tls_client`: For handling HTTP sessions with JA3 spoofing.
- `fingerprint`: For generating fingerprints.
- `mods`: For payload encryption and PC generation.
- `hashlib`: For hashing operations.
- `wgl`: For generating real WebGL fingerprints.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

This module is built on the foundation of the PerimeterX service and its associated technologies. Thank you to the developers and maintainers of the libraries used in this project.