# PDF Language Detection Docker App

This Docker application is designed to automatically detect the language of a PDF file. It utilizes a configuration file for customizable options and can be executed through various command-line arguments.

## Table of Contents

- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Exporting Configuration](#exporting-configuration)
  - [Running the Language Detection](#running-the-language-detection)
- [CLI Arguments](#cli-arguments)
- [License](#license)

## Getting Started

To use this Docker application, you'll need to have Docker installed on your system. If Docker is not installed, please follow the instructions on the [official Docker website](https://docs.docker.com/get-docker/) to install it.

## Usage
### Exporting Configuration
To export the configuration file, use the following command:
```bash
docker run -v <local_dir>:/data/ --rm pdfix/lang-detect:latest --config /data/
```

### Running the Language Detection
To run the language detection process on a PDF file with the following command:
```bash
docker run -v <local_dir>:/data/ --rm pdfix/lang-detect:latest -i /data/<example.pdf> -o /data/out.pdf
```

### CLI Arguments
For more detailed information about the available command-line arguments, you can run the following command:

```bash
docker run --rm pdfix/lang-detect:latest --help
```

## License
