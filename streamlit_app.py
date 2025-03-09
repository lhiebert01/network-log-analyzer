import streamlit as st
import requests
import json
import os
from model_config import get_gemini_models, get_openai_models
import google.generativeai as genai
import openai
import logging
from logging_config import setup_logging

# Setup logging
logger = setup_logging()

# Page config
st.set_page_config(
    page_title="Network Log Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "api_key_set" not in st.session_state:
    st.session_state.api_key_set = False
if "selected_model" not in st.session_state:
    st.session_state.selected_model = None
if "provider" not in st.session_state:
    st.session_state.provider = "gemini"
if "gemini_models" not in st.session_state:
    st.session_state.gemini_models = []
if "openai_models" not in st.session_state:
    st.session_state.openai_models = []
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = ""

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-bottom: 1rem;
    }
    .result-container {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
    .stTextArea textarea {
        height: 300px !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='main-header'>Network Log Analyzer</h1>", unsafe_allow_html=True)
st.markdown("Analyze network logs using AI to identify security threats and anomalies.")

# Sidebar for API key configuration
with st.sidebar:
    st.markdown("<h2 class='sub-header'>API Configuration</h2>", unsafe_allow_html=True)
    
    provider = st.radio("Select AI Provider", ["Google Gemini", "OpenAI"], 
                         index=0 if st.session_state.provider == "gemini" else 1,
                         help="Choose which AI provider to use for analysis")
    
    if provider == "Google Gemini":
        st.session_state.provider = "gemini"
        gemini_api_key = st.text_input("Google Gemini API Key", type="password", 
                                       help="Enter your Google Gemini API key")
        
        if gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                st.session_state.gemini_models = get_gemini_models()
                st.session_state.api_key_set = True
                st.success("API key configured successfully!")
            except Exception as e:
                st.error(f"Error configuring API key: {str(e)}")
                st.session_state.api_key_set = False
                
    else:  # OpenAI
        st.session_state.provider = "openai"
        openai_api_key = st.text_input("OpenAI API Key", type="password",
                                      help="Enter your OpenAI API key")
        
        if openai_api_key:
            try:
                openai.api_key = openai_api_key
                st.session_state.openai_models = get_openai_models()
                st.session_state.api_key_set = True
                st.success("API key configured successfully!")
            except Exception as e:
                st.error(f"Error configuring API key: {str(e)}")
                st.session_state.api_key_set = False
    
    # Model selection
    st.markdown("---")
    st.markdown("<h3>Model Selection</h3>", unsafe_allow_html=True)
    
    if st.session_state.provider == "gemini" and st.session_state.gemini_models:
        default_model = "gemini-2.0-flash-lite" if "gemini-2.0-flash-lite" in st.session_state.gemini_models else st.session_state.gemini_models[0]
        selected_model = st.selectbox("Select Gemini Model", 
                                     options=st.session_state.gemini_models,
                                     index=st.session_state.gemini_models.index(default_model) if default_model in st.session_state.gemini_models else 0)
        st.session_state.selected_model = selected_model
        
    elif st.session_state.provider == "openai" and st.session_state.openai_models:
        default_model = "gpt-4o-mini" if "gpt-4o-mini" in st.session_state.openai_models else st.session_state.openai_models[0]
        selected_model = st.selectbox("Select OpenAI Model", 
                                     options=st.session_state.openai_models,
                                     index=st.session_state.openai_models.index(default_model) if default_model in st.session_state.openai_models else 0)
        st.session_state.selected_model = selected_model
    
    # About section
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This tool analyzes network logs using AI to identify:
    - Attack patterns
    - Security threats
    - Anomalous behavior
    - Recommended mitigations
    """)

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<h2 class='sub-header'>Network Log Input</h2>", unsafe_allow_html=True)
    
    # Sample log selector
    sample_option = st.selectbox(
        "Select a sample log or paste your own",
        ["Custom Input", "Port Scan Sample", "DoS Attack Sample", "Brute Force Sample", "Data Exfiltration Sample"]
    )
    
    # Sample log content
    port_scan_sample = """
# Fields: ts uid id.orig_h id.resp_p proto scan_attempts anomaly_type severity
1709913600.123456 CXWfwc3LHJYnCZGbt3 192.168.1.100 22 tcp 15 Port_Scanning Medium
1709913605.234567 CXWfwc3LHJYnCZGbt4 192.168.1.100 23 tcp 12 Port_Scanning Medium
1709913610.345678 CXWfwc3LHJYnCZGbt5 192.168.1.100 25 tcp 18 Port_Scanning Medium
1709913615.456789 CXWfwc3LHJYnCZGbt6 192.168.1.100 80 tcp 20 Port_Scanning High
1709913620.567890 CXWfwc3LHJYnCZGbt7 192.168.1.100 443 tcp 25 Port_Scanning High
"""
    
    dos_sample = """
# Fields: ts uid id.orig_h id.resp_h id.resp_p proto service packets_count anomaly_type severity
1709913700.123456 CXWfwc3LHJYnCZGbt8 192.168.1.101 192.168.1.1 80 tcp http 5000 SYN_Flood High
1709913705.234567 CXWfwc3LHJYnCZGbt9 192.168.1.101 192.168.1.1 80 tcp http 6000 SYN_Flood High
1709913710.345678 CXWfwc3LHJYnCZGbta 192.168.1.101 192.168.1.1 80 tcp http 7500 SYN_Flood Critical
1709913715.456789 CXWfwc3LHJYnCZGbtb 192.168.1.101 192.168.1.1 80 tcp http 8000 SYN_Flood Critical
1709913720.567890 CXWfwc3LHJYnCZGbtc 192.168.1.101 192.168.1.1 80 tcp http 9000 SYN_Flood Critical
"""
    
    bruteforce_sample = """
# Fields: ts uid id.orig_h id.resp_h id.resp_p proto service login_attempts user anomaly_type severity
1709913800.123456 CXWfwc3LHJYnCZGbtd 192.168.1.102 192.168.1.1 22 tcp ssh 10 admin Brute_Force_SSH Medium
1709913805.234567 CXWfwc3LHJYnCZGbte 192.168.1.102 192.168.1.1 22 tcp ssh 15 admin Brute_Force_SSH Medium
1709913810.345678 CXWfwc3LHJYnCZGbtf 192.168.1.102 192.168.1.1 22 tcp ssh 20 admin Brute_Force_SSH High
1709913815.456789 CXWfwc3LHJYnCZGbtg 192.168.1.102 192.168.1.1 22 tcp ssh 25 admin Brute_Force_SSH High
1709913820.567890 CXWfwc3LHJYnCZGbth 192.168.1.102 192.168.1.1 22 tcp ssh 30 admin Brute_Force_SSH Critical
"""
    
    data_exfil_sample = """
# Fields: ts uid id.orig_h id.resp_h id.resp_p proto service data_size anomaly_type severity
1709913900.123456 CXWfwc3LHJYnCZGbti 192.168.1.103 203.0.113.100 53 udp dns 1024 DNS_Exfiltration Medium
1709913905.234567 CXWfwc3LHJYnCZGbtj 192.168.1.103 203.0.113.100 53 udp dns 2048 DNS_Exfiltration Medium
1709913910.345678 CXWfwc3LHJYnCZGbtk 192.168.1.103 203.0.113.100 53 udp dns 4096 DNS_Exfiltration High
1709913915.456789 CXWfwc3LHJYnCZGbtl 192.168.1.103 203.0.113.100 53 udp dns 8192 DNS_Exfiltration High
1709913920.567890 CXWfwc3LHJYnCZGbtm 192.168.1.103 203.0.113.100 53 udp dns 16384 DNS_Exfiltration Critical
"""
    
    # Set the log content based on selection
    if sample_option == "Port Scan Sample":
        log_content = port_scan_sample
    elif sample_option == "DoS Attack Sample":
        log_content = dos_sample
    elif sample_option == "Brute Force Sample":
        log_content = bruteforce_sample
    elif sample_option == "Data Exfiltration Sample":
        log_content = data_exfil_sample
    else:
        log_content = ""
    
    # Text area for log input
    user_log = st.text_area("Paste your network log here", value=log_content, height=300)
    
    # Analysis prompt
    st.markdown("### Analysis Instructions")
    analysis_prompt = st.text_area(
        "Customize the analysis instructions (optional)",
        value="Analyze this network log to identify attack patterns, severity, and provide recommended mitigations. Include a detailed explanation of what's happening in the log.",
        height=100
    )
    
    # Analyze button
    analyze_button = st.button("Analyze Log", type="primary", disabled=not st.session_state.api_key_set)
    
    if analyze_button and user_log:
        with st.spinner("Analyzing log data..."):
            try:
                # Prepare the prompt
                prompt = f"""
                You are a cybersecurity expert analyzing network logs. 
                
                {analysis_prompt}
                
                Here is the log data:
                ```
                {user_log}
                ```
                
                Provide a detailed analysis including:
                1. Type of attack or anomaly detected
                2. Severity assessment
                3. Technical explanation of what's happening
                4. Recommended mitigations
                5. Additional context that might be helpful
                
                Format your response in markdown for readability.
                """
                
                # Process with selected model
                if st.session_state.provider == "gemini":
                    try:
                        model = genai.GenerativeModel(st.session_state.selected_model)
                        response = model.generate_content(prompt)
                        analysis_result = response.text
                    except Exception as e:
                        logger.error(f"Error with primary Gemini model: {str(e)}")
                        st.warning(f"Error with selected model. Trying fallback model...")
                        
                        # Try fallback model
                        try:
                            fallback_model = "gemini-1.5-flash" if st.session_state.selected_model != "gemini-1.5-flash" else "gemini-1.0-pro"
                            model = genai.GenerativeModel(fallback_model)
                            response = model.generate_content(prompt)
                            analysis_result = response.text
                        except Exception as fallback_error:
                            raise Exception(f"Both primary and fallback models failed. Error: {str(fallback_error)}")
                
                else:  # OpenAI
                    try:
                        response = openai.chat.completions.create(
                            model=st.session_state.selected_model,
                            messages=[
                                {"role": "system", "content": "You are a cybersecurity expert analyzing network logs."},
                                {"role": "user", "content": prompt}
                            ]
                        )
                        analysis_result = response.choices[0].message.content
                    except Exception as e:
                        logger.error(f"Error with primary OpenAI model: {str(e)}")
                        st.warning(f"Error with selected model. Trying fallback model...")
                        
                        # Try fallback model
                        try:
                            fallback_model = "gpt-3.5-turbo" if st.session_state.selected_model != "gpt-3.5-turbo" else "gpt-4o-mini"
                            response = openai.chat.completions.create(
                                model=fallback_model,
                                messages=[
                                    {"role": "system", "content": "You are a cybersecurity expert analyzing network logs."},
                                    {"role": "user", "content": prompt}
                                ]
                            )
                            analysis_result = response.choices[0].message.content
                        except Exception as fallback_error:
                            raise Exception(f"Both primary and fallback models failed. Error: {str(fallback_error)}")
                
                # Store result in session state
                st.session_state.analysis_result = analysis_result
                
            except Exception as e:
                st.error(f"Error analyzing logs: {str(e)}")
                logger.error(f"Analysis error: {str(e)}")
                st.session_state.analysis_result = f"Error analyzing logs: {str(e)}"

# Results column
with col2:
    st.markdown("<h2 class='sub-header'>Analysis Results</h2>", unsafe_allow_html=True)
    
    if st.session_state.analysis_result:
        st.markdown('<div class="result-container">', unsafe_allow_html=True)
        st.markdown(st.session_state.analysis_result)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Export options
        st.download_button(
            label="Download Analysis",
            data=st.session_state.analysis_result,
            file_name="network_log_analysis.md",
            mime="text/markdown"
        )
    else:
        st.info("Analysis results will appear here after you analyze a log.")

# Footer
st.markdown("---")
st.markdown("Network Log Analyzer | Powered by AI | © 2025")
