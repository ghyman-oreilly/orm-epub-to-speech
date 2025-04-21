import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup, Comment
import re
from markdownify import markdownify as md


def extract_epub_to_markdown(epub_path, output_file, replace_stripped_elements_with_comments=False):
    """
    Process an EPUB file, extract content and headers, and save as markdown.
    Removes formatting elements like bold, italics, code blocks, figures, and tables.

    Args:
        epub_path: Path to the EPUB file
        output_file: Path to save the markdown output
        replace_stripped_elements_with_comments: if True, replace stripped elements with a comment

    Returns:
        str: Path to the created markdown file
    """
    try:
        # Read the EPUB file
        book = epub.read_epub(epub_path, {"ignore_ncx": True})
        spine = book.spine # List of (idref, properties), indicating the correct order of epub contents 

        # Start building markdown content
        markdown_content = []

        # Process each document in the EPUB
        for idref, _ in spine:
            item = book.get_item_with_id(idref)
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                # Get content as bytes and decode to string
                html_content = item.get_content().decode('utf-8')

                # Parse HTML with BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')

                # section classes to retain
                chapter_level_section_classes = ['afterword', 'appendix', 'chapter', 'colophon','conclusion', 'foreword', 'introduction', 'part', 'preface', 'titlepage']

                # skip any chapter-level sections that we don't want to keep
                try:
                    if not soup.select('section, div')[0].get('data-type') in chapter_level_section_classes:
                        continue
                except:
                    continue

                first_h1_found = False

                # promote all headings but the first (chapter title)
                for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    level = int(tag.name[1])

                    if tag.name == "h1" and not first_h1_found:
                        first_h1_found = True
                        continue  # Leave the first h1 untouched

                    if level < 6:
                        tag.name = f"h{level + 1}"  # Promote to the next level

                comment_placeholders = []

                # Remove unwanted elements
                for i, element in enumerate(soup(['script', 'style', 'table', 'figure', 'figcaption', 'pre'])):
                    if replace_stripped_elements_with_comments:
                        # replace with comment placeholder
                        placeholder = f"HTML-COMMENT-{i}"
                        comment = f"{element}"
                        comment_placeholders.append((placeholder, comment))
                        element.replace_with(placeholder)
                    else:
                        # simply remove
                        element.decompose()

                # Remove footnotes
                for element in soup.select('p[data-type="footnote"], a[data-type="noteref"]'):
                    element.decompose()

                # Remove formatting tags but keep their content
                for tag in soup.find_all(['strong', 'b', 'em', 'i', 'code']):
                    tag.replace_with(tag.get_text())

                # Get body element from the soup
                body = soup.body

                # Convert the HTML to markdown using markdownify library
                # Configure markdownify to skip certain conversions
                markdown_section = md(
                    str(body),
                    heading_style="ATX",
                    strip=['a', 'img', 'pre',
                            'table', 'tr', 'td', 'th', 'blockquote']
                )

                if replace_stripped_elements_with_comments:
                    # replace placeholder with intended comment
                    for placeholder, comment_text in comment_placeholders:
                        markdown_section = markdown_section.replace(placeholder, f"<!--{comment_text}-->")

                # Ensure proper spacing between sections
                markdown_content.append(f"\n{markdown_section}\n\n")
        
        # Clean up excessive newlines and spaces
        final_content = re.sub(r'\n{3,}', '\n\n', ''.join(markdown_content))

        # Add period to the end of headings that don't end with one
        # (to ensure model pause between heading and successive text)
        final_content = re.sub(r'^([#]+.*?[^\.])$', r'\1.', final_content, flags=re.MULTILINE)

        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_content)

        return output_file

    except Exception as e:
        return f"Error processing EPUB: {str(e)}"