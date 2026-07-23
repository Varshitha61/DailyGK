import os
import logging
from typing import List
from datetime import datetime
from src.storage.models import Fact

logger = logging.getLogger(__name__)

def get_badge_color(beat: str) -> str:
    beat_lower = beat.lower()
    if 'polity' in beat_lower or 'governance' in beat_lower:
        return 'linear-gradient(135deg, #2563eb, #3b82f6)' # Blue gradient
    elif 'economy' in beat_lower:
        return 'linear-gradient(135deg, #059669, #10b981)' # Emerald gradient
    elif 'science' in beat_lower or 'tech' in beat_lower:
        return 'linear-gradient(135deg, #7c3aed, #8b5cf6)' # Violet gradient
    elif 'international' in beat_lower or 'world' in beat_lower:
        return 'linear-gradient(135deg, #d97706, #f59e0b)' # Amber gradient
    elif 'environment' in beat_lower:
        return 'linear-gradient(135deg, #0d9488, #14b8a6)' # Teal gradient
    else:
        return 'linear-gradient(135deg, #475569, #64748b)' # Slate gradient

def generate_newspaper_image_pil(facts: List[Fact]) -> bytes:
    """Generates a high-impact Poster layout using HTML/CSS and html2image."""
    from html2image import Html2Image
    
    hti = Html2Image(output_path='.', size=(1080, 2100))
    # Set absolute path for temp_path to ensure Chrome correctly locates the temporary HTML file
    hti.temp_path = os.path.abspath('.')
    hti.browser.flags.extend([
        '--no-sandbox', 
        '--disable-gpu', 
        '--allow-file-access-from-files', 
        '--disable-dev-shm-usage'
    ])
    
    date_str = datetime.now().strftime("%B %d, %Y")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
            
            * {{
                box-sizing: border-box;
            }}
            
            body {{
                margin: 0;
                padding: 44px;
                background: linear-gradient(145deg, #080c14 0%, #0f172a 40%, #17153b 100%);
                font-family: 'Plus Jakarta Sans', sans-serif;
                color: #f8fafc;
                width: 1080px;
                min-height: 1920px;
            }}

            .poster-container {{
                background: rgba(15, 23, 42, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 24px;
                padding: 36px;
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
                position: relative;
            }}
            
            .header {{
                text-align: center;
                padding-bottom: 28px;
                margin-bottom: 28px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.12);
            }}
            
            .top-pill {{
                display: inline-block;
                padding: 6px 18px;
                background: linear-gradient(90deg, #6366f1, #a855f7);
                border-radius: 50px;
                font-size: 13px;
                font-weight: 800;
                letter-spacing: 1.5px;
                text-transform: uppercase;
                color: #ffffff;
                margin-bottom: 14px;
                box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
            }}

            .title {{
                font-family: 'Outfit', sans-serif;
                font-size: 52px;
                font-weight: 900;
                margin: 0 0 12px 0;
                letter-spacing: -1px;
                background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-transform: uppercase;
            }}

            .sub-header {{
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 16px;
                font-size: 15px;
                font-weight: 600;
                color: #94a3b8;
            }}

            .date-badge {{
                background: rgba(255, 255, 255, 0.08);
                padding: 4px 14px;
                border-radius: 8px;
                color: #38bdf8;
                border: 1px solid rgba(56, 189, 248, 0.2);
            }}

            .exam-tags {{
                color: #e2e8f0;
                letter-spacing: 0.5px;
                font-weight: 700;
            }}

            /* Lead Story Box */
            .lead-story {{
                background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(168, 85, 247, 0.08) 100%);
                border: 1.5px solid rgba(168, 85, 247, 0.4);
                border-radius: 18px;
                padding: 28px;
                margin-bottom: 28px;
                position: relative;
            }}

            .lead-tag {{
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 13px;
                font-weight: 800;
                color: #fbbf24;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 12px;
            }}

            .lead-headline {{
                font-family: 'Outfit', sans-serif;
                font-size: 28px;
                font-weight: 800;
                line-height: 1.25;
                margin: 0 0 14px 0;
                color: #ffffff;
            }}

            .lead-body {{
                font-size: 16px;
                line-height: 1.6;
                color: #cbd5e1;
                margin: 0 0 18px 0;
            }}

            .lead-key {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: rgba(99, 102, 241, 0.2);
                border: 1px solid rgba(165, 180, 252, 0.4);
                color: #a5b4fc;
                padding: 10px 18px;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 700;
            }}

            /* Grid Layout */
            .grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 22px;
                margin-bottom: 28px;
            }}

            .card {{
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
                padding: 22px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }}

            .badge {{
                align-self: flex-start;
                padding: 5px 12px;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 0.8px;
                color: #ffffff;
                margin-bottom: 14px;
            }}

            .card-headline {{
                font-family: 'Outfit', sans-serif;
                font-size: 20px;
                font-weight: 700;
                line-height: 1.3;
                margin: 0 0 10px 0;
                color: #f8fafc;
            }}

            .card-body {{
                font-size: 14.5px;
                line-height: 1.55;
                color: #94a3b8;
                margin: 0 0 16px 0;
                flex-grow: 1;
            }}

            .card-key {{
                font-size: 13.5px;
                font-weight: 700;
                color: #fbbf24;
                background: rgba(245, 158, 11, 0.1);
                border: 1px solid rgba(245, 158, 11, 0.25);
                padding: 8px 12px;
                border-radius: 8px;
            }}

            .footer {{
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                padding-top: 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 13.5px;
                font-weight: 600;
                color: #64748b;
            }}

            .footer-brand {{
                color: #38bdf8;
                font-weight: 700;
            }}
        </style>
    </head>
    <body>
        <div class="poster-container">
            <div class="header">
                <div class="top-pill">Daily GK Briefing Poster</div>
                <h1 class="title">Daily Current Affairs</h1>
                <div class="sub-header">
                    <span class="date-badge">{date_str}</span>
                    <span>•</span>
                    <span class="exam-tags">UPSC • SSC CGL • BANKING • RAILWAYS</span>
                </div>
            </div>
    """
    
    facts_to_draw = facts[:7] if facts else []
    
    if facts_to_draw:
        top_fact = facts_to_draw[0]
        top_badge_color = get_badge_color(top_fact.beat)
        
        html_content += f"""
            <div class="lead-story">
                <div class="lead-tag">
                    <span>🔥 TOP STORY OF THE DAY</span>
                    <span>•</span>
                    <span style="color: #a5b4fc;">{top_fact.beat}</span>
                </div>
                <h2 class="lead-headline">{top_fact.headline}</h2>
                <p class="lead-body">{top_fact.core_fact} {top_fact.why_it_matters}</p>
                {f'<div class="lead-key"><span>📌 Exam Pointer:</span> <span>{top_fact.number_or_name}</span></div>' if top_fact.number_or_name else ''}
            </div>
        """
        grid_facts = facts_to_draw[1:]
    else:
        html_content += '<div class="lead-story"><h2 class="lead-headline">No major news updates available today</h2></div>'
        grid_facts = []
        
    html_content += '<div class="grid">'
        
    for fact in grid_facts:
        badge_bg = get_badge_color(fact.beat)
        
        html_content += f"""
            <div class="card">
                <div>
                    <div class="badge" style="background: {badge_bg};">{fact.beat}</div>
                    <h3 class="card-headline">{fact.headline}</h3>
                    <p class="card-body">{fact.core_fact} {fact.why_it_matters}</p>
                </div>
                {f'<div class="card-key">🔑 Key Fact: {fact.number_or_name}</div>' if fact.number_or_name else ''}
            </div>
        """
        
    html_content += """
            </div>
            <div class="footer">
                <span class="footer-brand">⚡ DailyGK Infographic Edition</span>
                <span>Stay ahead with concise daily exam revision</span>
            </div>
        </div>
    </body>
    </html>
    """
    
    output_filename = "newspaper_out.jpg"
    try:
        hti.screenshot(html_str=html_content, save_as=output_filename)
        
        with open(output_filename, 'rb') as f:
            raw_bytes = f.read()
            
        if os.path.exists(output_filename):
            os.remove(output_filename)

        # Use PIL to automatically crop excess empty background space at bottom
        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(raw_bytes))
            rgb_img = img.convert('RGB')
            width, height = rgb_img.size
            bg_color = rgb_img.getpixel((20, height - 20))
            
            last_content_y = height
            for y in range(height - 10, 200, -10):
                sample_pixels = [rgb_img.getpixel((x, y)) for x in range(100, width - 100, 100)]
                diffs = [abs(p[0] - bg_color[0]) + abs(p[1] - bg_color[1]) + abs(p[2] - bg_color[2]) for p in sample_pixels]
                if any(d > 25 for d in diffs):
                    last_content_y = min(height, y + 50)
                    break
                    
            cropped_img = img.crop((0, 0, width, last_content_y))
            out_io = io.BytesIO()
            cropped_img.save(out_io, format='JPEG', quality=95)
            return out_io.getvalue()
        except Exception as crop_err:
            logger.warning(f"Failed to auto-crop poster image: {crop_err}")
            return raw_bytes
            
    except Exception as e:
        logger.exception("Error generating poster image via html2image")
        return None

if __name__ == "__main__":
    dummy = [
        Fact(headline="Supreme Court Upholds Article 370 Abrogation", beat="Polity", core_fact="The Supreme Court unanimously upheld the President's order abrogating Article 370 in J&K.", why_it_matters="Reaffirms integration.", number_or_name="Article 370"),
        Fact(headline="RBI Keeps Repo Rate Unchanged at 6.5%", beat="Economy", core_fact="The Monetary Policy Committee decided to maintain the status quo.", why_it_matters="Controls inflation.", number_or_name="6.5%"),
        Fact(headline="ISRO Successfully Launches XPoSat Mission", beat="Science", core_fact="India's first dedicated polarimetry mission to study X-ray emission.", why_it_matters="Advances astrophysics.", number_or_name="XPoSat"),
        Fact(headline="COP28 Summit Concludes in Dubai with Historic Deal", beat="International", core_fact="Nations agreed to transition away from fossil fuels in energy systems.", why_it_matters="Crucial for climate goals.", number_or_name="COP28"),
        Fact(headline="India Unveils World's Largest Renewable Energy Park", beat="Environment", core_fact="30 GW Khavda solar & wind park inaugurated in Gujarat.", why_it_matters="Boosts green transition.", number_or_name="30 GW Khavda Park")
    ]
    img_bytes = generate_newspaper_image_pil(dummy)
    if img_bytes:
        with open("test_infographic.jpg", "wb") as f:
            f.write(img_bytes)
        print("Test poster image generated: test_infographic.jpg")
    else:
        print("Failed to generate image.")

