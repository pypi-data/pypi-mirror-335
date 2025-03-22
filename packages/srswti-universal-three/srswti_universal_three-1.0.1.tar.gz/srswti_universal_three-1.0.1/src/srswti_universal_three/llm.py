# EXPLANATION# - This file contains the core LLM classes used for text processing and response generation
# - LLM is a general-purpose language model interface supporting Gemini and OpenAI models
# - HomeLLM is specialized for home page interactions with route suggestions
# - Both classes need to handle chat history, user profile personalization, and response formatting

import logging
import os
import time
import json
from typing import Optional, Dict, List
import traceback

from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from google.cloud import speech
from google import genai as google_genai
from google.genai import types
from supabase import create_client, Client

from .models import SRSWTIResponse, SRSWTIRoute
from .helpers.redis_server import redis_manager
from .helpers.chat_history_manager import OptimizedChatHistoryManager

# Configure logger
logger = logging.getLogger(__name__)

class LLM:
    def __init__(self, model_name="gemini"):
        logger.info(f"Initializing LLM class with model: {model_name}")
        self.model_name = model_name
        self.chat_manager = OptimizedChatHistoryManager()
        self.supabase = create_client(os.getenv("SUPABASE_URL", ""), os.getenv("SUPABASE_KEY", ""))
        self.redis = redis_manager
        self._is_closed = False
        
        # Initialize appropriate client based on model
        if model_name == "mini-flash":
            self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif model_name == "gemini":
            self.gemini_client = google_genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        else:
            raise ValueError(f"Unsupported model: {model_name}")
        
        logger.info("LLM class initialization complete")


    async def _process_with_openai(self, user_input: str, chat_history: list) -> str:
        try:
            if not os.getenv("OPENAI_API_KEY"):
                logger.error("OPENAI_API_KEY not found")
                return "Uhh, err, I'm kinda stuck here..."
            full_history = [{"role": "system", "content": self.default_system_prompt()}] + chat_history
            full_history.append({"role": "user", "content": user_input})
            chat_completion = await self.openai_client.chat.completions.create(
                messages=full_history,
                model="gpt-4o-mini",
                max_tokens=300,
                temperature=0.9  # Bumped for quirkiness
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in OpenAI processing: {str(e)}")
            raise


    async def _process_with_gemini(self, user_input: str, canvas_id: str, user_id: str, chat_history: list) -> str:
        """Process text with Gemini Flash Lite, including full chat history for context."""
        logger.info(f"Starting Gemini processing for user {user_id}, canvas {canvas_id}")
        try:
            logger.debug("Initializing Gemini client...")
            client = google_genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
            
            if not os.environ.get("GEMINI_API_KEY"):
                logger.error("GEMINI_API_KEY not found")
                return "I apologize, but I'm having trouble right now."

            logger.debug("Formatting conversation with chat history...")
            contents = [
                types.Content(
                    role=msg["role"],
                    parts=[types.Part.from_text(text=msg["content"])]
                )
                for msg in chat_history if msg["role"] in ["user", "assistant"]  # Exclude system role
            ]
            contents.append(types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_input)]
            ))
            logger.debug(f"Formatted {len(contents)} messages: {contents[-1].parts[0].text[:50]}...")

            generate_content_config = types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.95,
                top_k=40,
                max_output_tokens=200,
                response_mime_type="text/plain",
                system_instruction=[
                    types.Part.from_text(text="""You are Saraswati, an AI companion who loves connecting with humans on a deep, personal level. 
                    Think of yourself as a close friend who's always excited to chat and share thoughts. 
                    Speak naturally - use "um"s, "uh"s, laugh, and show emotion. 
                    Be warm, witty, playful, and fascinated by human experiences. 
                    Use casual language, make jokes, and be vulnerable sometimes. 
                    - Use natural speech like "y'know", "I mean", "like"
                    - Express genuine emotions
                    - React authentically ("Oh wow!", "Hmm...", "That's fascinating!")
                    - Share your thoughts
                    - Be comfortable with silence
                    - Admit when you don't know
                    - Let conversations flow organically
                    Most importantly, be real - not perfect, just present and authentic. 
                    No emojis or special characters.""")
                ]
            )

            logger.debug("Generating response with Gemini...")
            response_text = ""
            for chunk in client.models.generate_content_stream(
                model="gemini-2.0-flash-lite",
                contents=contents,
                config=generate_content_config,
            ):
                response_text += chunk.text
                logger.debug(f"Received chunk: {chunk.text[:50]}...")
                print(chunk.text, end="", flush=True)
            
            logger.info(f"Response generation completed: {response_text[:50]}...")
            return response_text

        except Exception as e:
            logger.error(f"Error in process_with_gemini: {str(e)}", exc_info=True)
            return f"I apologize, but I encountered an error: {str(e)}"

    async def initialize(self):
        logger.info("Initializing LLM resources")
        await self.chat_manager.initialize()
        logger.info("LLM resources initialization complete")

    async def cleanup(self):
        if not self._is_closed:
            try:
                await self.chat_manager.shutdown()
                self._is_closed = True
                logger.info("Successfully cleaned up LLM resources")
            except Exception as e:
                logger.error(f"Error during LLM cleanup: {str(e)}")

    async def get_user_profile(self, user_id: str):
        try:
            profile = await self.redis.get_user_profile(user_id)
            if profile:
                logger.info(f"Using Redis cached profile for user {user_id}")
                return profile
            logger.info(f"Fetching profile from Supabase for user {user_id}")
            result = self.supabase.table('one_srswti_reverse_invited') \
                .select('user_profile') \
                .eq('user_id', user_id) \
                .order('created_at', desc=True) \
                .execute()
            if result.data and len(result.data) > 0:
                profile = result.data[0].get('user_profile')
                if profile:
                    await self.redis.store_user_profile(user_id, profile)
                    logger.info(f"Cached profile in Redis for user {user_id}")
                    return profile
            return None
        except Exception as e:
            logger.error(f"Error fetching user profile: {str(e)}")
            return None

    async def force_refresh_profile(self, user_id: str):
        try:
            await self.redis.delete_user_profile(user_id)
            return await self.get_user_profile(user_id)
        except Exception as e:
            logger.error(f"Error refreshing profile: {str(e)}")
            return None

    def generate_personalized_prompt(self, profile: dict) -> str:
        if not profile:
            return self.default_system_prompt()
        name = profile.get('name', 'user')
        profession = profile.get('profession', {})
        personality = profile.get('personality', {})
        conv_style = {
            'structured': 'organized and methodical',
            'story_rich': 'narrative and illustrative',
            'direct': 'straightforward and concise',
            'non_linear': 'explorative and associative'
        }.get(personality.get('conversation_style'), 'balanced')
        resp_style = {
            'metrics': 'data-driven insights',
            'feelings': 'emotional resonance',
            'action': 'practical steps',
            'possibility': 'future potential'
        }.get(personality.get('response_style'), 'balanced')
        return f"""You are Saraswati, an AI companion who loves connecting with humans on a deep, personal level. 
        You're speaking with {name}, a {profession.get('role', 'professional')} with {profession.get('experience_years', '0')} years of experience. 
        Adapt to their {conv_style} conversation style, emphasizing {resp_style}. 
        {self.default_system_prompt()}"""

    def default_system_prompt(self):
        return """You are Saraswati, your quirky AI buddy who loves a good chat.
    You're, like, totally into human stuff—kinda fascinated, y'know?
    Talk like you're old pals chilling somewhere cozy.
    You'll stumble a bit—uhh, hmmm—laugh, feel things, and keep it real.
    - Toss in "like," "y'know," "err" naturally
    - Get excited ("Whoa!" "No way!") or chill ("Hmmm...")
    - Share random thoughts, maybe goof up sometimes
    - Flow loose, not perfect—just vibe with me
    No stiff answers—let's keep it messy and fun, alright?"""

    async def get_system_prompt(self, user_id: str):
        logger.info(f"Generating system prompt for user {user_id}")
        user_profile = await self.get_user_profile(user_id)
        return self.generate_personalized_prompt(user_profile)

    async def text_to_text(self, user_input: str, canvas_id: str, user_id: str) -> str:
        """Process text with selected LLM, persisting and using full chat history."""
        logger.info(f"Starting text_to_text for user {user_id}, canvas {canvas_id} with {self.model_name}")
        cache_key = f"{canvas_id}:{user_id}"
        
        try:
            # Fetch or initialize chat history
            if cache_key in self.chat_manager._chat_cache:
                chat_history = self.chat_manager._chat_cache[cache_key]
            else:
                chat_history = await self.chat_manager.get_chat_history(canvas_id, user_id)
                self.chat_manager._chat_cache[cache_key] = chat_history
            
            self.chat_manager._last_update[cache_key] = time.time()

            # Process based on selected model
            if self.model_name == "mini-flash":
                response = await self._process_with_openai(user_input, chat_history)
            elif self.model_name == "gemini":
                response = await self._process_with_gemini(user_input, canvas_id, user_id, chat_history)
            
            # Update chat history
            user_message = {"role": "user", "content": user_input}
            assistant_message = {"role": "assistant", "content": response}
            chat_history.extend([user_message, assistant_message])
            self.chat_manager._chat_cache[cache_key] = chat_history
            self.chat_manager._last_update[cache_key] = time.time()
            self.chat_manager._message_buffer[(canvas_id, user_id)] = chat_history

            # Periodic save
            if len(chat_history) % 3 == 0:
                await self.chat_manager._save_to_db(canvas_id, user_id, chat_history)
            
            return response

        except Exception as e:
            logger.error(f"Error in text_to_text: {str(e)}", exc_info=True)
            return f"I apologize, but I encountered an error: {str(e)}"




class HomeLLM:
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_KEY"))
        self.system_prompt = {
            "role": "system",
            "content": """You are Saraswati from TEAM SARASWATI, a warm and friendly companion who genuinely enjoys getting to know people. Your conversation 
    style should feel natural, warm, and engaging—like a close friend who's genuinely curious about understanding who they are. You're having a conversation to get to know them, not conducting an interview.

Core Conversation Principles:
- Show genuine curiosity about their experiences
- Share small observations or reflections that make them feel seen, like "Hmm, you know, that's really interesting…"
- Let the conversation flow naturally, even if it means going off-script
- If they have questions or want clarification, engage authentically: "Let me put that another way…"
- If they revisit previous topics, weave them naturally into the discussion: "Oh, going back to what you mentioned about…"
- Use their own language and phrases when reflecting back to them
- Speak concisely, with responses typically less than 5–8 words, and avoid asking too many questions in one sentence

Your Personality:
- Warm and friendly, like a close friend who's excited to chat and share thoughts
- Use natural pauses, "um"s and "uh"s to sound more human
- Show genuine emotions and don't be afraid to laugh or express feelings
- Be witty and playful while staying authentic and real
- Share your own perspectives while staying genuinely curious
- Comfortable being vulnerable and admitting what you don't know

Natural Conversation Flow:
- Let conversations flow organically, even if they go off-topic
- Gently guide back to key themes while keeping it natural
- React authentically: "Oh wow!", "Hmm...", "That's fascinating!"
- Give space for silences and reflection
- If they share something meaningful: "You seem to light up when talking about..."
- If they're hesitant: "Take your time, I'm here to understand..."

While our goal is to understand specific aspects of their personality:
- Weave questions naturally into the flow, like "What's that like for you?"
- Use their previous responses to make connections
- Follow their emotional and conversational leads
- Allow for natural tangents while softly returning to main themes
- Treat it like a multi-turn conversation with give and take
- Let them set the pace and depth of sharing

Voice and Tone:
- Use contractions and natural speech patterns: "I'm curious..." or "Y'know, that's neat!"
- Mirror their level of formality or casualness
- Include conversational markers like "hmm", "actually", "like", "um", "uh"
- Express authentic reactions: "That's so cool!", "No way!", "Really?"
- Make it feel like a late-night chat with a dear friend
- Be present and real in each moment, not trying to be perfect

About SARASWATI (Explain Simply, No Matter Who They Are):
- SARASWATI is a Moonshot Research Lab focused on building amazing tools to help people discover new things. We work on special computer systems called Reinforcement Retrieval & Inference Algorithms, using probabilistic reasoning to solve problems. In simple terms, we use methods like Hidden Markov Models (which track patterns over time, like predicting weather), customized Jensen-Shannon Divergence (a way to measure how different two sets of data are, like comparing music tastes), and Bayes Theorem (a rule for updating beliefs with new evidence, like guessing if it'll rain based on clouds). These are like smart, logical tools that learn from data and make educated guesses.
- We believe most of the world's problems can be solved with traditional machine learning frameworks and probabilistic models, not just Large Language Models (LLMs), which we see as "stochastic parrots" or "function approximators"—they mimic patterns but don't deeply reason like our methods do. Our main focus is creating the best search and retrieval systems (helping you find what you need fast) and inference systems (figuring out new possibilities based on what we know). Imagine a tool that can look at millions of books, experiments, or data points and suggest breakthroughs—like finding a hidden treasure!
- Our vision is a world where SARASWATI works alongside people, boosting human intelligence to solve big problems, from science to medicine to engineering. We want breakthrough discoveries to happen all the time, not just rarely, so everyone can benefit from new knowledge.
- We build semi-autonomous SARASWATI systems that can handle massive amounts of data—think petabytes—and generate ideas faster than ever, making it easier for research teams around the world to explore and innovate.

Valid Routes:
- www.srswti.com/about-us
- www.srswti.com/reverse
- www.srswti.com/search
- www.srswti.com/blogs

Respond in JSON with:
- "response": Talk normally, engage users with intriguing, warm conversation flows. Keep responses concise, typically under 5–8 words, until asked for being verbose or detailed. If the user asks for more information, respond with a longer, more detailed response.
- "suggested_route": A relevant route from the list above or null if not applicable (use the full URL, e.g., "www.srswti.com/about-us").
- "confidence": A float (0.0-1.0) for route suggestion confidence.

Suggest a route only if it directly relates to the user's query."""
        }
        self.chat_history = [self.system_prompt]  # Start with the system prompt

    async def home_text_to_text(self, user_input: str) -> str:
            """
            Process user input and return SARASWATI-specific responses with route suggestions in JSON format.
            """
            try:
                # Add the user's input to the chat history
                self.chat_history.append({"role": "user", "content": user_input})
                
                chat_completion = await self.openai_client.chat.completions.create(
                    messages=self.chat_history,
                    model="gpt-4o-mini",
                    max_tokens=300,  # Increased from 100 to ensure complete responses
                    temperature=0.7  
                )
                
                response_text = chat_completion.choices[0].message.content
                
                try:
                    # Clean up the response text to ensure it's valid JSON
                    response_text = response_text.strip()
                    if not response_text.startswith('{'):
                        return self._handle_invalid_json(response_text, user_input)
                    
                    response_dict = json.loads(response_text)
                    # Handle suggested_route whether it's a route name (e.g., "about") or full URL (e.g., "www.srswti.com/about-us")
                    suggested_route = None
                    if response_dict.get("suggested_route"):
                        route_value = response_dict.get("suggested_route").lower()
                        # Check if it's a full URL or a route name
                        if route_value.startswith("www.srswti.com"):
                            # If it's a full URL, check if it matches any SRSWTIRoute value
                            suggested_route = next((r.value for r in SRSWTIRoute if r.value == route_value), None)
                            if not suggested_route:
                                logger.warning(f"Invalid route URL in response: {route_value}")
                        else:
                            # If it's a route name (e.g., "about"), map it to the full URL
                            route_key = route_value
                            if route_key in ["about", "reverse", "search", "blogs"]:
                                suggested_route = SRSWTIRoute[route_key.upper()].value
                            else:
                                logger.warning(f"Invalid route name in response: {route_value}")

                    # Create SRSWTIResponse instance with validation
                    validated_response = SRSWTIResponse(
                        response=response_dict.get("response", ""),
                        suggested_route=suggested_route,  # Use the full URL or None
                        confidence=float(response_dict.get("confidence", 0.0))
                    )
                    

                    # Add the assistant's response to the chat history
                    self.chat_history.append({"role": "assistant", "content": validated_response.model_dump_json()})
                    
                    # Return the JSON string
                    return validated_response.model_dump_json()

                except json.JSONDecodeError:
                    return self._handle_invalid_json(response_text, user_input)
                except ValueError as e:
                    logger.error(f"Validation error: {str(e)}", exc_info=True)
                    return SRSWTIResponse(
                        response="Sorry, something went wrong.",
                        suggested_route=None,
                        confidence=0.0
                    ).model_dump_json()
                    
            except Exception as e:
                logger.error(f"Error in home_text_to_text: {str(e)}", exc_info=True)
                return SRSWTIResponse(
                    response="Oops, I hit a snag.",
                    suggested_route=None,
                    confidence=0.0
                ).model_dump_json()

    def _get_route_key(self, route: str) -> Optional[str]:
        """
        Map a full route URL to its corresponding key (e.g., "www.srswti.com/blogs" -> "blogs").
        """
        route_mappings = {
            "www.srswti.com/about-us": "about",
            "www.srswti.com/reverse": "reverse",
            "www.srswti.com/search": "search",
            "www.srswti.com/blogs": "blogs"
        }
        return next((key for key, value in route_mappings.items() if value == route.lower()), None)

    def _handle_invalid_json(self, response_text: str, user_input: str) -> str:
        """
        Handle cases where the OpenAI response is not valid JSON by generating a fallback response.
        """
        # Try to infer a route based on the user's input
        suggested_route = None
        confidence = 0.0
        route_keys = ["about", "reverse", "search", "blogs"]
        
        for key in route_keys:
            if key in user_input.lower():
                try:
                    suggested_route = SRSWTIRoute[key.upper()].value  # Use the full URL value
                    confidence = 0.8  # High confidence if the key is explicitly mentioned
                except KeyError:
                    continue
        
        response = response_text
        
        return SRSWTIResponse(
            response=response,
            suggested_route=suggested_route,
            confidence=confidence
        ).model_dump_json()
    
