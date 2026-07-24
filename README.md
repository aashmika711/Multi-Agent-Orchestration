# AI Poetry Studio

AI Poetry Studio is a Python-based application that generates poems using a role-based multi-agent architecture powered by Large Language Models (LLMs). The application accepts user preferences such as theme, language, poetic form, and tone to generate creative and polished poems.

## Features

- Role-based AI agents for different stages of poem generation
- User-defined theme, language, poetic form, and tone
- Automatic fallback between OpenAI models
- Interactive command-line interface
- Structured and formatted poem generation
- Automatic completion marker for the final poem

## Agent Roles

### Author Agent
- Collects the user's requirements.
- Initiates the poem generation process.

### Muse Agent
- Suggests three different poem concepts.
- Selects the most suitable concept.

### Verse Agent
- Generates the complete poem.
- Follows the requested language, tone, and poetic form.

### Editor Agent
- Refines the poem for better readability and rhythm.
- Produces the final version ending with `POEM_COMPLETE`.

## Technologies Used

- Python
- AutoGen 0.9.9
- OpenAI Python SDK 1.101.0
- GPT-5 Nano
- GPT-4o Mini (Fallback)

## Project Structure

```
AI-Poetry-Studio/
│
├── Project-MultiAgent.py
├── README.md
└── requirements.txt
```

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/AI-Poetry-Studio.git
```

Navigate to the project directory:

```bash
cd AI-Poetry-Studio
```

Install the required packages:

```bash
pip install autogen==0.9.9 openai==1.101.0
```

## API Key Configuration

Set your OpenAI API key before running the project.

```python
import os

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
```

## Running the Project

```bash
python Project-MultiAgent.py
```

## Sample Input

```
Language : English
Theme    : Chandrayaan-3's Journey to the Moon
Form     : Free Verse
Tone     : Inspirational
```

## Sample Output

```
Muse:
- Idea 1
- Idea 2
- Idea 3

Selected Concept:
...

Verse:
...

Editor:
...

POEM_COMPLETE
```

## Model Fallback

The application first attempts to generate responses using **GPT-5 Nano**. If the request fails, it automatically retries using **GPT-4o Mini**, improving reliability during temporary API or quota issues.

## Future Enhancements

- Streamlit or Gradio web interface
- Export poems to PDF or text files
- Additional poetry styles
- Voice input and speech output
- More specialized AI agents
- Save poem history

## Learning Outcomes

This project demonstrates:

- Multi-agent application design
- Prompt engineering
- LLM integration
- OpenAI API usage
- Automatic model fallback
- Object-oriented programming in Python

## Author

Aashmika Bavu

Computer Science Student with an interest in Artificial Intelligence, Machine Learning, and Large Language Models.

## License

This project is developed for educational and learning purposes.