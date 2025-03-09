# Network Log Analyzer

A powerful AI-powered tool for analyzing network attack logs using both Google Gemini and OpenAI models.

## Features

- **Multi-Model Support**: Use either Google Gemini or OpenAI models for analysis
- **Dynamic Model Discovery**: Automatically discovers available Gemini models via the API
- **Fallback Mechanism**: Tries alternative models if the primary one fails
- **User-Friendly Interface**: Simple UI for pasting logs and receiving detailed analysis
- **Detailed Analysis**: Get comprehensive explanations of attack types, severity, and recommended mitigations

## Default Models

- **Gemini**: gemini-2.0-flash-lite (default)
- **OpenAI**: gpt-4o-mini (default)

## Requirements

- Python 3.9+
- Streamlit
- Google Generative AI Python SDK
- OpenAI Python SDK (v1.0.0+)

## Setup

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_API_KEY=your_google_api_key
   ```
4. Run the application:
   ```
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

## Deployment

This application can be deployed on Streamlit Cloud. Make sure to set your API keys as secrets in the Streamlit Cloud dashboard.

## Author

Designed and developed by [Lindsay Hiebert](https://www.linkedin.com/in/lindsayhiebert/)

## License

MIT
