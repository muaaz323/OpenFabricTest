import logging
from typing import Dict

from ontology_dc8f06af066e4a7880a5938933236037.config import ConfigClass
from ontology_dc8f06af066e4a7880a5938933236037.input import InputClass
from ontology_dc8f06af066e4a7880a5938933236037.output import OutputClass
from openfabric_pysdk.context import AppModel, State
from core.stub import Stub
from core.llm_service import LLMService
from core.openfabric_service import OpenfabricService
from core.memory_manager import MemoryManager

# Configurations for the app
configurations: Dict[str, ConfigClass] = dict()

# Create services
llm_service = LLMService()
memory_manager = MemoryManager()

############################################################
# Config callback function
############################################################
def config(configuration: Dict[str, ConfigClass], state: State) -> None:
    """
    Stores user-specific configuration data.

    Args:
        configuration (Dict[str, ConfigClass]): A mapping of user IDs to configuration objects.
        state (State): The current state of the application (not used in this implementation).
    """
    for uid, conf in configuration.items():
        logging.info(f"Saving new config for user with id:'{uid}'")
        configurations[uid] = conf


############################################################
# Execution callback function
############################################################
def execute(model: AppModel) -> None:
    """
    Main execution entry point for handling a model pass.

    Args:
        model (AppModel): The model object containing request and response structures.
    """

    # Retrieve input
    request: InputClass = model.request
    user_prompt = request.prompt

    # Log the received prompt
    logging.info(f"Received prompt: {user_prompt}")

    # Retrieve user config
    user_config: ConfigClass = configurations.get('super-user', None)
    logging.info(f"Current configurations: {configurations}")

    # Initialize the Stub with app IDs
    app_ids = [
        OpenfabricService.TEXT_TO_IMAGE_APP_ID,
        OpenfabricService.IMAGE_TO_3D_APP_ID
    ]
    
    if user_config and user_config.app_ids:
        app_ids = user_config.app_ids
        
    stub = Stub(app_ids)
    
    # Initialize services
    openfabric_service = OpenfabricService(stub)
    
    # Process the request
    try:
        # Step 1: Get recent generations from memory for context
        recent_generations = memory_manager.get_long_term(5)
        
        # Step 2: Enhance the prompt using LLM and memory context
        enhanced_prompt = llm_service.analyze_memory(user_prompt, recent_generations)
        logging.info(f"Enhanced prompt: {enhanced_prompt}")
        
        # Store in short-term memory
        session_id = 'super-user'  # In a real app, this would be a unique session ID
        memory_manager.add_short_term(session_id, 'original_prompt', user_prompt)
        memory_manager.add_short_term(session_id, 'enhanced_prompt', enhanced_prompt)
        
        # Step 3: Generate image from enhanced prompt
        image_path = openfabric_service.text_to_image(enhanced_prompt)
        if not image_path:
            raise Exception("Failed to generate image from prompt")
            
        logging.info(f"Generated image saved at: {image_path}")
        memory_manager.add_short_term(session_id, 'image_path', image_path)
        
        # Step 4: Generate 3D model from image
        model_path = openfabric_service.image_to_3d(image_path)
        if not model_path:
            raise Exception("Failed to generate 3D model from image")
            
        logging.info(f"Generated 3D model saved at: {model_path}")
        memory_manager.add_short_term(session_id, 'model_path', model_path)
        
        # Step 5: Store the complete generation in long-term memory
        memory_manager.add_long_term(
            prompt=user_prompt,
            enhanced_prompt=enhanced_prompt,
            image_url=image_path,
            model_url=model_path
        )
        
        # Prepare success response
        response: OutputClass = model.response
        response.message = f"Successfully created 3D model from prompt: '{user_prompt}'"
        response.image_url = image_path
        response.model_url = model_path
        
    except Exception as e:
        logging.error(f"Error in execution pipeline: {e}")
        
        # Prepare error response
        response: OutputClass = model.response
        response.message = f"Error: {str(e)}"