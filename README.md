# Network Log Analyzer

A Streamlit-based tool for analyzing network logs using AI to identify security threats and anomalies.

## Features

- Support for both Google Gemini and OpenAI models
- Dynamic model discovery for Gemini models using the API
- Updated OpenAI client implementation using the new API format (openai>=1.0.0)
- Fallback mechanism to use alternative models if the selected model fails
- User-friendly GUI with model selection dropdown
- Detailed error handling and logging for debugging

## Deployment Instructions

### Local Development

1. Set up a Python virtual environment:
```bash
conda create -p venv python=3.12.9 -y
conda activate venv
pip install -r log-analyzer-requirements.txt
```

2. Run the Streamlit app:
```bash
streamlit run streamlit_app.py
```

### Deployment to Streamlit Cloud

1. Create a GitHub repository:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/network-log-analyzer.git
git push -u origin main
```

2. Visit [Streamlit Cloud](https://streamlit.io/cloud) and sign in with your GitHub account.

3. Create a new app by selecting your repository and the `streamlit_app.py` file.

4. Configure the app settings and deploy.

5. **Important**: You'll need to set up secrets in the Streamlit Cloud dashboard for your API keys:
   - For Gemini: Add `GEMINI_API_KEY` as a secret
   - For OpenAI: Add `OPENAI_API_KEY` as a secret

## Integration with Network Attack Simulator

The Network Log Analyzer is designed to work alongside the Network Attack Simulator. While they can be used independently, they provide the most value when used together.

## Requirements

See `log-analyzer-requirements.txt` for the full list of dependencies.

## License

For educational purposes only. Do not use for malicious activities.

## Author

Created by [Your Name]
