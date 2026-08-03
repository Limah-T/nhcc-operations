from django.http import HttpResponse
from weasyprint import HTML, CSS
from django.conf import settings

def file_naming_constructor(type, month, year, start, end) -> str:
    return f"{month}_{year}_{start.day}_to_{end.day}_{type.lower()}.pdf"


def pdf_generator(html_string, request, file_name, css_path):
    pdf = HTML(
        string=html_string,
        base_url=request.build_absolute_uri("/")
    ).write_pdf(
        stylesheets=[
            CSS(settings.STATIC_ROOT / css_path)
        ]
    )

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{file_name}"'
    return response