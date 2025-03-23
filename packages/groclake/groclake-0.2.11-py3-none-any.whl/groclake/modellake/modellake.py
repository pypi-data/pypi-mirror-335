import anthropic

from openai import OpenAI

import google.generativeai as genai
import os
from groq import Groq


class Modellake:
    def __init__(self):
        self.modellake_id = None
        self.params = {}

    # def translate(self, payload):
    #     api_endpoint = '/modellake/translate'
    #     return self.utillake.call_api(api_endpoint, payload, self)
    #
    # def text_to_speech(self, payload):
    #     api_endpoint = '/modellake/textToSpeech'
    #     return self.utillake.call_api(api_endpoint, payload, self)
    #
    #
    # def create(self, payload=None):
    #     api_endpoint = '/modellake/create'
    #     if not payload:
    #         payload = {}
    #
    #     response = self.utillake.call_api(api_endpoint, payload, self)
    #     if response and 'modellake_id' in response:
    #         self.modellake_id = response['modellake_id']
    #
    #     return response

    def openAI_model(self, messages, token_size=None, model_name=None):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            return {"error": "API key is missing. Please set OPENAI_API_KEY as an environment variable."}
        client = OpenAI(api_key=api_key)
        try:
            chat_completion = client.chat.completions.create(
                messages=messages,
                model=model_name,
                max_tokens=token_size,
                temperature=0.5,
            )
            usage = chat_completion.usage

            return {
                "answer": chat_completion.choices[0].message.content.strip(),
                "input_tokens": usage.prompt_tokens if usage else None,
                "output_tokens": usage.completion_tokens if usage else None,
                "total_tokens": usage.total_tokens if usage else None
            }

        except Exception as e:
            return str(e)

    def gemini_model(self, messages, token_size=None, model_name=None):
        try:
            GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
            if not GOOGLE_API_KEY:
                return {"error": "API key is missing. Please set GOOGLE_API_KEY as an environment variable."}

            genai.configure(api_key=GOOGLE_API_KEY)
            model_name = model_name or 'gemini-1.5-flash'
            model = genai.GenerativeModel(model_name)
            user_input = "\n".join([msg["content"] for msg in messages if msg["role"] == "user"])
            system_input = "\n".join([msg["content"] for msg in messages if msg["role"] == "system"])
            final_message = f"System message:{system_input} User message:{user_input}"
            response = model.generate_content(final_message, generation_config={"max_output_tokens": token_size})
            token_usage = response.usage_metadata
            return {
                "answer": response.text.strip(),
                "input_tokens": token_usage.prompt_token_count if token_usage else None,
                "output_tokens": token_usage.candidates_token_count if token_usage else None,
                "total_tokens": (
                            token_usage.prompt_token_count + token_usage.candidates_token_count) if token_usage else None
            }

        except Exception as e:
            return str(e)

    def deepseek_model(self, messages, token_size=None, model_name=None):
        try:
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                return {"error": "API key is missing. Please set DEEPSEEK_API_KEY as an environment variable."}

            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
            )
            model_name = model_name
            completion = client.chat.completions.create(
                extra_headers={
                },
                extra_body={},
                model=model_name,
                max_tokens=token_size,
                messages=messages
            )

            response = completion.choices[0].message.content
            if hasattr(completion, "usage"):
                token_usage = completion.usage
                input_tokens = getattr(token_usage, "prompt_tokens", 0)
                output_tokens = getattr(token_usage, "completion_tokens", 0)
                total_tokens = getattr(token_usage, "total_tokens", input_tokens + output_tokens)
            else:
                input_tokens = output_tokens = total_tokens = None

            return {

                "answer": response,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens
            }

        except Exception as e:
            return str(e)

    def llama_model(self, messages, token_size=None, model_name=None):
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                return {"error": "API key is missing. Please set GROQ_API_KEY as an environment variable."}

            client = Groq(api_key=api_key)

            completion = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=1,
                max_tokens=token_size,
                top_p=1,
                stream=False
            )

            response_text = completion.choices[0].message.content.strip()
            input_tokens = getattr(completion.usage, "prompt_tokens", 0)
            output_tokens = getattr(completion.usage, "completion_tokens", 0)
            total_tokens = getattr(completion.usage, "total_tokens", input_tokens + output_tokens)

            return {
                "answer": response_text,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens
            }
        except Exception as e:
            return str(e)

    def claude_model(self, messages, token_size=None, model_name=None):
        try:
            api_key = os.getenv("ANTROPHIC_API_KEY")
            if not api_key:
                return {"error": "API key is missing. Please set ANTROPHIC_API_KEY as an environment variable."}

            client = anthropic.Anthropic(api_key=api_key)

            msg_list = [msg for msg in messages if msg.get("role") == "user"]

            response = client.messages.create(
                model=model_name,
                max_tokens=token_size,
                messages=msg_list
            )

            model_response = response.content[0].text

            input_tokens = getattr(response.usage, "input_tokens", 0)
            output_tokens = getattr(response.usage, "output_tokens", 0)
            total_tokens = input_tokens + output_tokens

            return {
                "answer": model_response.strip(),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens
            }
        except Exception as e:
            return str(e)

    def chat_complete(self, payload):
        model_name = payload.get("model_name", "gpt-3.5-turbo").strip().lower()
        messages = payload.get("messages", [])
        token_size = payload.get("token_size", 150)

        self.valid_models = {
            "openai": {"gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o"},
            "gemini": {"gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro", "gemini-1.5-pro-latest"},
            "deepseek": {"deepseek/deepseek-r1:free", "deepseek/deepseek-r1:8b", "deepseek/deepseek-r1:7b",
                         "deepseek/deepseek-r1:67b"},
            "llama": {"llama3-70b-8192", "llama3-8b", "llama3-70b"},
            "claude": {"claude-3-5-sonnet-20241022", "claude-3-opus", "claude-3-sonnet", "claude-3-haiku"},
        }

        try:
            if "gpt" in model_name:
                return self.openAI_model(messages, token_size, model_name)
            elif "gemini" in model_name:
                return self.gemini_model(messages, token_size, model_name)
            elif "deepseek" in model_name:
                return self.deepseek_model(messages, token_size, model_name)
            elif "llama" in model_name:
                return self.llama_model(messages, token_size, model_name)
            elif "claude" in model_name:
                return self.claude_model(messages, token_size, model_name)
        except Exception as e:
            return {"error": str(e)}



