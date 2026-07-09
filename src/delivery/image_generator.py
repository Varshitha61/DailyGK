import os
import logging
from typing import List
from datetime import datetime
from src.storage.models import Fact

logger = logging.getLogger(__name__)

def get_badge_color(beat: str) -> str:
    beat_lower = beat.lower()
    if 'polity' in beat_lower or 'governance' in beat_lower:
        return '#3b5998' # Muted blue
    elif 'economy' in beat_lower:
        return '#8b0000' # Maroon
    elif 'science' in beat_lower or 'tech' in beat_lower:
        return '#008080' # Teal
    elif 'international' in beat_lower or 'world' in beat_lower:
        return '#cc5500' # Burnt Orange
    elif 'environment' in beat_lower:
        return '#2e8b57' # Sea Green
    else:
        return '#696969' # Dim Gray

def generate_newspaper_image_pil(facts: List[Fact]) -> bytes:
    """Generates a crisp infographic layout using HTML/CSS and html2image."""
    from html2image import Html2Image
    
    browser_executable = None
    if os.path.exists('/usr/bin/chromium-browser'):
        browser_executable = '/usr/bin/chromium-browser'
    elif os.path.exists('/usr/bin/chromium'):
        browser_executable = '/usr/bin/chromium'
        
    hti = Html2Image(browser_executable=browser_executable, output_path='.', size=(900, 1300))
    
    date_str = datetime.now().strftime("%B %d, %Y")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@400;600;700&display=swap');
            
            body {{
                margin: 0;
                padding: 40px;
                background-color: #f8f9fa; /* Very light gray */
                font-family: 'Inter', sans-serif;
                color: #1a1a1a;
                width: 820px;
                box-sizing: border-box;
            }}
            .header {{
                text-align: center;
                padding-bottom: 15px;
                margin-bottom: 20px;
                border-bottom: 2px solid #1a1a1a;
            }}
            .title {{
                font-family: 'Playfair Display', serif;
                font-size: 56px;
                font-weight: 900;
                margin: 0;
                color: #1a1a1a;
            }}
            .sub-header {{
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 20px;
                font-size: 16px;
                font-weight: 600;
                color: #4a4a4a;
                margin-top: 10px;
            }}
            .top-headline {{
                text-align: center;
                font-size: 32px;
                font-weight: 700;
                margin: 0 0 30px 0;
                color: #1a1a1a;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}
            .grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 25px;
                margin-bottom: 30px;
            }}
            .card {{
                background-color: #ffffff;
                border-radius: 8px;
                padding: 24px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.04);
                border: 1px solid #eaeaea;
                display: flex;
                flex-direction: column;
            }}
            .badge {{
                align-self: flex-start;
                padding: 4px 10px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 700;
                text-transform: uppercase;
                color: #ffffff;
                margin-bottom: 15px;
            }}
            .card-headline {{
                font-size: 22px;
                font-weight: 700;
                line-height: 1.3;
                margin: 0 0 12px 0;
                color: #1a1a1a;
            }}
            .card-body {{
                font-size: 16px;
                line-height: 1.5;
                color: #333333;
                margin: 0 0 15px 0;
                flex-grow: 1;
            }}
            .card-key {{
                font-size: 15px;
                font-weight: 600;
                color: #d32f2f;
                background-color: #fcede8;
                padding: 8px 12px;
                border-radius: 4px;
                margin: 0;
            }}
            .footer {{
                border-top: 1px solid #cccccc;
                padding-top: 15px;
                display: flex;
                justify-content: space-between;
                font-size: 14px;
                font-weight: 600;
                color: #666666;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1 class="title">Daily Current Affairs</h1>
            <div class="sub-header">
                <span>{date_str}</span>
                <span>•</span>
                <span>UPSC, SSC, and Govt Exam Prep</span>
            </div>
        </div>
    """
    
    facts_to_draw = facts[:6] if facts else []
    
    if facts_to_draw:
        top_headline = facts_to_draw[0].headline
        html_content += f'<div class="top-headline">{top_headline}</div>'
    else:
        html_content += '<div class="top-headline">No major news updates available today</div>'
        
    html_content += '<div class="grid">'
        
    for fact in facts_to_draw:
        badge_color = get_badge_color(fact.beat)
        
        html_content += f"""
            <div class="card">
                <div class="badge" style="background-color: {badge_color};">{fact.beat}</div>
                <h2 class="card-headline">{fact.headline}</h2>
                <p class="card-body">{fact.core_fact} {fact.why_it_matters}</p>
                <div class="card-key">Key Fact: {fact.number_or_name}</div>
            </div>
        """
        
    html_content += """
        </div>
        <div class="footer">
            <span>Page 1 of today's brief</span>
            <span>5 minutes today, one step closer to your exam.</span>
        </div>
    </body>
    </html>
    """
    
    output_filename = "newspaper_out.jpg"
    try:
        # Generate the image
        hti.screenshot(html_str=html_content, save_as=output_filename)
        
        # Read the generated image bytes
        with open(output_filename, 'rb') as f:
            image_bytes = f.read()
            
        # Clean up
        if os.path.exists(output_filename):
            os.remove(output_filename)
            
        return image_bytes
    except Exception as e:
        logger.exception("Error generating html2image")
        return None

if __name__ == "__main__":
    # Test script
    dummy = [
        Fact(headline="Supreme Court Upholds Article 370 Abrogation", beat="Polity", core_fact="The Supreme Court unanimously upheld the President's order abrogating Article 370 in J&K.", why_it_matters="Reaffirms integration.", number_or_name="Article 370"),
        Fact(headline="RBI Keeps Repo Rate Unchanged at 6.5%", beat="Economy", core_fact="The Monetary Policy Committee decided to maintain the status quo.", why_it_matters="Controls inflation.", number_or_name="6.5%"),
        Fact(headline="ISRO Successfully Launches XPoSat Mission", beat="Science", core_fact="India's first dedicated polarimetry mission to study X-ray emission.", why_it_matters="Advances astrophysics.", number_or_name="XPoSat"),
        Fact(headline="COP28 Summit Concludes in Dubai with Historic Deal", beat="International", core_fact="Nations agreed to transition away from fossil fuels in energy systems.", why_it_matters="Crucial for climate goals.", number_or_name="COP28")
    ]
    img_bytes = generate_newspaper_image_pil(dummy)
    if img_bytes:
        with open("test_infographic.jpg", "wb") as f:
            f.write(img_bytes)
        print("Test image generated: test_infographic.jpg")
    else:
        print("Failed to generate image.")
