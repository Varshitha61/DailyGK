import os
from typing import List
from datetime import datetime
from src.storage.models import Fact

def generate_newspaper_image_pil(facts: List[Fact]) -> bytes:
    """Generates a crisp, traditional newspaper layout using HTML/CSS and html2image."""
    from html2image import Html2Image
    
    hti = Html2Image(output_path='.', size=(800, 1000))
    
    date_str = datetime.now().strftime("%B %d, %Y")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Lora:ital,wght@0,400;0,600;1,400&display=swap');
            
            body {{
                margin: 0;
                padding: 40px;
                background-color: #f4f1ea;
                font-family: 'Lora', serif;
                color: #2c2c2c;
                width: 720px;
                box-sizing: border-box;
            }}
            .header {{
                text-align: center;
                border-bottom: 4px solid #2c2c2c;
                border-top: 4px solid #2c2c2c;
                padding: 20px 0;
                margin-bottom: 30px;
            }}
            .title {{
                font-family: 'Playfair Display', serif;
                font-size: 64px;
                font-weight: 900;
                margin: 0;
                letter-spacing: -1px;
                text-transform: uppercase;
            }}
            .sub-header {{
                display: flex;
                justify-content: space-between;
                font-size: 14px;
                text-transform: uppercase;
                margin-top: 10px;
                font-weight: 600;
                border-top: 1px solid #2c2c2c;
                padding-top: 5px;
            }}
            .columns {{
                display: column;
            }}
            .article {{
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 1px solid #ccc;
            }}
            .article:last-child {{
                border-bottom: none;
            }}
            .beat {{
                font-family: 'Playfair Display', serif;
                font-size: 14px;
                font-weight: 700;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 5px;
            }}
            .headline {{
                font-family: 'Playfair Display', serif;
                font-size: 32px;
                font-weight: 700;
                line-height: 1.1;
                margin: 0 0 10px 0;
            }}
            .content {{
                font-size: 18px;
                line-height: 1.5;
                text-align: justify;
                margin: 0;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1 class="title">The DailyGK Times</h1>
            <div class="sub-header">
                <span>The Premier Daily Digest for UPSC</span>
                <span>{date_str}</span>
            </div>
        </div>
        <div class="columns">
    """
    
    facts_to_draw = facts[:4] if facts else []
    
    if not facts_to_draw:
        html_content += """
            <div class="article">
                <p class="content">No major news updates available today. Check back tomorrow!</p>
            </div>
        """
        
    for fact in facts_to_draw:
        html_content += f"""
            <div class="article">
                <div class="beat">{fact.beat}</div>
                <h2 class="headline">{fact.headline}</h2>
                <p class="content"><strong>What happened:</strong> {fact.core_fact}</p>
                <p class="content"><strong>Why it matters:</strong> {fact.why_it_matters}</p>
            </div>
        """
        
    html_content += """
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
        print(f"Error generating html2image: {e}")
        return None

if __name__ == "__main__":
    # Test script
    dummy = [
        Fact(headline="Supreme Court Upholds Article 370 Abrogation", beat="Polity and Governance", core_fact="The Supreme Court unanimously upheld the President's order abrogating Article 370 in J&K.", why_it_matters="Reaffirms the complete integration of Jammu & Kashmir into the Union of India."),
        Fact(headline="RBI Keeps Repo Rate Unchanged at 6.5%", beat="Economy", core_fact="The Monetary Policy Committee decided to maintain the status quo on the repo rate.", why_it_matters="Aims to control inflation while supporting economic growth.")
    ]
    img_bytes = generate_newspaper_image_pil(dummy)
    if img_bytes:
        with open("test_newspaper_html.jpg", "wb") as f:
            f.write(img_bytes)
        print("Test image generated: test_newspaper_html.jpg")
    else:
        print("Failed to generate image.")
