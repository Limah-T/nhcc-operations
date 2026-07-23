from django.contrib import messages
from django.shortcuts import render, redirect

def error_response(
        request, template, context, message, status_code
    ):
    messages.error(request, message)
    return render(
        request=request, 
        template_name=template,
        context=context,
        status=status_code
    )
    
def success_response(request, url_name, message):
    if message:
        messages.success(request, message)
    return redirect(url_name)