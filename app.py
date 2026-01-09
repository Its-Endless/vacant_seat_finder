import os
import json
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
from scraper import start_scraping
from dotenv import load_dotenv 
load_dotenv()

app = Flask(__name__)

# --- CONFIGURATION ---
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ ERROR: API Key not found! Make sure .env file exists.")

client = genai.Client(api_key=API_KEY)

# --- 1. PYTHON LOGIC (Table Data) ---
def process_seat_data(raw_data_list):
    optimized_seats = []
    for coach_data in raw_data_list:
        coach_name = coach_data.get('scraped_coach_name', coach_data.get('coachName', 'Unknown'))
        seats = coach_data.get('bdd', [])
        for seat in seats:
            seat_no = seat['berthNo']
            seat_type = seat['berthCode'] 
            legs = seat.get('bsd', [])
            current_journey = None
            for leg in legs:
                is_vacant = not leg['occupancy'] 
                if is_vacant:
                    if current_journey is None:
                        current_journey = {"Coach": coach_name, "Seat": seat_no, "Type": seat_type, "From": leg['from'], "To": leg['to']}
                    else:
                        if leg['from'] == current_journey['To']:
                            current_journey['To'] = leg['to']
                        else:
                            optimized_seats.append(current_journey)
                            current_journey = {"Coach": coach_name, "Seat": seat_no, "Type": seat_type, "From": leg['from'], "To": leg['to']}
                else:
                    if current_journey:
                        optimized_seats.append(current_journey)
                        current_journey = None
            if current_journey: optimized_seats.append(current_journey)
    return optimized_seats

# --- 2. AI LOGIC (Grouping + Micro-Hops) ---
def simplify_data_for_ai(raw_data_list):
    vacant_fragments = []
    for coach in raw_data_list:
        coach_name = coach.get('scraped_coach_name', 'Unknown')
        for seat in coach.get('bdd', []):
            for leg in seat.get('bsd', []):
                if not leg['occupancy']:
                    vacant_fragments.append(f"{coach_name}-{seat['berthNo']} ({leg['from']}->{leg['to']})")
    return vacant_fragments

def ask_gemini_narrative(vacant_list, src, dest):
    print(">>> 🧠 Asking Gemini (Grouped Mode)...")
    
    # Increase data limit to ensure we capture all small hops
    data_summary = str(vacant_list[:400]) 

    prompt = f"""
    Role: Master Logistics Planner.
    User Journey: {src} to {dest}.
    Available Seats: {data_summary}

    YOUR GOAL:
    Build the most complete "Stitched Itinerary" possible. 
    The user wants to reach the destination even if they have to change seats 10 times.

    CRITICAL RULES:
    1. **GROUP SEATS:** If multiple seats cover the EXACT SAME leg (e.g. B1-12, B3-9, B3-14 all go DDU->CNB), list them on ONE LINE. 
       *Example:* "Seats B1-12, B3-9, B3-14 (DDU -> CNB)"
       *Do NOT make separate options for each seat.*

    2. **MICRO-HOPS MATTER:** Do NOT ignore short journeys. If there is a seat for just 1 station (e.g. BBS->CTC), USE IT. Do not leave a gap if a short seat exists.

    3. **FILL THE GAPS:** Try to cover every single mile. If there is absolutely no seat for a section, only then say "❌ NO SEAT".

    4. **STATION NAMES:** Use Full Station Names + Codes (e.g. "Bhubaneswar (BBS)").

    STRICT OUTPUT FORMAT:
    
    ### 🛤️ RECOMMENDED ITINERARY
    * **Leg 1:** {src} -> [Next Station]
      - **Available:** Coach X-Y, Coach Z-A (List all seats for this leg here)
    
    * **Leg 2:** [Prev Station] -> [Next Station]
      - **Available:** Coach B2-12, B5-40
    
    ... (Continue until {dest}) ...

    (If a gap exists between legs):
    * **⚠️ GAP:** [Station A] -> [Station B]
      - ❌ No vacant seats found for this section.

    ### 📝 SUMMARY
    * **Total Switches:** (Count how many times user must move)
    * **Best Path:** (Quick summary of the best coaches to stick to)
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
        
        # Debug Print
        print("\n" + "="*30)
        print("🤖 AI RESPONSE:")
        print(response.text)
        print("="*30 + "\n")

        return response.text
    except Exception as e:
        print(f"❌ Gemini Error: {e}") 
        return "AI Analysis Failed. Check terminal."

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/find_seats', methods=['POST'])
def find_seats():
    try:
        data = request.json
        train = data.get('train_no')
        station = data.get('station')
        dest = data.get('dest_station')
        class_pref = data.get('class_pref', 'ALL')

        print(f"\n>>> API CALL: Train {train} | {station} -> {dest}")

        # 1. Scrape
        raw_data = start_scraping(train, class_filter=class_pref)
        if not raw_data: return jsonify({"status": "error", "message": "No data found."}), 400

        # 2. Table Data
        table_data = process_seat_data(raw_data)

        # 3. AI Data
        ai_input = simplify_data_for_ai(raw_data)
        if ai_input and station and dest:
            ai_text = ask_gemini_narrative(ai_input, station, dest)
        else:
            ai_text = "Enter Source & Destination for AI Advice."

        return jsonify({
            "status": "success",
            "raw_data": table_data,
            "ai_advice": ai_text
        })

    except Exception as e:
        print(f"SERVER ERROR: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':

    app.run(debug=True, port=5000)
