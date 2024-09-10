# PDF Language Detection Docker App

This Docker application is designed to automatically detect the language of a PDF file. It utilizes a configuration file for customizable options and can be executed through various command-line arguments.

## Table of Contents

- [PDF Language Detection Docker App](#pdf-language-detection-docker-app)
  - [Table of Contents](#table-of-contents)
  - [Getting Started](#getting-started)
  - [Running the Language Detection](#running-the-language-detection)
    - [Running with PDFix license](#running-with-pdfix-license)
    - [Exporting Configuration for Integration](#exporting-configuration-for-integration)
  - [License](#license)

## Getting Started

To use this Docker application, you'll need to have Docker installed on your system. If Docker is not installed, please follow the instructions on the [official Docker website](https://docs.docker.com/get-docker/) to install it.


## Running the Language Detection

To run the language detection on a PDF file with the following command:
```bash
docker run -v <local_dir>:/data/ --rm pdfix/lang-detect:latest -i /data/<example.pdf> -o /data/out.pdf
```

Just detect language and save language code to txt file
```bash
docker run -v <local_dir>:/data/ --rm pdfix/lang-detect:latest -i /data/<example.pdf> -o /data/out.txt
```

- __local_dir__ is a folder shared with docker container where the PDF file is and will be saved

For more detailed information about the available command-line arguments, you can run the following command:

```bash
docker run --rm pdfix/lang-detect:latest --help
```

### Running with PDFix license

Add arguments
```
--name <license_name> --key <license_key>
```

### Exporting Configuration for Integration
To export the configuration file, use the following command:
```bash
docker run -v <local_dir>:/data/ --rm pdfix/lang-detect:latest --config /data/
```

## License
- PDFix license https://pdfix.net/terms
- Contact us for purchasing a license 