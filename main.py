import streamlit as st
import openai
import json
import os
import threading
from datetime import datetime

# Access the OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ================== Data Handling ================== #

DATA_FILE = 'data.json'
LOG_FILE = 'save_log.txt'

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
                    "Biga": [],
                    "Tricolor": []
                },
                "content_ideas": {
                    "Biga": [],
                    "Tricolor": []
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
                }
            }
            with open(DATA_FILE, 'w') as f:
                json.dump(default_data, f, indent=4)
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        return data

# Function to save data to the JSON file and update session state
def save_data(data, action_details="Data updated"):
    with lock:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    # Update session state to reflect changes
    st.session_state['data'] = data
    # Log the save action
    log_save_action(action_details)

# Function to display the save log
def display_save_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as log_file:
            log_data = log_file.read()
            st.text_area("Save Log", log_data, height=200)
    else:
        st.write("No save log available yet.")

# Initialize session state
if 'data' not in st.session_state:
    st.session_state['data'] = load_data()

# ================== OpenAI Query Function ================== #

def query_openai_about_data(query, data):
    """Ask OpenAI a question about the loaded data."""
    # Convert the data to a string format for GPT to process
    data_str = json.dumps(data, indent=2)
    
    # Define the prompt including the data
    prompt = f"You are given the following data: {data_str}\n\nAnswer the following question: {query}"

    try:
        # Use the OpenAI ChatCompletion API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.5
        )
        
        # Extract the response content
        message_content = response['choices'][0]['message']['content'].strip()
        return message_content

    except openai.error.RateLimitError:
        return "Error: You have exceeded your API quota. Please check your OpenAI account for details."
    except openai.error.OpenAIError as e:
        return f"Error querying OpenAI: {str(e)}"


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
    "Pricing & Billing",
    "Ask AI",
    "Save Log"
]
selection = st.sidebar.radio("Go to", options)

# ================== Section Functions ================== #

# Function for Strategic Objectives Section
def strategic_objectives():
    st.header("🎯 Strategic Objectives")
    client = st.selectbox("Select Client", ["Biga", "Tricolor"], key="strat_client")
    objective = st.text_input(f"Add Strategic Objective for {client}", key="strat_input")
    if st.button("Add Objective", key="strat_add_btn"):
        if objective:
            st.session_state['data']['strategic_objectives'][client].append(objective)
            save_data(st.session_state['data'], f"Added objective for {client}")
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
            st.session_state['data']['strategic_objectives'][client].pop(idx-1)
            save_data(st.session_state['data'], f"Deleted objective for {client}")

    if st.button(f"Delete All Objectives for {client}", key="delete_all_strat"):
        st.session_state['data']['strategic_objectives'][client] = []
        save_data(st.session_state['data'], f"Deleted all objectives for {client}")
        st.success("All objectives deleted!")

# Function for Content Ideas Section
def content_ideas():
    st.header("📝 Content Ideas")
    client = st.selectbox("Select Client", ["Biga", "Tricolor"], key="content_client")
    
    search_term = st.text_input("Search Content Ideas", key="search_content")
    idea = st.text_input(f"Add Content Idea for {client}", key="content_input")
    category = st.selectbox("Select Category", ["Trendy Posts", "Carousels", "Reels", "Polls"], key="content_category")
    if st.button("Add Content Idea", key="content_add_btn"):
        if idea:
            st.session_state['data']['content_ideas'][client].append({'idea': idea, 'category': category})
            save_data(st.session_state['data'], f"Added content idea for {client}")
            st.success("Content idea added!")
        else:
            st.warning("Please enter a content idea.")
    
    st.subheader(f"{client} Content Ideas")
    filtered_ideas = [item for item in st.session_state['data']['content_ideas'][client] if search_term.lower() in item['idea'].lower()]
    for idx, item in enumerate(filtered_ideas, 1):
        col1, col2 = st.columns([4, 1])
        new_idea = col1.text_input(f"Edit Idea {idx}", value=item['idea'], key=f"edit_idea_{idx}")
        if col2.button(f"Save Edit {idx}", key=f"save_edit_{idx}"):
            st.session_state['data']['content_ideas'][client][idx-1]['idea'] = new_idea
            save_data(st.session_state['data'], f"Edited content idea for {client}")
            st.success(f"Idea {idx} updated!")

    if st.button(f"Delete All Content Ideas for {client}", key="delete_all_content"):
        st.session_state['data']['content_ideas'][client] = []
        save_data(st.session_state['data'], f"Deleted all content ideas for {client}")
        st.success("All content ideas deleted!")

# Function for Weekly Goals Section
def weekly_goals():
    st.header("📅 Weekly Goals")
    client = st.selectbox("Select Client", ["Biga", "Tricolor"], key="goals_client")
    
    goal = st.text_input(f"Add Weekly Goal for {client}", key="goals_input")
    if st.button("Add Weekly Goal", key="goals_add_btn"):
        if goal:
            st.session_state['data']['weekly_goals'][client].append(goal)
            save_data(st.session_state['data'], f"Added weekly goal for {client}")
            st.success("Weekly goal added!")
        else:
            st.warning("Please enter a weekly goal.")

    st.subheader(f"{client} Weekly Goals")
    for idx, goal in enumerate(st.session_state['data']['weekly_goals'][client], 1):
        col1, col2 = st.columns([4, 1])
        col1.write(f"{idx}. {goal}")
        if col2.button(f"Delete {idx}", key=f"delete_goal_{idx}"):
            st.session_state['data']['weekly_goals'][client].pop(idx-1)
            save_data(st.session_state['data'], f"Deleted weekly goal for {client}")

# Function for Captions Section
def captions():
    st.header("📝 Captions")
    client = st.selectbox("Select Client", ["Biga", "Tricolor"], key="captions_client")
    
    caption = st.text_input(f"Add Caption for {client}", key="caption_input")
    if st.button("Add Caption", key="caption_add_btn"):
        if caption:
            st.session_state['data']['captions'][client].append(caption)
            save_data(st.session_state['data'], f"Added caption for {client}")
            st.success("Caption added!")
        else:
            st.warning("Please enter a caption.")

    st.subheader(f"{client} Captions")
    for idx, caption in enumerate(st.session_state['data']['captions'][client], 1):
        col1, col2 = st.columns([4, 1])
        col1.write(f"{idx}. {caption}")
        if col2.button(f"Delete {idx}", key=f"delete_caption_{idx}"):
            st.session_state['data']['captions'][client].pop(idx-1)
            save_data(st.session_state['data'], f"Deleted caption for {client}")

# Function for Notes Section
def notes():
    st.header("📝 Notes")
    client = st.selectbox("Select Client", ["Biga", "Tricolor"], key="notes_client")
    
    note = st.text_area(f"Add Note for {client}", key="note_input")
    if st.button("Add Note", key="note_add_btn"):
        if note:
            st.session_state['data']['notes'][client].append(note)
            save_data(st.session_state['data'], f"Added note for {client}")
            st.success("Note added!")
        else:
            st.warning("Please enter a note.")

    st.subheader(f"{client} Notes")
    for idx, note in enumerate(st.session_state['data']['notes'][client], 1):
        col1, col2 = st.columns([4, 1])
        col1.write(f"{idx}. {note}")
        if col2.button(f"Delete {idx}", key=f"delete_note_{idx}"):
            st.session_state['data']['notes'][client].pop(idx-1)
            save_data(st.session_state['data'], f"Deleted note for {client}")

# Function for Analytics Section
def analytics():
    st.header("📊 Analytics")
    client = st.selectbox("Select Client", ["Biga", "Tricolor"], key="analytics_client")
    analytics_data = st.session_state['data']['analytics'][client]

    st.write(f"Views: {analytics_data['views']}")
    st.write(f"Engagement: {analytics_data['engagement']}")
    st.write(f"Likes: {analytics_data['likes']}")

    views = st.number_input("Update Views", value=analytics_data['views'], step=1)
    engagement = st.number_input("Update Engagement", value=analytics_data['engagement'], step=1)
    likes = st.number_input("Update Likes", value=analytics_data['likes'], step=1)

    if st.button("Update Analytics"):
        st.session_state['data']['analytics'][client] = {"views": views, "engagement": engagement, "likes": likes}
        save_data(st.session_state['data'], f"Updated analytics for {client}")
        st.success("Analytics updated!")

# Function for Pricing & Billing Section
def pricing_billing():
    st.header("💰 Pricing & Billing")
    client = st.selectbox("Select Client", ["Biga", "Tricolor"], key="pricing_client")
    pricing_data = st.session_state['data']['pricing'][client]

    amount = st.number_input("Amount Due", value=pricing_data['amount'], step=1.0)
    due_date = st.text_input("Due Date", value=pricing_data['due_date'])

    if st.button("Update Pricing"):
        st.session_state['data']['pricing'][client] = {"amount": amount, "due_date": due_date}
        save_data(st.session_state['data'], f"Updated pricing for {client}")
        st.success("Pricing & Billing updated!")

# ================== AI Query Section ================== #

if selection == "Ask AI":
    st.header("🤖 Ask AI About the Data")
    query = st.text_input("Enter your question about the data:")
    
    if st.button("Submit Query"):
        if query:
            # Query OpenAI with the input and data from data.json
            response = query_openai_about_data(query, st.session_state['data'])
            st.write(response)
        else:
            st.warning("Please enter a query.")

# ================== Other Sections ================== #

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
elif selection == "Save Log":
    st.header("📝 Save Log")
    display_save_log()

# ================== Footer ================== #

st.markdown("---")
st.markdown("© 2024 Your SMMA. All rights reserved.")
