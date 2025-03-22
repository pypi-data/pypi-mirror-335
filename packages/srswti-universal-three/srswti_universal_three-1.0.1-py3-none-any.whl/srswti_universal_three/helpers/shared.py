import queue

# Shared queue for communication between STT and WebSocket handler
transcript_queue = queue.Queue()

# Streaming limit in milliseconds (4 minutes)
STREAMING_LIMIT = 240000