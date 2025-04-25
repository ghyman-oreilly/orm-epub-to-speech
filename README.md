# ORM EPUB to Speech Converter

Modified script based on Chris Bremseth's awesome [epub-to-speech script](https://github.com/cbremseth/epub-to-speech). 

This tool allows you to extract content from EPUB files and convert it to speech using OpenAI's Text-to-Speech API. This version has some modifications that make it suitable for the ORM/HTMLBook use case.

## Features

- Extract content and headers from EPUB files and save as Markdown
- Convert Markdown content to speech files using OpenAI's TTS API
- Process EPUBs to speech in a single command
- Customizable voice selection
- Support for large files by chunking them and then reassembling the resulting audio
- Suitable for HTMLBook specifically: Only chapter-level sections with specific data-types are retained ('chapter', 'preface', etc.)
- Headings after the first in a chapter are promoted, to keep chapter content together
- Support for OpenAI, Google Cloud, and Azure TTS services
- Support for limited Speech Markdown features and conversion to SSML (for use with Azure TTS service)

## Installation

### Requirements

- Python 3.7+
- OpenAI API key
- ffmpeg or libav (used by pydub to edit/combine the MP3s)

### Setup

1. Clone the repository or download the source files:

```bash
git clone https://github.com/cbremseth/epub-to-speech.git
cd epub-to-speech
```

2. Install required dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory to store the credentials for the TTS services you'll use, as applicable:

```bash
# OpenAI
echo "OPENAI_API_KEY=sk-your-api-key-here" >> .env
```

```bash
# Google
# 1. obtain and save key.json to project
# 2. then save path as an env variable:
echo "GOOGLE_APPLICATION_CREDENTIALS=/path/to/key_file" >> .env
```

```bash
# Azure
echo "SPEECH_KEY=your-key-here" >> .env
echo "SPEECH_REGION=your-region" >> .env
```

4. Install [ffmpeg](https://www.ffmpeg.org) or libav on your system. On mac, you can use brew to install ffmpeg:

```bash
brew install ffmpeg
```


## Usage

The tool provides a command-line interface with three main commands:

### 1. Extract content from an EPUB file

```bash
python main.py extract path/to/book.epub --output book.md
```

Options:
- `--output`, `-o`: Output markdown filename (default: same as input with .md extension)
- `--replace-stripped-elements-with-comments', '-c'`: When stripping out unwanted elements from the EPUB HTML (e.g., images, pre blocks, etc.), insert a comment where the elements have been removed. Default is to simply remove the elements.

### 2. Convert a Markdown file to speech

```bash
python main.py speak path/to/file.md --output-dir ./audio_files --voice nova
```

Options:
- `--output-dir`, `-o`: Directory for audio output files (default: ./audio_output)
- `--voice`, `-v`: Voice to use (OpenAI: alloy, echo, fable, onyx, nova, shimmer; Google: female, male; Azure: cora, adam, nancy, emma, jane, jason, davis, samuel)
- `--split-at-subheadings`, `-s`: Split audio files by subheadings (all H1 and H2) instead of the default of chapter-level audio files (H1)
- `--use-ssml`, `-u`: Convert chunked Markdown content to SSML before passing to TTS service. At this time, compatible with Azure service only. Limited Speech Markdown conventions supported.

### 3. Process an EPUB file to speech in one step

```bash
python main.py process path/to/book.epub --output-dir ./audio_files --voice alloy --keep-markdown
```

Options:
- `--output-dir`, `-o`: Directory for audio output files (default: ./audio_output)
- `--voice`, `-v`: Voice to use (options: alloy, echo, fable, onyx, nova, shimmer)
- `--keep-markdown`, `-k`: Keep the intermediate markdown file (default: removed after processing)
- `--split-at-subheadings`, `-s`: Split audio files by subheadings (all H1 and H2) instead of the default of chapter-level audio files (H1)

## Example

```bash
# Process "The Great Gatsby" to audio files with the "nova" voice
python main.py process books/great_gatsby.epub --output-dir ./gatsby_audio --voice nova --keep-markdown
```

## File Structure

- `main.py`: Command-line interface using Click
- `epub_processor.py`: EPUB to Markdown conversion functions
- `speech_generator.py`: Markdown to speech conversion using TTS service
- `audio_concatenator.py`: Combines audio files that represent parts of a section
- `speech_services.py`: Custom classes for the available TTS services
- `requirements.txt`: List of required Python packages

## Dependencies

- click: Command-line interface creation
- ebooklib: EPUB file processing
- beautifulsoup4: HTML parsing
- markdown: Markdown processing
- openai: OpenAI API client
- python-dotenv: Environment variable management
- markdown_to_ssml_converter: Markdown to SSML conversion, with limited support for Speech Markdown conventions
- ffmpeg or libav (non-python dependency): Crossplatform multimedia framework

## Limitations

- OpenAI's TTS API has a 4096 character limit per request, so long sections are split
- API rate limits may apply when processing large books
- Some EPUB formatting may not translate perfectly to Markdown

## Resources

* [IPA keyboard](https://www.internationalphoneticalphabet.org/html-ipa-keyboard-v1/keyboard/)
* [toPhonetics transcriber](https://tophonetics.com/)
* [Azure SSML overview](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-synthesis-markup)
* [Speech Markdown](https://www.speechmarkdown.org/)
