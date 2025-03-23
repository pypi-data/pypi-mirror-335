# NeT2I (Network to Image)

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/Python-3.8%2B-green.svg)

**NeT2I** is a Python package designed to convert network traffic data into image representations. These images can be used to train and test Convolutional Neural Networks (CNNs) for network traffic analysis, anomaly detection, and other machine learning tasks. The package processes network data from CSV format, handles MAC and IP addresses, converts data into RGB format, and generates visual representations of network traffic.

---

## Features

- **CSV to Structured Data**: Convert network traffic data from CSV files into structured data.
- **MAC and IP Processing**: Handle MAC addresses and IP addresses for data processing.
- **RGB Conversion**: Transform network data into RGB format for image generation.
- **Image Generation**: Create visual representations of network traffic for machine learning applications.

---

## Installation

You can install **NeT2I** using `pip`:

```bash
pip install net2i
```
## Usage

Here’s a quick example of how to use **NeT2I**:



from net2i import converter

# Read and process CSV data
data = converter.csv_to_2Dlist("your_network_data.csv")
processed_data = converter.convert_to_integer(data)

# Convert to images
processed_data = converter.splitIP(processed_data)
rgb_data = converter.convertContentToRGB(processed_data)
converter.imagesCreatorForMultiLines(rgb_data)


# Requirements
- Python 3.8+
- NumPy
- Pillow

# License
This project is licensed under the MIT License. See the LICENSE file for details.

# Contributing
Contributions are welcome! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes.
4. Submit a pull request.
For major changes, please open an issue first to discuss what you'd like to change.

# Issues
If you encounter any issues or have suggestions for improvements, please file an issue on the Issues page.

# Authors
- Dr. Omesh Fernando - omeshf@gmail.com
- Dr. Sajid Fadlelseed - sajidqurashi1@gmail.com

# Links
- Homepage: https://github.com/omeshF/NeT2I
- Issues: https://github.com/omeshF/NeT2I/issues


