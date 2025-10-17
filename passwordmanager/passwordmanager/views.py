from django.shortcuts import render


from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from django.views.decorators.csrf import ensure_csrf_cookie

from passwordmanager.utils import get_vite_assets


@ensure_csrf_cookie
def index(request):
    manifest = get_vite_assets()
    main_js = manifest["index.html"].get("file")
    main_css = manifest["index.html"].get("css", [None])[0]
    return render(
        request,
        "index.html",
        {
            "main_js": main_js,
            "main_css": main_css,
            "user_is_authenticated": request.user.is_authenticated,
            "username": (
                request.user.username if request.user.is_authenticated else None
            ),
        },
    )
