# 🚄 Broken Journey Optimizer (Smart Seat Finder)

### 🚀 Don't let "Waitlisted" stop your journey.
**A smart tool that finds "hidden" empty seats in trains by stitching together broken journeys.**

---

## 🧐 What is this?
In India, direct train tickets often get waitlisted. However, seats are frequently empty for **parts** of the journey (e.g., Station A to Station B is empty, and Station B to Station C is empty).

This project solves that problem. It scrapes real-time train charts and uses **Google Gemini AI** to "stitch" these gaps together. It tells you:
*"Book Seat 72 from Delhi to Agra, then switch to Seat 15 from Agra to Bhopal."*

## ✨ Key Features
* **🧩 Broken Journey Logic:** Finds vacant seats between intermediate stations.
* **🤖 AI-Powered Itineraries:** Uses **Google Gemini 2.5 Flash** to analyze complex seat data and recommend the best "seat-switching" plan.
* **📊 Real-Time Scraping:** Automates IRCTC chart checking using Selenium to get live data.
* **⚡ Smart Filtering:** Instantly filters by AC classes (1A, 2A, 3A) or Sleeper (SL).
* **🌑 Dark Mode UI:** A clean, responsive interface for easy viewing.

---

## 🛠️ Tech Stack
* **Backend:** Python (Flask)
* **AI Engine:** Google Gemini API (GenAI SDK)
* **Automation:** Selenium & Selenium Wire (Web Scraping)
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
* **Browser Driver:** Chrome WebDriver

---

## ⚙️ Installation & Setup

Follow these simple steps to run the project on your machine.

### 1. Clone the Repository
```bash
git clone 
cd broken-journey-optimizer

```

### 2. Set Up Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

```

### 3. Install Dependencies

```bash
pip install -r requirements.txt

```

### 4. Configure API Key

Create a `.env` file in the main folder and add your Google Gemini API key:

```ini
GEMINI_API_KEY=your_actual_api_key_here

```

### 5. Run the App

```bash
python app.py

```

* The app will start running at `http://127.0.0.1:5000/`
* Open this URL in your browser.

---

## 📂 Project Structure

* `app.py`: The main Flask server. It handles the API requests and talks to Gemini AI.
* `scraper.py`: The bot script. It opens a hidden Chrome browser, goes to the IRCTC website, and scrapes the chart data.
* `requirements.txt`: List of all Python libraries needed.
* `templates/index.html`: The main website page (Frontend).
* `static/`: Contains the CSS (styling) and JavaScript (logic) files.

---

## 📸 How It Works (Demo)

1. **Enter Details:** Put in the Train Number (e.g., 12815), Date, and Stations.
2. **The Bot Works:** The backend opens a browser in the background and scans the train chart.
3. **AI Analysis:** The raw seat data is sent to **Google Gemini**.
4. **Result:** You get a smart itinerary telling you exactly which seats to book to complete your full journey.

---

## ⚠️ Disclaimer

This project is for **educational purposes only**. It demonstrates the power of AI in solving logistics problems. Please use it responsibly and adhere to IRCTC's terms of service.

---

## 🤝 Contributing

Found a bug? Want to add a map feature? Feel free to **fork** this repo and submit a **pull request**!

**Built with ❤️ for the Google AI Hackathon.**

```

```
