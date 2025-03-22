from fastapi import FastAPI
from redis.asyncio import Redis
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import logging, uvicorn

logger = logging.getLogger(__name__)

app = FastAPI(
    title="SRSWTI Redis Server",
    description="Redis server for SRSWTI that manages user profiles, selected nodes and other stateful data. Provides endpoints for storing and retrieving user selections and profile information.",
    version="1.5"
)
class SelectedNode(BaseModel):
    id: str
    data: Dict[str, Any] 

class UserProfile(BaseModel):
    user_id: str
    profile_data: Dict[str, Any]

class RedisReverseManager:
    def __init__(self):
        self.redis = Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )

    async def store_selected_nodes(self, canvas_id: str, user_id: str, nodes: List[Dict]) -> bool:
        """Store selected nodes with minimal required data. 
        Sending an empty nodes list will clear all selections.
        
        Args:
            canvas_id (str): The ID of the canvas
            user_id (str): The ID of the user
            nodes (List[Dict]): List of node dictionaries. Can be empty to clear selections
            
        Returns:
            bool: True if operation was successful, False otherwise
        """
        try:
            key = f"selected:{user_id}:{canvas_id}"
            
            # Handle deselection via empty list
            if not nodes:
                await self.redis.delete(key)
                logger.info(f"Cleared selected nodes for canvas: {canvas_id}")
                return True
            
            # Format nodes to store only necessary data
            formatted_nodes = [{
                "id": node.get('id'),
                "title": node.get('data', {}).get('title', ''),
                "content": node.get('data', {}).get('content', ''),
                "parent": node.get('parent_id', None)
            } for node in nodes]
            
            # Store the formatted nodes
            await self.redis.set(key, json.dumps(formatted_nodes))
            logger.info(f"Stored {len(formatted_nodes)} nodes for canvas: {canvas_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing selected nodes: {str(e)}")
            return False

    async def clear_selected_nodes(self, canvas_id: str, user_id: str) -> bool:
        """Clear all selected nodes for a specific user and canvas
        
        Args:
            canvas_id (str): The ID of the canvas
            user_id (str): The ID of the user
            
        Returns:
            bool: True if operation was successful, False otherwise
        """
        try:
            key = f"selected:{user_id}:{canvas_id}"
            deleted = await self.redis.delete(key)
            logger.info(f"Cleared selected nodes for canvas: {canvas_id}")
            return bool(deleted)
        except Exception as e:
            logger.error(f"Error clearing selected nodes: {str(e)}")
            return False

    async def get_selected_nodes(self, canvas_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Get selected nodes matching your existing format"""
        try:
            key = f"selected:{user_id}:{canvas_id}"
            data = await self.redis.get(key)
            
            if data:
                nodes = json.loads(data)
                logger.info(f"Retrieved {len(nodes)} selected nodes for canvas: {canvas_id}")
                return nodes
            
            logger.info(f"No selected nodes found for canvas: {canvas_id}")
            return []
            
        except Exception as e:
            logger.error(f"Error fetching selected nodes: {str(e)}")
            return []

    # New methods for user profile management
    async def store_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Store user profile in Redis"""
        try:
            key = f"user_profile:{user_id}"
            await self.redis.set(key, json.dumps(profile_data))
            logger.info(f"Stored profile for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error storing user profile: {str(e)}")
            return False

    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile from Redis"""
        try:
            key = f"user_profile:{user_id}"
            data = await self.redis.get(key)
            
            if data:
                profile = json.loads(data)
                logger.info(f"Retrieved profile for user: {user_id}")
                return profile
            
            logger.info(f"No profile found for user: {user_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching user profile: {str(e)}")
            return None

    async def delete_user_profile(self, user_id: str) -> bool:
        """Delete user profile from Redis (for force refresh)"""
        try:
            key = f"user_profile:{user_id}"
            deleted = await self.redis.delete(key)
            logger.info(f"Deleted profile for user: {user_id}")
            return bool(deleted)
        except Exception as e:
            logger.error(f"Error deleting user profile: {str(e)}")
            return False

redis_manager = RedisReverseManager()

# Existing endpoints
@app.post("/nodes/selected/{canvas_id}/{user_id}")
async def update_selected_nodes(canvas_id: str, user_id: str, nodes: List[dict]):
    """Update or clear selected nodes
    
    Send an empty list to clear selections, or a list of nodes to update selections.
    """
    success = await redis_manager.store_selected_nodes(canvas_id, user_id, nodes)
    return {
        "status": "success" if success else "failed",
        "message": "Nodes updated successfully" if success else "Failed to update nodes"
    }

@app.delete("/nodes/selected/{canvas_id}/{user_id}")
async def clear_selected_nodes(canvas_id: str, user_id: str):
    """Clear all selected nodes for a specific user and canvas"""
    success = await redis_manager.clear_selected_nodes(canvas_id, user_id)
    return {
        "status": "success" if success else "failed",
        "message": f"Selected nodes cleared for canvas {canvas_id}" if success else "Failed to clear selected nodes"
    }

@app.get("/nodes/selected/{canvas_id}/{user_id}")
async def get_selected_nodes(canvas_id: str, user_id: str):
    nodes = await redis_manager.get_selected_nodes(canvas_id, user_id)
    return {"selected_nodes": nodes}

# New endpoints for user profiles
@app.post("/users/profile/{user_id}")
async def store_user_profile(user_id: str, profile: Dict[str, Any]):
    success = await redis_manager.store_user_profile(user_id, profile)
    return {"status": "success" if success else "failed"}

@app.get("/users/profile/{user_id}")
async def get_user_profile(user_id: str):
    profile = await redis_manager.get_user_profile(user_id)
    if profile:
        return {"profile": profile}
    return {"profile": None}

@app.delete("/users/profile/{user_id}")
async def delete_user_profile(user_id: str):
    success = await redis_manager.delete_user_profile(user_id)
    return {"status": "success" if success else "failed"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)