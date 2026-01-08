#!/usr/bin/env python3
"""
Demo: Slides to PNG Conversion

This script demonstrates converting presentation slides to PNG images
optimized for AI vision inspection.

Usage:
    python examples/demo_slides_to_png.py
    python examples/demo_slides_to_png.py /path/to/presentation.odp
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from slides_to_png import convert_slides_to_png, get_slide_dimensions, estimate_output_size
import tempfile


def create_sample_presentation():
    """Create a sample presentation for demonstration"""
    print("📝 Creating sample presentation...")

    from libremcp import create_document, insert_text_at_position

    # Create a simple presentation
    temp_dir = tempfile.gettempdir()
    presentation_path = os.path.join(temp_dir, "demo_presentation.odp")

    # Note: This creates an empty presentation
    # In real usage, you'd populate it with content using LibreOffice UNO API
    result = create_document(presentation_path, "impress", "")

    print(f"✅ Created sample presentation: {presentation_path}")
    print("   Note: This is a minimal presentation. Use LibreOffice to add content.")

    return presentation_path


def demo_basic_conversion(presentation_path: str):
    """Demonstrate basic slides-to-PNG conversion"""
    print("\n" + "="*60)
    print("Demo 1: Basic Conversion (200 DPI)")
    print("="*60)

    output_dir = tempfile.mkdtemp(prefix="slides_basic_")

    print(f"\n📁 Input:  {presentation_path}")
    print(f"📁 Output: {output_dir}")
    print("\n🔄 Converting...")

    result = convert_slides_to_png(
        presentation_path=presentation_path,
        output_dir=output_dir,
        dpi=200
    )

    if result.success:
        print(f"\n✅ Success! Exported {result.slide_count} slides")
        print(f"\n📄 Generated files:")
        for i, slide_file in enumerate(result.slide_files, 1):
            file_size = Path(slide_file).stat().st_size / 1024  # KB
            print(f"   {i}. {Path(slide_file).name} ({file_size:.1f} KB)")

        # Calculate total size
        total_size = sum(Path(f).stat().st_size for f in result.slide_files) / (1024 * 1024)
        print(f"\n📊 Total size: {total_size:.2f} MB")
    else:
        print(f"\n❌ Conversion failed: {result.error_message}")

    return result


def demo_quality_comparison(presentation_path: str):
    """Demonstrate different DPI settings"""
    print("\n" + "="*60)
    print("Demo 2: Quality Comparison (150, 200, 300 DPI)")
    print("="*60)

    dpi_settings = [
        (150, "Low (web thumbnails)"),
        (200, "Medium (AI vision - recommended)"),
        (300, "High (detailed graphics)")
    ]

    results = []

    for dpi, description in dpi_settings:
        output_dir = tempfile.mkdtemp(prefix=f"slides_dpi{dpi}_")

        print(f"\n🔄 Converting at {dpi} DPI - {description}")
        print(f"   Output: {output_dir}")

        result = convert_slides_to_png(
            presentation_path=presentation_path,
            output_dir=output_dir,
            dpi=dpi
        )

        if result.success:
            avg_size = sum(Path(f).stat().st_size for f in result.slide_files) / len(result.slide_files) / 1024
            print(f"   ✅ {result.slide_count} slides, avg {avg_size:.0f} KB per slide")
            results.append((dpi, description, avg_size, result))
        else:
            print(f"   ❌ Failed: {result.error_message}")

    # Summary comparison
    if results:
        print("\n📊 Quality Comparison Summary:")
        print(f"{'DPI':<6} {'Description':<35} {'Avg Size/Slide':<15}")
        print("-" * 60)
        for dpi, desc, avg_size, _ in results:
            print(f"{dpi:<6} {desc:<35} {avg_size:>10.0f} KB")


def demo_custom_naming(presentation_path: str):
    """Demonstrate custom naming patterns"""
    print("\n" + "="*60)
    print("Demo 3: Custom Naming Patterns")
    print("="*60)

    naming_patterns = [
        ("slide_{index:03d}.png", "Default (slide_001.png)"),
        ("page_{index:04d}.png", "Four digits (page_0001.png)"),
        ("s{index}.png", "Short (s1.png)"),
    ]

    for pattern, description in naming_patterns:
        output_dir = tempfile.mkdtemp(prefix="slides_naming_")

        print(f"\n🔄 Pattern: {pattern} - {description}")

        result = convert_slides_to_png(
            presentation_path=presentation_path,
            output_dir=output_dir,
            naming_pattern=pattern
        )

        if result.success:
            print(f"   ✅ Created files:")
            for slide_file in result.slide_files[:3]:  # Show first 3
                print(f"      - {Path(slide_file).name}")
            if len(result.slide_files) > 3:
                print(f"      ... and {len(result.slide_files) - 3} more")
        else:
            print(f"   ❌ Failed: {result.error_message}")


def demo_size_estimation(presentation_path: str):
    """Demonstrate file size estimation"""
    print("\n" + "="*60)
    print("Demo 4: Size Estimation (before conversion)")
    print("="*60)

    print(f"\n📊 Analyzing: {Path(presentation_path).name}")

    # Get presentation info
    info = get_slide_dimensions(presentation_path)

    if "error" not in info:
        slide_count = info.get('slide_count', 0)
        print(f"\n📄 Presentation has {slide_count} slides")

        if 'width_pts' in info:
            print(f"   Size: {info['width_pts']:.0f} x {info['height_pts']:.0f} points")

        # Estimate sizes for different DPIs
        print("\n💾 Estimated file sizes:")
        print(f"{'DPI':<6} {'Per Slide':<15} {'Total':<15} {'Use Case'}")
        print("-" * 60)

        for dpi in [150, 200, 300]:
            estimate = estimate_output_size(slide_count, dpi)
            use_cases = {
                150: "Web thumbnails",
                200: "AI vision (recommended)",
                300: "High detail"
            }
            print(f"{dpi:<6} {estimate['estimated_size_per_slide_mb']:>10.1f} MB   "
                  f"{estimate['estimated_total_size_mb']:>10.1f} MB   {use_cases[dpi]}")

        print(f"\n💡 Note: {estimate['note']}")
    else:
        print(f"❌ Could not analyze: {info['error']}")


def main():
    """Run all demonstrations"""
    print("="*60)
    print("🎨 Slides to PNG Converter - Demo")
    print("="*60)
    print("\nThis demo shows how to convert presentation slides to PNG images")
    print("optimized for AI vision inspection.\n")

    # Get presentation path
    if len(sys.argv) > 1:
        presentation_path = sys.argv[1]
        if not Path(presentation_path).exists():
            print(f"❌ Error: File not found: {presentation_path}")
            return 1
    else:
        print("⚠️  No presentation provided. You can:")
        print("   1. Run: python demo_slides_to_png.py /path/to/presentation.odp")
        print("   2. Create a sample presentation (limited content)")
        print()

        choice = input("Create sample presentation? (y/n): ").strip().lower()
        if choice == 'y':
            try:
                presentation_path = create_sample_presentation()
            except Exception as e:
                print(f"❌ Failed to create sample: {e}")
                print("\n💡 Tip: Provide your own presentation file:")
                print("   python demo_slides_to_png.py /path/to/your/presentation.odp")
                return 1
        else:
            print("\n💡 Run again with a presentation file:")
            print("   python demo_slides_to_png.py /path/to/presentation.odp")
            return 0

    print(f"\n📋 Using presentation: {presentation_path}")

    # Check dependencies
    try:
        import pdf2image
        print("✅ pdf2image is installed")
    except ImportError:
        print("❌ pdf2image not installed")
        print("   Install with: pip install pdf2image")
        print("   Or: uv sync")
        return 1

    # Run demos
    try:
        # Demo 1: Basic conversion
        result = demo_basic_conversion(presentation_path)

        if result.success:
            # Demo 2: Quality comparison
            demo_quality_comparison(presentation_path)

            # Demo 3: Custom naming
            demo_custom_naming(presentation_path)

            # Demo 4: Size estimation
            demo_size_estimation(presentation_path)

        print("\n" + "="*60)
        print("✅ Demo completed!")
        print("="*60)
        print("\n📚 For more information, see:")
        print("   - docs/SLIDES_TO_PNG_USAGE.md")
        print("   - docs/SLIDES_TO_PNG_DESIGN.md")

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
