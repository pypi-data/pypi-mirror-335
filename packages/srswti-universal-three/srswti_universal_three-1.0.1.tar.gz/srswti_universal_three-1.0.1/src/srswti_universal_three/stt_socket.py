# EXPLANATION# - This file contains the SRSWTISTT class for handling speech-to-text only WebSocket interfaces
# - It's the simplest of the WebSocket handlers, just forwarding transcript data
# - It doesn't need LLM or TTS functionality, only STT processing
# - Session management and cleanup are still important for resource management

import asyncio
import json
import logging
import uuid
import os
import time
import queue
from typing import Dict, Any

from .helpers.stt import main as stt_main, ResumableMicrophoneStream
from .helpers.shared import transcript_queue, STREAMING_LIMIT

# Configure logger
logger = logging.getLogger(__name__)
class SRSWTISTT:
    """Handles WebSocket connections for speech-to-text only functionality."""
    
    def __init__(self):
        """Initialize the STT handler with a unique session ID."""
        self.session_id = str(uuid.uuid4())
        self.stt_task = None
        self.queue_processor = None
        self.last_restart_time = time.time()
        
        # Set up session-specific logger
        self.session_logger = self._setup_logger()
    
    def _setup_logger(self):
        """Set up session-specific logger with file and console handlers."""
        session_logger = logging.getLogger(f"stt_session_{self.session_id}")
        session_logger.setLevel(logging.DEBUG)
        
        log_directory = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_directory, exist_ok=True)
        log_file_path = os.path.join(log_directory, f"stt_session_{self.session_id}.log")
        
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        
        session_logger.handlers = [file_handler, console_handler]
        session_logger.propagate = False
        
        session_logger.info(f"Starting new STT WebSocket session: {self.session_id}")
        return session_logger
    
    async def process_transcript(self, websocket):
        """
        Process transcript data from STT and forward to WebSocket.
        
        Args:
            websocket: WebSocket connection
        """
        self.session_logger.info("Starting transcript processing")
        with ResumableMicrophoneStream() as stream:
            while not stream.closed:
                try:
                    transcript_data = transcript_queue.get_nowait()
                    if stream.restart_counter > 0 and "timestamp" in transcript_data:
                        if transcript_data["timestamp"] > self.last_restart_time + STREAMING_LIMIT / 1000:
                            self.last_restart_time = time.time()
                            self.session_logger.info(f"Stream restarted, updated last_restart_time to {self.last_restart_time}")
                    
                    if isinstance(transcript_data, dict) and transcript_data.get("type") == "transcript":
                        text = transcript_data.get("text", "").strip()
                        speech_final = transcript_data.get("speech_final", False)
                        timestamp = transcript_data.get("timestamp", 0)
                        
                        if timestamp < self.last_restart_time:
                            self.session_logger.debug(f"Ignoring old transcript: {text}")
                            continue
                        
                        if text:
                            self.session_logger.debug(f"Received transcript: {text}, speech_final: {speech_final}")
                            await websocket.send(json.dumps({
                                "type": "transcript",
                                "content": text,
                                "speech_final": speech_final
                            }))
                    transcript_queue.task_done()
                except queue.Empty:
                    await asyncio.sleep(0.1)
                except Exception as e:
                    self.session_logger.error(f"Error processing transcript: {str(e)}")
    
    async def handle_stt_websocket(self, websocket):
        """
        Main WebSocket handler for STT-only functionality.
        
        Args:
            websocket: WebSocket connection
        """
        try:
            self.session_logger.info("Starting STT WebSocket handler")
            loop = asyncio.get_event_loop()
            self.stt_task = loop.run_in_executor(None, stt_main)
            self.session_logger.info("STT task started")

            self.queue_processor = asyncio.create_task(self.process_transcript(websocket))
            
            # Simply wait for connection to close
            await websocket.wait_closed()
            
        except Exception as e:
            self.session_logger.error(f"Error in STT websocket handler: {str(e)}", exc_info=True)
            try:
                await websocket.send(json.dumps({
                    "type": "error",
                    "content": f"Internal server error occurred: {str(e)}"
                }))
            except:
                pass
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Clean up resources when WebSocket connection closes."""
        self.session_logger.info("Starting STT cleanup")
        
        if self.stt_task:
            self.stt_task.cancel()
            self.session_logger.info("STT task cancelled")
            
        if self.queue_processor:
            self.queue_processor.cancel()
            try:
                await asyncio.wait_for(self.queue_processor, timeout=2.0)
                self.session_logger.info("Queue processor shut down")
            except asyncio.TimeoutError:
                self.session_logger.error("Queue processor shutdown timed out")
            except Exception as e:
                self.session_logger.error(f"Error shutting down queue processor: {e}")
                
        self.session_logger.info(f"STT session {self.session_id} fully closed") 