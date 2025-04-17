"""
Test script to verify basic functionality of the core components.
This doesn't test the full pipeline but validates that each service can be initialized.
"""

import logging
import os
import unittest

from core.llm_service import LLMService
from core.memory_manager import MemoryManager
from core.openfabric_service import OpenfabricService
from core.stub import Stub

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class TestAppComponents(unittest.TestCase):
    """Test case for verifying basic functionality of app components."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create test directories
        os.makedirs("datastore/test", exist_ok=True)
        
        # Initialize test memory manager with test DB
        self.memory_manager = MemoryManager(db_path="datastore/test/test_memory.db")
        
        # Initialize LLM service (will just check connection)
        self.llm_service = LLMService()
        
        # Initialize stub and Openfabric service
        app_ids = [
            OpenfabricService.TEXT_TO_IMAGE_APP_ID, 
            OpenfabricService.IMAGE_TO_3D_APP_ID
        ]
        self.stub = Stub(app_ids)
        self.openfabric_service = OpenfabricService(self.stub)
    
    def test_memory_manager(self):
        """Test the memory manager's short-term memory functionality."""
        # Test short-term memory
        session_id = "test_session"
        self.memory_manager.add_short_term(session_id, "test_key", "test_value")
        value = self.memory_manager.get_short_term(session_id, "test_key")
        self.assertEqual(value, "test_value")
        
        # Test clearing short-term memory
        self.memory_manager.clear_short_term(session_id)
        value = self.memory_manager.get_short_term(session_id, "test_key")
        self.assertIsNone(value)
    
    def test_llm_service_initialization(self):
        """Test that the LLM service initializes without errors."""
        # Just checking if the service was initialized without errors
        self.assertIsNotNone(self.llm_service)
    
    def test_openfabric_service_initialization(self):
        """Test that the Openfabric service initializes without errors."""
        # Just checking if the service was initialized without errors
        self.assertIsNotNone(self.openfabric_service)
        self.assertEqual(self.openfabric_service.TEXT_TO_IMAGE_APP_ID, "f0997a01-d6d3-a5fe-53d8-561300318557")
        self.assertEqual(self.openfabric_service.IMAGE_TO_3D_APP_ID, "69543f29-4d41-4afc-7f29-3d51591f11eb")


if __name__ == "__main__":
    unittest.main() 