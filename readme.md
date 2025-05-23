## Setup Instructions

### 1. Backend Setup

1. **Install Dependencies**:
    
    ```bash
    pip install -r requirements.txt
    ```
    
2. **Set Environment Variable**:
  ```bash
	cp .env.example .env
  ```
  set `GOOGLE_PLACES_API_KEY=your_google_places_api_key_here` to your API Key in the `.env` file




# Edit .env and add your actual API key
GOOGLE_PLACES_API_KEY=your_actual_api_key_here

3. **Run the Backend**:
    
    ```bash
    python main.py
    ```
    

### 2. Frontend Setup

1. **Update API Key**: In `static/index.html`, replace `YOUR_GOOGLE_MAPS_API_KEY` with your actual Google Maps API key in two places:
    
    - Line with `const GOOGLE_MAPS_API_KEY = 'YOUR_GOOGLE_MAPS_API_KEY';`
    - Script tag: `src="https://maps.googleapis.com/maps/api/js?key=YOUR_GOOGLE_MAPS_API_KEY&callback=initMap&libraries=geometry"`
2. **Access the Application**: Open your browser and go to:
    
    ```
    http://localhost:8000
    ```

### 3. How to Get Google API Keys

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
    - **Maps JavaScript API**
    - **Places API**
4. Create credentials (API Key):
    - Go to "Credentials" → "Create Credentials" → "API Key"
    - Copy the API key for later use