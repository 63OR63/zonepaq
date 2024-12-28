import re
from pathlib import Path

# Define the working directory
WORKING_DIR = Path(__file__).resolve().parent.parent


def markdown_to_bbcode(markdown_text):
    # Convert headers
    bbcode_text = re.sub(
        r"^# (.+)$", r"[size=6][b]\1[/b][/size]", markdown_text, flags=re.MULTILINE
    )
    bbcode_text = re.sub(
        r"^## (.+)$", r"[size=5][b]\1[/b][/size]", bbcode_text, flags=re.MULTILINE
    )
    bbcode_text = re.sub(
        r"^### (.+)$", r"[size=4][b]\1[/b][/size]", bbcode_text, flags=re.MULTILINE
    )
    bbcode_text = re.sub(
        r"^#### (.+)$", r"[size=3][b]\1[/b][/size]", bbcode_text, flags=re.MULTILINE
    )

    # Convert links
    bbcode_text = re.sub(r"\[(.*?)\]\((.*?)\)", r"[url=\2]\1[/url]", bbcode_text)

    # Convert bold and italic text
    bbcode_text = re.sub(r"\*\*(.*?)\*\*", r"[b]\1[/b]", bbcode_text)
    bbcode_text = re.sub(r"\*(.*?)\*", r"[i]\1[/i]", bbcode_text)

    # Convert list items with headers
    def convert_list_with_headers(match):
        item = match.group(0).strip()
        header_match = re.match(r"^- (#+) (.+)$", item)
        if header_match:
            header_level = len(header_match.group(1))
            header_text = header_match.group(2)
            size = 7 - header_level  # Adjust size based on header level
            return f"[list]\n[*][size={size}][b]{header_text}[/b][/size]\n[/list]"
        return item

    bbcode_text = re.sub(
        r"^- (#+) .+$", convert_list_with_headers, bbcode_text, flags=re.MULTILINE
    )

    # Convert unordered lists
    def convert_unordered_list(match):
        items = match.group(0).strip().split("\n")
        return "[list]" + "".join(f"\n[*]{item[2:]}" for item in items) + "\n[/list]"

    bbcode_text = re.sub(
        r"(?:^- .+\n)+", convert_unordered_list, bbcode_text, flags=re.MULTILINE
    )

    # Convert ordered lists
    def convert_ordered_list(match):
        lines = match.group(0).strip().split("\n")
        bbcode_list = "[list=1]"
        for line in lines:
            if re.match(r"^\d+\. .+", line):  # If it's a numbered item
                content = line.split(".", 1)[1].strip()
                bbcode_list += f"\n[*]{content}"
            elif re.match(r"^\s{4,}```", line):  # If it's a code block start
                bbcode_list += f"\n[code]{line.strip()}"
            else:
                bbcode_list += f"\n{line.strip()}"
        bbcode_list += "\n[/list]"
        return bbcode_list

    bbcode_text = re.sub(
        r"(?:^\d+\. .+(\n\s{4,}.+)*\n*)+",
        convert_ordered_list,
        bbcode_text,
        flags=re.MULTILINE,
    )

    # Convert code blocks
    bbcode_text = re.sub(
        # r"```[a-zA-Z]*\n([\s\S]*?)```",
        r"```[a-zA-Z]*\n\s*([\s\S]*?)\s*?```",
        r"[code]\1[/code]",
        bbcode_text,
        flags=re.MULTILINE,
    )

    # Convert inline code
    bbcode_text = re.sub(r"`([^`]+)`", r"[code]\1[/code]", bbcode_text)

    # Convert images
    bbcode_text = re.sub(r"!\[(.*?)\]\((.*?)\)", r"[img]\2[/img]", bbcode_text)

    # Ensure headers and lists have blank lines
    # bbcode_text = re.sub(r"(\[/list\])\n(\[size=)", r"\1\n\n\2", bbcode_text)
    # bbcode_text = re.sub(r"(\[/size\]\[/b\])\n(\[list)", r"\1\n\n\2", bbcode_text)

    # bbcode_text = re.sub(r"(\[/list\])(\[size=)", r"\1\n\n\2", bbcode_text)

    bbcode_text = re.sub(r"(\[/list\])\s*(\S)", r"\1\n\2", bbcode_text)
    bbcode_text = re.sub(r"(list\])\s*(\[size)", r"\1\n\n\2", bbcode_text)

    return bbcode_text


# Define input and output files
input_file = WORKING_DIR / "README.md"
output_file = WORKING_DIR / "README.bbcode"

# Read the Markdown file
with open(input_file, "r", encoding="utf-8") as md_file:
    markdown_content = md_file.read()

# Convert Markdown to BBCode
bbcode_content = markdown_to_bbcode(markdown_content)

# Save the BBCode to a file
with open(output_file, "w", encoding="utf-8") as bbcode_file:
    bbcode_file.write(bbcode_content)

print(f"Converted {input_file} to {output_file} successfully!")
