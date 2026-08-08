from django.views import View
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.shortcuts import redirect
from core.utils.error_responses import SERVER_ERROR
from .forms import ChatForm
from .orchestration.orchestrator import ask_assistant
import markdown

chat_temp = "ai_assistant/chat_ui.html"
chat_url_name = "ask_ai"

@method_decorator(login_required, "dispatch")
class AskAssistant(View):

    def get(self, request):
        return render(request, template_name=chat_temp)

    def formatted_response(self, response):
        
        return markdown.markdown(
            response,
            extensions=["tables", "nl2br"]
        )

    def post(self, request):
        form = ChatForm(data={"prompt": request.POST.get("prompt")})
        if form.is_valid():
            try:
                prompt = form.cleaned_data["prompt"]
                response = ask_assistant(prompt)
                print(response)
                return JsonResponse({
                    "response": self.formatted_response(response)
                })
            except Exception:
                code = 500
                messages.error(request, SERVER_ERROR)

        messages.error(request, form.errors)
        code = 400
        return render(
            request=request, template_name=chat_temp, 
            status=code
        )

            






