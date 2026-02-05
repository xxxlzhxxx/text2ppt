"""
Text2PPT - Main Application

This application converts text input into a PowerPoint presentation by:
1. Using Seed 2.0 LLM to generate structured PPT content and image prompts
2. Using Seadream 4.5 to generate images for each slide
3. Using python-pptx to assemble the final presentation

Usage:
    python main.py [--input INPUT_FILE] [--output OUTPUT_NAME] [--slides NUM_SLIDES]
    
    Or run interactively:
    python main.py
"""
import os
import sys
import argparse
import time
from datetime import datetime
from typing import Optional

from llm_client import LLMClient
from image_generator import ImageGenerator
from ppt_generator import PPTGenerator
from config import OUTPUT_DIR

# Force stdout to be unbuffered
import functools
print = functools.partial(print, flush=True)


def create_ppt_from_text(
    text_input: str,
    output_name: Optional[str] = None,
    num_slides: int = 5,
    verbose: bool = True
) -> str:
    """
    Main pipeline to create a PPT from text input.
    
    Args:
        text_input: The text content to convert to PPT
        output_name: Name for the output file (auto-generated if not provided)
        num_slides: Number of slides to generate
        verbose: Whether to print progress messages
        
    Returns:
        Path to the generated PPTX file
    """
    # Generate output name if not provided
    if not output_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"presentation_{timestamp}"
    
    if verbose:
        print("=" * 60)
        print("Text2PPT - Converting Text to PowerPoint")
        print("=" * 60)
        print(f"\nInput text ({len(text_input)} chars):")
        print(text_input[:200] + "..." if len(text_input) > 200 else text_input)
        print(f"\nTarget slides: {num_slides}")
        print("=" * 60)
    
    # Step 1: Generate PPT structure using LLM
    if verbose:
        print("\n[Step 1/3] Generating PPT structure with Seed 2.0...")
        
    start_time = time.time()
    llm_client = LLMClient()
    slides_data = llm_client.generate_ppt_structure(text_input, num_slides)
    llm_time = time.time() - start_time
    
    if verbose:
        print(f"Generated {len(slides_data)} slides in {llm_time:.1f}s")
        for slide in slides_data:
            print(f"  - Slide {slide.get('slide_number', '?')}: {slide.get('title', 'N/A')}")
    
    # Step 2: Generate images for each slide
    if verbose:
        print("\n[Step 2/3] Generating images with Seadream 4.5...")
        print("(This may take a few minutes...)")
        
    start_time = time.time()
    image_generator = ImageGenerator()
    image_paths = image_generator.generate_slides_images(slides_data, output_name)
    image_time = time.time() - start_time
    
    if verbose:
        print(f"Generated {len(image_paths)} images in {image_time:.1f}s")
    
    # Step 3: Create PPT from images
    if verbose:
        print("\n[Step 3/3] Creating PowerPoint presentation...")
        
    start_time = time.time()
    ppt_generator = PPTGenerator()
    ppt_path = ppt_generator.create_ppt_from_images(image_paths, output_name, slides_data)
    ppt_time = time.time() - start_time
    
    if verbose:
        print(f"Created presentation in {ppt_time:.1f}s")
        print("\n" + "=" * 60)
        print("COMPLETED!")
        print(f"Output file: {ppt_path}")
        print(f"Total time: {llm_time + image_time + ppt_time:.1f}s")
        print("=" * 60)
    
    return ppt_path


def interactive_mode():
    """Run in interactive mode, prompting user for input."""
    print("\n" + "=" * 60)
    print("Text2PPT - Interactive Mode")
    print("=" * 60)
    print("\nEnter your text content below.")
    print("(Press Enter twice to finish, or Ctrl+C to cancel)")
    print("-" * 60)
    
    lines = []
    empty_count = 0
    
    try:
        while True:
            line = input()
            if line == "":
                empty_count += 1
                if empty_count >= 2:
                    break
                lines.append(line)
            else:
                empty_count = 0
                lines.append(line)
    except KeyboardInterrupt:
        print("\nCancelled.")
        return
    
    text_input = "\n".join(lines[:-1] if lines and lines[-1] == "" else lines)
    
    if not text_input.strip():
        print("No input provided. Exiting.")
        return
    
    # Ask for number of slides
    try:
        num_slides_input = input("\nNumber of slides (default: 5): ").strip()
        num_slides = int(num_slides_input) if num_slides_input else 5
    except ValueError:
        num_slides = 5
    
    # Ask for output name
    output_name = input("Output filename (press Enter for auto): ").strip()
    if not output_name:
        output_name = None
    
    print("")
    create_ppt_from_text(text_input, output_name, num_slides)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Convert text to PowerPoint presentation using AI"
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Path to input text file"
    )
    parser.add_argument(
        "--text", "-t",
        type=str,
        help="Direct text input"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output filename (without extension)"
    )
    parser.add_argument(
        "--slides", "-s",
        type=int,
        default=5,
        help="Number of slides to generate (default: 5)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Reduce output verbosity"
    )
    
    args = parser.parse_args()
    
    # Determine input source
    if args.input:
        # Read from file
        if not os.path.exists(args.input):
            print(f"Error: Input file not found: {args.input}")
            sys.exit(1)
        with open(args.input, 'r', encoding='utf-8') as f:
            text_input = f.read()
    elif args.text:
        # Use direct text input
        text_input = args.text
    else:
        # Interactive mode
        interactive_mode()
        return
    
    # Create PPT
    create_ppt_from_text(
        text_input,
        args.output,
        args.slides,
        verbose=not args.quiet
    )


if __name__ == "__main__":
    main()
