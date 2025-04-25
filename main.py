import click
import os
import shutil
import time
import warnings
from audio_concatenator import merge_audio_files
from epub_processor import extract_epub_to_markdown
from speech_generator import generate_speech_from_markdown

# filter FutureWarnings from ebooklib\epub
# warning that prompted adding the filter: ebooklib/epub.py:1423: FutureWarning: This search incorrectly ignores the root element, and will be fixed in a future version.  If you rely on the current behaviour, change it to './/xmlns:rootfile[@media-type]'
warnings.filterwarnings("ignore", category=FutureWarning, module=r"^ebooklib\.epub$")


@click.group()
def cli():
    """EPUB Processing and Text-to-Speech Conversion Tool."""
    pass


@cli.command()
@click.argument('epub_file', type=click.Path(exists=True))
@click.option('--output', '-o', default=None, help='Output markdown filename')
@click.option('--replace-stripped-elements-with-comments', '-c', is_flag=True, help='When stripping out unwanted elements from the EPUB HTML (e.g., images, pre blocks, etc.), insert a comment where the elements have been removed.')
def extract(epub_file, output, replace_stripped_elements_with_comments):
    """Extract content from an EPUB file and save as markdown."""
    if output is None:
        # Use the EPUB filename but with .md extension
        output = os.path.splitext(os.path.basename(epub_file))[0] + '.md'

    click.echo(f"Extracting content from {epub_file} to {output}...")
    result = extract_epub_to_markdown(epub_file, output, replace_stripped_elements_with_comments)
    
    if replace_stripped_elements_with_comments:
        click.echo("IMPORTANT: Stripped elements converted to comments in the markdown. Please review and remove, as needed, before converting to audio.")
    
    click.echo(f"Extraction complete: {result}")


@cli.command()
@click.argument('markdown_file', type=click.Path(exists=True))
@click.option('--service', type=click.Choice(['openai', 'google', 'azure']), default='openai', help='Choose between OpenAI or Google TTS services (default: OpenAI)')
@click.option('--output-dir', '-o', default='./audio_output', help='Output directory for audio files')
@click.option('--voice', '-v', default=None, help='Voice to use (OpenAI: alloy, echo, fable, onyx, nova, shimmer; Google: female, male; Azure: cora, adam, nancy, emma, jane, jason, davis, samuel)')
@click.option('--split-at-subheadings', '-s', is_flag=True, help='Split audio content at H1 and H2 heading levels. If you do not pass this flag, content is split at H1 (chapter) level only.')
@click.option('--use-ssml', '-u', is_flag=True, help='Convert chunked Markdown content to SSML before passing to TTS service. Compatible with Azure service only. Limited Speech Markdown conventions supported.')
def speak(markdown_file, service, output_dir, voice, split_at_subheadings, use_ssml):
    """Convert markdown content to speech using a text-to-speech service."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        click.echo(f"Created output directory: {output_dir}")

    # Create temporary directory
    temp_dir = os.path.join(output_dir, f"temp_{int(time.time())}")
    os.makedirs(temp_dir, exist_ok=True)

    service = service.lower()

    SERVICES = ['openai', 'google']
    OPENAI_VOICES = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
    GOOGLE_VOICES_MAPPING = {
        "female": "en-US-Studio-O",
        "male": "en-US-Studio-Q"
    }
    GOOGLE_VOICES = [k for k, _ in GOOGLE_VOICES_MAPPING.items()]
    AZURE_VOICES_MAPPING = {
        "cora": "en-US-CoraMultilingualNeural",
        "adam": "en-US-AdamMultilingualNeural",
        "nancy": "en-US-LewisMultilingualNeural",
        "emma": "en-US-EmmaMultilingualNeural",
        "jane": "en-US-JaneNeural",
        "jason": "en-US-JasonNeural",
        "davis": "en-US-DavisMultilingualNeural",
        "samuel": "en-US-SamuelMultilingualNeural"
    }
    AZURE_VOICES = [k for k, _ in AZURE_VOICES_MAPPING.items()]
    OPENAI_DEFAULT_VOICE = 'alloy'
    GOOGLE_DEFAULT_VOICE = 'en-US-Studio-O'
    AZURE_DEFAULT_VOICE = 'en-US-SamuelMultilingualNeural'

    if service == 'openai':
        valid_voices = OPENAI_VOICES
    elif service == 'google':
        valid_voices = GOOGLE_VOICES
    elif service == 'azure':
        valid_voices = AZURE_VOICES
    else:
        # invalid service
        raise click.BadParameter(
                f'Invalid service "{service}".'
                f'Valid options are: {", ".join(SERVICES)}'
            )

    if voice is not None:
        if voice not in valid_voices:
            raise click.BadParameter(
                f'Invalid voice "{voice}" for service "{service}". '
                f'Valid options are: {", ".join(valid_voices)}'
            )
        elif service == 'google':
            # look up actual voice name from menu option
            voice = GOOGLE_VOICES_MAPPING.get(voice, GOOGLE_DEFAULT_VOICE)
        elif service == 'azure':
            # look up actual voice name from menu option
            voice = AZURE_VOICES_MAPPING.get(voice, AZURE_DEFAULT_VOICE)
    elif service == 'openai':
        # default openai voice
        voice = OPENAI_DEFAULT_VOICE
    elif service == 'google':
        # default google voice
        voice = GOOGLE_DEFAULT_VOICE
    else:
        # default azure voice
        voice = AZURE_DEFAULT_VOICE

    modifier = ''

    if service == 'google':
        modifier = ' (' + next((k for k, v in GOOGLE_VOICES_MAPPING.items() if v == voice), '') + ')'
    elif service == 'azure':
        modifier = ' (' + next((k for k, v in AZURE_VOICES_MAPPING.items() if v == voice), '') + ')'

    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    instructions = """
    Do not read aloud any of the following characters: #, *, _, ®
    Do not read aloud a backslash if it immediately precedes any of the following characters: #, *, _
    Do not read aloud any HTML comments (wrapped in <!-- and -->).
    When a line begins with a number and a period (e.g., 1., 10., etc.), make sure to read the number aloud.
    """

    click.echo(
        f"Converting {markdown_file} to speech using voice '{voice}'{modifier}...")
    chunked_audio = generate_speech_from_markdown(markdown_content, temp_dir, service, voice, split_at_subheadings, instructions, use_ssml)
    
    click.echo("Merging and saving final audio files...")
    merged_audio = merge_audio_files(chunked_audio, output_dir, temp_dir)

    shutil.rmtree(temp_dir)

    click.echo(f"Audio files saved:")
    for filepath in merged_audio: 
        click.echo(filepath)
    click.echo(f"Speech conversion complete.")


@cli.command()
@click.argument('epub_file', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='./audio_output', help='Output directory for audio files')
@click.option('--voice', '-v', default='alloy', help='Voice to use (alloy, echo, fable, onyx, nova, shimmer)')
@click.option('--keep-markdown', '-k', is_flag=True, help='Keep the intermediate markdown file')
@click.option('--split-at-subheadings', '-s', is_flag=True, help='Split audio content at H1 and H2 heading levels. If you do not pass this flag, content is split at H1 (chapter) level only.')
def process(epub_file, output_dir, voice, keep_markdown, split_at_subheadings):
    """Process an EPUB file to extract content and convert to speech in one step."""
    # Generate temporary markdown filename
    md_filename = os.path.splitext(os.path.basename(epub_file))[0] + '.md'

    click.echo(f"Processing {epub_file}...")

    # Extract EPUB to markdown
    extract_result = extract_epub_to_markdown(epub_file, md_filename)
    click.echo(f"Extraction complete: {extract_result}")

    # Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create temporary directory
    temp_dir = os.path.join(output_dir, f"temp_{int(time.time())}")
    os.makedirs(temp_dir, exist_ok=True)

    chunked_audio = generate_speech_from_markdown(md_filename, temp_dir, voice, split_at_subheadings)

    click.echo("Merging and saving final audio files...")
    merged_audio = merge_audio_files(chunked_audio, output_dir, temp_dir)

    shutil.rmtree(temp_dir)

    click.echo(f"Audio files saved:")
    for filepath in merged_audio: 
        click.echo(filepath)
    click.echo(f"Speech conversion complete.")

    # Remove markdown file if not keeping it
    if not keep_markdown and os.path.exists(md_filename):
        os.remove(md_filename)
        click.echo(f"Removed intermediate markdown file: {md_filename}")


if __name__ == '__main__':
    cli()
