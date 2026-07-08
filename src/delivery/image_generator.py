import io
from typing import List
from PIL import Image, ImageDraw, ImageFont
import textwrap
from datetime import datetime
from src.storage.models import Fact

def generate_newspaper_image_pil(facts: List[Fact]) -> bytes:
    """Generates a clean, readable newspaper image using Pillow."""
    width, height = 1080, 1080
    bg_color = (30, 30, 30)
    text_color = (255, 255, 255)
    accent_color = (255, 215, 0) # Gold
    
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    try:
        # Load a default font if custom font is not available
        try:
            # Try to load Arial (Windows standard)
            title_font = ImageFont.truetype("arialbd.ttf", 80)
            date_font = ImageFont.truetype("arial.ttf", 30)
            headline_font = ImageFont.truetype("arialbd.ttf", 40)
            body_font = ImageFont.truetype("arial.ttf", 30)
            beat_font = ImageFont.truetype("arialbd.ttf", 25)
        except IOError:
            # Fallback to default
            title_font = ImageFont.load_default()
            date_font = ImageFont.load_default()
            headline_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            beat_font = ImageFont.load_default()
    except Exception:
        title_font = ImageFont.load_default()
        date_font = ImageFont.load_default()
        headline_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        beat_font = ImageFont.load_default()

    # Draw Header
    draw.text((50, 50), "DailyGK", fill=accent_color, font=title_font)
    
    # Draw Date
    date_str = datetime.now().strftime("%B %d, %Y")
    draw.text((width - 300, 90), date_str, fill=(200, 200, 200), font=date_font)
    
    # Draw line under header
    draw.line([(50, 150), (width - 50, 150)], fill=accent_color, width=3)
    
    y_pos = 180
    
    # Print up to 3 facts
    facts_to_draw = facts[:3] if facts else []
    
    if not facts_to_draw:
        draw.text((50, y_pos), "No news available today.", fill=text_color, font=body_font)
    
    for idx, fact in enumerate(facts_to_draw, 1):
        if y_pos > height - 100:
            break
            
        # Draw Beat
        draw.text((50, y_pos), f"{fact.beat.upper()}", fill=accent_color, font=beat_font)
        y_pos += 40
        
        # Draw Headline
        wrapped_headline = textwrap.fill(fact.headline, width=50)
        draw.multiline_text((50, y_pos), wrapped_headline, fill=text_color, font=headline_font, spacing=10)
        
        # Calculate height taken by headline
        lines = wrapped_headline.count('\n') + 1
        y_pos += (lines * 50) + 10
        
        # Draw Core Fact
        wrapped_fact = textwrap.fill(fact.core_fact, width=65)
        draw.multiline_text((50, y_pos), wrapped_fact, fill=(220, 220, 220), font=body_font, spacing=8)
        
        # Calculate height taken by core fact
        lines = wrapped_fact.count('\n') + 1
        y_pos += (lines * 40) + 30
        
        # Draw line separator
        if idx < len(facts_to_draw):
            draw.line([(50, y_pos), (width - 50, y_pos)], fill=(100, 100, 100), width=1)
            y_pos += 30

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=90)
    return img_byte_arr.getvalue()

if __name__ == "__main__":
    # Test script
    from src.storage.models import Fact
    dummy = [
        Fact(headline="Supreme Court Upholds Article 370 Abrogation", beat="Polity and Governance", core_fact="The Supreme Court unanimously upheld the President's order abrogating Article 370 in J&K.", why_it_matters="Reaffirms integration."),
        Fact(headline="RBI Keeps Repo Rate Unchanged at 6.5%", beat="Economy", core_fact="The Monetary Policy Committee decided to maintain the status quo on the repo rate.", why_it_matters="Controls inflation.")
    ]
    img_bytes = generate_newspaper_image_pil(dummy)
    with open("test_newspaper.jpg", "wb") as f:
        f.write(img_bytes)
    print("Test image generated: test_newspaper.jpg")
