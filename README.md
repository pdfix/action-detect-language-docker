# Language Detection

A Docker image that detects the language of a PDF or text and writes the result to a TXT file or sets language on a PDF output.

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

- `lang-detect`: Detect language from PDF, TXT, inline text, or text string → output PDF or TXT

## Arguments

### `lang-detect`

Supported combinations: PDF → PDF, PDF → TXT, TXT → TXT, or free text → TXT.

| Option | Required | Type / expected value | Description |
|---|:---:|---|---|
| `--input`, `-i` | yes | Path to an existing `.pdf` or `.txt` file, or a raw text string | Source text or file |
| `--output`, `-o` | yes | Path for output `.pdf` or `.txt` (must match the chosen mode) | Output file |
| `--name` | no | String (PDFix account license name); required for **PDF → PDF** | PDFix license name |
| `--key` | no | String (PDFix account license key); required for **PDF → PDF** | PDFix license key |

## Examples

Detect language and write a language code to `output.txt`:

```bash
docker run --rm -v "$(pwd)":/data -w /data pdfix/detect-language:latest \
  lang-detect -i /data/input.pdf -o /data/output.txt
```

Set detected language on an output PDF (requires PDFix license for PDF output):

```bash
docker run --rm -v "$(pwd)":/data -w /data pdfix/detect-language:latest \
  lang-detect --name "${LICENSE_NAME}" --key "${LICENSE_KEY}" \
  -i /data/input.pdf -o /data/output.pdf
```

## Help & support

For PDFix SDK licensing or issues, contact `support@pdfix.net`.

## Licenses

- [PDFix Terms](https://pdfix.net/terms)

Trial versions of the PDFix SDK may apply watermarks and redact random content in the output PDF.
