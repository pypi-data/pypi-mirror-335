import websocket
import json
import threading
from typing import Dict, Any, Optional, Callable

class WebSocketGenerator:
    """
    WebSocket-based text generation stream.
    
    Allows streaming text generation with real-time token updates.
    """
    def __init__(
        self, 
        base_url: str, 
        worker_id: str, 
        params: Dict[str, Any]
    ):
        """
        Initialize WebSocket generator.
        
        Args:
            base_url (str): Base URL of the service
            worker_id (str): Worker ID to use for generation
            params (dict): Generation parameters
        """
        # Remove trailing slash and construct WebSocket URL
        base_url = base_url.rstrip('/')
        self.ws_url = base_url.replace('http://', 'ws://').replace('https://', 'wss://') + '/ws/generate'
        
        self.worker_id = worker_id
        self.params = params
        
        self._ws = None
        self._stop_event = threading.Event()
        
        # Placeholders for callback functions
        self._on_token = None
        self._on_status = None
        self._on_error = None
        self._on_done = None
    
    def connect(self) -> None:
        """
        Establish WebSocket connection.
        """
        self._ws = websocket.create_connection(self.ws_url)
        
        # Send initial request
        request = {
            'workerId': self.worker_id,
            'params': self.params
        }
        self._ws.send(json.dumps(request))
    
    def generate(self) -> str:
        """
        Synchronous generation method.
        
        Returns:
            str: Complete generated text
        """
        full_text = []
        
        self.on_token(lambda token: full_text.append(token))
        self.start()
        
        # Wait for generation to complete
        while not self._stop_event.is_set():
            self._stop_event.wait(0.1)
        
        return ''.join(full_text)
    
    def start(self) -> threading.Thread:
        """
        Start asynchronous generation.
        
        Returns:
            threading.Thread: Generation thread
        """
        self.connect()
        
        def _generate_thread():
            try:
                while not self._stop_event.is_set():
                    message = self._ws.recv()
                    if not message:
                        break
                    
                    response = json.loads(message)
                    msg_type = response.get('type')
                    
                    if msg_type == 'token' and self._on_token:
                        self._on_token(response.get('text', ''))
                    elif msg_type == 'status' and self._on_status:
                        self._on_status(response.get('message', ''))
                    elif msg_type == 'error' and self._on_error:
                        self._on_error(response.get('message', 'Unknown error'))
                        self._stop_event.set()
                    elif msg_type == 'done':
                        if self._on_done:
                            self._on_done()
                        self._stop_event.set()
            
            except Exception as e:
                if self._on_error:
                    self._on_error(str(e))
            finally:
                if self._ws:
                    self._ws.close()
                self._stop_event.set()
        
        thread = threading.Thread(target=_generate_thread, daemon=True)
        thread.start()
        return thread
    
    def stop(self) -> None:
        """
        Stop the generation process.
        """
        self._stop_event.set()
        if self._ws:
            self._ws.close()
    
    def on_token(self, callback: Callable[[str], None]) -> 'WebSocketGenerator':
        """
        Set callback for token generation.
        
        Args:
            callback (callable): Function to call with each token
        
        Returns:
            WebSocketGenerator: Self, for method chaining
        """
        self._on_token = callback
        return self
    
    def on_status(self, callback: Callable[[str], None]) -> 'WebSocketGenerator':
        """
        Set callback for status updates.
        
        Args:
            callback (callable): Function to call with status messages
        
        Returns:
            WebSocketGenerator: Self, for method chaining
        """
        self._on_status = callback
        return self
    
    def on_error(self, callback: Callable[[str], None]) -> 'WebSocketGenerator':
        """
        Set callback for error handling.
        
        Args:
            callback (callable): Function to call with error messages
        
        Returns:
            WebSocketGenerator: Self, for method chaining
        """
        self._on_error = callback
        return self
    
    def on_done(self, callback: Callable[[], None]) -> 'WebSocketGenerator':
        """
        Set callback for generation completion.
        
        Args:
            callback (callable): Function to call when generation is done
        
        Returns:
            WebSocketGenerator: Self, for method chaining
        """
        self._on_done = callback
        return self
    
    def __iter__(self):
        """
        Allows the generator to be used as an iterator.
        
        Yields:
            str: Generated tokens
        """
        tokens = []
        
        def token_callback(token):
            tokens.append(token)
            yield token
        
        self.on_token(token_callback)
        self.start()
        
        while not self._stop_event.is_set():
            if tokens:
                yield tokens.pop(0)
            else:
                self._stop_event.wait(0.1)