"""
Slides to PNG Converter - Optimized for AI Vision Quality

This module converts presentation slides to high-quality PNG images suitable
for AI vision models (like Claude) to inspect and evaluate.

Uses PDF intermediate approach for maximum fidelity:
1. LibreOffice converts presentation → PDF (best rendering quality)
2. pdf2image splits PDF pages → individual PNGs (preserves visual fidelity)
"""

import os
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SlideConversionResult(BaseModel):
    """Result of converting slides to PNG images"""
    source_path: str = Field(description="Source presentation path")
    output_dir: str = Field(description="Directory containing PNG files")
    slide_count: int = Field(description="Number of slides exported")
    slide_files: List[str] = Field(description="Paths to generated PNG files")
    success: bool = Field(description="Whether conversion was successful")
    error_message: Optional[str] = Field(description="Error message if conversion failed")


def convert_slides_to_png(
    presentation_path: str,
    output_dir: str,
    dpi: int = 200,
    naming_pattern: str = "slide_{index:03d}.png"
) -> SlideConversionResult:
    """
    Convert all slides in a presentation to individual PNG images.

    Optimized for AI vision quality - produces high-fidelity images that
    accurately represent how the slides would appear to humans.

    Args:
        presentation_path: Path to presentation file (.odp, .pptx, .ppt)
        output_dir: Directory where PNG files will be saved
        dpi: DPI for output images (default: 200)
             - 150: Good for most text, smaller files
             - 200: Recommended for AI vision (sharp text, good file size)
             - 300: High quality for detailed graphics/small fonts
        naming_pattern: Pattern for output filenames
                       Must include {index} placeholder

    Returns:
        SlideConversionResult with success status and list of generated files

    Example:
        result = convert_slides_to_png(
            "presentation.odp",
            "/tmp/slides",
            dpi=200
        )

        if result.success:
            print(f"Exported {result.slide_count} slides")
            for slide_file in result.slide_files:
                print(f"  - {slide_file}")
    """

    presentation_path_obj = Path(presentation_path)
    output_dir_obj = Path(output_dir)

    # Validate input
    if not presentation_path_obj.exists():
        return SlideConversionResult(
            source_path=presentation_path,
            output_dir=output_dir,
            slide_count=0,
            slide_files=[],
            success=False,
            error_message=f"Presentation file not found: {presentation_path}"
        )

    # Create output directory
    try:
        output_dir_obj.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return SlideConversionResult(
            source_path=presentation_path,
            output_dir=output_dir,
            slide_count=0,
            slide_files=[],
            success=False,
            error_message=f"Failed to create output directory: {str(e)}"
        )

    try:
        # Step 1: Convert presentation to PDF using LibreOffice CLI
        # This gives us the best quality rendering
        import subprocess

        with tempfile.TemporaryDirectory() as tmp_dir:
            # Run LibreOffice conversion
            result = subprocess.run([
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', tmp_dir,
                str(presentation_path_obj.absolute())
            ], capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                return SlideConversionResult(
                    source_path=presentation_path,
                    output_dir=output_dir,
                    slide_count=0,
                    slide_files=[],
                    success=False,
                    error_message=f"LibreOffice conversion failed: {result.stderr}"
                )

            # Find the generated PDF
            pdf_path = Path(tmp_dir) / f"{presentation_path_obj.stem}.pdf"
            if not pdf_path.exists():
                return SlideConversionResult(
                    source_path=presentation_path,
                    output_dir=output_dir,
                    slide_count=0,
                    slide_files=[],
                    success=False,
                    error_message=f"PDF not generated at expected location: {pdf_path}"
                )

            # Step 2: Convert PDF pages to PNG images using pdf2image
            try:
                from pdf2image import convert_from_path
            except ImportError:
                return SlideConversionResult(
                    source_path=presentation_path,
                    output_dir=output_dir,
                    slide_count=0,
                    slide_files=[],
                    success=False,
                    error_message="pdf2image library not installed. Install with: pip install pdf2image"
                )

            # Convert PDF to images
            # pdf2image handles the PDF → PNG conversion with high quality
            images = convert_from_path(
                str(pdf_path),
                dpi=dpi,
                fmt='png'
            )

            # Save each image
            slide_files = []
            for i, image in enumerate(images):
                output_filename = naming_pattern.format(index=i+1)
                output_path = output_dir_obj / output_filename

                # Save as PNG (lossless, good for text)
                image.save(str(output_path), 'PNG', optimize=True)
                slide_files.append(str(output_path.absolute()))

            return SlideConversionResult(
                source_path=str(presentation_path_obj.absolute()),
                output_dir=str(output_dir_obj.absolute()),
                slide_count=len(images),
                slide_files=slide_files,
                success=True,
                error_message=None
            )

    except subprocess.TimeoutExpired:
        return SlideConversionResult(
            source_path=presentation_path,
            output_dir=output_dir,
            slide_count=0,
            slide_files=[],
            success=False,
            error_message="LibreOffice conversion timed out (>60s)"
        )
    except Exception as e:
        return SlideConversionResult(
            source_path=presentation_path,
            output_dir=output_dir,
            slide_count=0,
            slide_files=[],
            success=False,
            error_message=f"Conversion failed: {str(e)}"
        )


def get_slide_dimensions(presentation_path: str) -> Dict[str, Any]:
    """
    Get the dimensions and slide count of a presentation without converting.

    This is useful for estimating output file sizes before conversion.

    Args:
        presentation_path: Path to presentation file

    Returns:
        Dictionary with slide_count, width, height (in points)
    """
    try:
        import subprocess

        # Use pdfinfo (part of poppler-utils) to get PDF info
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Convert to PDF first
            result = subprocess.run([
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', tmp_dir,
                presentation_path
            ], capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                return {"error": "Failed to convert presentation"}

            pdf_path = Path(tmp_dir) / f"{Path(presentation_path).stem}.pdf"

            # Get PDF info
            result = subprocess.run([
                'pdfinfo', str(pdf_path)
            ], capture_output=True, text=True)

            if result.returncode == 0:
                info = {}
                for line in result.stdout.split('\n'):
                    if 'Pages:' in line:
                        info['slide_count'] = int(line.split(':')[1].strip())
                    elif 'Page size:' in line:
                        # Example: "Page size:      720 x 540 pts"
                        parts = line.split(':')[1].strip().split('x')
                        info['width_pts'] = float(parts[0].strip())
                        info['height_pts'] = float(parts[1].split()[0].strip())
                return info
            else:
                # Fallback: use pdf2image to count pages
                from pdf2image import pdfinfo_from_path
                info = pdfinfo_from_path(str(pdf_path))
                return {
                    'slide_count': info.get('Pages', 0)
                }

    except Exception as e:
        return {"error": str(e)}


def estimate_output_size(slide_count: int, dpi: int = 200, width: int = 1920) -> Dict[str, Any]:
    """
    Estimate the total file size for converting slides to PNG.

    Useful for checking disk space before large conversions.

    Args:
        slide_count: Number of slides
        dpi: DPI setting
        width: Target width in pixels

    Returns:
        Dictionary with estimated sizes in MB
    """
    # Rough estimates based on typical presentation content
    # PNG file sizes vary based on content complexity

    # Average PNG sizes at different DPIs (MB per slide)
    size_estimates = {
        150: 0.5,   # ~500 KB per slide
        200: 0.8,   # ~800 KB per slide
        300: 1.5,   # ~1.5 MB per slide
    }

    # Get closest DPI estimate
    closest_dpi = min(size_estimates.keys(), key=lambda x: abs(x - dpi))
    size_per_slide = size_estimates[closest_dpi]

    # Adjust for width (relative to 1920px baseline)
    width_factor = (width / 1920.0) ** 2
    size_per_slide *= width_factor

    total_size = slide_count * size_per_slide

    return {
        'slide_count': slide_count,
        'estimated_size_per_slide_mb': round(size_per_slide, 2),
        'estimated_total_size_mb': round(total_size, 2),
        'note': 'Actual sizes vary based on content complexity'
    }
