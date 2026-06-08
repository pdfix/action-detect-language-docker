# Language Detection

A Docker image that detects the language of PDF documents or text using LangDetect. For PDF output, a **PDFix SDK** license is required.

## Table of Contents

- [Language Detection](#language-detection)
  - [Getting started](#getting-started)
  - [Usage](#usage)
  - [Commands](#commands)
  - [Arguments](#arguments)
  - [Examples](#examples)
  - [Help \& support](#help--support)
  - [Licenses](#licenses)

## Getting started

You need Docker installed. The first run downloads the image and may take longer than later runs.

## Usage

Mount a folder into the container and run a subcommand:

```bash
docker run --rm -v "$(pwd)":/data -w /data pdfix/detect-language:latest <command> [options]
```

## Commands

- `set-document-language`: Detect language from a PDF and set it in document metadata (PDF → PDF)
- `set-tag-language`: Detect language for filtered tags and save it on each tag (PDF → PDF)
- `set-content-language`: Detect language for filtered page content and save it as marked content (PDF → PDF)
- `detect_language`: Detect language from a TXT file or raw text string and write the language code to a TXT file (TXT → TXT; text → TXT)

## Arguments

### Common (PDF commands)

| Option | Required | Type / expected value | Description |
|---|:---:|---|---|
| `--input`, `-i` | yes | Path to an existing `.pdf` file | Input PDF |
| `--output`, `-o` | yes | Path for output `.pdf` file | Output PDF |
| `--name` | no | String (PDFix account license name) | PDFix license name |
| `--key` | no | String (PDFix account license key) | PDFix license key |
| `--maxwords` | no | Integer (default: **100**) | How many words are considered for language detection |

### `set-document-language`

Uses the [Common (PDF commands)](#common-pdf-commands) arguments.

### `set-tag-language`

Uses the [Common (PDF commands)](#common-pdf-commands) arguments, plus:

| Option | Required | Type / expected value | Description |
|---|:---:|---|---|
| `--overwrite` | no | Boolean string (default: `false`) | Overwrite already existing language on a tag |

### `set-content-language`

Uses the [Common (PDF commands)](#common-pdf-commands) arguments, plus:

| Option | Required | Type / expected value | Description |
|---|:---:|---|---|
| `--overwrite` | no | Boolean string (default: `false`) | Overwrite already existing language on content |

### `detect_language`

| Option | Required | Type / expected value | Description |
|---|:---:|---|---|
| `--input`, `-i` | yes | Path to an existing `.txt` file, or a raw text string | Source text or file |
| `--output`, `-o` | yes | Path for output `.txt` file | Output file containing the detected language code |
| `--maxwords` | no | Integer (default: **100**) | How many words are considered for language detection |

## Examples

Set detected language in PDF document metadata:

```bash
docker run --rm -v "$(pwd)":/data -w /data pdfix/detect-language:latest \
  set-document-language --name "${LICENSE_NAME}" --key "${LICENSE_KEY}" \
  --input /data/input.pdf --output /data/output.pdf --maxwords 100
```

Set detected language on PDF tags:

```bash
docker run --rm -v "$(pwd)":/data -w /data pdfix/detect-language:latest \
  set-tag-language --name "${LICENSE_NAME}" --key "${LICENSE_KEY}" \
  --input /data/input.pdf --output /data/output.pdf --maxwords 100 --overwrite true
```

Set detected language on PDF page content:

```bash
docker run --rm -v "$(pwd)":/data -w /data pdfix/detect-language:latest \
  set-content-language --name "${LICENSE_NAME}" --key "${LICENSE_KEY}" \
  --input /data/input.pdf --output /data/output.pdf --maxwords 100 --overwrite true
```

Detect language from a text file and write the language code to `output.txt`:

```bash
docker run --rm -v "$(pwd)":/data -w /data pdfix/detect-language:latest \
  detect_language --input /data/input.txt --output /data/output.txt --maxwords 100
```

## Help & support

For PDFix SDK licensing or issues, contact `support@pdfix.net`.

## Licenses

- [PDFix Terms](https://pdfix.net/terms)

Trial versions of the PDFix SDK may apply watermarks and redact random content in the output PDF.
