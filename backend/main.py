import random
import urllib.request
import urllib.parse
from xml.etree import ElementTree
import html
import os
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI(
    title="Google News AI Aggregator",
    description="A multi-page Google News aggregator with dynamic RSS feed integration and offline fallback data.",
    version="1.3.0"
)

# Setup path dynamics relative to this file (in /backend)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "../frontend")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Mount static files from /frontend
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Templates setup from /backend/templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)


class ChatRequest(BaseModel):
    message: str


# Robust Fallback News database to display when Google News RSS throttles/blocks GCP cloud requests
FALLBACK_DATABASE = {
    "WORLD": [
        {
            "id": 101,
            "title": "Global Climate Accord Reaches Milestone Agreement",
            "category": "World",
            "snippet": "Delegates from 190 nations agree on new green transition funding metrics and emissions ceilings at the summit.",
            "content": "The new accord focuses on setting strict target metrics for carbon reductions and providing direct financial pathways for developing nations to build renewable solar and wind grids. Analysts praise the compromise as a turning point in international environmental coordination.",
            "image_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=600&q=80",
            "date": "July 1, 2026",
            "read_time": "4 min read",
            "author": "Associated Press",
            "link": "https://news.google.com"
        },
        {
            "id": 102,
            "title": "Deep Ocean Expedition Uncovers Unprecedented Biodiversity",
            "category": "World",
            "snippet": "Marine biologists exploring the Mariana Trench trench catalog over 50 new species using deep-diving rovers.",
            "content": "Equipped with advanced robotic arms and ultra-high-definition cameras, the international research team captured video documentation of previously unknown organisms thriving in extreme pressures. The discoveries are prompting new debates on ocean conservation policies.",
            "image_url": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?auto=format&fit=crop&w=600&q=80",
            "date": "June 30, 2026",
            "read_time": "5 min read",
            "author": "Reuters",
            "link": "https://news.google.com"
        }
    ],
    "BUSINESS": [
        {
            "id": 201,
            "title": "Tech Stocks Rally Drives Market Indices to Record Highs",
            "category": "Business",
            "snippet": "Major indexes closed at historic peaks today, fueled by better-than-expected retail reports and strong chip manufacturer gains.",
            "content": "Investment sentiment remains bullish as inflation numbers begin to cool down globally. Consumer discretionary and microchip hardware stocks led today's market rally, with financial analysts forecasting continued steady growth through the next fiscal quarter.",
            "image_url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=600&q=80",
            "date": "July 1, 2026",
            "read_time": "3 min read",
            "author": "Bloomberg",
            "link": "https://news.google.com"
        },
        {
            "id": 202,
            "title": "Global Supply Chains Stabilize as Shipping Rates Normalize",
            "category": "Business",
            "snippet": "A comprehensive logistics industry index reports container costs have returned to pre-congestion averages.",
            "content": "The shipping sector shows strong recovery signs after two years of extreme volatility. Improved port operations, newly built mega-freighters, and automated cargo handling stations have successfully eliminated long wait bottlenecks at global shipping corridors.",
            "image_url": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=600&q=80",
            "date": "June 29, 2026",
            "read_time": "4 min read",
            "author": "Financial Times",
            "link": "https://news.google.com"
        }
    ],
    "TECHNOLOGY": [
        {
            "id": 301,
            "title": "Google Unveils Gemini 1.5 Pro with Unprecedented 2M Token Context",
            "category": "Technology",
            "snippet": "Developers can now analyze full codebases or massive hours of video files in a single, high-fidelity prompt.",
            "content": "Google's updated context window enables unprecedented reasoning capabilities. Cloud developers can ingest hundreds of files or dense documentation directly inside Vertex AI to build complex agent workflows. The release represents a major milestone in foundation model memory scaling.",
            "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=600&q=80",
            "date": "July 1, 2026",
            "read_time": "4 min read",
            "author": "Google Press Office",
            "link": "https://news.google.com"
        },
        {
            "id": 302,
            "title": "Next-Gen Quantum Processor Reaches Quantum Supremacy Milestone",
            "category": "Technology",
            "snippet": "A leading research laboratory demonstrates error-corrected operations on a new 120-qubit superconducting unit.",
            "content": "The quantum research community celebrates the achievement of low-error, fault-tolerant operations. The new chip successfully processed complex chemistry modeling algorithms in seconds that would require classical supercomputers thousands of years to solve.",
            "image_url": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=600&q=80",
            "date": "June 28, 2026",
            "read_time": "5 min read",
            "author": "TechCrunch",
            "link": "https://news.google.com"
        }
    ],
    "SPORTS": [
        {
            "id": 401,
            "title": "Underdog Team Clinches Historic Championship Victory",
            "category": "Sports",
            "snippet": "A thrilling final match ends in a penalty shootout, crowning a first-time champion in front of a sold-out stadium.",
            "content": "Against all odds, the lower-ranked team executed a flawless defensive strategy, forcing the tournament favorites into double overtime. A decisive save in the final shootout round sealed the victory, initiating city-wide celebrations.",
            "image_url": "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?auto=format&fit=crop&w=600&q=80",
            "date": "July 1, 2026",
            "read_time": "3 min read",
            "author": "ESPN",
            "link": "https://news.google.com"
        },
        {
            "id": 402,
            "title": "World Record Shattered in Women's 100m Athletics Final",
            "category": "Sports",
            "snippet": "A stunning performance at the international grand prix sees the sprint record beaten by 0.04 seconds.",
            "content": "Wind conditions were perfect as the gold medalist exploded out of the blocks, maintaining an unmatched velocity through the finish line. Sports scientists attribute the record-breaking speed to advanced carbon-plated running shoe technology.",
            "image_url": "https://images.unsplash.com/photo-1517649763962-0c623066013b?auto=format&fit=crop&w=600&q=80",
            "date": "June 29, 2026",
            "read_time": "3 min read",
            "author": "Sports Illustrated",
            "link": "https://news.google.com"
        }
    ],
    "SCIENCE": [
        {
            "id": 501,
            "title": "Space Telescope Discovers Biosignature Elements on Exoplanet",
            "category": "Science",
            "snippet": "Astronomers detect water vapor and carbon molecules in the atmosphere of a planet orbiting a nearby red dwarf.",
            "content": "Analyzing spectroscopic data gathered over three transits, researchers confirmed atmospheric composition compatible with biological activity. While not definitive proof of life, the discovery designates the planet as a high-priority target for future missions.",
            "image_url": "https://images.unsplash.com/photo-1507668077129-56e32842fceb?auto=format&fit=crop&w=600&q=80",
            "date": "July 1, 2026",
            "read_time": "4 min read",
            "author": "NASA Science Portal",
            "link": "https://news.google.com"
        },
        {
            "id": 502,
            "title": "Breakthrough Fusion Reactor Sustains Core for 10 Minutes",
            "category": "Science",
            "snippet": "A magnetic confinement tokamak device achieves a stable, high-temperature plasma core generating net positive energy.",
            "content": "By utilizing custom high-temperature superconducting magnets, the laboratory successfully controlled the highly volatile plasma stream for over 600 seconds. The breakthrough brings clean, unlimited fusion power closer to grid-scale viability.",
            "image_url": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=600&q=80",
            "date": "June 27, 2026",
            "read_time": "5 min read",
            "author": "Nature Scientific",
            "link": "https://news.google.com"
        }
    ],
    "HEALTH": [
        {
            "id": 601,
            "title": "New Vaccine Delivery System Uses Biodegradable Skin Patches",
            "category": "Health",
            "snippet": "A painless microneedle patch enters Phase III trials, offering temperature-stable vaccine distribution.",
            "content": "The microneedle system dissolves harmlessly within the top layer of skin, stimulating a stronger immune response than standard muscular injections. Because the patch does not require refrigeration, it offers a major logistics solution for rural health clinics.",
            "image_url": "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?auto=format&fit=crop&w=600&q=80",
            "date": "July 1, 2026",
            "read_time": "3 min read",
            "author": "World Health Organization",
            "link": "https://news.google.com"
        },
        {
            "id": 602,
            "title": "Study Links Mediterranean Diet to Slower Cognitive Decline",
            "category": "Health",
            "snippet": "A decade-long study tracking 5,000 seniors shows high correlations between plant-based nutrition and brain elasticity.",
            "content": "Neurologists tracking brain scan metrics observed significantly less cortical shrinkage in participants adhering to diet systems rich in olive oil, nuts, and leafy greens. The study emphasizes preventive nutrition as a major defense against dementia.",
            "image_url": "https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=600&q=80",
            "date": "June 29, 2026",
            "read_time": "4 min read",
            "author": "Harvard Health Blog",
            "link": "https://news.google.com"
        }
    ],
    "INDIA": [
        {
            "id": 701,
            "title": "ISRO Successfully Launches Next-Generation Weather Satellite",
            "category": "India",
            "snippet": "The Indian Space Research Organisation puts the INSAT-4G spacecraft into a perfect geosynchronous orbit.",
            "content": "Launching from Sriharikota, ISRO's heavy-lift rocket carried the satellite to assist the Meteorological Department with high-resolution weather forecasting and ocean monitoring. The launch marks another successful milestone for the space agency.",
            "image_url": "https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=600&q=80",
            "date": "July 1, 2026",
            "read_time": "3 min read",
            "author": "ISRO Media",
            "link": "https://news.google.com"
        },
        {
            "id": 702,
            "title": "Indian Economy Projecting Strong 7.2% GDP Growth",
            "category": "India",
            "snippet": "The Reserve Bank of India reports robust domestic consumption and industrial production indexes.",
            "content": "Fueled by digital public infrastructure scaling, rural recovery, and manufacturing export boosts, major credit rating agencies have updated economic indicators to position India as the fastest-growing major economy for this fiscal year.",
            "image_url": "https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&w=600&q=80",
            "date": "June 30, 2026",
            "read_time": "4 min read",
            "author": "The Economic Times",
            "link": "https://news.google.com"
        }
    ]
}


def fetch_google_news(topic: str = None):
    # Search-based mapping to bypass Geo-IP blocks/503 limits on GCP datacenters
    if topic:
        topic_upper = topic.upper().strip()
        if topic_upper == "INDIA":
            url = "https://news.google.com/rss/search?q=India+news&hl=en-IN&gl=IN&ceid=IN:en"
        elif topic_upper == "WORLD":
            url = "https://news.google.com/rss/search?q=world+news&hl=en-US&gl=US&ceid=US:en"
        elif topic_upper == "BUSINESS":
            url = "https://news.google.com/rss/search?q=business+news&hl=en-US&gl=US&ceid=US:en"
        elif topic_upper == "TECHNOLOGY":
            url = "https://news.google.com/rss/search?q=technology+news&hl=en-US&gl=US&ceid=US:en"
        elif topic_upper == "SPORTS":
            url = "https://news.google.com/rss/search?q=sports+news&hl=en-US&gl=US&ceid=US:en"
        elif topic_upper == "SCIENCE":
            url = "https://news.google.com/rss/search?q=science+news&hl=en-US&gl=US&ceid=US:en"
        elif topic_upper == "HEALTH":
            url = "https://news.google.com/rss/search?q=health+news&hl=en-US&gl=US&ceid=US:en"
        else:
            url = "https://news.google.com/rss/search?q=news&hl=en-US&gl=US&ceid=US:en"
    else:
        url = "https://news.google.com/rss/search?q=news&hl=en-US&gl=US&ceid=US:en"

    xml_data = None
    parsed_articles = None

    # Step 1: Try api.cors.lol proxy (Raw XML, Real-time)
    try:
        encoded_url = urllib.parse.quote(url, safe='')
        proxy_url = f"https://api.cors.lol/?url={encoded_url}"
        req = urllib.request.Request(
            proxy_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=4.0) as response:
            xml_data = response.read()
    except Exception as e:
        print(f"Proxy 1 (cors.lol) failed: {e}")

    # Step 2: Try api.allorigins.win JSON proxy (JSON wrapped XML, Real-time)
    if not xml_data:
        try:
            import json
            encoded_url = urllib.parse.quote(url, safe='')
            proxy_url = f"https://api.allorigins.win/get?url={encoded_url}"
            req = urllib.request.Request(
                proxy_url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=5.0) as response:
                json_res = json.loads(response.read().decode('utf-8'))
                contents = json_res.get("contents", "")
                if contents:
                    xml_data = contents.encode('utf-8')
        except Exception as e:
            print(f"Proxy 2 (AllOrigins) failed: {e}")

    # Step 3: Try api.codetabs.com proxy (Raw XML, Real-time backup)
    if not xml_data:
        try:
            encoded_url = urllib.parse.quote(url, safe='')
            proxy_url = f"https://api.codetabs.com/v1/proxy?quest={encoded_url}"
            req = urllib.request.Request(
                proxy_url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=4.0) as response:
                xml_data = response.read()
        except Exception as e:
            print(f"Proxy 3 (Codetabs) failed: {e}")

    # Step 4: Try rss2json.com API (Parsed JSON, Cached backup)
    if not xml_data:
        try:
            import json
            encoded_url = urllib.parse.quote(url, safe='')
            proxy_url = f"https://api.rss2json.com/v1/api.json?rss_url={encoded_url}"
            req = urllib.request.Request(
                proxy_url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=3.0) as response:
                json_res = json.loads(response.read().decode('utf-8'))
                if json_res.get("status") == "ok":
                    parsed_articles = []
                    items = json_res.get("items", [])
                    for item in items[:18]:
                        title = item.get("title", "")
                        link = item.get("link", "https://news.google.com")
                        pub_date = item.get("pubDate", "")
                        
                        parts = title.rsplit(" - ", 1)
                        title_clean = parts[0] if parts else title
                        source = parts[1] if len(parts) > 1 else "Google News"
                        
                        parsed_articles.append({
                            "title": title_clean,
                            "link": link,
                            "pub_date": pub_date,
                            "source": source
                        })
        except Exception as e:
            print(f"Proxy 4 (RSS2JSON) failed: {e}")

    # Define visual assets for categories
    category_images = {
        "WORLD": [
            "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?auto=format&fit=crop&w=600&q=80"
        ],
        "BUSINESS": [
            "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=600&q=80"
        ],
        "TECHNOLOGY": [
            "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=600&q=80"
        ],
        "SPORTS": [
            "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1517649763962-0c623066013b?auto=format&fit=crop&w=600&q=80"
        ],
        "SCIENCE": [
            "https://images.unsplash.com/photo-1507668077129-56e32842fceb?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1453728013993-6d66e9c9123a?auto=format&fit=crop&w=600&q=80"
        ],
        "HEALTH": [
            "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=600&q=80"
        ],
        "INDIA": [
            "https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&w=600&q=80"
        ],
        "DEFAULT": [
            "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1503694978374-8a2fa686963a?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?auto=format&fit=crop&w=600&q=80"
        ]
    }

    topic_key = topic.upper().strip() if topic else "DEFAULT"
    images = category_images.get(topic_key, category_images["DEFAULT"])
    cat_display = topic.capitalize() if topic else "Top Stories"

    # Route 1 & 2: Parse raw XML if fetched successfully
    if xml_data:
        try:
            root = ElementTree.fromstring(xml_data)
            articles = []
            for idx, item in enumerate(root.findall('.//item')[:18]):
                raw_title = item.find('title').text or ""
                link = item.find('link').text or ""
                pub_date = item.find('pubDate').text or ""
                
                parts = raw_title.rsplit(" - ", 1)
                title = parts[0] if parts else raw_title
                source = parts[1] if len(parts) > 1 else "Google News"
                
                date_display = pub_date
                if len(pub_date) > 16:
                    date_display = pub_date[5:16]
                
                img_url = images[idx % len(images)]
                
                articles.append({
                    "id": idx + 1,
                    "title": html.unescape(title),
                    "category": cat_display,
                    "snippet": f"Latest updates reported by {source}. Head to Google News to view the full details and live publisher coverage.",
                    "content": f"This live story was compiled by {source} on {pub_date}. As a Google News aggregator, we pull the freshest feeds in real-time. To read the full article directly from the publisher, please click the link below to visit their official site.",
                    "image_url": img_url,
                    "date": date_display,
                    "read_time": f"{random.randint(2, 5)} min read",
                    "author": source,
                    "link": link
                })
            return articles
        except Exception as e:
            print(f"Error parsing XML data: {e}")

    # Route 3: Process parsed JSON articles from rss2json
    if parsed_articles:
        try:
            articles = []
            for idx, item in enumerate(parsed_articles):
                title = item["title"]
                link = item["link"]
                pub_date = item["pub_date"]
                source = item["source"]
                
                date_display = pub_date
                if len(pub_date) > 16:
                    date_display = pub_date[5:16]
                
                img_url = images[idx % len(images)]
                
                articles.append({
                    "id": idx + 1,
                    "title": html.unescape(title),
                    "category": cat_display,
                    "snippet": f"Latest updates reported by {source}. Head to Google News to view the full details and live publisher coverage.",
                    "content": f"This live story was compiled by {source} on {pub_date}. As a Google News aggregator, we pull the freshest feeds in real-time. To read the full article directly from the publisher, please click the link below to visit their official site.",
                    "image_url": img_url,
                    "date": date_display,
                    "read_time": f"{random.randint(2, 5)} min read",
                    "author": source,
                    "link": link
                })
            return articles
        except Exception as e:
            print(f"Error processing rss2json articles: {e}")

    return []


def get_offline_fallback_news(topic: str = None):
    # Helper to return static mock databases when RSS fetching is unavailable/timed out
    if topic:
        topic_upper = topic.upper().strip()
        if topic_upper in FALLBACK_DATABASE:
            return FALLBACK_DATABASE[topic_upper]
    
    # Return a mix of all categories for 'all' / 'default'
    mix = []
    for cat, items in FALLBACK_DATABASE.items():
        mix.extend(items)
    
    # Sort or shuffle a bit
    random.shuffle(mix)
    return mix


# Page Routes
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request, response: Response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/about", response_class=HTMLResponse)
async def get_about(request: Request, response: Response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return templates.TemplateResponse(request=request, name="about.html")


@app.get("/contact", response_class=HTMLResponse)
async def get_contact(request: Request, response: Response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return templates.TemplateResponse(request=request, name="contact.html")


# API Routes
@app.get("/api/news")
async def get_news(response: Response, category: str = None):
    # Prevent browser caching of the API response
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    
    clean_category = category
    if category and category.lower() in ["all", "top stories"]:
        clean_category = None

    # Fetch live feeds
    articles = fetch_google_news(clean_category)
    
    # Fallback to local high-quality mock data if Google News blocks/timeouts
    if not articles:
        print(f"Loading local fallback database for category: {category}")
        articles = get_offline_fallback_news(clean_category)
        
    return articles


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    msg = request.message.lower().strip()

    if "world" in msg:
        response = (
            "I am currently pulling the latest international headlines from Google News! "
            "You can click on the 'World' category filter on the home page to read current stories from global outlets."
        )
    elif "business" in msg or "finance" in msg or "stocks" in msg:
        response = (
            "Market dynamics are moving fast! Google News covers global business stories in real-time. "
            "Filter by the 'Business' tab on our homepage to see the latest updates."
        )
    elif "tech" in msg or "gemini" in msg or "ai" in msg:
        response = (
            "Google continues to make giant strides in Gemini 1.5 development and enterprise agents. "
            "Check out our 'Technology' filter to see the latest Google News RSS posts on AI and hardware!"
        )
    elif "sports" in msg or "game" in msg or "scores" in msg:
        response = (
            "Sports stories are live! I pull sports coverage directly from Google's feeds. "
            "Click on the 'Sports' filter to read up-to-the-minute reports on soccer, basketball, tennis, and more."
        )
    elif "science" in msg or "space" in msg:
        response = (
            "Fascinating updates are emerging in research and space exploration. "
            "You can select the 'Science' filter on the homepage to browse scientific publications compiled by Google News."
        )
    elif "health" in msg or "medicine" in msg:
        response = (
            "Stay informed on health policy, research, and fitness. "
            "The 'Health' filter compiles the latest wellness updates from reputable publishers."
        )
    elif "india" in msg or "indian" in msg:
        response = (
            "Namaste! I aggregate the latest Indian news directly from regional Google News feeds. "
            "Select the 'India' tab on our homepage to view the top headlines from India!"
        )
    elif "hello" in msg or "hi" in msg or "hey" in msg:
        response = (
            "Hello! I am your Google News AI Assistant. I fetch live RSS feeds from Google News. "
            "Ask me about any section, such as World, Business, Tech, Sports, Science, Health, or India!"
        )
    else:
        response = (
            "I'm your live Google News aggregator assistant! I pull directly from Google News RSS feeds. "
            "You can browse categories like World, Business, Tech, Sports, Science, Health, or India on the homepage, "
            "or ask me for details about them!"
        )

    return {"response": response}
