# Language Detection

A Docker image that detects the language of PDF documents or text using LangDetect. For PDF output, a **PDFix SDK** license is required.

## Table of Contents

- [Language Detection](#language-detection)
  - [Getting started](#getting-started)
  - [Usage](#usage)
  - [Commands](#commands)
  - [Arguments](#arguments)
  - [Params JSON](#params-json)
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
| `--params` | yes | Path to a `.json` file | Tag filter parameters (see [Params JSON](#params-json)) |
| `--overwrite` | no | Boolean string (default: `false`) | Overwrite already existing language on a tag |
| `--default-language` | no | Language code (default: `en`) | Language applied when detection fails (e.g. numbers only) |

### `set-content-language`

Uses the [Common (PDF commands)](#common-pdf-commands) arguments, plus:

| Option | Required | Type / expected value | Description |
|---|:---:|---|---|
| `--params` | yes | Path to a `.json` file | Object filter parameters (see [Params JSON](#params-json)) |
| `--overwrite` | no | Boolean string (default: `false`) | Overwrite already existing language on content |
| `--default-language` | no | Language code (default: `en`) | Language applied when detection fails (e.g. numbers only) |



### `detect_language`

| Option | Required | Type / expected value | Description |
|---|:---:|---|---|
| `--input`, `-i` | yes | Path to an existing `.txt` file, or a raw text string | Source text or file |
| `--output`, `-o` | yes | Path for output `.txt` file | Output file containing the detected language code |
| `--maxwords` | no | Integer (default: **100**) | How many words are considered for language detection |

## Params JSON

`--params` points to a JSON array of parameter objects. Each object has at least `name` and `value`; the CLI reads those fields to decide which tags or page objects to process.

### `set-tag-language` (`tag_names`)

`tag_names` is an ECMAScript regular expression matching tag names, or a template `tag_update` object.

Example (`tests/params_tag.json`) — match only `P` tags:

```json
[
    {
        "title": "Tags",
        "desc": "Specify the tags using a ECMAScript regular expression or define them by template tag_update",
        "name": "tag_names",
        "type": "tag",
        "value": "^P$",
        "values": [
            {
                "desc": "All tags",
                "value": ".*"
            }
        ]
    }
]
```

Use `"value": ".*"` to match all tags.

### `set-content-language` (`object_types`)

`object_types` is an ECMAScript regular expression matching page object types, or a template `object_update` object.

Example (`tests/params_content.json`) — match only text objects:

```json
[
    {
        "title": "Objects",
        "desc": "Define the objects by the template object_update",
        "name": "object_types",
        "type": "object",
        "value": "^pds_text$",
        "values": [
            {
                "desc": "All page objects",
                "value": ".*"
            }
        ]
    }
]
```

Use `"value": ".*"` to match all page objects.

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
  --input /data/input.pdf --output /data/output.pdf --maxwords 100 \
  --overwrite true --params /data/params_tag.json
```

Set detected language on PDF page content:

```bash
docker run --rm -v "$(pwd)":/data -w /data pdfix/detect-language:latest \
  set-content-language --name "${LICENSE_NAME}" --key "${LICENSE_KEY}" \
  --input /data/input.pdf --output /data/output.pdf --maxwords 100 \
  --overwrite true --params /data/params_content.json
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
