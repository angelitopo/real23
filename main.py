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

# Function to save data to the JSON file
def save_data(data):
    with lock:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state['data'] = load_data()

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

# ================== Helper Functions ================== #

def delete_item(section, client, idx):
    del st.session_state['data'][section][client][idx]
    save_data(st.session_state['data'])
    st.success("Item deleted!")

def edit_item(section, client, idx, new_value):
    st.session_state['data'][section][client][idx]['idea'] = new_value
    save_data(st.session_state['data'])
    st.success("Item edited!")

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

def analytics():
    st.header("📊 Analytics Tracking")
    client = st.selectbox("Select Client", ["Biga", "Tricolor"], key="analytics_client")
    st.subheader(f"{client} Current Analytics")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Views", st.session_state['data']['analytics'][client]['views'])
        views = st.number_input("Add Views", min_value=0, step=1, key="views_input")
        if st.button("Update Views", key="views_btn"):
            st.session_state['data']['analytics'][client]['views'] += views
            save_data(st.session_state['data'])
            st.success("Views updated!")
    with col2:
        st.metric("Engagements", st.session_state['data']['analytics'][client]['engagement'])
        engagement = st.number_input("Add Engagements", min_value=0, step=1, key="engagement_input")
        if st.button("Update Engagements", key="engagement_btn"):
            st.session_state['data']['analytics'][client]['engagement'] += engagement
            save_data(st.session_state['data'])
            st.success("Engagements updated!")
    with col3:
        st.metric("Likes", st.session_state['data']['analytics'][client]['likes'])
        likes = st.number_input("Add Likes", min_value=0, step=1, key="likes_input")
        if st.button("Update Likes", key="likes_btn"):
            st.session_state['data']['analytics'][client]['likes'] += likes
            save_data(st.session_state['data'])
            st.success("Likes updated!")

    # Visualizing Progress towards Goals
    st.subheader("Progress Towards Goals")

    # Define the goals
    goals = st.session_state['data']['goals'][client]

    # Current metrics
    current_metrics = {
        "Views": st.session_state['data']['analytics'][client]['views'],
        "Engagements": st.session_state['data']['analytics'][client]['engagement'],
        "Likes": st.session_state['data']['analytics'][client]['likes']
    }

    # Data for plotting
    metrics = list(current_metrics.keys())
    values = list(current_metrics.values())
    goal_values = [goals[metric] for metric in metrics]

    x = range(len(metrics))  # [0, 1, 2]

    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.35

    # Bars for current metrics
    bars1 = ax.bar([i - bar_width/2 for i in x], values, bar_width, label='Current', color='skyblue')

    # Bars for goal metrics
    bars2 = ax.bar([i + bar_width/2 for i in x], goal_values, bar_width, label='Goal', color='lightgreen')

    # Add labels, title, and custom x-axis tick labels
    ax.set_xlabel('Metrics')
    ax.set_ylabel('Count')
    ax.set_title(f'Current Metrics vs Goals for {client}')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend()

    # Adding value labels on top of bars
    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.annotate('{}'.format(height),
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    add_labels(bars1)
    add_labels(bars2)

    plt.tight_layout()
    st.pyplot(fig)

def pricing_billing():
    st.header("💰 Pricing & Billing")
    client = st.selectbox("Select Client", ["Biga", "Tricolor"], key="pricing_client")
    amount = st.number_input(f"Set Monthly Fee for {client} ($)", min_value=0, step=50, key="pricing_input")
    if st.button("Set Pricing", key="pricing_btn"):
        st.session_state['data']['pricing'][client]['amount'] = amount
        # Set due date as the 30th of the next month
        today = datetime.today()
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=30)
        else:
            next_month = today.replace(month=today.month + 1, day=30)
        due_date = next_month.strftime("%d/%m/%Y")
        st.session_state['data']['pricing'][client]['due_date'] = due_date
        save_data(st.session_state['data'])
        st.success(f"Pricing set! Billing Date: {due_date}")
    st.subheader(f"{client} Pricing")
    st.write(f"**Monthly Fee:** ${st.session_state['data']['pricing'][client]['amount']}")
    st.write(f"**Next Billing Date:** {st.session_state['data']['pricing'][client]['due_date']}")

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
elif selection == "Analytics":
    analytics()
elif selection == "Pricing & Billing":
    pricing_billing()

# ================== Footer ================== #

st.markdown("---")
st.markdown("© 2024 Your SMMA. All rights reserved.")
