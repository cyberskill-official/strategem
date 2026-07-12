from __future__ import annotations


def security_headers(*, hsts: bool = True) -> dict[str, str]:
    h = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "no-referrer",
        "Content-Security-Policy": "default-src 'self'",
        "Permissions-Policy": "geolocation=()",
        "X-TLS-Min-Version": "1.3",
    }
    if hsts:
        h["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    return h
