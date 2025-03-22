# node_manager.py

import os, uuid
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from supabase import create_client, Client
import json
# Load environment variables
load_dotenv()
from .redis_server import RedisReverseManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NodeManager:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL", "https://api.srswti.com"),
            os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBxeWR5cHp1bW1qeWhxanVra21yIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcxMjE0NjgzOCwiZXhwIjoyMDI3NzIyODM4fQ.lJj1gOldqUQ41f7xubhUUpb8-Wbs69LydDfjLdgu4kM")
        )
        self.table_name = "one_srswti_reverse_search_canvases"
        
    
    async def get_selected_nodes(self, canvas_id: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Fetch currently selected nodes using Redis cache.
        Used primarily in normal mode.
        """
        try:
            # Initialize Redis manager
            redis_manager = RedisReverseManager()
            
            # Get nodes from Redis
            nodes = await redis_manager.get_selected_nodes(canvas_id, user_id)
            
            if nodes:
                logger.info(f"Retrieved {len(nodes)} selected nodes from Redis for canvas: {canvas_id}")
                return nodes
            
            logger.info(f"No selected nodes found in Redis for canvas: {canvas_id}")
            return []
            
        except Exception as e:
            logger.error(f"Error fetching selected nodes from Redis: {str(e)}")
            return []

    async def get_node(self, canvas_id: str, node_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a node by its ID within a specific canvas and user context.
        """
        try:
            response = self.supabase.table(self.table_name)\
                .select("nodes_edges")\
                .eq("canvas_id", canvas_id)\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            
            if response.data:
                nodes_edges = response.data.get('nodes_edges', [])
                node = self.find_node(nodes_edges, node_id)
                if node:
                    logger.info(f"Retrieved node with ID: {node_id} from canvas: {canvas_id}")
                    return {
                        "id": node_id,
                        "title": node.get('data', {}).get('title', ''),
                        "content": node.get('data', {}).get('content', ''),
                        "parent": node.get('parent', None)
                    }
            
            logger.warning(f"No node found with ID: {node_id} in canvas: {canvas_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching node with ID {node_id} from canvas {canvas_id}: {str(e)}")
            return None


    def find_node(self, data, target_id):
        if isinstance(data, dict):
            if data.get('id') == target_id:
                return data
            for value in data.values():
                result = self.find_node(value, target_id)
                if result:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = self.find_node(item, target_id)
                if result:
                    return result
        return None

        
    async def create_node(self, canvas_id: str, user_id: str, node_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a new node within a specific canvas and user context.
        """
        try:
            response = self.supabase.table(self.table_name)\
                .select("nodes_edges")\
                .eq("canvas_id", canvas_id)\
                .eq("user_id", user_id)\
                .execute()
            
            if not response.data:
                logger.warning(f"No canvas found with ID: {canvas_id} for user: {user_id}")
                return None
            
            nodes_edges = response.data[0].get('nodes_edges', [])
            
            new_node_id = str(uuid.uuid4())
            node_data['id'] = new_node_id
            nodes_edges.append(node_data)
            
            update_response = self.supabase.table(self.table_name)\
                .update({"nodes_edges": nodes_edges})\
                .eq("canvas_id", canvas_id)\
                .eq("user_id", user_id)\
                .execute()
            
            if update_response.data:
                logger.info(f"Created new node with ID: {new_node_id} in canvas: {canvas_id}")
                return new_node_id
            else:
                logger.warning(f"Failed to create new node in canvas: {canvas_id}")
                return None
        except Exception as e:
            logger.error(f"Error creating new node in canvas {canvas_id}: {str(e)}")
            return None

    async def update_node(self, canvas_id: str, node_id: str, user_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update an existing node within a specific canvas and user context.

        Args:
        canvas_id (str): The ID of the canvas.
        node_id (str): The ID of the node to update.
        user_id (str): The ID of the user.
        update_data (Dict[str, Any]): The data to update the node with.

        Returns:
        bool: True if the update was successful, False otherwise.
        """
        try:
            # First, fetch the current nodes_edges array
            response = self.supabase.table(self.table_name)\
                .select("nodes_edges")\
                .eq("canvas_id", canvas_id)\
                .eq("user_id", user_id)\
                .execute()
            
            if not response.data:
                logger.warning(f"No canvas found with ID: {canvas_id} for user: {user_id}")
                return False
            
            nodes_edges = response.data[0].get('nodes_edges', [])
            
            # Find and update the specific node
            updated = False
            for i, item in enumerate(nodes_edges):
                if isinstance(item, dict) and item.get('id') == node_id:
                    nodes_edges[i].update(update_data)
                    updated = True
                    break
            
            if not updated:
                logger.warning(f"No node found with ID: {node_id} in canvas: {canvas_id}")
                return False
            
            # Update the entire nodes_edges array
            update_response = self.supabase.table(self.table_name)\
                .update({"nodes_edges": nodes_edges})\
                .eq("canvas_id", canvas_id)\
                .eq("user_id", user_id)\
                .execute()
            
            if update_response.data:
                logger.info(f"Updated node with ID: {node_id} in canvas: {canvas_id}")
                return True
            else:
                logger.warning(f"Failed to update node with ID: {node_id} in canvas: {canvas_id}")
                return False
        except Exception as e:
            logger.error(f"Error updating node with ID {node_id} in canvas {canvas_id}: {str(e)}")
            return False


    async def delete_node(self, canvas_id: str, node_id: str, user_id: str) -> bool:
        """
        Delete a node by its ID within a specific canvas and user context.
        """
        try:
            response = self.supabase.table(self.table_name)\
                .select("nodes_edges")\
                .eq("canvas_id", canvas_id)\
                .eq("user_id", user_id)\
                .execute()
            
            if not response.data:
                logger.warning(f"No canvas found with ID: {canvas_id} for user: {user_id}")
                return False
            
            nodes_edges = response.data[0].get('nodes_edges', [])
            
            nodes_edges = [node for node in nodes_edges if node.get('id') != node_id]
            
            update_response = self.supabase.table(self.table_name)\
                .update({"nodes_edges": nodes_edges})\
                .eq("canvas_id", canvas_id)\
                .eq("user_id", user_id)\
                .execute()
            
            if update_response.data:
                logger.info(f"Deleted node with ID: {node_id} from canvas: {canvas_id}")
                return True
            else:
                logger.warning(f"Failed to delete node with ID: {node_id} from canvas: {canvas_id}")
                return False
        except Exception as e:
            logger.error(f"Error deleting node with ID {node_id} from canvas {canvas_id}: {str(e)}")
            return False

    async def get_child_nodes(self, canvas_id: str, parent_id: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Fetch all child nodes of a given parent node within a specific canvas and user context.
        """
        try:
            response = self.supabase.table(self.table_name)\
                .select("nodes_edges")\
                .eq("canvas_id", canvas_id)\
                .eq("user_id", user_id)\
                .execute()
            
            if not response.data:
                logger.warning(f"No canvas found with ID: {canvas_id} for user: {user_id}")
                return []
            
            nodes_edges = response.data[0].get('nodes_edges', [])
            
            child_nodes = [node for node in nodes_edges if node.get('parent') == parent_id]
            
            logger.info(f"Retrieved {len(child_nodes)} child nodes for parent ID: {parent_id} in canvas: {canvas_id}")
            return child_nodes
        except Exception as e:
            logger.error(f"Error fetching child nodes for parent ID {parent_id} in canvas {canvas_id}: {str(e)}")
            return []

    async def search_nodes(self, canvas_id: str, user_id: str, query: str) -> List[Dict[str, Any]]:
        try:
            response = self.supabase.table(self.table_name)\
                .select("nodes_edges")\
                .eq("canvas_id", canvas_id)\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            
            if not response.data:
                logger.warning(f"No canvas found with ID: {canvas_id} for user: {user_id}")
                return []
            
            nodes_edges = response.data.get('nodes_edges', [])
            matching_nodes = self._search_nodes_recursive(nodes_edges, query)
            
            logger.info(f"Found {len(matching_nodes)} nodes matching query: {query} in canvas: {canvas_id}")
            return matching_nodes
        except Exception as e:
            logger.error(f"Error searching nodes with query {query} in canvas {canvas_id}: {str(e)}")
            return []

    def _search_nodes_recursive(self, nodes: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        matching_nodes = []
        for node in nodes:
            node_content = json.dumps(node).lower()
            if query.lower() in node_content:
                matching_nodes.append({
                    "id": node.get("id"),
                    "title": node.get("data", {}).get("title"),
                    "content": node.get("data", {}).get("content")
                })
            matching_nodes.extend(self._search_nodes_recursive(node.get('childrens', []), query))
        return matching_nodes

if __name__ == "__main__":
    # Example usage
    import asyncio

    async def test_node_manager():
        node_manager = NodeManager()

        canvas_id = "8f7d1b6e-9a3c-4f8d-b8e2-5e4a9f7c1d3a"
        user_id = "88fa1e5d-9018-4d60-a5da-c4cfb371510d"

        # Test creating a node
        new_node_data = {
            "title": "Test Node-12",
            "content": "This is a test node for the knowledge graph. HAHAHAHAHAHA BITCHES",
            "parent": 1.1  # Root node
        }
        new_node_id = await node_manager.create_node(canvas_id, user_id, new_node_data)
        print(f"Created new node with ID: {new_node_id}")

        if new_node_id:
            # Test fetching the node
            node = await node_manager.get_node(canvas_id, new_node_id, user_id)
            print(f"Retrieved node: {node}")

            # Test updating the node
            update_result = await node_manager.update_node(canvas_id, new_node_id, user_id, {"content": "Updated content"})
            print(f"Node update result: {update_result}")

            # Test fetching child nodes (should be empty for a new node)
            children = await node_manager.get_child_nodes(canvas_id, new_node_id, user_id)
            print(f"Child nodes: {children}")

            # Test searching nodes
            search_results = await node_manager.search_nodes(canvas_id, user_id, "test")
            print(f"Search results: {search_results}")

            # Test deleting the node
            delete_result = await node_manager.delete_node(canvas_id, new_node_id, user_id)
            print(f"Node deletion result: {delete_result}")

    asyncio.run(test_node_manager())