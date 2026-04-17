from fastapi import Request


def build_tracking_context(request: Request) -> dict[str, str | None]:
    user_agent = request.headers.get("user-agent", "")
    referer = request.headers.get("referer")
    return {
        "ip": extract_client_ip(request),
        "user_agent": user_agent,
        "referer": referer,
        "country": extract_country(request),
        "device_type": detect_device_type(user_agent),
        "source": detect_source(user_agent, referer),
    }


def extract_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    for header in ("cf-connecting-ip", "x-real-ip"):
        value = request.headers.get(header)
        if value:
            return value.strip()

    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def extract_country(request: Request) -> str | None:
    for header in ("cf-ipcountry", "x-country-code"):
        value = request.headers.get(header)
        if value and value.upper() != "XX":
            return value.upper()
    return None


def detect_device_type(user_agent: str) -> str:
    normalized = user_agent.lower()
    mobile_terms = ("mobile", "android", "iphone", "ipad", "phone", "opera mini", "windows phone")
    return "mobile" if any(term in normalized for term in mobile_terms) else "desktop"


def detect_source(user_agent: str, referer: str | None) -> str:
    normalized_agent = user_agent.lower()
    normalized_referer = (referer or "").lower()

    checks = {
        "whatsapp": ("whatsapp", "wa.me", "api.whatsapp.com"),
        "instagram": ("instagram",),
        "facebook": ("facebook", "fb."),
        "google": ("google",),
        "email": ("outlook", "gmail", "mail"),
    }

    for source, terms in checks.items():
        if any(term in normalized_agent or term in normalized_referer for term in terms):
            return source

    if normalized_referer:
        return "referral"

    return "direct"
