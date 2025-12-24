import textwrap
from typing import Any

from fastapi.openapi.docs import swagger_ui_default_parameters
from jinja2 import Template
from starlette.responses import HTMLResponse


# fastapi.openapi.docs.get_swagger_ui_html 참고
# 기존 함수는 StandaloneLayout 를 사용할 수 없으므로 (js, layout 정의 문제) swagger_ui_parameters["urls"] 사용 불가
def get_custom_swagger_ui_html(
    *,
    openapi_url: str,
    title: str,
    oauth2_redirect_url: str | None = None,
    init_oauth: dict[str, Any] | None = None,
    swagger_ui_parameters: dict = None,
) -> HTMLResponse:
    current_swagger_ui_parameters = swagger_ui_default_parameters.copy()
    if swagger_ui_parameters:
        current_swagger_ui_parameters.update(swagger_ui_parameters)

    current_swagger_ui_parameters["url"] = openapi_url

    if oauth2_redirect_url:
        current_swagger_ui_parameters["oauth2RedirectUrl"] = f"window.location.origin + '{oauth2_redirect_url}'"

    html_template = textwrap.dedent("""
    <!DOCTYPE html>
    <html>
    <head>
        <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
        <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
        <title>{{ title }}</title>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
        <script>
            const config = {{ swagger_params | tojson(4) }};
            config.presets = [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset]

            const ui = SwaggerUIBundle(config)
            {% if init_oauth %}
            ui.initOAuth({{ init_oauth | tojson(4) }});
            {% endif %}
        </script>
    </body>
    </html>
    """).strip()

    template = Template(html_template)
    final_html = template.render(
        title=title,
        swagger_params=current_swagger_ui_parameters,
        init_oauth=init_oauth,
    )

    return HTMLResponse(content=final_html)
