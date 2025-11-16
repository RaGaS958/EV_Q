import streamlit as st
import api
import os
import asyncio
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import AgentTool, google_search
from google.genai import types
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="EV_Q:? - Your EV Expert System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Background */
    .stApp {
background: #4EF0B8;
color: #ffffff;            

    /* Headers */
    .main-header {
       font-size: 4rem;
        font-weight: bold;
        background: linear-gradient(90deg, #ffffff 0%, #ffffff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    
    .sub-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff !important;
        margin: 2rem 0 1rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .page-subtitle {
        text-align: center;
        color: #ffffff !important;
        font-size: 1.3rem;
        font-weight: 400;
        margin-bottom: 2rem;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
        opacity: 0.95;
    }
    
    /* Content Boxes */
    .content-box {
        border-radius: 20px;
        padding: 2.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.4);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .content-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.2);
    }
    
    .content-box h1, .content-box h2, .content-box h3, 
    .content-box h4, .content-box p, .content-box li,
    .content-box span, .content-box div {
        color: #2d3748 !important;
    }
    
    /* Feature Cards */
    .feature-card {
        background: linear-gradient(135deg, #ffffff %, #f0f0f0 100%);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        color: #ffffff !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .feature-card:hover::before {
        opacity: 1;
    }
    
    .feature-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
    }
    
    .feature-card h3, .feature-card p {
        color: #ffffff !important;
        margin: 0.5rem 0;
        position: relative;
        z-index: 1;
    }
    
    .feature-icon {
        font-size: 3.5rem;
        margin-bottom: 1rem;
        filter: drop-shadow(0 4px 6px rgba(0,0,0,0.2));
    }
    
    /* Agent Cards */
    .agent-card {
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        border-left: 5px solid #fffff0;
    }
    
    .agent-card:hover {
        transform: translateX(10px);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.15);
    }
    
    .agent-card h3 {
        color: #667eea !important;
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .agent-card .agent-role {
        color: #718096 !important;
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .agent-card ul {
        color: #2d3748 !important;
        margin-left: 1.5rem;
    }
    
    /* Agent Badges */
    .agent-badge {
        display: inline-block;
        padding: 0.6rem 1.2rem;
        border-radius: 30px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.3rem;
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .agent-badge:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }
    
    .tech-badge { background: linear-gradient(135deg, #D8B4FF 0%, #A5F3FC 100%);




 }
    .reseller-badge { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .finance-badge { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    .policy-badge { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
    .recommend-badge { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
    
    /* Chat Messages */
    .stChatMessage {
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        background: rgba(255, 255, 255, 0.98) !important;
    }
    
    .stChatMessage [data-testid="stMarkdownContainer"] p,
    .stChatMessage [data-testid="stMarkdownContainer"] li,
    .stChatMessage [data-testid="stMarkdownContainer"] span {
        color: #000000 !important;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    div[data-testid="stChatMessageContent"] * {
        color: #2d3748 !important;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
background-color: #4EF0B8;
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.15);
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 255, 255, 0.2);
        color: #ffffff !important;
        border: 2px solid rgba(255, 255, 255, 0.3);
        transition: all 0.3s ease;
        border-radius: 10px;
        font-weight: 600;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 255, 255, 0.3);
        border-color: #ffffff;
        transform: translateX(5px);
    }
    
    /* Primary Buttons */
    .stButton > button {
background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
        color: #000000 !important;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-weight: 700;
        font-size: 1.05rem;
        transition: all 0.3s ease;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
        cursor: pointer;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    /* Info Boxes */
    .info-box {
        background: rgba(255, 255, 255, 0.2);
        border-left: 4px solid #ffffff;
        padding: 1.2rem;
        border-radius: 10px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    .info-box p, .info-box li {
        color: #ffffff !important;
        margin: 0.3rem 0;
    }
    
    /* Stats Cards */
    .stat-card {
        background: rgba(255, 255, 255, 0.25);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: transform 0.3s ease;
    }
    
    .stat-card:hover {
        transform: scale(1.05);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #ffffff !important;
        line-height: 1;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #ffffff !important;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    /* Animations */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .fade-in {
        animation: fadeInUp 0.8s ease-in-out;
    }
    
    .slide-in {
        animation: slideInRight 0.6s ease-out;
    }
    
    .pulse {
        animation: pulse 2s ease-in-out infinite;
    }
    
    /* Text Visibility */
    .stMarkdown, .stMarkdown p, .stMarkdown li, 
    .stMarkdown span, .stMarkdown h1, .stMarkdown h2, 
    .stMarkdown h3, .stMarkdown h4 {
        color: #ffffff !important;
    }
    
    .content-box .stMarkdown, .content-box .stMarkdown p, 
    .content-box .stMarkdown li, .content-box .stMarkdown span {
        color: #2d3748 !important;
    }
    
    /* Chat Input */
    .stChatInput > div {
        border-radius: 25px;
        border: 2px solid rgba(102, 126, 234, 0.3);
    }
    
    .stChatInput input {
        color: #2d3748 !important;
    }
    
    /* Hero Section */
    .hero-section {
        text-align: center;
        padding: 3rem 0;
        animation: fadeInDown 1s ease-in-out;
    }
    
    /* Quick Action Buttons */
    .quick-action-btn {
        background: rgba(255, 255, 255, 0.25);
        border: 2px solid rgba(255, 255, 255, 0.4);
        border-radius: 15px;
        padding: 1rem;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .quick-action-btn:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    }
    
    /* Architecture Diagram */
    .arch-node {
        background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.5rem;
        color: #ffffff !important;
        text-align: center;
        font-weight: 700;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .arch-node:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    /* Timeline */
    .timeline-item {
        position: relative;
        padding-left: 3rem;
        padding-bottom: 2rem;
    }
    
    .timeline-item::before {
        content: '';
        position: absolute;
        left: 0.75rem;
        top: 0;
        bottom: 0;
        width: 2px;
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .timeline-dot {
        position: absolute;
        left: 0;
        top: 0;
        width: 2rem;
        height: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_initialized" not in st.session_state:
    st.session_state.agent_initialized = False
if "runner" not in st.session_state:
    st.session_state.runner = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# Agent Icons
AGENT_ICONS = {
    "TechnicianAgent": "🔧",
    "ResellerAgent": "🚗",
    "FinancierAgent": "💰",
    "PolicyAgent": "🛡️",
    "RecommendationAgent": "🧠",
    "EVQ_Manager": "⚡"
}

# Initialize Agents
def initialize_agents():
    """Initialize all agents and return the runner"""
    try:
        os.environ["GOOGLE_API_KEY"] = api.api
        
        retry_config = types.HttpRetryOptions(
            attempts=5,
            exp_base=7,
            initial_delay=1,
            http_status_codes=[429, 500, 503, 504],
        )
        
        technician_agent = Agent(
            name="TechnicianAgent",
            model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
            instruction="""You are a certified EV technical support specialist. 
Your only job is to diagnose EV issues, explain battery/charging/range details,
and provide step-by-step troubleshooting instructions.
Use tools only when needed to fetch EV specs or technical documentation.
Respond in bullet points, be concise, and avoid assumptions.""",
            tools=[google_search],
            output_key="tech_support_response",
        )
        
        reseller_agent = Agent(
            name="ResellerAgent",
            model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
            instruction="""You are an EV dealership & resale expert.
Your tasks:
- Compare EV models and recommend top options
- Retrieve price & inventory data
- Estimate resale value and depreciation
- Present comparisons in structured tables when possible""",
            tools=[google_search],
            output_key="reseller_recommendation",
        )
        
        financier_agent = Agent(
            name="FinancierAgent",
            model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
            instruction="""You are an EV finance specialist.
Your responsibilities:
- Calculate EMI, interest, and total cost of ownership
- Suggest financing, leasing, and subscription options
- Inform about EV subsidies and government incentives""",
            tools=[google_search],
            output_key="finance_calculation",
        )
        
        policy_agent = Agent(
            name="PolicyAgent",
            model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
            instruction="""You are an EV legal, warranty, and compliance advisor.
Your job is to clarify:
- Insurance requirements
- Battery warranty policies
- EV safety & recycling regulations
- State/central government incentives""",
            tools=[google_search],
            output_key="policy_guidance",
        )
        
        recommendation_agent = Agent(
            name="RecommendationAgent",
            model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
            instruction="""You are an EV personalization advisor.
Learn user needs (budget, range, usage, charging access) and output
tailored EV recommendations ranked by suitability.""",
            tools=[google_search],
            output_key="personalized_recommendation",
        )
        
        evq_manager = Agent(
            name="EVQ_Manager",
            model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
            instruction="""You are EV_Q Manager, the central orchestrator for an Electric Vehicle Expert System.
Your role: Understand the user's request and decide which specialist agent(s) to call.

Workflow Rules (MUST FOLLOW):
1️⃣ If the query involves technical issues, battery, charging, range, or maintenance,
   you MUST call TechnicianAgent.
2️⃣ If the query is about buying/selling, model comparison, pricing, availability,
   or resale value, you MUST call ResellerAgent.
3️⃣ If the query involves EMI, loan, interest, subsidies, or total cost analysis,
   you MUST call FinancierAgent.
4️⃣ If the query asks about insurance, warranty, policy, government rules, or compliance,
   you MUST call PolicyAgent.
5️⃣ If the query is about personalization or "which EV is best for me",
   you SHOULD call RecommendationAgent (if available).

After you receive the output from specialist agents:
- Combine the responses when multiple agents are used.
- Present a single final response to the user.
- Be clear, structured, and avoid internal system/tool details.

Important:
- Always call an agent tool before answering when the query matches its domain.
- Never hallucinate specifications, always rely on agent outputs/tools when possible.""",
            tools=[
                AgentTool(technician_agent),
                AgentTool(reseller_agent),
                AgentTool(financier_agent),
                AgentTool(policy_agent),
                AgentTool(recommendation_agent),
            ],
        )
        
        runner = InMemoryRunner(agent=evq_manager)
        return runner, True, "✅ All agents initialized successfully!"
    
    except Exception as e:
        return None, False, f"❌ Initialization failed: {str(e)}"

# Enhanced Sidebar
with st.sidebar:
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    st.markdown("### ⚡ EV_Q:? Navigation")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Current page indicator
    current_icon = {"Home": "🏠", "Chatbot": "💬", "Agents": "🤖", "About": "ℹ️"}
    st.markdown(f"""
    <div class="info-box" style="text-align: center; margin-bottom: 1rem;">
        <p style="font-size: 1.2rem; margin: 0; font-weight: 700;">
            {current_icon.get(st.session_state.current_page, '📄')} {st.session_state.current_page}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation Menu
    pages = {
        "🏠 Home": "Home",
        "💬 Chatbot": "Chatbot",
        "🤖 Agents": "Agents",
        "ℹ️ About": "About"
    }
    
    for label, page in pages.items():
        button_type = "primary" if st.session_state.current_page == page else "secondary"
        if st.button(label, key=f"nav_{page}", use_container_width=True):
            st.session_state.current_page = page
            st.rerun()
    
    st.markdown("---")
    
    # Agent Status
    st.markdown("### 🤖 Active Agents")
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    agent_info = {
        "🔧 Technician": "Technical Support",
        "🚗 Reseller": "Sales & Inventory",
        "💰 Financier": "Loans & EMI",
        "🛡️ Policy": "Legal & Compliance",
        "🧠 Recommender": "Personalization"
    }
    
    for agent, desc in agent_info.items():
        st.markdown(f"**{agent}**")
        st.caption(desc)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Stats
    st.markdown("### 📊 Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="stat-card"><div class="stat-value">5</div><div class="stat-label">Agents</div></div>', unsafe_allow_html=True)
    with col2:
        msg_count = len(st.session_state.messages)
        st.markdown(f'<div class="stat-card"><div class="stat-value">{msg_count}</div><div class="stat-label">Messages</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # System Info
    st.markdown("### ⚙️ System")
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("**Version:** 2.0.0")
    st.markdown("**Model:** Gemini 2.5 Flash")
    st.markdown("**Status:** 🟢 Active")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Clear Chat (only on chatbot page)
    if st.session_state.current_page == "Chatbot" and len(st.session_state.messages) > 0:
        st.markdown("---")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# PAGE ROUTING
current_page = st.session_state.current_page

# ==================== HOME PAGE ====================
if current_page == "Home":
    st.markdown('<h1 class="main-header">⚡ EV_Q:?</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Your Intelligent Electric Vehicle Expert System</p>', unsafe_allow_html=True)
    
    # Hero Section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="content-box fade-in" style="text-align: center;">
            <h2> Welcome to the Future of EV Assistance</h2>
            <p style="font-size: 1.15rem; margin: 1.5rem 0; line-height: 1.8;">
                EV_Q:? uses advanced multi-agent AI architecture to provide comprehensive support 
                for all your electric vehicle needs. From technical troubleshooting to financial 
                planning, we've got you covered with specialized AI agents.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Feature Grid
    st.markdown('<h2 class="sub-header">🌟 Key Features</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    features = [
        ("🔧", "Technical Support", "Expert diagnosis for battery, charging, and maintenance"),
        ("🚗", "Sales & Resale", "Model comparisons and resale value estimates"),
        ("💰", "Financial Planning", "EMI calculations and subsidy information"),
        ("🛡️", "Policy & Legal", "Insurance, warranties, and regulations"),
        ("🧠", "Smart Recommendations", "Personalized EV suggestions for your needs"),
        ("⚡", "Real-time Data", "Up-to-date information via web search")
    ]
    
    cols = [col1, col2, col3]
    for idx, (icon, title, desc) in enumerate(features):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">{icon}</div>
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Sample Queries
    st.markdown('<h2 class="sub-header">💡 Try These Sample Queries</h2>', unsafe_allow_html=True)
    
    sample_queries = [
        ("🔋", "Battery draining fast", "Get technical diagnosis"),
        ("🚙", "Compare Tata Nexon EV vs MG ZS", "Detailed comparison"),
        ("💳", "Calculate EMI for ₹12 lakh", "Financial breakdown"),
        ("🏛️", "Maharashtra EV subsidies", "Government incentives"),
        ("🎯", "Best EV for 50km commute", "Personalized recommendation")
    ]
    
    col1, col2 = st.columns(2)
    for idx, (icon, query, desc) in enumerate(sample_queries):
        with col1 if idx % 2 == 0 else col2:
            if st.button(f"{icon} {query}", key=f"home_q_{idx}", use_container_width=True):
                st.session_state.current_page = "Chatbot"
                st.session_state.pending_query = query
                st.rerun()
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 1rem;">
                <p style="font-size: 0.9rem; color: #ffffff; opacity: 0.9;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # CTA
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Start Chatting Now", use_container_width=True, type="primary"):
            st.session_state.current_page = "Chatbot"
            st.rerun()

# ==================== CHATBOT PAGE ====================
elif current_page == "Chatbot":
    st.markdown('<h1 class="main-header">💬 EV_Q Chatbot</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Ask me anything about Electric Vehicles</p>', unsafe_allow_html=True)
    
    # Quick action buttons
    if len(st.session_state.messages) == 0:
        st.markdown('<h3 style="text-align: center; color: #ffffff; margin-bottom: 1rem;">🚀 Quick Start</h3>', unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns(5)
        
        quick_queries = [
            ("🔋", "Battery issue"),
            ("🚙", "Compare EVs"),
            ("💰", "EMI calculator"),
            ("🏛️", "Subsidies"),
            ("🎯", "Best EV")
        ]
        
        cols = [col1, col2, col3, col4, col5]
        for idx, (icon, query) in enumerate(quick_queries):
            with cols[idx]:
                if st.button(f"{icon}\n{query}", key=f"quick_{idx}", use_container_width=True):
                    st.session_state.pending_query = query
                    st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Initialize agents
    if not st.session_state.agent_initialized:
        with st.spinner("🚀 Initializing EV_Q Agent System..."):
            runner, success, message = initialize_agents()
            
            if success:
                st.session_state.runner = runner
                st.session_state.agent_initialized = True
                st.success(message, icon="✅")
            else:
                st.error(message, icon="❌")
                st.stop()
    
    # Chat Container
    chat_container = st.container()
    
    # Check for pending query
    if "pending_query" in st.session_state:
        prompt = st.session_state.pending_query
        del st.session_state.pending_query
    else:
        prompt = None
    
    with chat_container:
        # Welcome message
        if len(st.session_state.messages) == 0:
            st.markdown("""
            <div class="content-box fade-in" style="text-align: center; margin: 2rem 0;">
                <h2>👋 Welcome to EV_Q Chatbot!</h2>
                <p style="font-size: 1.1rem; margin: 1rem 0;">
                    I'm your AI-powered Electric Vehicle assistant. Ask me anything about:
                </p>
                <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 0.5rem; margin: 1.5rem 0;">
                    <span class="agent-badge tech-badge">🔧 Technical Issues</span>
                    <span class="agent-badge reseller-badge">🚗 Model Comparisons</span>
                    <span class="agent-badge finance-badge">💰 Financial Planning</span>
                    <span class="agent-badge policy-badge">🛡️ Policies</span>
                    <span class="agent-badge recommend-badge">🧠 Recommendations</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Display messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"], avatar=message.get("avatar", None)):
                st.markdown(message["content"])
                
                if "metadata" in message and "agents_used" in message["metadata"]:
                    agents = message["metadata"]["agents_used"]
                    if agents:
                        badge_html = "<div style='margin-top: 1rem;'><strong>🤖 Agents:</strong><br>"
                        for agent in agents:
                            icon = AGENT_ICONS.get(agent, "🤖")
                            agent_name = agent.replace('Agent', '')
                            badge_class = "tech-badge" if "Tech" in agent else "reseller-badge" if "Reseller" in agent else "finance-badge" if "Financier" in agent else "policy-badge" if "Policy" in agent else "recommend-badge"
                            badge_html += f'<span class="agent-badge {badge_class}">{icon} {agent_name}</span>'
                        badge_html += "</div>"
                        st.markdown(badge_html, unsafe_allow_html=True)
    
    # Chat input
    if prompt is None:
        prompt = st.chat_input("Type your question here...")
    
    # Process input
    if prompt:
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "avatar": "👤"
        })
        
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        with st.chat_message("assistant", avatar="⚡"):
            message_placeholder = st.empty()
            status_placeholder = st.empty()
            
            try:
                status_placeholder.markdown("""
                <div class="pulse" style="text-align: center; padding: 1rem;">
                    <div style="font-size: 2rem;">🤖</div>
                    <strong>Processing your query...</strong>
                </div>
                """, unsafe_allow_html=True)
                
                async def get_response():
                    return await st.session_state.runner.run_debug(prompt)
                
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_closed():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                response = loop.run_until_complete(get_response())
                status_placeholder.empty()
                
                # Extract response
                response_text = ""
                agents_used = []
                
                if isinstance(response, list):
                    for event in response:
                        if hasattr(event, 'content') and event.content:
                            content = event.content
                            if hasattr(content, 'parts') and content.parts:
                                for part in content.parts:
                                    if hasattr(part, 'function_call') and part.function_call:
                                        agent_name = part.function_call.name
                                        if agent_name and agent_name not in agents_used:
                                            agents_used.append(agent_name)
                                    if hasattr(part, 'text') and part.text:
                                        response_text = part.text
                    
                    for event in response:
                        if hasattr(event, 'author') and event.author and event.author not in ['EVQ_Manager', None]:
                            if event.author not in agents_used:
                                agents_used.append(event.author)
                
                elif hasattr(response, 'content'):
                    content = response.content
                    if hasattr(content, 'parts') and content.parts:
                        for part in content.parts:
                            if hasattr(part, 'text') and part.text:
                                response_text = part.text
                
                response_text = response_text.strip()
                if not response_text:
                    response_text = "I've processed your request. Please try rephrasing your question."
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "avatar": "⚡",
                    "metadata": {"agents_used": agents_used}
                })
                message_placeholder.markdown(response_text)
                
            except Exception as e:
                status_placeholder.empty()
                error_msg = f"❌ **Error:** {str(e)}"
                message_placeholder.markdown(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "avatar": "⚡"
                })

# ==================== AGENTS PAGE ====================
elif current_page == "Agents":
    st.markdown('<h1 class="main-header">🤖 Agentic Architecture</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Multi-Agent System Design</p>', unsafe_allow_html=True)
    
    # Overview
    st.markdown('<h2 class="sub-header">📐 System Overview</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="content-box fade-in">
        <h3>Multi-Agent Orchestration Model</h3>
        <p style="font-size: 1.1rem; line-height: 1.8;">
            EV_Q employs a sophisticated multi-agent architecture where specialized AI agents 
            collaborate to provide comprehensive EV support. The system uses a central manager 
            agent (EVQ_Manager) that intelligently routes queries to appropriate specialist agents 
            based on the user's needs, ensuring optimal response quality and accuracy.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Architecture Diagram
    st.markdown('<h2 class="sub-header">🔄 Agent Flow Diagram</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="content-box" style="text-align: center;">
            <div class="arch-node" style="margin: 1rem auto; max-width: 300px;">
                ⚡ EVQ Manager Agent
            </div>
            <div style="font-size: 2.5rem; color: #667eea; margin: 1rem 0;">⬇️</div>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; margin: 1rem 0;">
                <div class="arch-node" style="flex: 1; margin: 0.5rem; min-width: 120px;">🔧 Technician</div>
                <div class="arch-node" style="flex: 1; margin: 0.5rem; min-width: 120px;">🚗 Reseller</div>
                <div class="arch-node" style="flex: 1; margin: 0.5rem; min-width: 120px;">💰 Financier</div>
            </div>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; margin: 1rem 0;">
                <div class="arch-node" style="flex: 1; margin: 0.5rem; min-width: 150px;">🛡️ Policy</div>
                <div class="arch-node" style="flex: 1; margin: 0.5rem; min-width: 150px;">🧠 Recommender</div>
            </div>
            <div style="font-size: 2.5rem; color: #667eea; margin: 1rem 0;">⬇️</div>
            <div class="arch-node" style="margin: 1rem auto; max-width: 300px; background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                📤 Unified Response
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Specialist Agents
    st.markdown('<h2 class="sub-header">🤖 Specialist Agents</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="agent-card">
            <h3>🔧 Technician Agent</h3>
            <p class="agent-role">Technical Support Specialist</p>
            <p><strong>Capabilities:</strong></p>
            <ul>
                <li>Battery diagnostics and health analysis</li>
                <li>Charging system troubleshooting</li>
                <li>Range optimization strategies</li>
                <li>Maintenance recommendations</li>
                <li>Technical specifications lookup</li>
            </ul>
            <p><strong>Tools:</strong> Google Search, Technical Database</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="agent-card">
            <h3>💰 Financier Agent</h3>
            <p class="agent-role">Financial Planning Expert</p>
            <p><strong>Capabilities:</strong></p>
            <ul>
                <li>EMI calculation and loan structuring</li>
                <li>Total cost of ownership analysis</li>
                <li>Subsidy and incentive information</li>
                <li>Leasing vs buying comparisons</li>
                <li>Financial product recommendations</li>
            </ul>
            <p><strong>Tools:</strong> Google Search, Loan Calculator</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="agent-card">
            <h3>🧠 Recommendation Agent</h3>
            <p class="agent-role">Personalization Specialist</p>
            <p><strong>Capabilities:</strong></p>
            <ul>
                <li>User requirement analysis</li>
                <li>Personalized EV matching</li>
                <li>Usage pattern optimization</li>
                <li>Budget-based recommendations</li>
                <li>Comparative ranking</li>
            </ul>
            <p><strong>Tools:</strong> Google Search, Inventory Lookup</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="agent-card">
            <h3>🚗 Reseller Agent</h3>
            <p class="agent-role">Sales & Inventory Specialist</p>
            <p><strong>Capabilities:</strong></p>
            <ul>
                <li>Model comparison and analysis</li>
                <li>Price and inventory tracking</li>
                <li>Resale value estimation</li>
                <li>Depreciation calculations</li>
                <li>Market trend analysis</li>
            </ul>
            <p><strong>Tools:</strong> Google Search, Inventory Lookup</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="agent-card">
            <h3>🛡️ Policy Agent</h3>
            <p class="agent-role">Legal & Compliance Advisor</p>
            <p><strong>Capabilities:</strong></p>
            <ul>
                <li>Insurance policy guidance</li>
                <li>Warranty terms explanation</li>
                <li>Government regulation updates</li>
                <li>State-specific incentives</li>
                <li>Compliance requirements</li>
            </ul>
            <p><strong>Tools:</strong> Google Search, Policy Database</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Technical Stack
    st.markdown('<h2 class="sub-header">⚙️ Technical Stack</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="content-box">
            <h4>🤖 AI Framework</h4>
            <ul>
                <li>Google ADK (Agent Development Kit)</li>
                <li>Gemini 2.5 Flash Lite</li>
                <li>Multi-agent orchestration</li>
                <li>Tool integration support</li>
                <li>Async execution</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="content-box">
            <h4>🎨 Frontend</h4>
            <ul>
                <li>Streamlit framework</li>
                <li>Custom CSS styling</li>
                <li>Responsive design</li>
                <li>Real-time chat interface</li>
                <li>Multi-page navigation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="content-box">
            <h4>🔧 Backend</h4>
            <ul>
                <li>Python 3.8+</li>
                <li>Async/await architecture</li>
                <li>In-memory state management</li>
                <li>API integration layer</li>
                <li>Error handling & retry logic</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Key Features
    st.markdown('<h2 class="sub-header">✨ Architectural Highlights</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="content-box">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem;">
            <div>
                <h4>🎯 Intelligent Routing</h4>
                <p>Manager agent analyzes queries and routes to appropriate specialists automatically</p>
            </div>
            <div>
                <h4>🔄 Parallel Processing</h4>
                <p>Multiple agents can be consulted simultaneously for complex queries</p>
            </div>
            <div>
                <h4>🌐 Web Integration</h4>
                <p>Real-time data fetching through Google Search integration</p>
            </div>
            <div>
                <h4>💾 State Management</h4>
                <p>Conversation context maintained across agent interactions</p>
            </div>
            <div>
                <h4>🛡️ Error Handling</h4>
                <p>Robust retry mechanisms and graceful fallback strategies</p>
            </div>
            <div>
                <h4>📊 Response Synthesis</h4>
                <p>Manager combines specialist outputs into coherent responses</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==================== ABOUT PAGE ====================
elif current_page == "About":
    st.markdown('<h1 class="main-header">📝 About EV_Q</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Your Intelligent EV Companion</p>', unsafe_allow_html=True)
    
    # Mission
    st.markdown('<h2 class="sub-header">🎯 Our Mission</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="content-box fade-in">
        <h3>Democratizing Electric Vehicle Knowledge</h3>
        <p style="font-size: 1.15rem; line-height: 1.8;">
            EV_Q was created to make electric vehicle ownership accessible and understandable for everyone. 
            We believe that the transition to electric mobility should be smooth, informed, and supported by 
            intelligent technology that understands your unique needs.
        </p>
        <p style="font-size: 1.15rem; line-height: 1.8;">
            By combining cutting-edge AI technology with specialized domain expertise, we've created a system 
            that can answer virtually any question about electric vehicles - from technical diagnostics to 
            financial planning, from policy guidance to personalized recommendations.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # What We Offer
    st.markdown('<h2 class="sub-header">🚀 What We Offer</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="content-box">
            <h3>🔧 Technical Expertise</h3>
            <p>Get instant help with battery issues, charging problems, range anxiety, and maintenance 
            questions. Our technical agent provides step-by-step troubleshooting and expert advice.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="content-box">
            <h3>💰 Financial Clarity</h3>
            <p>Understand the true cost of EV ownership with detailed EMI calculations, subsidy information, 
            and comprehensive total cost of ownership analysis.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="content-box">
            <h3>🧠 Smart Recommendations</h3>
            <p>Find the perfect EV for your lifestyle with personalized recommendations based on your budget, 
            usage patterns, and preferences.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="content-box">
            <h3>🚗 Market Intelligence</h3>
            <p>Compare models, check pricing, track inventory, and get accurate resale value estimates 
            to make informed purchase decisions.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="content-box">
            <h3>🛡️ Policy Guidance</h3>
            <p>Navigate the complex world of EV policies, insurance, warranties, and government incentives 
            with expert guidance.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="content-box">
            <h3>🌐 Real-time Data</h3>
            <p>Access the latest information with our web search integration, ensuring you always get 
            current and accurate answers.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Technology
    st.markdown('<h2 class="sub-header">💡 The Technology</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="content-box">
        <h3>Powered by Advanced AI</h3>
        <p style="font-size: 1.15rem; line-height: 1.8;">
            EV_Q leverages Google's Gemini 2.5 Flash Lite model through a sophisticated multi-agent architecture. 
            Each specialist agent is trained with specific domain knowledge and equipped with powerful tools to 
            provide accurate, contextual responses.
        </p>
        <br>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem;">
            <div style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 3rem;">🤖</div>
                <strong style="font-size: 1.1rem;">5 Specialist Agents</strong>
                <p>Each expert in their domain</p>
            </div>
            <div style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 3rem;">⚡</div>
                <strong style="font-size: 1.1rem;">Lightning Fast</strong>
                <p>Gemini 2.5 Flash Lite</p>
            </div>
            <div style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 3rem;">🌐</div>
                <strong style="font-size: 1.1rem;">Web Connected</strong>
                <p>Real-time information</p>
            </div>
            <div style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 3rem;">🎯</div>
                <strong style="font-size: 1.1rem;">Context Aware</strong>
                <p>Understands your needs</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Use Cases
    st.markdown('<h2 class="sub-header">📋 Who Can Benefit?</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔰</div>
            <h3>First-time Buyers</h3>
            <p>Understand EV basics, compare models, and make confident decisions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">👤</div>
            <h3>Current Owners</h3>
            <p>Get technical support, maintenance tips, and optimization advice</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💼</div>
            <h3>Fleet Managers</h3>
            <p>Analyze costs, plan financing, and manage multiple vehicles</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Version Info
    st.markdown('<h2 class="sub-header">📦 Version Information</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="content-box">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
            <div><strong>Version:</strong> 2.0.0</div>
            <div><strong>Release Date:</strong> November 2025</div>
            <div><strong>Model:</strong> Gemini 2.5 Flash Lite</div>
            <div><strong>Framework:</strong> Streamlit + Google ADK</div>
        </div>
        <h4>Recent Updates:</h4>
        <ul>
            <li>✨ Multi-page interface with enhanced navigation</li>
            <li>🎨 Modern gradient-based UI design with animations</li>
            <li>🤖 Improved agent coordination and response synthesis</li>
            <li>📊 Real-time statistics and agent tracking</li>
            <li>🔍 Enhanced web search integration</li>
            <li>💬 Better chat history management</li>
            <li>🛡️ Robust error handling and retry mechanisms</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # CTA
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("💬 Try EV_Q Now", use_container_width=True, type="primary"):
            st.session_state.current_page = "Chatbot"
            st.rerun()

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #ffffff; padding: 2rem;'>
    <p style='font-size: 1.3rem; font-weight: 700;'>⚡ EV_Q:? - Your Electric Vehicle Expert System</p>
    <p style='font-size: 1rem; margin-top: 0.5rem; opacity: 0.95;'>
        Multi-Agent AI Architecture • Real-time Information • Personalized Assistance
    </p>
    <p style='font-size: 0.9rem; margin-top: 1rem; opacity: 0.9;'>
        Powered by Gemini 2.5 Flash Lite | Built with Streamlit & Google ADK
    </p>
    <p style='font-size: 0.85rem; margin-top: 0.5rem; opacity: 0.85;'>
        © 2025 EV_Q. Making Electric Mobility Accessible for Everyone.
    </p>
</div>
""", unsafe_allow_html=True)