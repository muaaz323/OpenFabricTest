import streamlit as st
import os
import logging
import base64
from PIL import Image
from pathlib import Path
from typing import List, Dict, Any

from core.llm_service import LLMService
from core.memory_manager import MemoryManager
from core.openfabric_service import OpenfabricService
from core.stub import Stub

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler()])

# Initialize services
@st.cache_resource
def initialize_services():
    """Initialize all services needed for the app and cache them."""
    llm_service = LLMService()
    memory_manager = MemoryManager()
    
    # Initialize the Stub with app IDs
    app_ids = [
        OpenfabricService.TEXT_TO_IMAGE_APP_ID,
        OpenfabricService.IMAGE_TO_3D_APP_ID
    ]
    
    stub = Stub(app_ids)
    openfabric_service = OpenfabricService(stub)
    
    return llm_service, memory_manager, openfabric_service

# Get path to image in local filesystem
def get_image_path(filename: str) -> str:
    """Convert a relative path to an absolute path for display."""
    return os.path.abspath(filename)

# Get base64 encoded image for display
def get_image_as_base64(filename: str) -> str:
    """Convert an image to base64 for embedding in HTML."""
    try:
        with open(filename, "rb") as f:
            data = f.read()
            return base64.b64encode(data).decode()
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return ""

# Display 3D model viewer
def display_3d_model(model_path: str):
    """Display a 3D model using HTML/JavaScript."""
    if not os.path.exists(model_path):
        st.error(f"Model file not found: {model_path}")
        return
    
    # Generate a unique ID for the container
    model_id = model_path.split('/')[-1].split('.')[0]
    
    # Create HTML for model viewer
    model_viewer_html = f"""
    <div style="width: 100%; height: 400px; margin-bottom: 20px;">
        <model-viewer 
            src="data:model/gltf-binary;base64,{get_image_as_base64(model_path)}"
            alt="3D Model"
            auto-rotate
            camera-controls
            style="width: 100%; height: 100%;"
            id="{model_id}">
        </model-viewer>
    </div>
    
    <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
    """
    
    st.components.v1.html(model_viewer_html, height=450)

# Display past creations
def display_past_creations(past_generations: List[Dict[str, Any]]):
    """Display past generations with options to view or use as reference."""
    if not past_generations:
        st.info("No past creations found.")
        return
    
    st.subheader("📚 Past Creations")
    
    # Create a three-column layout for each creation
    for i, gen in enumerate(past_generations):
        with st.expander(f"#{gen['id']}: {gen['prompt'][:50]}..."):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**Original Prompt:**")
                st.write(gen['prompt'])
                
                st.markdown("**Enhanced Prompt:**")
                st.write(gen['enhanced_prompt'])
                
                # Add a button to reuse this prompt as reference
                if st.button(f"Use as Reference", key=f"ref_{gen['id']}"):
                    st.session_state.prompt = f"Create something similar to #{gen['id']} but "
                    
            with col2:
                if os.path.exists(gen['image_url']):
                    st.image(gen['image_url'], caption="Generated Image", use_column_width=True)
                else:
                    st.warning("Image not found")
                
                if os.path.exists(gen['model_url']):
                    if st.button(f"View 3D Model", key=f"view_{gen['id']}"):
                        st.session_state.view_model = gen['model_url']
                else:
                    st.warning("3D Model not found")

# Main App
def main():
    st.set_page_config(
        page_title="AI Creativity Pipeline",
        page_icon="🎨",
        layout="wide",
    )
    
    # Add custom CSS
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        color: #1E88E5;
    }
    .stButton button {
        background-color: #1E88E5;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'prompt' not in st.session_state:
        st.session_state.prompt = ""
    if 'image_path' not in st.session_state:
        st.session_state.image_path = None
    if 'model_path' not in st.session_state:
        st.session_state.model_path = None
    if 'view_model' not in st.session_state:
        st.session_state.view_model = None
        
    # Initialize services
    llm_service, memory_manager, openfabric_service = initialize_services()
    
    # Page header
    st.title("🚀 AI Creativity Pipeline")
    st.markdown("Transform your text prompts into vivid images and interactive 3D models.")
    
    # Sidebar for app info and settings
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This application uses:
        - Local LLM (DeepSeek/Llama) for prompt enhancement
        - Openfabric's Text-to-Image API
        - Memory system for contextual awareness
        """)
        
        st.header("⚙️ Settings")
        llm_model = st.selectbox(
            "LLM Model",
            ["deepseek-coder", "llama3"],
            index=0
        )
        
        # Check if Ollama is running
        try:
            llm_service._test_connection()
            st.success("✅ Ollama is running")
        except:
            st.error("❌ Ollama is not running. Please start it with 'ollama serve'")
    
    # Create two main columns
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.header("🎨 Create")
        
        # Prompt input
        prompt = st.text_area("Enter your prompt", 
                              value=st.session_state.prompt, 
                              height=100,
                              placeholder="Example: Make me a glowing dragon standing on a cliff at sunset.")
        
        # Process prompt button
        generate_col1, generate_col2 = st.columns([1, 3])
        with generate_col1:
            generate_button = st.button("🚀 Generate", 
                                      type="primary", 
                                      use_container_width=True,
                                      disabled=st.session_state.processing or not prompt)
        
        with generate_col2:
            status_placeholder = st.empty()
        
        # Process the prompt
        if generate_button and prompt:
            st.session_state.processing = True
            st.session_state.prompt = prompt
            
            try:
                # Processing steps with status updates
                status_placeholder.info("🧠 Enhancing prompt with LLM...")
                
                # Step 1: Get recent generations for context
                recent_generations = memory_manager.get_long_term(5)
                
                # Step 2: Enhance the prompt with LLM
                enhanced_prompt = llm_service.analyze_memory(prompt, recent_generations)
                status_placeholder.info(f"🖼️ Generating image... Enhanced prompt: {enhanced_prompt[:50]}...")
                
                # Store in short-term memory
                session_id = 'streamlit-user'
                memory_manager.add_short_term(session_id, 'original_prompt', prompt)
                memory_manager.add_short_term(session_id, 'enhanced_prompt', enhanced_prompt)
                
                # Step 3: Generate image
                image_path = openfabric_service.text_to_image(enhanced_prompt)
                if not image_path:
                    raise Exception("Failed to generate image from prompt")
                
                st.session_state.image_path = image_path
                
                
                
                status_placeholder.success("✅ Generation complete!")
                
            except Exception as e:
                status_placeholder.error(f"❌ Error: {str(e)}")
                logging.error(f"Error in Streamlit app: {e}")
            
            st.session_state.processing = False
            
        # Display results
        if st.session_state.image_path:
            
            status_placeholder.success("Generated Image Path: "+ st.session_state.image_path)
            
    
    with col2:
        st.header("📚 Memory")
        
        # Display past creations from memory
        past_generations = memory_manager.get_long_term(10)
        display_past_creations(past_generations)
    
    

if __name__ == "__main__":
    main() 