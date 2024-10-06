import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
from datetime import datetime
import os
import threading

# ================== Data Handling ================== #

# Path to the data file
DATA_FILE = 'data.json'

# Lock for thread-safe file operations
lock = threading.Lock()

# Function to log save actions
def log_save_action(action_details):
    """Log the action of saving data with details and timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {action_details}\n"
    
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(log_message)

# Function to load data from the JSON file
def load_data():
    with lock:
        if not os.path.exists(DATA_FILE):
            # Initialize with default structure if file doesn't exist
            default_data = {
                "strategic_objectives": {
                    "Biga": [
                        "Create 3 trend videos",
                        "Post two pictures and story posts",
                        "Conduct twice polls (e.g., favorite drink, duel between plates)"
                    ],
                    "Tricolor": [
                        "Create 3 trend videos focusing on food",
                        "Post two pictures and story posts",
                        "Conduct twice polls (e.g., favorite arepa)"
                    ]
                },
                "content_ideas": {
                    "Biga": [
                        {"idea": "On and off coffee video", "category": "Reels"},
                        {"idea": "Do you work here", "category": "Trendy Posts"},
                        {"idea": "Enjoy you too video", "category": "Reels"},
                        {"idea": "ASMR video", "category": "Carousels"},
                        {"idea": "Ghost pour over", "category": "Reels"},
                        {"idea": "Zombie mask video", "category": "Reels"}
                    ],
                    "Tricolor": [
                        {"idea": "Colombian beverage try for people in the street", "category": "Reels"},
                        {"idea": "Empanada try three types", "category": "Carousels"},
                        {"idea": "Which type are you poll", "category": "Polls"},
                        {"idea": "Mystery empanada", "category": "Trendy Posts"},
                        {"idea": "Arepa reaction", "category": "Reels"},
                        {"idea": "Word of the week: Colombian slang", "category": "Trendy Posts"},
                        {"idea": "Trick or Treat", "category": "Reels"}
                    ]
                },
                "weekly_goals": {
                    "Biga": [],
                    "Tricolor": []
                },
                "captions": {
                    "Biga": [],
                    "Tricolor": []
                },
                "notes": {
                    "Biga": [],
                    "Tricolor": []
                },
                "analytics": {
                    "Biga": {"views": 0, "engagement": 0, "likes": 0},
                    "Tricolor": {"views": 0, "engagement": 0, "likes": 0}
                },
                "pricing": {
                    "Biga": {"amount": 0, "due_date": ""},
                    "Tricolor": {"amount": 0, "due_date": ""}
                },
                "goals": {
                    "Biga": {"Views": 10000, "Engagements": 500, "Likes": 1000},
                    "Tricolor": {"Views": 8000, "Engagements": 400, "Likes": 800}
                }
            }
            with open(DATA_FILE, 'w') as f:
                json.dump(default_data, f, indent=4)
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        return data

# Function to save data to the JSON file and update session state
def save_data(data):
    with lock:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    # Update session state to reflect changes
    st.session_state['data'] = data

# Initialize session state
if 'data' not in st.session_state:
    st.session_state['data'] = load_data()

# ================== Helper Functions ================== #

def delete_item(section, client, idx):
    del st.session_state['data'][section][client][idx]
    save_data(st.session_state['data'])
    st.success("Item deleted!")

def delete_all_items(section, client):
    st.session_state['data'][section][client].clear()
    save_data(st.session_state['data'])
    st.success("All items deleted!")

def edit_item(section, client, idx, new_value):
    st.session_state['data'][section][client][idx]['idea'] = new_value
    save_data(st.session_state['data'])
    st.success("Item edited!")

# ================== App Layout ================== #

st.title("📈 SMMA Planning and Tracking App")

# Sidebar for Navigation
st.sidebar.title("Navigation")
options = [
    "Strategic Objectives",
    "Content Ideas",
    "Weekly Goals",
    "Captions",
    "Notes",
    "Analytics",
    "Pricing & Billing"
]
selection = st.sidebar.radio("Go to", options)

# ================== Section Functions ================== #

def strategic_objectives():
    st.header("🎯 Strategic Objectives")
    client = st.selectbox("Select Client", ["Biga", "Tricolor"], key="strat_client")
    objective = st.text_input(f"Add Strategic Objective for {client}", key="strat_input")
    if st.button("Add Objective", key="strat_add_btn"):
        if objective:
            st.session_state['data']['strategic_objectives'][client].append(objective)
            save_data(st.session_state['data'])
            st.success("Objective added!")
        else:
            st.warning("Please enter an objective.")
    
    search_term = st.text_input("Search Objectives", key="search_objectives")
    st.subheader(f"{client} Objectives")
    filtered_objectives = [obj for obj in st.session_state['data']['strategic_objectives'][client] if search_term.lower() in obj.lower()]
    for idx, obj in enumerate(filtered_objectives, 1):
        col1, col2 = st.columns([4, 1])
        col1.write(f"{idx}. {obj}")
        if col2.button(f"Delete {idx}", key=f"delete_strat_{idx}"):
            delete_item('strategic_objectives', client, idx-1)

    if st.button(f"Delete All Objectives for {client}", key="delete_all_strat"):
        delete_all_items('strategic_objectives', client)

def content_ideas():
    st.header("📝 Content Ideas")
    client = st.selectbox("Select Client", ["Biga", "Tricolor"], key="content_client")
    
    search_term = st.text_input("Search Content Ideas", key="search_content")
    idea = st.text_input(f"Add Content Idea for {client}", key="content_input")
    category = st.selectbox("Select Category", ["Trendy Posts", "Carousels", "Reels", "Polls"], key="content_category")
    if st.button("Add Content Idea", key="content_add_btn"):
        if idea:
            st.session_state['data']['content_ideas'][client].append({'idea': idea, 'category': category})
            save_data(st.session_state['data'])
            st.success("Content idea added!")
        else:
            st.warning("Please enter a content idea.")
    
    st.subheader(f"{client} Content Ideas")
    filtered_ideas = [item for item in st.session_state['data']['content_ideas'][client] if search_term.lower() in item['idea'].lower()]
    for idx, item in enumerate(filtered_ideas, 1):
        col1, col2 = st.columns([4, 1])
        new_idea = col1.text_input(f"Edit Idea {idx}", value=item['idea'], key=f"edit_idea_{idx}")
        if col2.button(f"Save Edit {idx}", key=f"save_edit_{idx}"):
            edit_item('content_ideas', client, idx-1, new_idea)

    if st.button(f"Delete All Content Ideas for {client}", key="delete_all_content"):
        delete_all_items('content_ideas', client)

def weekly_goals():
    st.header("🎯 Weekly Goals (SMART)")
    client = st.selectbox("Select Client", ["Biga", "Tricolor"], key="goal_client")
    
    search_term = st.text_input("Search Weekly Goals", key="search_goals")
    with st.form(key='goal_form'):
        goal = st.text_input("Enter SMART Goal", key="goal_input")
        submitted = st.form_submit_button("Add Goal")
        if submitted:
            if goal:
                st.session_state['data']['weekly_goals'][client].append(goal)
                save_data(st.session_state['data'])
                st.success("Goal added!")
            else:
                st.warning("Please enter a goal.")
    
    st.subheader(f"{client} Weekly Goals")
    filtered_goals = [g for g in st.session_state['data']['weekly_goals'][client] if search_term.lower() in g.lower()]
    for idx, g in enumerate(filtered_goals, 1):
        col1, col2 = st.columns([4, 1])
        col1.write(f"{idx}. {g}")
        if col2.button(f"Delete {idx}", key=f"delete_goal_{idx}"):
            delete_item('weekly_goals', client, idx-1)

    if st.button(f"Delete All Weekly Goals for {client}", key="delete_all_goals"):
        delete_all_items('weekly_goals', client)

def captions():
    st.header("✍️ Captions")
    client = st.selectbox("Select Client", ["Biga", "Tricolor"], key="caption_client")
    
    search_term = st.text_input("Search Captions", key="search_captions")
    caption = st.text_input(f"Add Caption for {client}", key="caption_input")
    if st.button("Add Caption", key="caption_add_btn"):
        if caption:
            st.session_state['data']['captions'][client].append(caption)
            save_data(st.session_state['data'])
            st.success("Caption added!")
        else:
            st.warning("Please enter a caption.")
    
    st.subheader(f"{client} Captions")
    filtered_captions = [cap for cap in st.session_state['data']['captions'][client] if search_term.lower() in cap.lower()]
    for idx, cap in enumerate(filtered_captions, 1):
        col1, col2 = st.columns([4, 1])
        col1.write(f"{idx}. {cap}")
        if col2.button(f"Delete {idx}", key=f"delete_caption_{idx}"):
            delete_item('captions', client, idx-1)

    if st.button(f"Delete All Captions for {client}", key="delete_all_captions"):
        delete_all_items('captions', client)

def notes():
    st.header("🗒️ Notes for Planning")
    client = st.selectbox("Select Client", ["Biga", "Tricolor"], key="notes_client")
    
    search_term = st.text_input("Search Notes", key="search_notes")
    note = st.text_area(f"Add Note for {client}", key="notes_input")
    if st.button("Add Note", key="notes_add_btn"):
        if note:
            st.session_state['data']['notes'][client].append(note)
            save_data(st.session_state['data'])
            st.success("Note added!")
        else:
            st.warning("Please enter a note.")
    
    st.subheader(f"{client} Notes")
    filtered_notes = [note for note in st.session_state['data']['notes'][client] if search_term.lower() in note.lower()]
    for idx, note in enumerate(filtered_notes, 1):
        col1, col2 = st.columns([4, 1])
        col1.write(f"{idx}. {note}")
        if col2.button(f"Delete {idx}", key=f"delete_note_{idx}"):
            delete_item('notes', client, idx-1)

    if st.button(f"Delete All Notes for {client}", key="delete_all_notes"):
        delete_all_items('notes', client)

# ================== Section Navigation ================== #

# Navigation between different sections
if selection == "Strategic Objectives":
    strategic_objectives()
elif selection == "Content Ideas":
    content_ideas()
elif selection == "Weekly Goals":
    weekly_goals()
elif selection == "Captions":
    captions()
elif selection == "Notes":
    notes()

# ================== Footer ================== #

st.markdown("---")
st.markdown("© 2024 Your SMMA. All rights reserved.")
