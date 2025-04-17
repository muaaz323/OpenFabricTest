import os
import json
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime


class MemoryManager:
    """
    A class to manage both short-term (session) and long-term (persistent) memory for the application.
    
    Short-term memory is stored in-memory during runtime.
    Long-term memory is stored in SQLite database.
    """
    
    def __init__(self, db_path: str = "datastore/memory.db"):
        """
        Initialize the memory manager with paths to storage.
        
        Args:
            db_path (str): Path to SQLite database for long-term memory
        """
        self.short_term_memory: Dict[str, Dict[str, Any]] = {}
        self.db_path = db_path
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize SQLite database for long-term memory
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize the SQLite database schema if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table for storing generations
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS generations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            prompt TEXT,
            enhanced_prompt TEXT,
            image_url TEXT,
            model_url TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_short_term(self, session_id: str, key: str, value: Any) -> None:
        """
        Add item to short-term memory
        
        Args:
            session_id (str): Unique identifier for the session
            key (str): Key for the memory item
            value (Any): Value to store
        """
        if session_id not in self.short_term_memory:
            self.short_term_memory[session_id] = {}
        
        self.short_term_memory[session_id][key] = value
    
    def get_short_term(self, session_id: str, key: str) -> Optional[Any]:
        """
        Retrieve item from short-term memory
        
        Args:
            session_id (str): Unique identifier for the session
            key (str): Key for the memory item
            
        Returns:
            Optional[Any]: The stored value or None if not found
        """
        if session_id not in self.short_term_memory:
            return None
        
        return self.short_term_memory[session_id].get(key)
    
    def clear_short_term(self, session_id: str) -> None:
        """
        Clear all short-term memory for a session
        
        Args:
            session_id (str): Unique identifier for the session
        """
        if session_id in self.short_term_memory:
            del self.short_term_memory[session_id]
    
    def add_long_term(self, prompt: str, enhanced_prompt: str, image_url: str, model_url: str) -> int:
        """
        Add a generation to long-term memory
        
        Args:
            prompt (str): Original user prompt
            enhanced_prompt (str): Enhanced prompt from LLM
            image_url (str): URL to the generated image
            model_url (str): URL to the generated 3D model
            
        Returns:
            int: ID of the inserted record
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute(
            '''INSERT INTO generations (timestamp, prompt, enhanced_prompt, image_url, model_url) 
            VALUES (?, ?, ?, ?, ?)''',
            (timestamp, prompt, enhanced_prompt, image_url, model_url)
        )
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return record_id
    
    def get_long_term(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve recent generations from long-term memory
        
        Args:
            limit (int): Maximum number of records to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of generation records
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            '''SELECT * FROM generations ORDER BY timestamp DESC LIMIT ?''',
            (limit,)
        )
        
        rows = cursor.fetchall()
        result = [dict(row) for row in rows]
        
        conn.close()
        return result
    
    def search_long_term(self, query: str) -> List[Dict[str, Any]]:
        """
        Search long-term memory for relevant generations
        
        Args:
            query (str): Search query string
            
        Returns:
            List[Dict[str, Any]]: List of matching generation records
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        search_term = f"%{query}%"
        cursor.execute(
            '''SELECT * FROM generations 
            WHERE prompt LIKE ? OR enhanced_prompt LIKE ? 
            ORDER BY timestamp DESC''',
            (search_term, search_term)
        )
        
        rows = cursor.fetchall()
        result = [dict(row) for row in rows]
        
        conn.close()
        return result 