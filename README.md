# Language Detection

A Docker image that automatically detects the language of a PDF file. It uses a configuration file for customizable options and can be run with various command-line arguments.

## Table of Contents

- [Language Detection](#language-detection)
  - [Table of Contents](#table-of-contents)
  - [Getting Started](#getting-started)
  - [Run using Command Line Interface](#run-using-command-line-interface)
  - [Exporting Configuration for Integration](#exporting-configuration-for-integration)
  - [License](#license)
  - [Help \& Support](#help--support)

## Getting Started

To use this Docker application, you'll need to have Docker installed on your system. If Docker is not installed, please follow the instructions on the [official Docker website](https://docs.docker.com/get-docker/) to install it.


## Run using Command Line Interface

To run docker container as CLI you should share the folder with PDF to process using `-i` parameter. In this example it's current folder.

```bash
docker run -v $(pwd):/data -w /data --rm pdfix/detect-language:latest lang-detect -i input.pdf -o output.pdf
```

Just detect language and save language code to txt file
```bash
docker run -v $(pwd):/data -w /data --rm pdfix/detect-language:latest lang-detect -i input.pdf -o output.txt
```
With PDFix License add these arguments. 
```bash
--name ${LICENSE_NAME} --key ${LICENSE_KEY}
```
Contact support for more information.

The first run will pull the docker image, which may take some time. Make your own image for more advanced use.

For more detailed information about the available command-line arguments, you can run the following command:

```bash
docker run --rm pdfix/detect-language:latest --help
```

## Exporting Configuration for Integration
To export the configuration JSON file, use the following command:
```bash
docker run -v $(pwd):/data -w /data --rm pdfix/detect-language:latest config -o config.json
```

## License
- PDFix license https://pdfix.net/terms

The trial version of the PDFix SDK may apply a watermark on the page and redact random parts of the PDF including the scanned image in the background. Contact us to get an evaluation or production license.

## Help & Support
To obtain a PDFix SDK license or report an issue please contact us at support@pdfix.net.
For more information visit https://pdfix.net
