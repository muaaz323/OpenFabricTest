#!/bin/bash

# Set Python path to include the app directory
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Start Streamlit app
streamlit run streamlit_app.py 