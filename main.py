import click
import os
from epub_processor import extract_epub_to_markdown
from speech_generator import convert_markdown_to_speech


@click.group()
def cli():
    """EPUB Processing and Text-to-Speech Conversion Tool."""
    pass


@cli.command()
@click.argument('epub_file', type=click.Path(exists=True))
@click.option('--output', '-o', default=None, help='Output markdown filename')
def extract(epub_file, output):
    """Extract content from an EPUB file and save as markdown."""
    if output is None:
        # Use the EPUB filename but with .md extension
        output = os.path.splitext(os.path.basename(epub_file))[0] + '.md'

    click.echo(f"Extracting content from {epub_file} to {output}...")
    result = extract_epub_to_markdown(epub_file, output)
    click.echo(f"Extraction complete: {result}")


@cli.command()
@click.argument('markdown_file', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='./audio_output', help='Output directory for audio files')
@click.option('--voice', '-v', default='alloy', help='Voice to use (alloy, echo, fable, onyx, nova, shimmer)')
def speak(markdown_file, output_dir, voice):
    """Convert markdown content to speech using OpenAI's Text-to-Speech."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        click.echo(f"Created output directory: {output_dir}")

    click.echo(
        f"Converting {markdown_file} to speech using voice '{voice}'...")
    result = convert_markdown_to_speech(markdown_file, output_dir, voice)
    click.echo(f"Speech conversion complete: {result}")


@cli.command()
@click.argument('epub_file', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='./audio_output', help='Output directory for audio files')
@click.option('--voice', '-v', default='alloy', help='Voice to use (alloy, echo, fable, onyx, nova, shimmer)')
@click.option('--keep-markdown', '-k', is_flag=True, help='Keep the intermediate markdown file')
def process(epub_file, output_dir, voice, keep_markdown):
    """Process an EPUB file to extract content and convert to speech in one step."""
    # Generate temporary markdown filename
    md_filename = os.path.splitext(os.path.basename(epub_file))[0] + '.md'

    click.echo(f"Processing {epub_file}...")

    # Extract EPUB to markdown
    extract_result = extract_epub_to_markdown(epub_file, md_filename)
    click.echo(f"Extraction complete: {extract_result}")

    # Convert markdown to speech
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    speech_result = convert_markdown_to_speech(md_filename, output_dir, voice)
    click.echo(f"Speech conversion complete: {speech_result}")

    # Remove markdown file if not keeping it
    if not keep_markdown and os.path.exists(md_filename):
        os.remove(md_filename)
        click.echo(f"Removed intermediate markdown file: {md_filename}")


if __name__ == '__main__':
    cli()
