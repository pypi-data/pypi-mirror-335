# EXPLANATION# - This file restores the FastAPI app and /process_selected_nodes endpoint from r1.py.
# - It needs FastAPI, CORSMiddleware, and HTTPException for the API setup.
# - TextInput is imported from .models for the endpoint parameter.
# - ResponseGenerator and NodeManager are external dependencies used in the original logic.
# - Logging is set up to match the package's style.

import logging, traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import TextInput  # Importing from package's models
from .helpers.response_gen_v2 import ResponseGenerator  # External dependency    
from .helpers.node_manager import NodeManager  # External dependency

# Configure logger
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (adjust in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.post("/process_selected_nodes")
async def process_selected_nodes(input_data: TextInput):
    """
    Process text input with selected nodes using normal mode.
    This endpoint handles node-related queries with detailed analysis.

    Args:
        input_data (TextInput): Pydantic model containing text_input, canvas_id, and user_id

    Returns:
        dict: Response with mode, content, nodes, and search details

    Raises:
        HTTPException: If no response is generated (404) or an internal error occurs (500)
    """
    try:
        response_generator = ResponseGenerator()

        logger.info(f"Processing selected nodes request for user: {input_data.user_id}")
        logger.info(f"Input text: {input_data.text_input}")
        
        # Generate response using normal mode
        response = await response_generator.generate_response(
            user_input=input_data.text_input,
            canvas_id=input_data.canvas_id,
            user_id=input_data.user_id,
            mode="normal"  # Force normal mode for selected nodes
        )
        
        if not response:
            raise HTTPException(
                status_code=404, 
                detail="No response generated"
            )
        
        # Return the response with all its components
        return {
            "mode": response.get("mode", "normal"),
            "content": response.get("content", {}),
            "nodes": response.get("nodes", []),
            "search_required": response.get("search_required", False),
            "search_reasoning": response.get("search_reasoning", ""),
            "flow_path": response.get("flow_path", "direct"),
            "search_results": response.get("search_results", None)
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing selected nodes: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )