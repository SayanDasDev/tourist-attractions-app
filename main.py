from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import httpx
import os
from typing import List, Dict, Any
from pydantic import BaseModel
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Tourist Attractions API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Google Places API configuration
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
PLACES_NEARBY_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
PLACES_PHOTO_URL = "https://maps.googleapis.com/maps/api/place/photo"

class Attraction(BaseModel):
    name: str
    lat: float
    lng: float
    rating: float
    user_ratings_total: int
    photo_url: str = None
    place_id: str

@app.get("/")
async def serve_frontend():
    """Serve the frontend HTML page"""
    try:
        with open("static/index.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return HTMLResponse("<h1>Frontend not found. Please create static/index.html</h1>")

@app.get("/attractions", response_model=List[Attraction])
async def get_attractions(
    north: float,
    south: float,
    east: float,
    west: float,
    radius: int = 5000  # Search radius in meters
):
    """
    Get tourist attractions within the specified bounds with more than 500 reviews
    """
    if not GOOGLE_PLACES_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Google Places API key not configured. Set GOOGLE_PLACES_API_KEY environment variable."
        )

    # Calculate center point for the search
    center_lat = (north + south) / 2
    center_lng = (east + west) / 2

    attractions = []

    # Search for different types of tourist attractions
    # You can easily modify this list to focus on specific types
    place_types = [
        # Core tourist attractions
        "tourist_attraction",
        "museum",
        "amusement_park",
        "zoo",
        "art_gallery",
        "aquarium",

        # Religious & Cultural sites
        "church",
        "hindu_temple",
        "mosque",
        "synagogue",
        "place_of_worship",

        # Entertainment & Recreation
        "casino",
        "night_club",
        "bowling_alley",
        "movie_theater",

        # Nature & Parks
        "park",
        "campground",
        "rv_park",

        # Shopping & Markets
        "shopping_mall",
        "department_store",

        # Sports & Activities
        "stadium",
        "gym",
        "spa",

        # Historical & Educational
        "library",
        "university",
        "school",

        # Food & Dining (popular destinations)
        "restaurant",
        "cafe",
        "bar",

        # Accommodation (landmark hotels)
        "lodging",

        # Transportation hubs (major landmarks)
        "airport",
        "train_station",
        "subway_station",

        # Health & Wellness
        "hospital",

        # Government & Civic
        "city_hall",
        "courthouse",
        "embassy",

        # Miscellaneous
        "cemetery",
        "funeral_home",
        "storage"
    ]

    async with httpx.AsyncClient() as client:
        # Search for each place type
        for place_type in place_types:
            params = {
                "location": f"{center_lat},{center_lng}",
                "radius": radius,
                "type": place_type,
                "key": GOOGLE_PLACES_API_KEY
            }

            try:
                response = await client.get(PLACES_NEARBY_URL, params=params)
                response.raise_for_status()
                data = response.json()

                if data.get("status") == "OK":
                    for place in data.get("results", []):
                        # Filter places with more than 500 reviews
                        if place.get("user_ratings_total", 0) > 500:
                            location = place.get("geometry", {}).get("location", {})
                            place_lat = location.get("lat")
                            place_lng = location.get("lng")

                            # Check if the place is within bounds
                            if (place_lat and place_lng and
                                south <= place_lat <= north and
                                west <= place_lng <= east):

                                # Get photo URL if available
                                photo_url = None
                                photos = place.get("photos", [])
                                if photos and len(photos) > 0:
                                    photo_reference = photos[0].get("photo_reference")
                                    if photo_reference:
                                        photo_url = f"{PLACES_PHOTO_URL}?maxwidth=200&photoreference={photo_reference}&key={GOOGLE_PLACES_API_KEY}"

                                attraction = Attraction(
                                    name=place.get("name", "Unknown"),
                                    lat=place_lat,
                                    lng=place_lng,
                                    rating=place.get("rating", 0),
                                    user_ratings_total=place.get("user_ratings_total", 0),
                                    photo_url=photo_url,
                                    place_id=place.get("place_id", "")
                                )

                                # Avoid duplicates
                                if not any(a.place_id == attraction.place_id for a in attractions):
                                    attractions.append(attraction)

            except httpx.HTTPError as e:
                print(f"Error fetching data for {place_type}: {e}")
                continue

            # Add delay to avoid rate limiting
            await asyncio.sleep(0.1)

    return attractions

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "api_key_configured": bool(GOOGLE_PLACES_API_KEY)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)