import datetime
import random
import uuid
import pandas as pd

# --- CONFIGURATION & PARAMETERS ---
NUM_USERS = 2500
TARGET_ROWS = 52000  # Generates slightly over 50k to allow for filtering
START_DATE = datetime.datetime(2026, 6, 1, 0, 0, 0)

# Define standard event funnel
FUNNEL_STEPS = ["app_open", "view_task_list", "start_task", "complete_task", "claim_points"]

# Typo mappings for specific events (Simulating poor front-end tracking implementation)
TYPO_CHANCE = 0.04
TYPOS = {
    "app_open": "ap_open",
    "view_task_list": "view_tasklist",
    "claim_points": "clck_reward"
}

print("Initializing user database...")
# Pre-generate users with fixed OS allocation (60% Android, 40% iOS)
users = []
for _ in range(NUM_USERS):
    user_id = f"USR_{random.randint(100000, 999999)}"
    os_type = "Android" if random.random() < 0.60 else "iOS"
    users.append({"user_id": user_id, "os": os_type})

all_events = []
current_time = START_DATE

print("Generating 50,000+ messy event logs...")
while len(all_events) < TARGET_ROWS:
    # Pick a random user
    user = random.choice(users)
    user_id = user["user_id"]
    device_os = user["os"]
    
    # Create a unique session ID
    session_id = str(uuid.uuid4())[:18]
    
    # Determine how far this user progresses through the funnel in this session
    # Base drop-off configuration
    max_step_index = len(FUNNEL_STEPS)
    rand_roll = random.random()
    
    if rand_roll < 0.15:
        max_step_index = 1  # Drops off after open
    elif rand_roll < 0.35:
        max_step_index = 2  # Drops off after viewing list
    elif rand_roll < 0.55:
        max_step_index = 3  # Drops off after starting task
    elif rand_roll < 0.70:
        max_step_index = 4  # Drops off after completing task (The critical business leak)

    # Increment time slightly between user sessions to keep timelines realistic
    current_time += datetime.timedelta(seconds=random.randint(5, 45))
    session_time = current_time

    # Generate events for this specific session
    for i in range(max_step_index):
        event_name = FUNNEL_STEPS[i]
        
        # Advance time slightly for each step within the session
        session_time += datetime.timedelta(seconds=random.randint(2, 120))
        
        # --- FLAW 1: SYSTEMATIC ANDROID SERVER ERROR ---
        # If an Android user reaches the "claim_points" step, inject a heavy 35% crash/error loop
        if device_os == "Android" and event_name == "claim_points" and random.random() < 0.35:
            all_events.append({
                "timestamp": session_time.strftime("%Y-%m-%d %H:%M:%S"),
                "user_id": user_id,
                "session_id": session_id,
                "event_name": "server_error_500",
                "device_os": device_os
            })
            # The error breaks their session; they fail to claim points
            break
            
        # --- FLAW 2: TEXT TYPOS IN EVENT NAMES ---
        if random.random() < TYPO_CHANCE and event_name in TYPOS:
            event_name = TYPOS[event_name]
            
        # --- FLAW 3: INCONSISTENT TIMESTAMP FORMATS ---
        # 8% of records write as raw Unix Epoch timestamps instead of Clean Strings
        if random.random() < 0.08:
            ts_value = str(int(session_time.timestamp()))
        else:
            ts_value = session_time.strftime("%Y-%m-%d %H:%M:%S")
            
        # --- FLAW 4: NULL SESSION IDs (App Crashes) ---
        # 3% of events completely lose their session identifier mid-stream
        final_session_id = None if random.random() < 0.03 else session_id
        
        # Append core event
        all_events.append({
            "timestamp": ts_value,
            "user_id": user_id,
            "session_id": final_session_id,
            "event_name": event_name,
            "device_os": device_os
        })
        
        # --- FLAW 5: DOUBLE-TAPPING DUPLICATES ---
        # Users double-clicking buttons creates instant duplicate records (millisecond differences)
        if event_name in ["start_task", "clck_reward", "claim_points"] and random.random() < 0.05:
            all_events.append({
                "timestamp": ts_value, 
                "user_id": user_id,
                "session_id": final_session_id,
                "event_name": event_name,
                "device_os": device_os
            })

# Convert to DataFrame and shuffle to break sequential generation pattern
df = pd.DataFrame(all_events)
df = df.sample(frac=1).reset_index(drop=True)

# Export to CSV
csv_filename = "raw_app_events.csv"
df.to_csv(csv_filename, index=False)

print(f"\nSuccess! Messy dataset created.")
print(f"Total Rows generated: {len(df)}")
print(f"File saved as: '{csv_filename}'")