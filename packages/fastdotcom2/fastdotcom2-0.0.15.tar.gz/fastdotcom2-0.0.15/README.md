# fastdotcom2

fastdotcom2 is a Python package that performs internet speed tests using [fast.com](https://fast.com). It measures download and upload speeds, and performs ping tests (both unloaded and loaded) to give you a comprehensive view of your internet performance.

## Features

- **Download Speed Test:** Measures the download speed in Mbps.
- **Upload Speed Test:** Measures the upload speed in Mbps.
- **Ping Tests:** Measures the average unloaded and loaded ping in milliseconds.

## Installation

Install fastdotcom2 from PyPI using pip:

```bash
pip install fastdotcom2
```
## Usage

Below is an example of how to use fastdotcom2 in your Python code:
```bash
import fastdotcom2

# Run the speed test with default parameters
result = fastdotcom2.fast_com2(verbose=False, maxtime=10)
print(result)
```

## Example Output

When you run the example above, you might see output similar to:
```bash
Download Speed: 140.00 Mbps
Upload Speed: 22.00 Mbps
Unloaded Ping: 24 ms
Loaded Ping: 59 ms
```

- **Download Speed:** Measured download speed in Mbps (displayed with two decimal places).
- **Upload Speed:** Measured upload speed in Mbps (displayed with two decimal places).
- **Unloaded Ping:** Average ping (latency) when the network is idle.
- **Loaded Ping:** Average ping (latency) during a download test.

## Requirements
- Python 3.8 or newer
- icmplib
- requests

## License

fastdotcom2 is released under the MIT License.

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request on GitHub.
