from groq import Groq
from nhcc_operations.config.settings.base import env
from ...finance.tools.mapper import expense_tools
from ...schemas import expense_schemas
from ...system_prompt import get_system_prompt
import json

client = Groq(api_key=env("GROQ_API_KEY"))

class RequestAPI:

    @staticmethod
    def initial_request(messages:list):
        return client.chat.completions.create(
            messages=messages, 
            model="openai/gpt-oss-120b",
            tools=expense_schemas,
            temperature=0.5, 
            tool_choice="auto",
            max_completion_tokens=300,
        )

    @staticmethod
    def tool_request(messages:list):
        return client.chat.completions.create(
            messages=messages, 
            model="openai/gpt-oss-120b",
            tools=expense_schemas,
            temperature=0.5, 
            tool_choice="auto",
            max_completion_tokens=300,
        )

    @staticmethod
    def final_request(messages:list):
        return client.chat.completions.create(
            messages=messages, 
            model="openai/gpt-oss-120b",
            tools=expense_schemas,
            temperature=0.5, 
            tool_choice="auto",
            max_completion_tokens=300,
        )

def tool_executor(tool_calls:list, messages:list):
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = expense_tools()[function_name]
        function_args = json.loads(tool_call.function.arguments)
    
    # Call the function with unpacked arguments
        result = function_to_call(**function_args)
        # Update the memory
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(result),
        })

def orchestrator():
    """Orchestrates the parallel agent workflow."""
    request = RequestAPI()
    # Make the initial request
    user_input = input("You: ")
    messages = [
        {
            "role": "system",
            "content": get_system_prompt()
        },
        {"role": "user", "content": user_input}
    ]
    max_iterations = 3
    try:
        initial_response = request.initial_request(messages)
        for _ in range(max_iterations):
            assistant_message = initial_response.choices[0].message
            messages.append(assistant_message)

            tool_calls = assistant_message.tool_calls or []
            if not tool_calls:
                continue
            
            tool_executor(tool_calls, messages)
            initial_response = request.tool_request(messages)
        final_message = initial_response.choices[0].message.content
        print(F"Assistant: {final_message}")

    except Exception as error:
        print(f"Error: {str(error)}")
        raise 

from django.core.management.base import BaseCommand
class Command(BaseCommand):
    help="Run NHCC AI assistant orchestrator"

    def handle(self, *args, **options):
        orchestrator()

