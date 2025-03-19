import re
from urllib.parse import urlparse

TEXT_MAX_LENGTH = 50

# Domain matchers: (category, regex pattern)
DOMAIN_MATCHERS = [
    ("blog", r"blog\..*"),
    ("blog", r"medium\.com$"),
    ("community", r"community\..*"),
    ("community", r"forum\..*"),
    ("documentation", r"docs\..*"),
    ("e-commerce", r"amazon\.com$"),
    ("e-commerce", r"ebay\.com$"),
    ("jobs", r"teamtailor\.com$"),
    ("jobs", r"^(jobs\.|careers?\.).*"),
    ("jobs", r"job-boards.greenhouse.io"),
    ("newsletter", r"substack\.(com|net|app)$"),
    ("podcast", r"podcasts?\..*"),
    ("social media", r"youtube\.com$"),
    ("social media", r"youtu.be$"),
    ("social media", r"discord(app)?\.com$|discord\.gg$"),
    ("social media", r"t\.me$|telegram\.(me|org)$"),
    ("social media", r"slack\.(com|net|app)$"),
    ("social media", r"reddit\.(com|net|app)$"),
    ("social media", r"pinterest\.(com|net|app)$"),
    ("social media", r"twitch\.(com|tv)$"),
    ("social media", r"(facebook|fb)\.com$"),
    ("social media", r"linkedin\.com"),
    ("social media", r"tiktok\.com$"),
    ("social media", r"twitter\.com$|^x\.com$"),
    ("social media", r"instagram\.com$"),
    ("support", r"support\..*"),
]

# Path matchers
PATH_MATCHERS = [
    ("about", r"about(-us|-company)?/?$"),
    ("blog", r"(blog)/?$"),
    ("community", r"(community|forum|discussion|groups)/?$"),
    ("contact", r"contact(-us)?/?$"),
    ("faq", r"(faqs?|frequently-asked-questions|help)/?$"),
    ("jobs", r"(jobs|careers?|work-with-us|opportunities|join-us|open-roles)/?$"),
    ("press", r"(press|press-room|press-kit)/?$"),
    ("pricing", r"(pricing|plans|buy-now|pricing-and-plans)/?$"),
    ("podcast", r"(podcasts?)/?$"),
    ("privacy", r"(privacy-policy|privacy)/?$"),
    ("reviews", r"(testimonials|reviews|what-people-say)/?$"),
    ("services", r"(services|what-we-do|our-services)/?$"),
    ("signup", r"(signup|sign-up)/?$"),
    ("support", r"(support)/?$"),
    ("team", r"(team|our-team|meet-the-team)/?$"),
    ("work", r"(work|projects|portfolio)/?$"),
]

# Text matchers
TEXT_MATCHERS = [
    ("about", r"about(\s+)?(us|our\s+company)?"),
    ("contact", r"^contact$|^contact us$"),
    ("faq", r"faq|frequently\s+asked\s+questions"),
    ("home", r"^home$"),
    ("login", r"^(log\s*in|sign\s*in)$"),
    ("jobs", r"^(jobs|careers|work\s*with\s*us|opportunities|join\s*us|open\s*roles)"),
    ("privacy", r"privacy\s+policy"),
    ("media", r"media\s+kit"),
    ("press", r"press\s+room"),
    ("press", r"press\s+release"),
    ("press", r"press\s+kit"),
    ("press", r"news\s+room"),
    ("register", r"^(register|sign\s*up)$"),
    ("security", r"security\s+policy"),
    ("security", r"responsible\s+disclosure"),
    ("security", r"bug\s+bounty"),
    ("security", r"bug\s+bounties"),
    ("security", r"security\s+reporting"),
    ("security", r"security\s+disclosure"),
    ("terms", r"terms\s+(of\s+service|and\s+conditions)"),
]

# Patterns to ignore completely
IGNORE_REGEXES = [
    r"javascript:",  # JavaScript pseudo-links
    r"print=1|printable=true",  # Printer-friendly versions
    r"utm_source|utm_medium|utm_campaign",  # UTM tracking links
    r"sid=\d+|session_id=",  # Session IDs
    r"void\(0\)",  # JavaScript void links
    r"#$",  # Empty anchors
    r"^#[^/]",  # Page fragment links
    r"/cdn-cgi/",  # Cloudflare internal paths
    r"/wp-content/cache/",  # WordPress cache
    r"/wp-admin/",  # WordPress admin
    r"google\.com/url\?",  # Google redirect links
    r"facebook\.com/sharer",  # Social sharing links
    r"twitter\.com/intent/tweet",  # Twitter share links
]


def categorize_links(links: list[dict]) -> list[dict]:
    """Categorize a list of links based on a set of patterns.

    Args:
        links: List of dictionaries containing 'url', 'text', and 'title'
               - url: The full URL of the link
               - text: The anchor text
               - title: The title attribute or page title

    Returns:
        List of dictionaries containing 'url', 'text', 'title', and 'category'
        - url: The full URL of the link
        - text: The anchor text
        - title: The title attribute or page title
        - category: The category of the link

    """
    categorized_links = []

    for link_info in links:
        category = categorize_link(link_info)
        if category:
            link_info["category"] = category
            categorized_links.append(link_info)

    return categorized_links


def categorize_link(link_info: dict) -> str | None:  # noqa: C901, PLR0911, PLR0912
    """Categorize a link based on a set of patterns.

    Args:
        link_info: Dictionary containing 'url', 'text', and 'title'
                  - url: The full URL of the link
                  - text: The anchor text
                  - title: The title attribute or page title

    Returns:
        String containing the category or None if the link should be ignored

    """
    url = link_info.get("href", "")
    anchor_text = link_info.get("text", "").replace("\n", " ").strip()
    title = link_info.get("title", "").replace("\n", " ").strip()

    # Check ignore patterns first
    for pattern in IGNORE_REGEXES:
        if re.search(pattern, url, re.IGNORECASE):
            return "ignored"

    # Parse URL to extract domain and path
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    path = parsed_url.path

    if parsed_url.scheme == "mailto":
        return "email"

    if parsed_url.scheme in ["tel", "fax"]:
        return "telephone"

    if parsed_url.scheme in ["sms"]:
        return "sms"

    if parsed_url.scheme in ["data"]:
        return "data"

    # Check domain matchers
    for category, pattern in DOMAIN_MATCHERS:
        if re.search(pattern, domain, re.IGNORECASE):
            return category

    # Check path matchers
    for category, pattern in PATH_MATCHERS:
        if re.search(pattern, path, re.IGNORECASE):
            return category

    # Check title matchers
    if title and len(title) < TEXT_MAX_LENGTH:
        for category, pattern in TEXT_MATCHERS:
            if re.search(pattern, title, re.IGNORECASE):
                return category

    # Check anchor text matchers
    if anchor_text and len(anchor_text) < TEXT_MAX_LENGTH:
        for category, pattern in TEXT_MATCHERS:
            if re.search(pattern, anchor_text, re.IGNORECASE):
                return category

    # Check if it's just a home page (domain with no path or only /)
    if path in ["", "/"]:
        return "home"

    # If nothing matched
    return "unknown"
