# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
from datetime import datetime, timedelta
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
                    "Biga": {
                        "pending": [
                            "Create 3 trend videos",
                            "Post two pictures and story posts",
                            "Conduct twice polls (e.g., favorite drink, duel between plates)"
                        ],
                        "completed": []
                    },
                    "Tricolor": {
                        "pending": [
                            "Create 3 trend videos focusing on food",
                            "Post two pictures and story posts",
                            "Conduct twice polls (e.g., favorite arepa)"
                        ],
                        "completed": []
                    }
                },
                "content_ideas": {
                    "Biga": {
                        "pending": [
                            {"idea": "On and off coffee video", "category": "Reels"},
                            {"idea": "Do you work here", "category": "Trendy Posts"},
                            {"idea": "Enjoy you too video", "category": "Reels"},
                            {"idea": "ASMR video", "category": "Carousels"},
                            {"idea": "Ghost pour over", "category": "Reels"},
                            {"idea": "Zombie mask video", "category": "Reels"}
                        ],
                        "completed": []
                    },
                    "Tricolor": {
                        "pending": [
                            {"idea": "Colombian beverage try for people in the street", "category": "Reels"},
                            {"idea": "Empanada try three types", "category": "Carousels"},
                            {"idea": "Which type are you poll", "category": "Polls"},
                            {"idea": "Mystery empanada", "category": "Trendy Posts"},
                            {"idea": "Arepa reaction", "category": "Reels"},
                            {"idea": "Word of the week: Colombian slang", "category": "Trendy Posts"},
                            {"idea": "Trick or Treat", "category": "Reels"}
                        ],
                        "completed": []
                    }
                },
                "weekly_goals": {
                    "Biga": {"pending": [], "completed": []},
                    "Tricolor": {"pending": [], "completed": []}
                },
                "captions": {
                    "Biga": {"pending": [], "completed": []},
                    "Tricolor": {"pending": [], "completed": []}
                },
                "notes": {
                    "Biga": {"pending": [], "completed": []},
                    "Tricolor": {"pending": [], "completed": []}
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

        # Ensure all sections have 'completed' lists
        sections_with_completed = ["strategic_objectives", "content_ideas", "weekly_goals", "captions", "notes"]
        for section in sections_with_completed:
            for client in ["Biga", "Tricolor"]:
                if "pending" not in data[section][client]:
                    data[section][client]["pending"] = []
                if "completed" not in data[section][client]:
                    data[section][client]["completed"] = []
        return data

# Function to save data to the JSON file
def save_data(data):
    with lock:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state['data'] = load_data()

# ================== Helper Functions ================== #

def delete_item(section, client, item, status):
    """
    Deletes an item from the specified section, client, and status.
    """
    with lock:
        st.session_state['data'][section][client][status].remove(item)
        save_data(st.session_state['data'])
        st.success(f"Deleted item from {status} list.")
        st.experimental_rerun()

def edit_item(section, client, old_item, status, new_item):
    """
    Edits an existing item in the specified section, client, and status.
    """
    with lock:
        try:
            index = st.session_state['data'][section][client][status].index(old_item)
            st.session_state['data'][section][client][status][index] = new_item
            save_data(st.session_state['data'])
            st.success(f"Edited item in {status} list.")
            st.experimental_rerun()
        except ValueError:
            st.warning("Item not found.")

def get_upcoming_notifications(data):
    """
    Retrieves upcoming billing dates and tasks within the next 7 days.
    """
    notifications = []
    today = datetime.today()

    # Check billing due dates
    for client in ["Biga", "Tricolor"]:
        due_date_str = data['pricing'][client]['due_date']
        if due_date_str:
            due_date = datetime.strptime(due_date_str, "%d/%m/%Y")
            days_left = (due_date - today).days
            if 0 <= days_left <= 7:
                notifications.append(f"🔔 Billing for {client} is due in {days_left} day(s) on {due_date_str}.")

    # Check for upcoming goals/tasks within the next 7 days
    # (This can be expanded based on specific task deadlines if available)

    return notifications

def search_filter(items, search_term, is_dict=False):
    """
    Filters items based on the search term.
    """
    if is_dict:
        return [item for item in items if search_term.lower() in item['idea'].lower() or search_term.lower() in item['category'].lower()]
    else:
        return [item for item in items if search_term.lower() in item.lower()]

# ================== App Layout ================== #

st.set_page_config(page_title="📈 SMMA Planning and Tracking App", layout="wide")

st.title("📈 SMMA Planning and Tracking App")

# Display Notifications
notifications = get_upcoming_notifications(st.session_state['data'])
if notifications:
    st.sidebar.header("🔔 Notifications")
    for note in notifications:
        st.sidebar.info(note)

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

    # Search functionality
    search_term = st.text_input("Search Objectives", key="strat_search")

    objective = st.text_input(f"Add Strategic Objective for {client}", key="strat_input")
    if st.button("Add Objective", key="strat_add_btn"):
        if objective:
            st.session_state['data']['strategic_objectives'][client]['pending'].append(objective)
            save_data(st.session_state['data'])
            st.success("Objective added!")
        else:
            st.warning("Please enter an objective.")

    st.subheader(f"{client} Objectives")

    # Display pending objectives with checkboxes
    pending = st.session_state['data']['strategic_objectives'][client]['pending']
    completed = st.session_state['data']['strategic_objectives'][client]['completed']

    if search_term:
        filtered_pending = search_filter(pending, search_term)
    else:
        filtered_pending = pending

    for obj in filtered_pending.copy():  # Use copy to avoid issues while modifying the list
        col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
        with col1:
            if st.checkbox(obj, key=f"strat_pending_{client}_{obj}"):
                pending.remove(obj)
                completed.append(obj)
                save_data(st.session_state['data'])
                st.success(f"Marked '{obj}' as completed!")
        with col2:
            if st.button("✏️", key=f"strat_edit_{client}_{obj}"):
                new_obj = st.text_input("Edit Objective", value=obj, key=f"strat_edit_input_{client}_{obj}")
                if st.button("Save", key=f"strat_save_{client}_{obj}"):
                    edit_item("strategic_objectives", client, obj, "pending", new_obj)
        with col3:
            if st.button("🗑️", key=f"strat_delete_{client}_{obj}"):
                delete_item("strategic_objectives", client, obj, "pending")

    # Display completed objectives with options to edit/delete
    if completed:
        st.markdown("### ✅ Completed Objectives")
        if search_term:
            filtered_completed = search_filter(completed, search_term)
        else:
            filtered_completed = completed

        for obj in filtered_completed.copy():
            col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
            with col1:
                st.write(f"• {obj}")
            with col2:
                if st.button("✏️", key=f"strat_edit_completed_{client}_{obj}"):
                    new_obj = st.text_input("Edit Completed Objective", value=obj, key=f"strat_edit_completed_input_{client}_{obj}")
                    if st.button("Save", key=f"strat_save_completed_{client}_{obj}"):
                        edit_item("strategic_objectives", client, obj, "completed", new_obj)
            with col3:
                if st.button("🗑️", key=f"strat_delete_completed_{client}_{obj}"):
                    delete_item("strategic_objectives", client, obj, "completed")

def content_ideas():
    st.header("📝 Content Ideas")
    client = st.selectbox("Select Client", ["Biga", "Tricolor"], key="content_client")

    # Search functionality
    search_term = st.text_input("Search Content Ideas", key="content_search")

    idea = st.text_input(f"Add Content Idea for {client}", key="content_input")
    category = st.selectbox("Select Category", ["Trendy Posts", "Carousels", "Reels", "Polls"], key="content_category")
    if st.button("Add Content Idea", key="content_add_btn"):
        if idea:
            st.session_state['data']['content_ideas'][client]['pending'].append({'idea': idea, 'category': category})
            save_data(st.session_state['data'])
            st.success("Content idea added!")
        else:
            st.warning("Please enter a content idea.")

    st.subheader(f"{client} Content Ideas")

    # Display pending content ideas with checkboxes
    pending = st.session_state['data']['content_ideas'][client]['pending']
    completed = st.session_state['data']['content_ideas'][client]['completed']

    if search_term:
        filtered_pending = search_filter(pending, search_term, is_dict=True)
    else:
        filtered_pending = pending

    for item in filtered_pending.copy():
        label = f"{item['category']}: {item['idea']}"
        col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
        with col1:
            if st.checkbox(label, key=f"content_pending_{client}_{item['idea']}"):
                pending.remove(item)
                completed.append(item)
                save_data(st.session_state['data'])
                st.success(f"Marked '{item['idea']}' as completed!")
        with col2:
            if st.button("✏️", key=f"content_edit_{client}_{item['idea']}"):
                new_idea = st.text_input("Edit Idea", value=item['idea'], key=f"content_edit_idea_{client}_{item['idea']}")
                new_category = st.selectbox("Edit Category", ["Trendy Posts", "Carousels", "Reels", "Polls"], index=["Trendy Posts", "Carousels", "Reels", "Polls"].index(item['category']), key=f"content_edit_category_{client}_{item['idea']}")
                if st.button("Save", key=f"content_save_{client}_{item['idea']}"):
                    new_item = {'idea': new_idea, 'category': new_category}
                    edit_item("content_ideas", client, item, "pending", new_item)
        with col3:
            if st.button("🗑️", key=f"content_delete_{client}_{item['idea']}"):
                delete_item("content_ideas", client, item, "pending")

    # Display completed content ideas with options to edit/delete
    if completed:
        st.markdown("### ✅ Completed Content Ideas")
        if search_term:
            filtered_completed = search_filter(completed, search_term, is_dict=True)
        else:
            filtered_completed = completed

        for item in filtered_completed.copy():
            label = f"{item['category']}: {item['idea']}"
            col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
            with col1:
                st.write(f"• {label}")
            with col2:
                if st.button("✏️", key=f"content_edit_completed_{client}_{item['idea']}"):
                    new_idea = st.text_input("Edit Completed Idea", value=item['idea'], key=f"content_edit_completed_idea_{client}_{item['idea']}")
                    new_category = st.selectbox("Edit Completed Category", ["Trendy Posts", "Carousels", "Reels", "Polls"], index=["Trendy Posts", "Carousels", "Reels", "Polls"].index(item['category']), key=f"content_edit_completed_category_{client}_{item['idea']}")
                    if st.button("Save", key=f"content_save_completed_{client}_{item['idea']}"):
                        new_item = {'idea': new_idea, 'category': new_category}
                        edit_item("content_ideas", client, item, "completed", new_item)
            with col3:
                if st.button("🗑️", key=f"content_delete_completed_{client}_{item['idea']}"):
                    delete_item("content_ideas", client, item, "completed")

def weekly_goals():
    st.header("🎯 Weekly Goals (SMART)")
    client = st.selectbox("Select Client", ["Biga", "Tricolor"], key="goal_client")

    # Search functionality
    search_term = st.text_input("Search Weekly Goals", key="goal_search")

    with st.form(key='goal_form'):
        goal = st.text_input("Enter SMART Goal", key="goal_input")
        submitted = st.form_submit_button("Add Goal")
        if submitted:
            if goal:
                st.session_state['data']['weekly_goals'][client]['pending'].append(goal)
                save_data(st.session_state['data'])
                st.success("Goal added!")
            else:
                st.warning("Please enter a goal.")

    st.subheader(f"{client} Weekly Goals")

    # Display pending goals with checkboxes
    pending = st.session_state['data']['weekly_goals'][client]['pending']
    completed = st.session_state['data']['weekly_goals'][client]['completed']

    if search_term:
        filtered_pending = search_filter(pending, search_term)
    else:
        filtered_pending = pending

    for g in filtered_pending.copy():
        col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
        with col1:
            if st.checkbox(g, key=f"goal_pending_{client}_{g}"):
                pending.remove(g)
                completed.append(g)
                save_data(st.session_state['data'])
                st.success("Marked goal as completed!")
        with col2:
            if st.button("✏️", key=f"goal_edit_{client}_{g}"):
                new_goal = st.text_input("Edit Goal", value=g, key=f"goal_edit_input_{client}_{g}")
                if st.button("Save", key=f"goal_save_{client}_{g}"):
                    edit_item("weekly_goals", client, g, "pending", new_goal)
        with col3:
            if st.button("🗑️", key=f"goal_delete_{client}_{g}"):
                delete_item("weekly_goals", client, g, "pending")

    # Display completed goals with options to edit/delete
    if completed:
        st.markdown("### ✅ Completed Goals")
        if search_term:
            filtered_completed = search_filter(completed, search_term)
        else:
            filtered_completed = completed

        for g in filtered_completed.copy():
            col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
            with col1:
                st.write(f"• {g}")
            with col2:
                if st.button("✏️", key=f"goal_edit_completed_{client}_{g}"):
                    new_goal = st.text_input("Edit Completed Goal", value=g, key=f"goal_edit_completed_input_{client}_{g}")
                    if st.button("Save", key=f"goal_save_completed_{client}_{g}"):
                        edit_item("weekly_goals", client, g, "completed", new_goal)
            with col3:
                if st.button("🗑️", key=f"goal_delete_completed_{client}_{g}"):
                    delete_item("weekly_goals", client, g, "completed")

def captions():
    st.header("✍️ Captions")
    client = st.selectbox("Select Client", ["Biga", "Tricolor"], key="caption_client")

    # Search functionality
    search_term = st.text_input("Search Captions", key="caption_search")

    caption = st.text_input(f"Add Caption for {client}", key="caption_input")
    if st.button("Add Caption", key="caption_add_btn"):
        if caption:
            st.session_state['data']['captions'][client]['pending'].append(caption)
            save_data(st.session_state['data'])
            st.success("Caption added!")
        else:
            st.warning("Please enter a caption.")

    st.subheader(f"{client} Captions")

    # Display pending captions with checkboxes
    pending = st.session_state['data']['captions'][client]['pending']
    completed = st.session_state['data']['captions'][client]['completed']

    if search_term:
        filtered_pending = search_filter(pending, search_term)
    else:
        filtered_pending = pending

    for cap in filtered_pending.copy():
        col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
        with col1:
            if st.checkbox(cap, key=f"caption_pending_{client}_{cap}"):
                pending.remove(cap)
                completed.append(cap)
                save_data(st.session_state['data'])
                st.success("Marked caption as completed!")
        with col2:
            if st.button("✏️", key=f"caption_edit_{client}_{cap}"):
                new_cap = st.text_input("Edit Caption", value=cap, key=f"caption_edit_input_{client}_{cap}")
                if st.button("Save", key=f"caption_save_{client}_{cap}"):
                    edit_item("captions", client, cap, "pending", new_cap)
        with col3:
            if st.button("🗑️", key=f"caption_delete_{client}_{cap}"):
                delete_item("captions", client, cap, "pending")

    # Display completed captions with options to edit/delete
    if completed:
        st.markdown("### ✅ Completed Captions")
        if search_term:
            filtered_completed = search_filter(completed, search_term)
        else:
            filtered_completed = completed

        for cap in filtered_completed.copy():
            col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
            with col1:
                st.write(f"• {cap}")
            with col2:
                if st.button("✏️", key=f"caption_edit_completed_{client}_{cap}"):
                    new_cap = st.text_input("Edit Completed Caption", value=cap, key=f"caption_edit_completed_input_{client}_{cap}")
                    if st.button("Save", key=f"caption_save_completed_{client}_{cap}"):
                        edit_item("captions", client, cap, "completed", new_cap)
            with col3:
                if st.button("🗑️", key=f"caption_delete_completed_{client}_{cap}"):
                    delete_item("captions", client, cap, "completed")

def notes():
    st.header("🗒️ Notes for Planning")
    client = st.selectbox("Select Client", ["Biga", "Tricolor"], key="notes_client")

    # Search functionality
    search_term = st.text_input("Search Notes", key="notes_search")

    note = st.text_area(f"Add Note for {client}", key="notes_input")
    if st.button("Add Note", key="notes_add_btn"):
        if note:
            st.session_state['data']['notes'][client]['pending'].append(note)
            save_data(st.session_state['data'])
            st.success("Note added!")
        else:
            st.warning("Please enter a note.")

    st.subheader(f"{client} Notes")

    # Display pending notes with checkboxes
    pending = st.session_state['data']['notes'][client]['pending']
    completed = st.session_state['data']['notes'][client]['completed']

    if search_term:
        filtered_pending = search_filter(pending, search_term)
    else:
        filtered_pending = pending

    for n in filtered_pending.copy():
        col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
        with col1:
            if st.checkbox(n, key=f"note_pending_{client}_{n}"):
                pending.remove(n)
                completed.append(n)
                save_data(st.session_state['data'])
                st.success("Marked note as completed!")
        with col2:
            if st.button("✏️", key=f"note_edit_{client}_{n}"):
                new_note = st.text_area("Edit Note", value=n, key=f"note_edit_input_{client}_{n}")
                if st.button("Save", key=f"note_save_{client}_{n}"):
                    edit_item("notes", client, n, "pending", new_note)
        with col3:
            if st.button("🗑️", key=f"note_delete_{client}_{n}"):
                delete_item("notes", client, n, "pending")

    # Display completed notes with options to edit/delete
    if completed:
        st.markdown("### ✅ Completed Notes")
        if search_term:
            filtered_completed = search_filter(completed, search_term)
        else:
            filtered_completed = completed

        for n in filtered_completed.copy():
            col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
            with col1:
                st.write(f"• {n}")
            with col2:
                if st.button("✏️", key=f"note_edit_completed_{client}_{n}"):
                    new_note = st.text_area("Edit Completed Note", value=n, key=f"note_edit_completed_input_{client}_{n}")
                    if st.button("Save", key=f"note_save_completed_{client}_{n}"):
                        edit_item("notes", client, n, "completed", new_note)
            with col3:
                if st.button("🗑️", key=f"note_delete_completed_{client}_{n}"):
                    delete_item("notes", client, n, "completed")

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
            try:
                next_month = today.replace(month=today.month + 1, day=30)
            except ValueError:
                # Handle months with fewer than 30 days
                next_month = today + timedelta(days=30)
                next_month = next_month.replace(day=30)
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
