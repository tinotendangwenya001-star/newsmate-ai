"""Build the approved, copy-ready publishing package."""
import datetime as dt

DISCLOSURE = "This story was drafted with AI assistance and reviewed and approved by a journalist."


def to_markdown(pkg: dict, approved_by: str) -> str:
    stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""# {pkg['headline']}

{pkg['article']}

_{DISCLOSURE}_

---
## Social copy
**Facebook**
{pkg['facebook']}

**X**
{pkg['x_post']}

**WhatsApp**
{pkg['whatsapp']}

---
Approved by: {approved_by} | {stamp}
"""
