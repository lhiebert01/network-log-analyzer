# Network Log Analyzer

A powerful AI-powered tool for analyzing network attack logs using both Google Gemini and OpenAI models to identify security threats and anomalies.

## Features

- **Multi-Model Support**: Use either Google Gemini or OpenAI models for analysis
- **Dynamic Model Discovery**: Automatically discovers available Gemini models via the API
- **Fallback Mechanism**: Tries alternative models if the primary one fails
- **User-Friendly Interface**: Simple UI for pasting logs and receiving detailed analysis
- **Detailed Analysis**: Get comprehensive explanations of attack types, severity, and recommended mitigations
- **Detailed Error Handling**: Comprehensive logging and debugging output

## Default Models

- **Gemini**: gemini-2.0-flash-lite (default)
- **OpenAI**: gpt-4o-mini (default)

## Requirements

- Python 3.9+
- Streamlit
- Google Generative AI Python SDK
- OpenAI Python SDK (v1.0.0+)

## Setup

### Local Development

1. Set up a Python virtual environment:
```bash
conda create -p venv python=3.12.9 -y
conda activate venv
pip install -r requirements.txt
```

2. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
```

3. Run the application:
```bash
streamlit run log_analyzer_api.py
```

## Usage

1. Select your preferred AI model provider (Gemini or OpenAI)
2. Choose a specific model from the dropdown
3. Paste your network attack log into the text area
4. Click "Analyze Log" to receive a detailed analysis

## Security Notes

- API keys are stored in a `.env` file which is excluded from version control
- Never commit your `.env` file or expose your API keys in your code

## Deployment to Streamlit Cloud

1. Create a GitHub repository and push your code:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/lhiebert01/network-log-analyzer.git
git push -u origin main
```

2. Deploy on Streamlit Cloud:
   - Connect your GitHub repository to Streamlit Cloud
   - Add your API keys as secrets in the Streamlit Cloud dashboard
   - Deploy the application

## Author

Designed and developed by [Lindsay Hiebert](https://www.linkedin.com/in/lindsayhiebert/)

## License

MIT
