import streamlit as st
import openai
import json
import os
import threading
from datetime import datetime
import matplotlib.pyplot as plt

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
            default_data = {
                "strategic_objectives": {"Biga": [], "Tricolor": []},
                "content_ideas": {"Biga": [], "Tricolor": []},
                "weekly_goals": {"Biga": [], "Tricolor": []},
                "captions": {"Biga": [], "Tricolor": []},
                "notes": {"Biga": [], "Tricolor": []},
                "analytics": {"Biga": {"views": 0, "engagement": 0, "likes": 0},
                              "Tricolor": {"views": 0, "engagement": 0, "likes": 0}},
                "pricing": {"Biga": {"amount": 0, "due_date": ""}, "Tricolor": {"amount": 0, "due_date": ""}}
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
    st.session_state['data'] = data
    log_save_action(action_details)

# ================== Initialize session state ================== #
if 'data' not in st.session_state:
    st.session_state['data'] = load_data()

# ================== AI Content Generation ================== #

def ai_generate_content(query, section):
    """Use OpenAI to generate content for specific sections using chat completions."""
    prompt = f"You are an expert in social media marketing. Generate a new {section} based on the following query: {query}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        generated_content = response['choices'][0]['message']['content'].strip()
        return generated_content
    except openai.error.OpenAIError as e:
        return f"Error generating content: {str(e)}"

# ================== AI General Assistant for Various Tasks ================== #

def ai_general_assistant(query):
    """Allow ChatGPT to handle a variety of tasks, including code assistance, content generation, and data queries."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ],
            max_tokens=150,
            temperature=0.7
        )
        result = response['choices'][0]['message']['content'].strip()
        return result
    except openai.error.OpenAIError as e:
        return f"Error processing the request: {str(e)}"

# ================== Enhanced AI Assistant for Mixed Queries ================== #

def ai_assistant(query, data):
    """Process any type of query: content generation, data queries, or general assistant help."""
    query_lower = query.lower()

    # Check for content generation keywords
    generate_keywords = ["generate", "produce", "create", "make", "come up with"]

    # Check for data-related queries
    data_keywords = ["what", "how many", "how much", "count", "give me", "list", "find", "show"]

    # Check if the query is about content generation
    if any(keyword in query_lower for keyword in generate_keywords):
        if "content idea" in query_lower:
            return ai_generate_content(query, "content idea")
        elif "caption" in query_lower:
            return ai_generate_content(query, "caption")

    # Handle data queries
    elif any(keyword in query_lower for keyword in data_keywords):
        if "views" in query_lower:
            client = "Biga" if "biga" in query_lower else "Tricolor"
            return f"{client} has {data['analytics'][client]['views']} views."
        elif "content ideas" in query_lower:
            client = "Biga" if "biga" in query_lower else "Tricolor"
            content_ideas = [idea['idea'] for idea in data['content_ideas'][client]]
            return f"Content ideas for {client}: {', '.join(content_ideas)}"
        elif "pricing" in query_lower:
            client = "Biga" if "biga" in query_lower else "Tricolor"
            pricing_data = data['pricing'][client]
            return f"Pricing for {client}: Amount - {pricing_data['amount']}, Due Date - {pricing_data['due_date']}"

    # If it's a general request (e.g., code help or explanations)
    else:
        return ai_general_assistant(query)

# ================== OpenAI Query Function ================== #

def query_openai_about_data(query, data):
    """Ask OpenAI a question about the loaded data and perform content generation or data queries."""
    try:
        return ai_assistant(query, data)
    except openai.error.RateLimitError:
        return "Error: You have exceeded your API quota. Please check your OpenAI account for details."
    except openai.error.OpenAIError as e:
        return f"Error querying OpenAI: {str(e)}"

# ================== Section Functions ================== #

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
    
    st.subheader(f"{client} Objectives")
    for idx, obj in enumerate(st.session_state['data']['strategic_objectives'][client], 1):
        st.write(f"{idx}. {obj}")
    
def content_ideas():
    st.header("📝 Content Ideas")
    client = st.selectbox("Select Client", ["Biga", "Tricolor"], key="content_client")
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
    for idx, item in enumerate(st.session_state['data']['content_ideas'][client], 1):
        st.write(f"{idx}. {item['idea']} - {item['category']}")
    
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
        st.write(f"{idx}. {goal}")
    
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
        st.write(f"{idx}. {caption}")

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
        st.write(f"{idx}. {note}")
    
def analytics():
    st.header("📊 Analytics")
    client = st.selectbox("Select Client", ["Biga", "Tricolor"], key="analytics_client")
    analytics_data = st.session_state['data']['analytics'][client]

    # Display current analytics data
    st.write(f"Views: {analytics_data['views']}")
    st.write(f"Engagement: {analytics_data['engagement']}")
    st.write(f"Likes: {analytics_data['likes']}")

    # Input for updating analytics
    views = st.number_input("Update Views", value=analytics_data['views'], step=1)
    engagement = st.number_input("Update Engagement", value=analytics_data['engagement'], step=1)
    likes = st.number_input("Update Likes", value=analytics_data['likes'], step=1)

    if st.button("Update Analytics"):
        st.session_state['data']['analytics'][client] = {"views": views, "engagement": engagement, "likes": likes}
        save_data(st.session_state['data'], f"Updated analytics for {client}")
        st.success("Analytics updated!")

    # ================== Analytics Graphs ================== #

    metrics = ['Views', 'Engagement', 'Likes']
    values = [analytics_data['views'], analytics_data['engagement'], analytics_data['likes']]

    fig, ax = plt.subplots()
    ax.bar(metrics, values, color=['blue', 'green', 'orange'])

    ax.set_title(f"Analytics Overview for {client}")
    ax.set_ylabel("Count")
    ax.set_xlabel("Metrics")

    st.pyplot(fig)

def pricing_billing():
    st.header("💰 Pricing & Billing")
    client = st.selectbox("Select Client", ["Biga", "Tricolor"], key="pricing_client")
    pricing_data = st.session_state['data']['pricing'][client]

    # Ensure that the amount is a numeric type
    amount = pricing_data['amount']
    if not isinstance(amount, (int, float)):
        amount = 0.0

    amount = st.number_input("Amount Due", value=float(amount), step=1.0)
    due_date = st.text_input("Due Date", value=pricing_data['due_date'])

    if st.button("Update Pricing"):
        st.session_state['data']['pricing'][client] = {"amount": amount, "due_date": due_date}
        save_data(st.session_state['data'], f"Updated pricing for {client}")
        st.success("Pricing & Billing updated!")

def display_save_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as log_file:
            log_data = log_file.read()
            st.text_area("Save Log", log_data, height=200)
    else:
        st.write("No save log available yet.")

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

# ================== AI Query Section ================== #

if selection == "Ask AI":
    st.header("🤖 Ask AI About the Data")
    query = st.text_input("Enter your question or request (e.g., 'Generate a new content idea for Biga'):")

    if st.button("Submit Query"):
        if query:
            response = query_openai_about_data(query, st.session_state['data'])
            st.write(response)
        else:
            st.warning("Please enter a query.")

# ================== Other Sections ================== #

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
