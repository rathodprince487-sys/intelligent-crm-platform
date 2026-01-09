#!/bin/bash
# Convert Markdown to Word using textutil (macOS built-in)

echo "Converting PROJECT_PROPOSAL.md to Word format..."

# First convert to HTML
cat PROJECT_PROPOSAL.md | python3 -c "
import markdown
import sys

md_content = sys.stdin.read()
html = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'toc'])

# Add styling
styled_html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset=\"UTF-8\">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{
            color: #2563eb;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #1e40af;
            border-bottom: 2px solid #93c5fd;
            padding-bottom: 5px;
            margin-top: 30px;
        }}
        h3 {{
            color: #1e3a8a;
            margin-top: 20px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th {{
            background-color: #2563eb;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            border: 1px solid #ddd;
            padding: 10px;
        }}
        tr:nth-child(even) {{
            background-color: #f9fafb;
        }}
        code {{
            background-color: #f1f5f9;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
        }}
        pre {{
            background-color: #1e293b;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        blockquote {{
            border-left: 4px solid #2563eb;
            padding-left: 20px;
            margin-left: 0;
            color: #64748b;
        }}
    </style>
</head>
<body>
{html}
</body>
</html>
'''
print(styled_html)
" > PROJECT_PROPOSAL.html

# Convert HTML to RTF (which Word can open)
textutil -convert rtf PROJECT_PROPOSAL.html -output PROJECT_PROPOSAL.rtf

# Try to convert to docx if possible
if command -v pandoc &> /dev/null; then
    pandoc PROJECT_PROPOSAL.md -o PROJECT_PROPOSAL.docx
    echo "✅ Created PROJECT_PROPOSAL.docx (using pandoc)"
else
    echo "✅ Created PROJECT_PROPOSAL.rtf (open in Word and save as .docx)"
fi

echo "✅ Created PROJECT_PROPOSAL.html"
echo ""
echo "Files created:"
ls -lh PROJECT_PROPOSAL.* | grep -E '\.(html|rtf|docx)$'
