# Text2PPT - Demo
 

An AI-powered tool that converts text content into beautiful PowerPoint presentations.

## Features

- **Intelligent Content Planning**: Uses Seed 2.0 language model to automatically convert input text into structured PPT content
- **AI Image Generation**: Uses Seadream 4.5 text-to-image model to generate beautiful images for each slide
- **Automatic PPT Assembly**: Uses python-pptx to automatically assemble generated images into PowerPoint presentations

## Workflow

```
User Input Text
    ↓
[Seed 2.0 LLM] Generate PPT structure and image prompts
    ↓
[Seadream 4.5] Generate images for each slide
    ↓
[python-pptx] Assemble into PPTX file
    ↓
Output complete PPT file
```

## Installation

1. Install dependencies:

```bash
cd text2ppt
pip install -r requirements.txt
```

2. Configure environment variables:

```bash
# Copy example configuration
cp .env.example .env

# Edit .env file and fill in your API Key
ARK_API_KEY=your-api-key-here
```

## Usage

### Interactive Mode

Run the program directly and follow the prompts:

```bash
python main.py
```

### Command Line Mode

Generate PPT from a text file:

```bash
python main.py --input your_content.txt --output my_presentation --slides 6
```

Pass text directly:

```bash
python main.py --text "AI applications in healthcare..." --slides 5
```

### Parameters

| Parameter | Short | Description |
|-----------|-------|-------------|
| `--input` | `-i` | Input text file path |
| `--text` | `-t` | Direct text input |
| `--output` | `-o` | Output filename (without extension) |
| `--slides` | `-s` | Number of slides to generate (default: 5) |
| `--quiet` | `-q` | Reduce output verbosity |

## Project Structure

```
text2ppt/
├── main.py              # Main entry point
├── config.py            # Configuration file
├── llm_client.py        # LLM client (Seed 2.0)
├── image_generator.py   # Image generator (Seadream 4.5)
├── ppt_generator.py     # PPT generator
├── web_server.py        # Flask web service
├── static/              # Frontend static files
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .env                 # Environment variables (create yourself)
└── output/              # Output directory
    ├── images/          # Generated images
    └── *.pptx           # Generated PPT files
```

## Models

### Seed 2.0 (Language Model)
- **Purpose**: Analyze user input text and convert it into structured PPT content, while generating English prompts suitable for text-to-image models

### Seadream 4.5 (Text-to-Image Model)
- **Purpose**: Generate high-quality PPT slide images based on prompts
- **Output**: 1920x1080 (16:9) resolution images

## Web Interface

Start the web service:

```bash
python web_server.py
```

Then visit http://localhost:5000

## Example

### Input

```
AI Applications in Healthcare:
- Disease Diagnosis Assistance
- Accelerated Drug Development
- Personalized Treatment Plans
- Medical Image Analysis
- Health Monitoring and Early Warning
```

### Output

Generates a PPTX file with 5 slides:
1. Cover Page: AI in Healthcare theme
2. Disease Diagnosis: AI-assisted diagnostic technology
3. Drug Development: Accelerating new drug discovery
4. Medical Imaging: Intelligent image analysis
5. Summary: Future vision of AI in medicine

## Notes

1. Make sure the `ARK_API_KEY` environment variable is properly configured
2. Image generation may take some time (about 30-60 seconds per image)
3. Generated images and PPT files are saved in the `output/` directory
4. It's recommended to generate 3-7 slides per PPT for best results

## Tech Stack

- **LLM**: Volcengine Ark - Seed 2.0
- **Text-to-Image**: Volcengine Ark - Seadream 4.5
- **PPT Generation**: python-pptx
- **Web Framework**: Flask
- **Frontend**: Vanilla HTML/CSS/JS

## Disclaimer

This is a demonstration project for educational and testing purposes. The generated content quality depends on the underlying AI models and may vary.

## License

MIT License
