# 🚀 AI Creativity Pipeline (OpenFabric)

A powerful end-to-end AI pipeline that transforms simple text prompts into vivid images.

## 🌟 Features

- **Local LLM Integration**: Uses DeepSeek or Llama via Ollama to enhance prompts with creative details
- **Text-to-Image Generation**: Creates stunning images from prompts using Openfabric's API
- **Memory System**: Maintains both short-term (session) and long-term (persistent) memory
- **Context-Aware Generation**: Uses past creations to inform new generations
- **Interactive GUI**: Streamlit interface for easy interaction and visualization

## 🛠️ Prerequisites

1. **Ollama**: To run the local LLM
   - Install [Ollama](https://ollama.ai/download)
   - Pull the DeepSeek model: `ollama pull deepseek-coder`
   - Ensure Ollama is running: `ollama serve`

2. **Openfabric SDK**: Already included in dependencies

## 🚀 Getting Started

## 🚀 Getting Started

1. **Clone the repository**

2. **Navigate to the app directory**
   ```bash
   cd app
   ```

3. **Create a virtual environment with Python 3.10**
   - For Windows:
     ```bash
     python -m venv venv
     ```
   - For macOS/Linux:
     ```bash
     python3.10 -m venv venv
     ```

4. **Activate the virtual environment**
   - For Windows:
     ```bash
     venv\Scripts\activate
     ```
   - For macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

5. **Install dependencies using the requirements file**
   ```bash
   pip install -r requirements.txt
   ```

6. **Run the application**

   - **Streamlit GUI Version:**
     ```bash
     # On Linux/Mac:
     ./start_streamlit.sh
     
     # On Windows:
     streamlit run streamlit_app.py
     ```

## 🧠 How It Works

### Pipeline Flow

```
User Prompt
↓
Local LLM (DeepSeek or Llama)
↓
Text-to-Image App (Openfabric)
↓
Image Output
```

### Memory System

The application uses two types of memory:

- **Short-Term Memory**: Stores prompt and generation details during a single session
- **Long-Term Memory**: Persists prompt, enhanced prompt, image URL, and 3D model URL across sessions using SQLite

When you reference previous creations, the LLM analyzes your history and incorporates relevant aspects into the new generation.

## 📊 Streamlit Interface

The Streamlit interface provides an intuitive way to interact with the application:

- **Input Area**: Enter your text prompt and generate content
- **Results Display**: View the path of generated image
- **Memory Browser**: Browse through past creations with thumbnails
- **Reference System**: Easily reference and build upon previous creations

To launch the Streamlit interface:
```bash
streamlit run streamlit_app.py
```

Then open your browser to `http://localhost:8501`

## 📁 Directory Structure

- `/core`: Core services for LLM, Openfabric, and memory management
- `/datastore`: Stores images, 3D models, and the memory database
- `/ontology_dc8f06af066e4a7880a5938933236037`: Data classes for input/output

## 🧪 Example Usage

Here are some example prompts to try:

1. **Basic Creation**:
   - "Make me a glowing dragon standing on a cliff at sunset."

2. **Creative Variation**:
   - "Create a futuristic cityscape with flying cars and neon lights."

3. **Context-Aware Generation** (after creating a dragon):
   - "Create another dragon but make it blue and in flight."

## 🔧 Troubleshooting

- **Ollama Connection Issues**: Ensure Ollama is running with `ollama serve`
- **Missing Model**: If the model is missing, run `ollama pull deepseek-coder` or `ollama pull llama3`
- **Openfabric API Errors**: Check your internet connection and the API status
- **Streamlit Not Found**: Ensure streamlit is installed with `pip install streamlit`

## 📝 License

This project is created as part of the AI Developer Challenge. 
