# Slides to PNG Converter - Design Document

## Problem Statement
LibreOffice CLI's `--convert-to png` only exports the first slide of presentations, making it unsuitable for converting entire presentations to PNG images.

## Solution Overview
Use LibreOffice UNO API with `GraphicExportFilter` to:
1. Load presentation document (ODP, PPT, PPTX)
2. Iterate through all slides (DrawPages collection)
3. Export each slide individually as PNG with configurable resolution
4. Support both standalone CLI and plugin modes

## Implementation Approaches

### Approach 1: UNO API (Recommended)
**For the plugin** (`plugin/pythonpath/uno_bridge.py`):

```python
def export_slides_to_png(
    self,
    presentation_path: str,
    output_dir: str,
    width: int = 1920,
    naming_pattern: str = "slide_{index:03d}.png"
) -> Dict[str, Any]:
    """Export all slides from a presentation to PNG files"""

    # 1. Load presentation
    url = uno.systemPathToFileUrl(presentation_path)
    doc = self.desktop.loadComponentFromURL(url, "_blank", 0, ())

    # 2. Get slides collection
    draw_pages = doc.getDrawPages()
    slide_count = draw_pages.getCount()

    # 3. Set up GraphicExportFilter
    exporter = self.smgr.createInstanceWithContext(
        "com.sun.star.drawing.GraphicExportFilter", self.ctx)

    output_files = []

    # 4. Export each slide
    for i in range(slide_count):
        slide = draw_pages.getByIndex(i)
        output_file = os.path.join(output_dir, naming_pattern.format(index=i+1))

        # Set export properties
        properties = (
            PropertyValue("MediaType", 0, "image/png", 0),
            PropertyValue("URL", 0, uno.systemPathToFileUrl(output_file), 0),
            PropertyValue("Width", 0, width, 0),
            PropertyValue("PixelWidth", 0, width, 0),
        )

        exporter.setSourceDocument(slide)
        exporter.filter(properties)
        output_files.append(output_file)

    doc.close(True)

    return {
        "success": True,
        "slide_count": slide_count,
        "output_files": output_files,
        "output_dir": output_dir
    }
```

### Approach 2: PDF Intermediate (Fallback for CLI)
**For standalone CLI** (`src/libremcp.py`):

```python
@mcp.tool()
def convert_slides_to_png(
    presentation_path: str,
    output_dir: str,
    width: int = 1920,
    dpi: int = 150,
    naming_pattern: str = "slide_{index:03d}.png"
) -> SlideConversionResult:
    """Convert presentation slides to individual PNG images

    Uses two-step process:
    1. Convert presentation to PDF
    2. Split PDF pages into individual PNGs using pdf2image
    """

    # Step 1: Convert to PDF
    pdf_path = tempfile.mktemp(suffix='.pdf')
    convert_document(presentation_path, pdf_path, 'pdf')

    # Step 2: Convert PDF pages to images
    from pdf2image import convert_from_path
    images = convert_from_path(pdf_path, dpi=dpi)

    output_files = []
    for i, image in enumerate(images):
        # Resize to target width while maintaining aspect ratio
        aspect_ratio = image.height / image.width
        new_height = int(width * aspect_ratio)
        image = image.resize((width, new_height))

        output_file = os.path.join(output_dir, naming_pattern.format(index=i+1))
        image.save(output_file, 'PNG')
        output_files.append(output_file)

    return SlideConversionResult(
        source_path=presentation_path,
        output_dir=output_dir,
        slide_count=len(images),
        slide_files=output_files,
        success=True,
        error_message=None
    )
```

## API Design

### Tool Signature
```python
convert_slides_to_png(
    presentation_path: str,      # Path to .odp/.pptx/.ppt file
    output_dir: str,              # Directory for PNG files
    width: int = 1920,            # Width in pixels (height auto-calculated)
    dpi: int = 150,               # DPI for quality (CLI fallback only)
    naming_pattern: str = "slide_{index:03d}.png"  # Filename pattern
) -> SlideConversionResult
```

### Response Model
```python
class SlideConversionResult(BaseModel):
    source_path: str              # Original presentation path
    output_dir: str               # Output directory
    slide_count: int              # Number of slides exported
    slide_files: List[str]        # Paths to generated PNGs
    success: bool                 # Overall success status
    error_message: Optional[str]  # Error details if failed
```

## Resolution & Quality Settings

| Use Case | Width | DPI | Notes |
|----------|-------|-----|-------|
| Web thumbnails | 800px | 72-96 | Small file size |
| Web display | 1280px | 96 | Standard web |
| HD display | 1920px | 150 | Default setting |
| Print quality | 2560px | 300 | High resolution |

## Additional Features

### Batch Processing
```python
@mcp.tool()
def batch_convert_presentations_to_png(
    source_dir: str,
    output_base_dir: str,
    width: int = 1920,
    file_patterns: List[str] = ["*.odp", "*.pptx", "*.ppt"]
) -> List[SlideConversionResult]:
    """Convert multiple presentations in a directory"""
```

### With Speaker Notes
```python
@mcp.tool()
def convert_slides_to_png_with_notes(
    presentation_path: str,
    output_dir: str,
    export_notes: bool = True  # Also save notes as .txt files
) -> SlideConversionResult:
    """Export slides with optional speaker notes"""
```

## Implementation Priority

1. **Phase 1** (MVP):
   - Basic UNO API implementation for plugin
   - Single presentation to multiple PNGs
   - Fixed naming pattern

2. **Phase 2** (Enhanced):
   - CLI fallback using PDF intermediate
   - Configurable resolution and DPI
   - Custom naming patterns

3. **Phase 3** (Advanced):
   - Batch processing
   - Speaker notes export
   - Animation frame export

## Dependencies

### For Plugin (UNO API approach)
- ✅ Already available: `uno`, `unohelper`
- ✅ Already available: `com.sun.star.drawing.GraphicExportFilter`

### For CLI (PDF fallback approach)
- ⚠️ New dependency: `pdf2image` (via `pip install pdf2image`)
- ⚠️ System dependency: `poppler-utils` (for pdf2image)

## Testing Strategy

1. Test with various formats (ODP, PPT, PPTX)
2. Test with different slide counts (1, 10, 50+ slides)
3. Test with different aspect ratios (4:3, 16:9, custom)
4. Test resolution scaling
5. Test error handling (missing files, corrupt presentations)

## Usage Examples

```python
# Basic usage
result = convert_slides_to_png(
    "/path/to/presentation.odp",
    "/output/dir"
)
# Creates: slide_001.png, slide_002.png, ...

# Custom resolution and naming
result = convert_slides_to_png(
    "/path/to/slides.pptx",
    "/output/dir",
    width=1280,
    naming_pattern="page_{index:04d}.png"
)
# Creates: page_0001.png, page_0002.png, ...

# High quality for print
result = convert_slides_to_png(
    "/path/to/presentation.odp",
    "/output/dir",
    width=2560,
    dpi=300
)
```
