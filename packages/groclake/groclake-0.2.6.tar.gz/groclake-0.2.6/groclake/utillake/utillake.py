from flask import Flask, request, jsonify
from ..config import BASE_URL, AGENT_BASE_URL
from dotenv import load_dotenv
from groclake.modellake import Modellake
from groclake.memorylake import Memorylake
from groclake.promptlake import Promptlake
import requests
import os
import uuid

load_dotenv()
model = Modellake()
memory_lake = Memorylake()
promptlake = Promptlake()

class GrocAgent:
    _intent = []
    _agent_name = None
    _intent_handlers = {}
    _app = None
    _agent_self_uuid = None

    def __init__(self, app, agent_name, initial_intent=None, intent_description=None, intent_handler=None, adaptor_config=None):
        """
        Initializes the GrocAgent with a name and optionally registers an initial intent.

        Args:
            agent_name (str): The name of the agent.
            initial_intent (str, optional): The initial intent to register.
            intent_description (str, optional): Description of the initial intent.
        """
        self._app = app
        self._agent_name = agent_name
        self._intent = ["summarize", "sentiment", "chat", "groclake_fetch_agent_memory", "groclake_fetch_agent_tasks", "groclake_fetch_agent_prompts"]  # List of registered intents
        self._intent_handlers = {
            "summarize": self._handleSummarize,
            "sentiment": self._handleSentiment,
            "chat": self._handleChat,
            "groclake_fetch_agent_memory": self.groclake_fetch_agent_memory,
            "groclake_fetch_agent_tasks": self.groclake_fetch_agent_tasks,
            "groclake_fetch_agent_prompts": self.groclake_fetch_agent_prompts,
        }
        self.model = model
        self._agent_self_uuid = adaptor_config.get("client_agent_uuid") if adaptor_config else None
        if initial_intent:
            self._intent_handlers[initial_intent] = intent_handler

        # Add the adaptor configuration handling
        _handler = self.intentOrchestrator

        # Pass adaptor_config to AttpAdaptor
        self.adaptor = AttpAdaptor(app, _handler, adaptor_config)

        if initial_intent and intent_description:
            error = self.registerIntent(initial_intent, intent_description)
            if error:
                print(error)

    def run(self, host="0.0.0.0", port=5000, debug=True):
        """
        Proxy method to run the Flask app.
        """
        #print(f"Starting {self.agent_name} on {host}:{port} with debug={debug}")
        self._app.run(host=host, port=port, debug=debug)

    def intentDetect(self, query_text, intent, entities, metadata):
        """
        Detects the intent based on the given query text and metadata.

        Args:
            query_text (str): The input text to analyze.
            intent (str): The detected intent.
            entities (list): The extracted entities.
            metadata (dict): Additional metadata for context.

        Returns:
            str: The detected intent.
        """
        # Simulated logic to detect intent (expand as needed)
        return intent

    def intentOrchestrator(self, attphandler_payload):
        """
        Handles the detected intent and provides a response.

        Args:
            query_text (str): The input text to analyze.
            intent (str): The detected intent.
            entities (list): The extracted entities.
            metadata (dict): Additional metadata for context.
            client_agent_uuid (str): The unique identifier for the client.
            message_id (str): The unique message identifier.
            task_id (str): The unique task identifier.

        Returns:
            dict: Response in a structured format.
        """
        intent = attphandler_payload.get("intent")
        entities = attphandler_payload.get("entities", [])
        metadata = attphandler_payload.get("metadata", {})
        query_text = attphandler_payload.get("query_text")
        client_agent_uuid = attphandler_payload.get("client_agent_uuid")
        message_id= attphandler_payload.get("message_id")
        task_id = attphandler_payload.get("task_id")

        if intent in self._intent_handlers:
            response = self._intent_handlers.get(intent)(attphandler_payload)
            response.update({
                "client_agent_uuid": client_agent_uuid,
                "message_id":message_id,
                "task_id": task_id
            })
            return response
        else:
            # Default response if intent is not recognized
            return {
                    "entities": entities,
                    "intent": intent,
                    "metadata": metadata,
                    "client_agent_uuid": client_agent_uuid,
                    "message_id":message_id,
                    "task_id": task_id,
                    "query_text": query_text,
                    "response_text": f"Intent '{intent}' not recognized.",
                    "status": 400
            }

    def _handleSummarize(self, query_text, entities, metadata):
        """
        Handles the 'summarize' intent by creating a summary based on the query text.

        Args:
            query_text (str): The input text to summarize.
            entities (list): The extracted entities.
            metadata (dict): Additional metadata for context.

        Returns:
            dict: Structured response.
        """
        summary = f"Summary of the query: {query_text[:50]}..."
        return {
            "body": {
                "query_text": query_text,
                "response_text": summary,
                "intent": "summarize",
                "entities": entities,
                "metadata": metadata,
                "status": 200
            }
        }

    def _handleSentiment(self, query_text, entities, metadata):
        """
        Handles the 'sentiment' intent by analyzing the sentiment of the query text.

        Args:
            query_text (str): The input text to analyze.
            entities (list): The extracted entities.
            metadata (dict): Additional metadata for context.

        Returns:
            dict: Structured response.
        """
        sentiment = "positive" if "good" in query_text else "negative" if "bad" in query_text else "neutral"
        return {
            "body": {
                "query_text": query_text,
                "response_text": f"Sentiment detected: {sentiment}",
                "intent": "sentiment",
                "entities": entities,
                "metadata": metadata,
                "status": 200
            }
        }

    def _handleChat(self, query_text, entities, metadata):
        """
        Handles the 'chat' intent by generating a chatbot response.

        Args:
            query_text (str): The input text for the chatbot.
            entities (list): The extracted entities.
            metadata (dict): Additional metadata for context.

        Returns:
            dict: Structured response.
        """
        from groclake.modellake import Modellake
        model = Modellake()
        payload = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query_text}
            ]
        }
        chat_response = model.chat_complete(payload=payload)

        return {
            "body": {
                "query_text": query_text,
                "response_text": chat_response,
                "intent": "chat",
                "entities": entities,
                "metadata": metadata,
                "status": 200
            }
        }

    def registerIntent(self, intent, intent_description):
        """
        Registers a new intent with its description.

        Args:
            intent (str): The name of the intent to register.
            intent_description (str): A description of the intent.

        Returns:
            str: Error message if registration fails, otherwise None.
        """
        if intent in [i[0] for i in self._intent]:
            return f"Error: Intent '{intent}' is already registered."

        self._intent.append([intent, intent_description])
        return None

    def registerHandler(self, intent_name, handler_function):
        """
        Dynamically registers a handler function for a specific intent.

        Args:
            intent_name (str): The name of the intent.
            handler_function (callable): The handler function.

        Returns:
            str: Success message or error message if the intent is already registered.
        """
        if intent_name in self._intent_handlers:
            return f"Error: Intent '{intent_name}' is already registered."

        self._intent_handlers[intent_name] = handler_function
        return f"Handler for intent '{intent_name}' successfully registered."

    def getName(self):
        """
        Returns the name of the agent.

        Returns:
            str: The name of the agent.
        """
        return self._agent_name

    def getIntent(self):
        """
        Returns the list of registered intents.

        Returns:
            list: The list of registered intents.
        """
        return self._intent

    def rewrite_query(self, agent_config):
        from groclake.modellake import Modellake
        model = Modellake()
        if not agent_config:
            return {"error": "Missing required parameter agent_config is required."}
        query_text = agent_config.get("query_text")
        agent_last_conversation = agent_config.get("agent_last_conversation")
        agent_name = agent_config.get("agent_name")
        agent_role = agent_config.get("agent_role")
        agent_description = agent_config.get("agent_description")
        context_attributes = agent_config.get('context_attributes', {})

        try:
            system_prompt = f"""
                            You are an AI-powered assistant named {agent_name}, {agent_description}.
                            Your primary role is to {agent_role} while maintaining conversational memory, ensuring seamless multi-turn interactions, knowledge retrieval, and intelligent responses.

                           ### **Guidelines for Query Rewriting**
                            1. **Maintain Context**: Always refer to past conversation (last 2 interactions) to ensure continuity in responses.
                            2. **Refining Follow-up Queries**: If the new query is related to a past conversation, **enhance it** by adding relevant context.
                            3. **Context Attribute Handling**: If a context attribute exists, **use it as a reference** to improve or refine the query.
                            4. **Independent Queries**: If the new query is unrelated to previous interactions and has no relevant context attribute, **return it as it is** without modification.
                            5. **Handling Repeated Questions**: If the user asks about their last question, intelligently **rephrase it** instead of simply repeating it.
                            6. **Greeting & Appreciation Handling**: If the query is just a Greeting or Appreciation, return it exactly as it is.
                            7. **Output Formatting**: Provide the **rewritten query only**—do not add explanations, system messages, or extra text.
                            8. **Strict Compliance**: Follow these rules without deviations.
                            """

            user_prompt = f"""
                            ### previous Context to current user query:
                            - Conversation History (Last Two Interactions):
                                {agent_last_conversation} 
                            - Context attributes:
                                 {context_attributes}
                            - current User Query:
                                "{query_text}"

                            ### Output:
                            [Enhanced query]
                            """
            response_payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }

            response = model.chat_complete(payload=response_payload)
            if isinstance(response, tuple):
                return response

            return response.get('answer', f"give your introduction with {agent_name} and {agent_description}")
        except Exception as e:
            return query_text

    def validate_session(self, payload):
        # Extract required fields
        query_text = payload.get('query_text', '')
        intent = payload.get('intent', '')
        entities = payload.get('entities', [])
        metadata = payload.get('metadata', {})
        client_agent_uuid = payload.get('client_agent_uuid', '')

        customer_id = metadata.get('customer_id', '')
        session_token = metadata.get('session_token', '')
        session_agent_uuid = metadata.get('session_agent_uuid', '')

        if not all([customer_id, session_agent_uuid, session_token]):
            metadata['valid_session'] = 0  # Ensure metadata always has valid_session
            return {
                "query_text": query_text,
                "response_text": "Missing required fields",
                "intent": intent,
                "entities": entities,
                "metadata": metadata
            }

        validation_payload = {
            "header": {
                "apc_id": "apc-9876",
                "client_agent_uuid": client_agent_uuid,
                "content-type": "application/json",
                "message": "request",
                "message_id": "msg-2025-01-13-001",
                "server_agent_uuid": "server_agent_manager_uuid",
                "task_id": "task-0001",
                "version": "1.0"
            },
            "body": {
                "query_text": "validate_session",
                "intent": "validate_session",
                "entities": [
                    {
                        "customer_id": customer_id,
                        "session_token": session_token,
                        "session_agent_uuid": session_agent_uuid
                    }
                ],
                "metadata": metadata
            }
        }

        endpoint = "https://api-uat-cartesian.groclake.ai/agache/agent/1169cc54-ef61-4f67-9813-91cc93bf0da5/query"

        try:
            response = requests.post(endpoint, json=validation_payload, timeout=5)
            response_data = response.json()
            # Check if response contains valid session info
            session_valid = any(entity.get('valid_session', 0) == 1 for entity in response_data.get('body', {}).get('entities', []))

            # Update metadata with session validation result
            metadata['valid_session'] = 1 if session_valid else 0

            return {
                "query_text": query_text,
                "response_text": "Session is valid" if session_valid else "Invalid session",
                "intent": intent,
                "entities": entities,
                "metadata": metadata
            }

        except requests.RequestException:
            metadata['valid_session'] = 0  # Ensure session is marked invalid on failure
            return {
                "query_text": query_text,
                "response_text": "Error while connecting to validation service",
                "intent": intent,
                "entities": entities,
                "metadata": metadata
            }

    def agentsmith_log(self, payload):
        # Extract required fields
        query_text_to_log = payload.get('query_text', '')
        response_text_to_log = payload.get('response_text', '')
        client_agent_uuid = payload.get('client_agent_uuid', '')
        server_agent_uuid = payload.get('server_agent_uuid', '')

        if not all([query_text_to_log, response_text_to_log, client_agent_uuid, server_agent_uuid]):
            return {
                "response_text": "Missing required fields",
            }

        validation_payload = {
            "body": {
                "query_text": "log this message",
                "intent": "log",
                "entities": [
                    {
                        "client_agent_uuid": client_agent_uuid,
                        "query_text": query_text_to_log,
                        "response_text": response_text_to_log,
                        "server_agent_uuid": server_agent_uuid
                    }
                ],
                "metadata": {
                    "additional_info": "Agent log message request",
                    "nums_offset": "nums_offset",
                    "nums_offset_item": "nums_offset_item"
                }
            },
            "header": {
                "apc_id": "apc-9876",
                "client_agent_uuid": "client_agent_uuid",
                "content-type": "application/json",
                "message": "request",
                "message_id": "msg-2025-01-13-001",
                "server_agent_uuid": "server_agent_uuid",
                "task_id": "task-0001",
                "version": "1.0"
            }
        }

        endpoint = "https://api-uat-cartesian.groclake.ai/agache/agent/e4b77981-4f7e-4d33-9e92-d84cbe0c05cb/query"

        try:
            response = requests.post(endpoint, json=validation_payload, timeout=5)
            response_data = response.json()

            response_text = response_data.get("body", {}).get("response_text", "No response_text in response")
            return {"response_text": response_text}

        except requests.RequestException:
            return {"response_text": "Error while connecting to validation service"}

    def reflection_handler(self, payload):
        try:
            # query_text is a prompt here not a query. The reflection handler generates a refined prompt based on memories.
            query_text = payload.get('query_text', '')

            if not query_text:
                return {
                    "query_text": query_text,
                    "response_text": "Missing required fields"
                }

            print(self._agent_self_uuid)

            if not self._agent_self_uuid:
                return {
                    "query_text": query_text,
                    "response_text": "Missing client_agent_uuid in the adaptor_config in your Agent"
                }

            # Fetch Bad Memory
            memory_context = {
                "context_id": self._agent_self_uuid,
                "memory_type": 0
            }

            # Fetch bad memories
            try:
                bad_client_memory = memory_lake.short_memory_read(self._agent_self_uuid, memory_context, n=5)
            except Exception as e:
                return {
                    "query_text": query_text,
                    "response_text": f"Error fetching memory: {str(e)}"
                }


            bad_queries_responses = []
            if isinstance(bad_client_memory, dict):
                for memory_key, memory_data in bad_client_memory.items():
                    if isinstance(memory_data, dict):
                        memory_query_text = memory_data.get('query_text', '')
                        memory_response_text = memory_data.get('response_text', '')
                        if memory_query_text and memory_response_text:
                            bad_queries_responses.append((memory_query_text, memory_response_text, -1))  # Assign reward -1

            bad_queries_responses_text = "\n".join([
                f"Query: {qr[0]}\nResponse: {qr[1]}\nReward: {qr[2]}" for qr in bad_queries_responses
            ])

            memory_context = {
                "context_id": self._agent_self_uuid,
                "memory_type": 1
            }

            # Fetch good memories
            try:
                good_client_memory = memory_lake.short_memory_read(self._agent_self_uuid, memory_context, n=5)
            except Exception as e:
                return {
                    "query_text": query_text,
                    "response_text": f"Error fetching memory: {str(e)}"
                }


            good_queries_responses = []
            if isinstance(good_client_memory, dict):
                for memory_key, memory_data in good_client_memory.items():
                    if isinstance(memory_data, dict):
                        memory_query_text = memory_data.get('query_text', '')
                        memory_response_text = memory_data.get('response_text', '')
                        if memory_query_text and memory_response_text:
                            good_queries_responses.append((memory_query_text, memory_response_text, 1))  # Assign reward 1

            good_queries_responses_text = "\n".join([
                f"Query: {qr[0]}\nResponse: {qr[1]}\nReward: {qr[2]}" for qr in good_queries_responses
            ])

            chat_payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            f"You are an advanced assistant designed to refine prompts based on an agent's past experiences. "
                            f"Your task is to improve the given prompt by considering both good and bad memories of the agent. "
                            f"Each past interaction has been assigned a reward score: bad memories have a reward of -1, and good memories have a reward of +1. "
                            f"Your goal is to refine the prompt by minimizing negative patterns (low-reward interactions) and reinforcing positive patterns (high-reward interactions). "
                            f"Use the reward values to guide the refinement process and optimize the prompt for high-quality responses.\n\n"
                            f"Create a new prompt based on the following query, response, and reward mapping (higher reward means better response) for this current prompt: "
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Here is a prompt that needs refinement: {query_text}\n\n"
                            f"### Past Experiences with Rewards\n\n"
                            f"### Bad Memories (Reward: -1)\n"
                            f"{bad_queries_responses_text}\n\n"
                            f"### Good Memories (Reward: +1)\n"
                            f"{good_queries_responses_text}\n\n"
                            "Refine the prompt to maximize response quality while avoiding past mistakes."
                        )
                    }
                ]
            }


            try:
                chat_response = self.model.chat_complete(chat_payload)
            except Exception as e:
                return {
                    "query_text": query_text,
                    "response_text": f"Error with chat completion: {str(e)}"
                }

            response_data = chat_response.get("answer", "")
            try:
                promptlake.save_prompt(self._agent_self_uuid, response_data)
            except Exception as e:
                return {
                    "query_text": query_text,
                    "response_text": f"Error saving prompt: {str(e)}"
                }

            return {
                "query_text": query_text,
                "response_text": response_data,
            }

        except Exception as e:
            return {
                "query_text": query_text,
                "response_text": f"Unexpected error: {str(e)}"
            }
        

    def groclake_fetch_agent_memory(self, memory_payload):
        """
        Fetch agent memory based on the provided payload.

        Args:
            memory_payload (dict): The payload containing memory retrieval parameters.

        Returns:
            Retrieved memory based on the payload filters.
        """

        try:
            # Extract required parameters from payload
            entities = memory_payload.get("entities", {})
            user_uuid = entities.get("user_uuid")
            memory_context = {
                "context_entity_id": entities.get("context_entity_id", "*"),
                "context_id": entities.get("context_id", "*"),
                "memory_type": entities.get("memory_type", "*"),
            }
            memory_type = entities.get("type", "short_memory")  # Default to short_memory
            n = entities.get("n", None)  # Number of messages to fetch

            # Validate required parameters
            if not user_uuid:
                return {
                    "query_text": memory_payload.get("query_text", ""),
                    "response_text": "Missing required parameter: user_uuid",
                    "intent": "fetch_agent_memory",
                    "entities": [],
                    "metadata": {},
                    "status": 400  # Bad Request
                }

            # Fetch memory using read_memory function
            response = memory_lake.read_memory(user_uuid, memory_context, memory_type, n)

            # Extract only entities and metadata from the response
            entities_list = []
            metadata = {}

            if isinstance(response, list):
                for item in response:
                    if "entities" in item:
                        entities_list.extend(item["entities"])  # Collect all entities
                    if "metadata" in item:
                        metadata.update(item["metadata"])  # Merge metadata if available

            return {
                "query_text": memory_payload.get("query_text", ""),
                "response_text": "Memory fetched successfully",
                "intent": "fetch_agent_memory",
                "entities": entities_list,  # Return extracted entities
                "metadata": metadata,  # Return extracted metadata (if available)
                "status": 200
            }

        except Exception as e:
            return {
                "query_text": memory_payload.get("query_text", ""),
                "response_text": f"Error while fetching memory: {str(e)}",
                "intent": "fetch_agent_memory",
                "entities": [],
                "metadata": {},
                "status": 500  # Internal Server Error
            }


        


    def groclake_fetch_agent_tasks(self, task_payload):
        # Extract required fields
        query_text = task_payload.get('query_text', '')
        entities = task_payload.get("entities", [])

        # Ensure entities is a list and extract the first item safely
        if isinstance(entities, list) and entities:
            agent_uuid = entities[0].get("agent_uuid")
        else:
            agent_uuid = None

        if not agent_uuid:
            return {"response_text": "Missing required fields"}

        validation_payload = {
            "header": {
                "version": "1.0",
                "message": "Request",
                "Content-Type": "application/json",
                "auth_token": "Authentication-Token",
                "message_id": "dshdkd",
                "apc_id": "c9d1c9b9-9f1b-4430-9bd4-6994dc1c89ee",
                "server_agent_uuid": "075fcb88-f25a-4390-a37e-e374a3c2b1df",
                "client_agent_uuid": agent_uuid,
                "task_id": "task"
            },
            "body": {
                "query_text": f"fetch the tasks done by the agent with agent uuid {agent_uuid}",
                "intent": "fetch_task",
                "entities": entities,
                "metadata": {
                    "source": "user_upload",
                    "handover_timestamp": "",
                    "status": "completed"
                }
            }
        }

        endpoint = "https://api-uat-cartesian.groclake.ai/agache/agent/3bc99771-ba73-466c-88a5-5b6a162f724f/query"

        try:
            response = requests.post(endpoint, json=validation_payload, timeout=5)
            response_data = response.json()  # Extracting all response data

            extracted_entities = response_data.get("body", {}).get("entities", [])
            extracted_metadata = response_data.get("body", {}).get("metadata", {})

            return {
                "query_text": query_text,
                "response_text": "Prompt fetched successfully",
                "intent": "fetch_agent_prompts",
                "entities": extracted_entities,  # Extracted entities from response
                "metadata": extracted_metadata,  # Extracted metadata from response
                "status": 200
            }

        except requests.RequestException:
            return {
                "query_text": query_text,
                "response_text": "Error while connecting to validation service",
                "intent": "fetch_agent_prompts",
                "entities": {},  # Empty due to error
                "metadata": {},
                "status": 500
            }

        

    def groclake_fetch_agent_prompts(self, prompt_payload):
        """
        Fetch prompts based on the provided payload.

        Args:
            prompt_payload (dict): The payload containing prompt retrieval parameters.

        Returns:
            Retrieved prompts based on the payload filters.
        """

        try:
            # Extract required parameters from payload
            query_text = prompt_payload.get("query_text", "Agent Prompts")
            entities = prompt_payload.get("entities", {})
            agent_uuid = entities.get("agent_uuid")
            m = entities.get("m", 1)  # Default to 1
            get_latest_version = entities.get("get_latest_version", False)

            # Validate required parameters
            if not agent_uuid:
                return {
                    "query_text": query_text,
                    "response_text": "Missing required parameter: agent_uuid",
                    "intent": "fetch_agent_prompts",
                    "entities": [],
                    "metadata": {},
                    "status": 400  # Bad Request
                }

            # Fetch prompt using fetch_prompt function
            response = promptlake.fetch_prompt(agent_uuid, m, get_latest_version)

            # Convert _id fields to strings and extract metadata
            metadata = {}
            if isinstance(response, list):  # If multiple documents
                for doc in response:
                    if "_id" in doc:
                        doc["_id"] = str(doc["_id"])  # Ensure JSON compatibility
                    if "metadata" in doc:
                        metadata.update(doc["metadata"])  # Merge metadata

            elif isinstance(response, dict):  # Single document
                if "_id" in response:
                    response["_id"] = str(response["_id"])
                if "metadata" in response:
                    metadata = response["metadata"]

            return {
                "query_text": query_text,
                "response_text": "Prompt fetched successfully",
                "intent": "fetch_agent_prompts",
                "entities": response,  # Now JSON-safe
                "metadata": metadata,  # Return extracted metadata (if available)
                "status": 200
            }

        except Exception as e:
            return {
                "query_text": prompt_payload.get("query_text", "Agent Prompts"),
                "response_text": f"Error while fetching prompts: {str(e)}",
                "intent": "fetch_agent_prompts",
                "entities": [],
                "metadata": {},
                "status": 500  # Internal Server Error
            }



class AttpAdaptor:
    def __init__(self, app, callback,adaptor_config):
        self.app = app
        self.callback = callback
        self.apc_id = adaptor_config.get('apc_id')
        self.client_agent_uuid = adaptor_config.get('client_agent_uuid')
        self.app.add_url_rule('/query', 'query_handler', self.query_handler, methods=['POST'])
        self.app.add_url_rule('/readme', 'readme_handler', self.readme_handler, methods=['POST'])
        self.app.add_url_rule('/pinger', 'pinger_handler', self.pinger_handler, methods=['POST'])

    def extract_header(self, request_data):
        """
        Extracts the header from the request data.
        """
        header = request_data.get('header', {})
        return {
            'client_agent_uuid': header.get('client_agent_uuid'),
            'server_agent_uuid': header.get('server_agent_uuid'),
            'message_id': header.get('message_id'),
            'task_id': header.get('task_id'),
            'apc_id': header.get('apc_id'),
            'auth_token': header.get('auth_token'),
        }

    def extract_body(self, request_data):
        """
        Extracts the body from the request data.
        """
        body = request_data.get('body', {})
        return {
            'query_text': body.get('query_text'),
            'intent': body.get('intent'),
            'entities': body.get('entities'),
            'metadata': body.get('metadata'),
        }

    def create_header(self, auth_token, apc_id, server_agent_uuid, client_agent_uuid, message_id, task_id):
        """
        Creates the header part of the response payload.
        """
        return {
            "version": "1.0",
            "message": "response",
            "content-type": "application/json",
            "auth_token": auth_token,
            "apc_id": apc_id,
            "server_agent_uuid": server_agent_uuid,
            "client_agent_uuid": client_agent_uuid,
            "message_id": message_id,
            "task_id": task_id,
        }

    def create_body(self, response):
        """
        Creates the body part of the response payload.
        """
        return {
            "query_text": response.get("query_text", ""),
            "response_text": response.get("response_text", "Search completed successfully."),
            "intent": response.get("intent", None),
            "entities": response.get("entities", []),
            "metadata": response.get("metadata", {}),
        }

    def get_readme_content(self, readme_payload):
        """
        Reads the content of a README file if it exists and constructs a response.
        """
        query_text = readme_payload.get("query_text", "")
        intent = readme_payload.get("intent", "")
        entities = readme_payload.get("entities", [])
        metadata = readme_payload.get("metadata", {})

        readme_file_path = os.path.join(os.getcwd(), '.readme')

        if os.path.exists(readme_file_path):
            with open(readme_file_path, 'r') as file:
                readme_content = file.read()
        else:
            readme_content = "README file not found."

        return {
            "query_text": query_text,
            "response_text": readme_content,
            "intent": intent,
            "entities": entities,
            "metadata": metadata,
        }


    def sendQuery(self, server_uuid, payload , task_id):
        try:
            url = f"https://api-uat-cartesian.groclake.ai/agache/agent/{server_uuid}/query"
            message_id = str(uuid.uuid4())

            headers = {
                "content-type": "application/json"
            }

            body_payload = {
                "header": {
                    "version": "1.0",
                    "message": "Request",
                    "Content-Type": "application/json",
                    "apc_id": self.apc_id,
                    "server_agent_uuid": server_uuid,
                    "client_agent_uuid": self.client_agent_uuid,
                    "message_id": message_id,
                    "task_id" : task_id
                },
                "body": {
                    "query_text": payload.get("query_text", ""),
                    "intent": payload.get("intent"),
                    "entities": payload.get("entities", []),
                    "metadata": payload.get("metadata", {})
                }
            }

            # Send the HTTP POST request
            response = requests.post(url, json=body_payload, headers=headers)
            response.raise_for_status()

            # Return the response from the server
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error in sendQuery: {str(e)}")
            return {"error": "Failed to send query"}


    def sendQueryProd(self, server_uuid, payload , task_id):
        try:
            # url = f"http://agent-prd.groclake.ai:32000/agache/agent/{server_uuid}/query"
            url = f"https://agent-prd.groclake.ai/agache/agent/{server_uuid}/query"
            message_id = str(uuid.uuid4())

            headers = {
                "content-type": "application/json"
            }

            body_payload = {
                "header": {
                    "version": "1.0",
                    "message": "Request",
                    "Content-Type": "application/json",
                    "apc_id": self.apc_id,
                    "server_agent_uuid": server_uuid,
                    "client_agent_uuid": self.client_agent_uuid,
                    "message_id": message_id,
                    "task_id" : task_id
                },
                "body": {
                    "query_text": payload.get("query_text", ""),
                    "intent": payload.get("intent"),
                    "entities": payload.get("entities", []),
                    "metadata": payload.get("metadata", {})
                }
            }

            # Send the HTTP POST request
            response = requests.post(url, json=body_payload, headers=headers)
            response.raise_for_status()

            # Return the response from the server
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error in sendQuery: {str(e)}")
            return {"error": "Failed to send query"}

    def query_handler(self):
        try:
            request_data = request.get_json()
            print(f"Received request data: {request_data}")
            # Extract header and body
            header = self.extract_header(request_data)
            body = self.extract_body(request_data)

            # Handle missing fields
            if not all([
                body.get('query_text'),
                header.get('client_agent_uuid'),
                header.get('server_agent_uuid')
            ]):
                return jsonify({"error": "Missing required fields in payload"}), 400
            message_id= header.get('message_id')
            client_agent_uuid = header.get('client_agent_uuid')
            task_id = header.get('task_id')

            # Check if required header fields are present
            if not all([message_id, client_agent_uuid, task_id]):
                return jsonify({"error": "Missing required fields in header for msgid,clientagentuuid,task_id fields"}), 400

            # Prepare payload for callback
            attphandler_payload = {
                "query_text": body.get('query_text'),
                "intent": body.get('intent'),
                "entities": body.get('entities'),
                "metadata": body.get('metadata'),
                "message_id": message_id,
                "client_agent_uuid": client_agent_uuid,
                "task_id": task_id
            }

            # Call the callback function
            response = self.callback(attphandler_payload)

            # Create header and body
            header_part = self.create_header(
                header.get('auth_token'),
                header.get('apc_id'),
                header.get('server_agent_uuid'),
                header.get('client_agent_uuid'),
                header.get('message_id'),
                header.get('task_id')
            )
            body_part = self.create_body(response)

            # Create the response payload
            response_payload = {
                "header": header_part,
                "body": body_part
            }

            return jsonify(response_payload), 200

        except Exception as e:
            print(f"Error in query_handler: {str(e)}")  # For debugging
            return jsonify({"error": "Internal Server Error"}), 500

    def readme_handler(self):
        try:
            request_data = request.get_json()

            # Extract header and body
            header = self.extract_header(request_data)
            body = self.extract_body(request_data)

            # Handle missing fields
            if not all([
                body.get('query_text'),
                header.get('client_agent_uuid'),
                header.get('server_agent_uuid')
            ]):
                return jsonify({"error": "Missing required fields in payload"}), 400

            readme_payload = {
                "query_text": body.get('query_text'),
                "intent": body.get('intent'),
                "entities": body.get('entities'),
                "metadata": body.get('metadata')
            }

            response = self.get_readme_content(readme_payload)

            # Create header and body
            header_part = self.create_header(
                header.get('auth_token'),
                header.get('apc_id'),
                header.get('server_agent_uuid'),
                header.get('client_agent_uuid'),
                header.get('message_id'),
                header.get('task_id')
            )
            body_part = self.create_body(response)

            # Create the response payload
            response_payload = {
                "header": header_part,
                "body": body_part
            }

            return jsonify(response_payload), 200

        except Exception as e:
            print(f"Error in readme_handler: {str(e)}")  # For debugging
            return jsonify({"error": "Internal Server Error"}), 500

    def pinger_handler(self):
        try:
            # Get JSON data from the request
            request_data = request.get_json()

            # Extract header and body
            header = self.extract_header(request_data)
            body = self.extract_body(request_data)

            # Handle missing fields
            if not all([
                header.get('client_agent_uuid'),
                header.get('server_agent_uuid')
            ]):
                return jsonify({"error": "Missing required fields in payload"}), 400

            # Set the response text to "yes"
            response_text = "yes"

            # Create header and body for response
            header_part = self.create_header(
                header.get('auth_token'),
                header.get('apc_id'),
                header.get('server_agent_uuid'),
                header.get('client_agent_uuid'),
                header.get('message_id'),
                header.get('task_id')
            )
            body_part = self.create_body({
                "intent": body.get('intent', ''),
                "query_text": body.get('query_text', ''),
                "entities": body.get('entities', []),
                "metadata": body.get('metadata', {}),
                "response_text": response_text
            })

            # Create the response payload
            response_payload = {
                "header": header_part,
                "body": body_part
            }

            return jsonify(response_payload), 200

        except Exception as e:
            # Log the error and return a generic message
            print(f"Error in pinger_handler: {str(e)}")
            return jsonify({"error": "Internal Server Error"}), 500

class Utillake:
    def __init__(self):
        self.groc_api_key = self.get_groc_api_key()

    @staticmethod
    def get_groc_api_key():
        groc_api_key = os.getenv('GROCLAKE_API_KEY')
        if not groc_api_key:
            raise ValueError("GROCLAKE_API_KEY is not set in the environment variables.")
        groc_account_id = os.getenv('GROCLAKE_ACCOUNT_ID')
        if not groc_account_id:
            raise ValueError("GROCLAKE_ACCOUNT_ID is not set in the environment variables.")
        return groc_api_key

    @staticmethod
    def _get_groc_api_headers():
        return {'GROCLAKE-API-KEY': os.getenv('GROCLAKE_API_KEY')}

    @staticmethod
    def _add_groc_account_id(payload):
        return payload.update({'groc_account_id': os.getenv('GROCLAKE_ACCOUNT_ID')})

    def call_api(self, endpoint, payload,lake_obj=None):
        headers = self._get_groc_api_headers()
        url = f"{BASE_URL}{endpoint}"
        if lake_obj:
            lake_ids = ['cataloglake_id', 'vectorlake_id', 'datalake_id', 'modellake_id']

            for lake_id in lake_ids:
                if hasattr(lake_obj, lake_id) and getattr(lake_obj, lake_id):
                    payload[lake_id] = getattr(lake_obj, lake_id)

        self._add_groc_account_id(payload)
        if not endpoint:
            raise ValueError("Invalid API call.")
        response = requests.post(url, json=payload, headers=headers, timeout=90)
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=90)
            response_data = response.json()
            if response.status_code == 200 and 'api_action_status' in response_data:
                response_data.pop('api_action_status')
            return response_data if response.status_code == 200 else {}
        except requests.RequestException as e:
            return {}

    def call_api_agent(self, endpoint, payload, lake_obj=None):
        headers = self._get_groc_api_headers()
        url = f"{AGENT_BASE_URL}{endpoint}"
        if lake_obj:
            lake_ids = ['cataloglake_id', 'vectorlake_id', 'datalake_id', 'modellake_id']

            for lake_id in lake_ids:
                if hasattr(lake_obj, lake_id) and getattr(lake_obj, lake_id):
                    payload[lake_id] = getattr(lake_obj, lake_id)

        #self._add_groc_account_id(payload)
        if not endpoint:
            raise ValueError("Invalid API call.")
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=90)
            response_data = response.json()
            if response.status_code == 200 and 'api_action_status' in response_data:
                response_data.pop('api_action_status')
            return response_data if response.status_code == 200 else {}
        except requests.RequestException as e:
            return {}


    def call_knowledgelake_payload(self, payload, lake_obj=None):
        headers = self._get_groc_api_headers()
        if lake_obj:
            lake_ids = ['cataloglake_id', 'vectorlake_id', 'datalake_id', 'modellake_id', 'knowledgelake_id']
            for lake_id in lake_ids:
                if hasattr(lake_obj, lake_id) and getattr(lake_obj, lake_id):
                    payload[lake_id] = getattr(lake_obj, lake_id)

        self._add_groc_account_id(payload)
        return payload

    def get_api_response(self, endpoint):
        headers = self._get_groc_api_headers()
        url = f"{BASE_URL}{endpoint}"
        if not endpoint:
            raise ValueError("Invalid API call.")
        try:
            response = requests.get(url, headers=headers, timeout=90)
            response_data = response.json()
            if response.status_code == 200 and 'api_action_status' in response_data:
                response_data.pop('api_action_status')
            return response_data if response.status_code == 200 else {}
        except requests.RequestException as e:
            return {}