# Slides to PNG Converter - Usage Guide

## Overview

Convert presentation slides to high-quality PNG images optimized for AI vision inspection. This tool enables Claude (or other AI assistants) to **visually inspect** presentations it creates, allowing for self-evaluation and iterative improvement.

## Why This Approach?

**PDF Intermediate = Best Quality for AI Vision**

1. **LibreOffice's PDF renderer is its best output** - same quality humans see
2. **Guarantees visual fidelity** - "what you see is what Claude sees"
3. **Sharp text for AI OCR** - PNG preserves crisp edges
4. **High DPI options** - readable text even for small fonts

Unlike `libreoffice --convert-to png` (which only exports the first slide), this tool:
- ✅ Exports **all slides** as individual PNG files
- ✅ Uses LibreOffice's **best rendering path** (PDF export)
- ✅ Produces **AI-vision-optimized** images
- ✅ Supports configurable DPI and naming

## Installation

### 1. Install Python Dependencies

```bash
# Using UV (recommended)
uv sync

# Or using pip
pip install pdf2image
```

### 2. Install System Dependencies

The tool requires `poppler-utils` for PDF processing:

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils
```

**macOS:**
```bash
brew install poppler
```

**Windows:**
Download from: https://github.com/oschwartz10612/poppler-windows/releases/

## Usage

### Basic Usage

```python
from libremcp import convert_presentation_to_png

# Convert slides to PNG
result = convert_presentation_to_png(
    presentation_path="/path/to/presentation.odp",
    output_dir="/tmp/slides"
)

if result.success:
    print(f"✅ Exported {result.slide_count} slides")
    for slide_file in result.slide_files:
        print(f"   - {slide_file}")
else:
    print(f"❌ Error: {result.error_message}")
```

### Custom DPI (Quality Settings)

```python
# Low quality (web thumbnails)
result = convert_presentation_to_png(
    presentation_path="slides.pptx",
    output_dir="/tmp/thumbs",
    dpi=150  # ~500KB per slide
)

# Medium quality (recommended for AI vision)
result = convert_presentation_to_png(
    presentation_path="slides.pptx",
    output_dir="/tmp/slides",
    dpi=200  # ~800KB per slide (DEFAULT)
)

# High quality (detailed graphics)
result = convert_presentation_to_png(
    presentation_path="slides.pptx",
    output_dir="/tmp/high_quality",
    dpi=300  # ~1.5MB per slide
)
```

### Custom Naming Pattern

```python
# Custom filename pattern
result = convert_presentation_to_png(
    presentation_path="presentation.odp",
    output_dir="/output",
    naming_pattern="page_{index:04d}.png"
)
# Creates: page_0001.png, page_0002.png, ...

# Short names
result = convert_presentation_to_png(
    presentation_path="presentation.odp",
    output_dir="/output",
    naming_pattern="s{index}.png"
)
# Creates: s1.png, s2.png, s3.png, ...
```

## MCP Tool Usage

When using via MCP protocol (Claude Desktop, Super Assistant, etc.):

```
User: "Create a 5-slide presentation about Python programming"

Claude: [creates presentation.odp]

User: "Convert it to PNG so you can review the design quality"

Claude: [uses convert_presentation_to_png tool]
        [reads the PNG files using vision capabilities]

        "I've created and reviewed the slides. Here's my assessment:

        Slide 1: Title slide looks good, font is readable
        Slide 2: Code example needs better syntax highlighting
        Slide 3: The diagram is clear but could use more contrast
        ...

        Would you like me to make these improvements?"
```

## Claude Self-Evaluation Workflow

This is the killer feature - Claude can review its own work:

### 1. Create Presentation
```
User: "Create a presentation about renewable energy"
Claude: [creates slides.odp]
```

### 2. Convert to PNG
```
User: "Show me what it looks like"
Claude: [uses convert_presentation_to_png]
        [reads PNG files with vision]
```

### 3. Self-Evaluate
```
Claude: "I've reviewed the slides. Here's what I see:

        ✅ Good: Clear hierarchy, readable fonts, consistent colors
        ⚠️  Issues found:
        - Slide 3: Text is too small (8pt font detected)
        - Slide 5: Chart colors have poor contrast
        - Slide 7: Image is pixelated

        Would you like me to fix these issues?"
```

### 4. Iterative Improvement
```
User: "Yes, fix them"
Claude: [modifies presentation]
        [re-converts to PNG]
        [verifies improvements]

        "✅ Fixed all issues:
        - Increased font to 14pt
        - Improved chart contrast
        - Replaced image with higher resolution version

        The presentation now meets accessibility standards."
```

## Supported Formats

### Input Formats
- ✅ LibreOffice Impress (`.odp`)
- ✅ PowerPoint (`.pptx`, `.ppt`)
- ✅ OpenOffice Impress (`.sxi`)
- ✅ Any format LibreOffice can open

### Output Format
- PNG (lossless, optimized for text and graphics)

## DPI Selection Guide

| DPI | Use Case | File Size | Text Quality |
|-----|----------|-----------|--------------|
| 72-96 | Web thumbnails | ~300KB | Readable for large text |
| 150 | Quick preview | ~500KB | Good for most text |
| **200** | **AI vision (default)** | **~800KB** | **Sharp, clear text** |
| 300 | High detail | ~1.5MB | Perfect for small fonts |
| 600 | Print quality | ~5MB | Overkill for screen use |

**Recommendation:** Use 200 DPI (default) for AI vision - it provides sharp, readable text without excessive file sizes.

## File Size Estimation

Approximate file sizes per slide (actual sizes vary by content):

```python
# For a 20-slide presentation at 200 DPI:
# ~800KB × 20 slides = ~16MB total

# Quick estimate:
slides = 20
dpi = 200
size_per_slide = 0.8  # MB at 200 DPI
total_size = slides * size_per_slide
print(f"Estimated size: {total_size:.1f} MB")
```

## Troubleshooting

### Error: "pdf2image library not installed"
```bash
pip install pdf2image
# or
uv sync
```

### Error: "Unable to get page count. Is poppler installed?"
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler

# Windows
# Download from: https://github.com/oschwartz10612/poppler-windows/releases/
```

### Error: "LibreOffice conversion failed"
- Ensure LibreOffice is installed and in PATH
- Try running: `libreoffice --version`
- Check presentation file isn't corrupted

### Slides look blurry
- Increase DPI: `dpi=300`
- Check original presentation quality
- Verify display scaling isn't affecting view

### File sizes too large
- Reduce DPI: `dpi=150`
- Use JPEG instead (requires code modification)
- Compress presentation images before conversion

## API Reference

### `convert_presentation_to_png()`

```python
def convert_presentation_to_png(
    presentation_path: str,
    output_dir: str,
    dpi: int = 200,
    naming_pattern: str = "slide_{index:03d}.png"
) -> SlideConversionResult
```

**Parameters:**
- `presentation_path` (str): Path to presentation file
- `output_dir` (str): Directory for output PNG files
- `dpi` (int, optional): Output resolution (default: 200)
- `naming_pattern` (str, optional): Filename template with `{index}` placeholder

**Returns:** `SlideConversionResult` with:
- `success` (bool): Whether conversion succeeded
- `slide_count` (int): Number of slides exported
- `slide_files` (List[str]): Paths to generated PNGs
- `output_dir` (str): Output directory path
- `error_message` (Optional[str]): Error details if failed

## Advanced Usage

### Batch Processing

```python
from pathlib import Path

presentations = Path("/presentations").glob("*.odp")

for pres in presentations:
    output_dir = f"/output/{pres.stem}"
    result = convert_presentation_to_png(str(pres), output_dir)
    print(f"{pres.name}: {result.slide_count} slides")
```

### Integration with Document Analysis

```python
# 1. Create presentation
create_document("/tmp/slides.odp", "impress", "")

# 2. Add content (using other MCP tools)
# ... populate slides ...

# 3. Convert to PNG
result = convert_presentation_to_png("/tmp/slides.odp", "/tmp/review")

# 4. Claude reviews each slide (vision capabilities)
for slide_path in result.slide_files:
    # Claude reads image and provides feedback
    feedback = review_slide_design(slide_path)
    print(feedback)
```

## Performance

**Conversion Speed:**
- Small presentation (5 slides): ~5 seconds
- Medium presentation (20 slides): ~15 seconds
- Large presentation (100 slides): ~60 seconds

**Bottlenecks:**
1. LibreOffice PDF export (~2-3 sec overhead)
2. PDF → PNG conversion (~0.5 sec per slide at 200 DPI)

**Optimization Tips:**
- Lower DPI for faster conversion (150 vs 200)
- Use SSD storage for temp files
- Process multiple presentations in parallel

## Examples

See `examples/demo_slides_to_png.py` for interactive demonstration.

## Related Documentation

- [Main README](../README.md) - Project overview
- [Design Document](SLIDES_TO_PNG_DESIGN.md) - Technical design details
- [Live Viewing Guide](LIVE_VIEWING_GUIDE.md) - Real-time document editing
