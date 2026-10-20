from starlette.middleware.cors import CORSMiddleware

from app.core.config import web_settings

origins = [o.strip() for o in web_settings.cors_origins.split(",") if o.strip()]
expose_headers = [
    h.strip() for h in web_settings.cors_expose_headers.split(",") if h.strip()
]

MIDDLEWARE = (
    CORSMiddleware,
    {
        "allow_origins": origins,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
        "expose_headers": expose_headers,
    },
)
