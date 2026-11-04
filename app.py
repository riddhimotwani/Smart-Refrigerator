import streamlit as st
from datetime import date, timedelta
import pandas as pd
import os, hashlib
from pathlib import Path
from PIL import Image
from io import BytesIO
from swiggy_instamart import get_addresses, search_products, update_cart, get_cart, checkout, logout

# ============================================================
# SMART REFRIGERATOR
# AI-Powered Food Inventory Management System
# ============================================================

st.set_page_config(
    page_title="Smart Refrigerator",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

/* ============================================================
   SMART REFRIGERATOR - PREMIUM ICE THEME
   ============================================================ */

/* Main application background */
.stApp {
    background: linear-gradient(
        135deg,
        #f4f9fc 0%,
        #eef7f8 50%,
        #f7fbfc 100%
    );
}

/* Main content */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

/* ============================================================
   SIDEBAR
   ============================================================ */

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #eaf7fa 0%,
        #f7fbfc 100%
    );

    border-right: 1px solid #d5e9ed;
}

[data-testid="stSidebar"] h1 {
    color: #087f8c;
}

[data-testid="stSidebar"] h2 {
    color: #164e63;
}

/* ============================================================
   TITLES
   ============================================================ */

.main-title {
    font-size: 42px;
    font-weight: 800;
    color: #123b4a;
    margin-bottom: 0px;
    letter-spacing: -1px;
}

.subtitle {
    color: #5f7c87;
    font-size: 17px;
    margin-bottom: 30px;
}

/* ============================================================
   SECTION HEADERS
   ============================================================ */

.section-title {
    font-size: 24px;
    font-weight: 750;
    color: #164e63;
    margin-top: 28px;
    margin-bottom: 15px;
}

/* ============================================================
   METRIC CARDS
   ============================================================ */

.metric-card {
    background: rgba(255,255,255,0.92);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #d8ebef;
    box-shadow: 0px 6px 20px rgba(19, 78, 92, 0.07);
    min-height: 130px;
    transition: all 0.2s ease;
}

.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0px 10px 25px rgba(19, 78, 92, 0.12);
}

.metric-icon {
    font-size: 28px;
}

.metric-title {
    color: #66828b;
    font-size: 14px;
    margin-top: 8px;
}

.metric-value {
    color: #164e63;
    font-size: 30px;
    font-weight: 800;
    margin-top: 3px;
}

/* ============================================================
   ALERT CARDS
   ============================================================ */

.alert-card {
    background: rgba(255,255,255,0.94);
    border-radius: 15px;
    padding: 17px;
    margin-bottom: 12px;
    border: 1px solid #dcebed;
    box-shadow: 0px 4px 14px rgba(19, 78, 92, 0.05);
}

.alert-red {
    border-left: 5px solid #ef4444;
}

.alert-orange {
    border-left: 5px solid #f59e0b;
}

.alert-green {
    border-left: 5px solid #10b981;
}

/* ============================================================
   RECIPE CARDS
   ============================================================ */

.recipe-card {
    background: rgba(255,255,255,0.96);
    padding: 24px;
    border-radius: 18px;
    border: 1px solid #d8ebef;
    min-height: 180px;
    box-shadow: 0px 6px 20px rgba(19, 78, 92, 0.07);
    margin-bottom: 10px;
}

.recipe-name {
    font-size: 21px;
    font-weight: 800;
    color: #164e63;
    margin-bottom: 12px;
}

.recipe-match {
    display: inline-block;
    background: #e8f8f2;
    color: #087f5b;
    padding: 6px 11px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 16px;
}

.recipe-ingredients {
    color: #667f88;
    font-size: 14px;
    line-height: 1.7;
}

.recipe-ingredients b {
    color: #164e63;
}
/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {
    border-radius: 10px;
    border: none;
    font-weight: 650;
    transition: all 0.2s ease;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(
        90deg,
        #0f9fae,
        #087f8c
    );
    color: white;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0px 5px 15px rgba(8, 127, 140, 0.2);
}

/* ============================================================
   FILE UPLOADER
   ============================================================ */

[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.75);
    border-radius: 16px;
    padding: 8px;
}

/* ============================================================
   DATAFRAME
   ============================================================ */

[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
}

/* ============================================================
   INFO / SUCCESS BOXES
   ============================================================ */

.stAlert {
    border-radius: 14px;
}

/* ============================================================
   DIVIDERS
   ============================================================ */

hr {
    border-color: #d8ebef;
}

/* ============================================================
   FOOTER
   ============================================================ */

.footer-text {
    color: #78909a;
    text-align: center;
    font-size: 13px;
}



.swiggy-card {
    background: rgba(255,255,255,0.96);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #d8ebef;
    box-shadow: 0px 6px 20px rgba(19, 78, 92, 0.07);
    margin-bottom: 14px;
}

.swiggy-badge {
    display: inline-block;
    background: #e8f8f2;
    color: #087f5b;
    padding: 6px 11px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 700;
}



/* ============================================================
   DIET PLANNER
   ============================================================ */
.diet-hero { background: linear-gradient(135deg, rgba(255,255,255,.97), rgba(235,248,249,.95)); border:1px solid #d8ebef; border-radius:22px; padding:28px 30px; box-shadow:0 8px 24px rgba(19,78,92,.07); margin-bottom:24px; }
.diet-card { background:rgba(255,255,255,.96); border:1px solid #d8ebef; border-radius:18px; padding:22px; box-shadow:0 6px 20px rgba(19,78,92,.06); height:100%; }
.diet-card-title { color:#164e63; font-size:20px; font-weight:800; margin-bottom:8px; }
.diet-muted { color:#66828b; font-size:14px; }
.diet-label { color:#66828b; font-size:13px; margin-top:2px; }
.meal-card { background:#fff; border:1px solid #d8ebef; border-radius:18px; padding:20px; margin-bottom:14px; box-shadow:0 5px 16px rgba(19,78,92,.05); }
.meal-name { color:#164e63; font-size:20px; font-weight:800; }
.meal-meta { color:#66828b; font-size:14px; margin-top:6px; }
.meal-ok { color:#087f5b; background:#e8f8f2; padding:6px 10px; border-radius:14px; font-weight:700; display:inline-block; margin-top:10px; }
.meal-missing { color:#9a6b00; background:#fff7d9; padding:6px 10px; border-radius:14px; font-weight:700; display:inline-block; margin-top:10px; }
.profile-note { color:#5f7c87; font-size:13px; line-height:1.6; }

</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================

if "inventory" not in st.session_state:

    st.session_state.inventory = [
        {
            "Food": "🍎 Apple",
            "Quantity": 4,
            "Unit": "pcs",
            "Status": "Available",
            "Expiry": date.today() + timedelta(days=6)
        },
        {
            "Food": "🍌 Banana",
            "Quantity": 3,
            "Unit": "pcs",
            "Status": "Available",
            "Expiry": date.today() + timedelta(days=4)
        },
        {
            "Food": "🍊 Orange",
            "Quantity": 3,
            "Unit": "pcs",
            "Status": "Available",
            "Expiry": date.today() + timedelta(days=7)
        },
        {
            "Food": "🍅 Tomato",
            "Quantity": 5,
            "Unit": "pcs",
            "Status": "Available",
            "Expiry": date.today() + timedelta(days=5)
        },
        {
            "Food": "🥔 Potato",
            "Quantity": 2,
            "Unit": "pcs",
            "Status": "Available",
            "Expiry": date.today() + timedelta(days=14)
        },
        {
            "Food": "🧅 Onion",
            "Quantity": 2,
            "Unit": "pcs",
            "Status": "Available",
            "Expiry": date.today() + timedelta(days=12)
        },
        {
            "Food": "🥒 Cucumber",
            "Quantity": 2,
            "Unit": "pcs",
            "Status": "Available",
            "Expiry": date.today() + timedelta(days=3)
        },
        {
            "Food": "🥕 Carrot",
            "Quantity": 4,
            "Unit": "pcs",
            "Status": "Available",
            "Expiry": date.today() + timedelta(days=8)
        },
        {
            "Food": "🥚 Eggs",
            "Quantity": 6,
            "Unit": "pcs",
            "Status": "Available",
            "Expiry": date.today() + timedelta(days=10)
        },
        {
            "Food": "🥛 Milk",
            "Quantity": 1,
            "Unit": "L",
            "Status": "Low Stock",
            "Expiry": date.today() + timedelta(days=2)
        },
        {
            "Food": "🧀 Cheese",
            "Quantity": 1,
            "Unit": "pack",
            "Status": "Available",
            "Expiry": date.today() + timedelta(days=15)
        },
        {
            "Food": "🥦 Broccoli",
            "Quantity": 1,
            "Unit": "pcs",
            "Status": "Expiring Soon",
            "Expiry": date.today() + timedelta(days=1)
        },
    ]


# ============================================================
# SWIGGY SESSION STATE
# ============================================================

for _key, _default in {
    "swiggy_connected": False,
    "swiggy_addresses": [],
    "swiggy_selected_address": None,
    "swiggy_products": [],
    "swiggy_cart": None,
    "swiggy_order": None,
    "swiggy_search_query": "milk",
}.items():
    if _key not in st.session_state:
        st.session_state[_key] = _default

for _key, _default in {
    "last_scan_hash": None, "last_scan_model": None,
    "last_scan_count": 0, "last_annotated_image": None
}.items():
    if _key not in st.session_state:
        st.session_state[_key] = _default

# Diet planner profile state
for _key, _default in {
    "diet_profile": None,
}.items():
    if _key not in st.session_state:
        st.session_state[_key] = _default


# ============================================================
# DIET PLANNER ENGINE
# ============================================================

FOOD_ALIASES = {
    "apple": "apple", "banana": "banana", "orange": "orange",
    "tomato": "tomato", "potato": "potato", "onion": "onion",
    "cucumber": "cucumber", "carrot": "carrot", "eggs": "egg",
    "egg": "egg", "milk": "milk", "cheese": "cheese",
    "broccoli": "broccoli", "bell pepper": "bell_pepper", "bell_pepper": "bell_pepper", "mushroom": "mushroom", "bread": "bread", "rice": "rice",
    "chicken": "chicken", "paneer": "paneer", "yogurt": "yogurt",
    "curd": "yogurt", "chickpeas": "chickpeas", "chana": "chickpeas",
}

DIET_RECIPES = [
    {"name":"🍳 Vegetable Omelette", "ingredients":["egg","tomato","onion","cheese"], "kcal":320, "protein":20, "diet":["Eggetarian","Non-vegetarian"], "meal":"Breakfast", "time":"15 min", "tip":"High-protein breakfast using refrigerator staples."},
    {"name":"🥔 Potato Egg Breakfast", "ingredients":["potato","egg","onion"], "kcal":330, "protein":15, "diet":["Eggetarian","Non-vegetarian"], "meal":"Breakfast", "time":"20 min", "tip":"A filling breakfast with potatoes and eggs."},
    {"name":"🥗 Chickpea Salad", "ingredients":["chickpeas","cucumber","tomato","onion"], "kcal":330, "protein":15, "diet":["Vegetarian","Vegan","Eggetarian","Non-vegetarian"], "meal":"Lunch", "time":"10 min", "tip":"Fiber-rich option with plant protein."},
    {"name":"🥦 Paneer Veggie Bowl", "ingredients":["paneer","broccoli","carrot","tomato"], "kcal":420, "protein":25, "diet":["Vegetarian","Eggetarian","Non-vegetarian"], "meal":"Lunch", "time":"25 min", "tip":"Protein-focused vegetarian bowl."},
    {"name":"🍗 Chicken Veggie Bowl", "ingredients":["chicken","rice","broccoli","carrot"], "kcal":520, "protein":40, "diet":["Non-vegetarian"], "meal":"Lunch", "time":"30 min", "tip":"High-protein meal for active goals."},
    {"name":"🥪 Cheese Veggie Sandwich", "ingredients":["bread","cheese","tomato","cucumber"], "kcal":360, "protein":14, "diet":["Vegetarian","Eggetarian","Non-vegetarian"], "meal":"Snack", "time":"10 min", "tip":"Quick snack when you want something light."},
    {"name":"🥛 Banana Milk Smoothie", "ingredients":["banana","milk"], "kcal":220, "protein":8, "diet":["Vegetarian","Eggetarian","Non-vegetarian"], "meal":"Snack", "time":"5 min", "tip":"Simple energy-rich snack."},
    {"name":"🍎 Apple Yogurt Bowl", "ingredients":["apple","yogurt","banana"], "kcal":240, "protein":12, "diet":["Vegetarian","Eggetarian","Non-vegetarian"], "meal":"Snack", "time":"5 min", "tip":"Fruit and yogurt combination for a quick snack."},
    {"name":"🥦 Broccoli Cheese Bowl", "ingredients":["broccoli","cheese","milk"], "kcal":280, "protein":14, "diet":["Vegetarian","Eggetarian","Non-vegetarian"], "meal":"Dinner", "time":"20 min", "tip":"Vegetable-forward dinner option."},
    {"name":"🥗 Fresh Veggie Bowl", "ingredients":["cucumber","carrot","tomato","onion"], "kcal":180, "protein":5, "diet":["Vegetarian","Vegan","Eggetarian","Non-vegetarian"], "meal":"Dinner", "time":"10 min", "tip":"Light vegetable-based meal."},
]

ACTIVITY_FACTORS = {
    "Sedentary": 1.20,
    "Lightly Active": 1.375,
    "Moderately Active": 1.55,
    "Very Active": 1.725,
    "Extremely Active": 1.90,
}

def calculate_targets(age, sex, height_cm, weight_kg, activity, goal):
    if sex == "Male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    maintenance = bmr * ACTIVITY_FACTORS[activity]
    if goal == "Lose Weight":
        calories = maintenance * 0.85
        protein_factor = 1.2
    elif goal == "Gain Weight":
        calories = maintenance * 1.10
        protein_factor = 1.2
    elif goal == "Build Muscle":
        calories = maintenance * 1.05
        protein_factor = 1.6
    else:
        calories = maintenance
        protein_factor = 0.8
    protein = weight_kg * protein_factor
    return round(bmr), round(maintenance), round(calories), round(protein)

def get_inventory_keys():
    keys = set()
    for item in st.session_state.inventory:
        raw = item["Food"].lower()
        for emoji in ["🍎","🍌","🍊","🍅","🥔","🧅","🥒","🥕","🥚","🥛","🧀","🥦"]:
            raw = raw.replace(emoji, "")
        raw = raw.strip()
        if raw in FOOD_ALIASES:
            keys.add(FOOD_ALIASES[raw])
    return keys

def render_diet_planner():
    st.markdown('<div class="main-title">🍽️ Diet Planner</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Personalized calorie targets, protein goals and meals from your refrigerator</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="diet-hero">
        <div style="font-size:14px;color:#087f8c;font-weight:800;letter-spacing:.8px;">SMART NUTRITION ENGINE</div>
        <div style="font-size:29px;color:#164e63;font-weight:800;margin-top:5px;">Eat smarter with what you already have.</div>
        <div class="diet-muted" style="margin-top:8px;">Set your profile once and the planner estimates your daily energy and protein needs, then ranks meals using your refrigerator inventory.</div>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([1.05, 1.45])
    with left:
        st.markdown('<div class="diet-card"><div class="diet-card-title">👤 Your Profile</div><div class="profile-note">These inputs are used only for the current planner session. Results are estimates, not medical advice.</div></div>', unsafe_allow_html=True)
        age = st.number_input("Age", min_value=13, max_value=100, value=21, step=1)
        sex = st.selectbox("Sex", ["Female", "Male"])
        height = st.number_input("Height (cm)", min_value=100.0, max_value=230.0, value=165.0, step=1.0)
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=250.0, value=65.0, step=0.5)
        activity = st.selectbox("Activity level", list(ACTIVITY_FACTORS.keys()), index=2)
        goal = st.selectbox("Goal", ["Maintain Weight", "Lose Weight", "Gain Weight", "Build Muscle"])
        diet = st.selectbox("Diet preference", ["Vegetarian", "Eggetarian", "Non-vegetarian", "Vegan"])
        if st.button("✨ Generate My Plan", type="primary", use_container_width=True):
            st.session_state.diet_profile = {"age":age,"sex":sex,"height":height,"weight":weight,"activity":activity,"goal":goal,"diet":diet}

    profile = st.session_state.diet_profile
    if not profile:
        st.info("Enter your profile and click **Generate My Plan** to calculate your targets and personalize meals.")
        return

    bmr, maintenance, target_calories, target_protein = calculate_targets(profile["age"], profile["sex"], profile["height"], profile["weight"], profile["activity"], profile["goal"])

    with right:
        st.markdown('<div class="diet-card"><div class="diet-card-title">🎯 Your Daily Targets</div><div class="diet-muted">Estimated from your profile using the Mifflin–St Jeor equation and activity multiplier.</div></div>', unsafe_allow_html=True)
        m1,m2,m3,m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-card"><div class="metric-icon">🔥</div><div class="metric-title">Daily Calories</div><div class="metric-value">{target_calories}</div><div class="diet-label">kcal/day</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><div class="metric-icon">💪</div><div class="metric-title">Protein Goal</div><div class="metric-value">{target_protein}g</div><div class="diet-label">per day</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-card"><div class="metric-icon">⚡</div><div class="metric-title">BMR</div><div class="metric-value">{bmr}</div><div class="diet-label">kcal/day</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-card"><div class="metric-icon">⚖️</div><div class="metric-title">Maintenance</div><div class="metric-value">{maintenance}</div><div class="diet-label">kcal/day</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">🥗 What Can I Make Today?</div>', unsafe_allow_html=True)
    inventory_keys = get_inventory_keys()
    matching = []
    for recipe in DIET_RECIPES:
        if profile["diet"] not in recipe["diet"]:
            continue
        available = [x for x in recipe["ingredients"] if x in inventory_keys]
        missing = [x for x in recipe["ingredients"] if x not in inventory_keys]
        match_pct = round(len(available) / len(recipe["ingredients"]) * 100)
        matching.append((match_pct, recipe, available, missing))
    matching.sort(key=lambda x: (len(x[3]) == 0, x[0], x[1]["protein"]), reverse=True)

    if not matching:
        st.warning("No recipes match the selected diet preference yet.")
    else:
        cols = st.columns(2)
        for idx, (match_pct, recipe, available, missing) in enumerate(matching[:6]):
            with cols[idx % 2]:
                status_html = f'<span class="meal-ok">✓ {match_pct}% ingredients available</span>' if not missing else f'<span class="meal-missing">⚠ Missing: {", ".join(missing)}</span>'
                st.markdown(f"""
                <div class="meal-card">
                    <div class="meal-name">{recipe["name"]}</div>
                    <div class="meal-meta">{recipe["meal"]} • {recipe["time"]} • <b>{recipe["kcal"]} kcal</b> • <b>{recipe["protein"]}g protein</b></div>
                    <div class="diet-muted" style="margin-top:10px;">{recipe["tip"]}</div>
                    {status_html}
                </div>
                """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">📅 Suggested Daily Plan</div>', unsafe_allow_html=True)
    full_available = [x for x in matching if not x[3]]
    if not full_available:
        full_available = matching
    plan = []
    for meal_type in ["Breakfast", "Lunch", "Snack", "Dinner"]:
        choices = [x for x in full_available if x[1]["meal"] == meal_type]
        if not choices:
            choices = [x for x in matching if x[1]["meal"] == meal_type]
        if choices:
            plan.append((meal_type, choices[0][1]))
    if plan:
        total_kcal = sum(r[1]["kcal"] for r in plan)
        total_protein = sum(r[1]["protein"] for r in plan)
        p1,p2 = st.columns(2)
        with p1:
            st.markdown(f'<div class="metric-card"><div class="metric-icon">🔥</div><div class="metric-title">Planned Calories</div><div class="metric-value">{total_kcal}</div><div class="diet-label">target {target_calories} kcal</div></div>', unsafe_allow_html=True)
        with p2:
            st.markdown(f'<div class="metric-card"><div class="metric-icon">💪</div><div class="metric-title">Planned Protein</div><div class="metric-value">{total_protein}g</div><div class="diet-label">target {target_protein}g</div></div>', unsafe_allow_html=True)
        for meal_type, recipe in plan:
            st.markdown(f'**{meal_type}:** {recipe["name"]} — {recipe["kcal"]} kcal • {recipe["protein"]}g protein')
        if total_kcal < target_calories * 0.8:
            st.info("Your selected refrigerator-based plan is below your estimated calorie target. Add another balanced meal/snack or adjust the profile if this does not reflect your normal eating pattern.")
        elif total_kcal > target_calories * 1.1:
            st.info("This refrigerator-based plan is above your estimated calorie target. Consider smaller portions or a lighter meal if your goal is weight maintenance/loss.")

    st.markdown('<div class="section-title">🧠 How Your Target Was Calculated</div>', unsafe_allow_html=True)
    st.info(f"Estimated BMR: **{bmr} kcal/day** → activity-adjusted maintenance: **{maintenance} kcal/day** → goal-adjusted target: **{target_calories} kcal/day**. Protein target: **{target_protein} g/day**. These are general estimates and should not replace individualized advice from a qualified clinician or dietitian.")


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("# 🧊")
    st.markdown("## Smart Refrigerator")
    st.caption("AI-Powered Food Management")

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "📦 Inventory",
            "🍳 Recipes",
            "🍽️ Diet Planner",
            "⚙️ Settings"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("### System Status")

    st.success("● AI System Online")

    st.caption("YOLO Food Detection")
    st.caption("Inventory Engine Active")
    st.caption("Recipe Engine Active")

    st.divider()

    st.caption("Smart Refrigerator v1.0")
    st.caption("Academic Project")


# ============================================================
# LIVE SWIGGY INSTAMART REORDERING
# ============================================================

def render_swiggy_reordering():

    st.markdown(
        '<div class="section-title">🛒 Smart Grocery Reordering</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="swiggy-card">'
        '<span class="swiggy-badge">LIVE SWIGGY INSTAMART</span>'
        '<h3 style="color:#164e63;margin-bottom:6px;">Shop groceries directly from Instamart</h3>'
        '<p style="color:#66828b;margin-bottom:0;">Open the official Swiggy Instamart dashboard to browse groceries, search products, manage your cart and place your order.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("### 🛍️ Swiggy Instamart")
    st.write("Click below to open the real Swiggy Instamart dashboard in a new browser tab.")

    link_html = (
        '<a href="https://www.swiggy.com/instamart" target="_blank" rel="noopener noreferrer" style="text-decoration:none;">'
        '<div style="background:linear-gradient(135deg,#ff5a36,#ff7a45);color:white;padding:18px 24px;border-radius:14px;text-align:center;font-size:20px;font-weight:800;box-shadow:0 6px 18px rgba(255,90,54,0.20);margin:12px 0 20px 0;">'
        '🛒 Open Swiggy Instamart →'
        '</div></a>'
    )
    st.markdown(link_html, unsafe_allow_html=True)

    st.info("💡 The official Instamart website will open in a new tab. You can log in there and use the normal Instamart dashboard, including search, categories and cart.")




# YOLO detection and inventory refresh helpers
FOOD_EMOJIS = {
    "apple":"🍎","banana":"🍌","orange":"🍊","tomato":"🍅","potato":"🥔",
    "onion":"🧅","cucumber":"🥒","carrot":"🥕","egg":"🥚","eggs":"🥚",
    "milk":"🥛","cheese":"🧀","broccoli":"🥦","bell_pepper":"🫑",
    "bell pepper":"🫑","mushroom":"🍄"
}

def find_yolo_model():
    override = os.getenv("SMART_FRIDGE_MODEL")
    if override and Path(override).is_file():
        return Path(override)
    candidates = list(Path(".").glob("runs/detect/**/weights/best.pt"))
    candidates += [Path("best.pt"), Path("fridge_best.pt")]
    candidates = [p for p in candidates if p.is_file()]
    return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None

@st.cache_resource(show_spinner="Loading food detection model...")
def load_food_model(path):
    from ultralytics import YOLO
    return YOLO(str(path))

def run_food_detection(image_bytes, confidence=0.25):
    path = find_yolo_model()
    if path is None:
        raise FileNotFoundError("Custom model best.pt not found. Put it in runs/detect/<training-folder>/weights/best.pt.")
    model = load_food_model(str(path))
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    result = model.predict(source=image, conf=confidence, verbose=False)[0]
    counts, scores_by_class = {}, {}
    if result.boxes is not None:
        for class_id, score in zip(result.boxes.cls.cpu().numpy().astype(int), result.boxes.conf.cpu().numpy()):
            label = str(result.names[int(class_id)]).strip().lower().replace("-", "_")
            counts[label] = counts.get(label, 0) + 1
            scores_by_class.setdefault(label, []).append(float(score))
    return counts, scores_by_class, result.plot(), str(path)

def inventory_from_detections(counts):
    today = date.today()
    rows = []
    for label, quantity in sorted(counts.items()):
        display = label.replace("_", " ").title()
        rows.append({
            "Food": f"{FOOD_EMOJIS.get(label, '🍽️')} {display}",
            "Quantity": int(quantity), "Unit": "pcs",
            "Status": "Low Stock" if quantity <= 1 else "Available",
            "Expiry": today + timedelta(days=7)
        })
    return rows

def dynamic_recipe_match(ingredients):
    present = set()
    for item in st.session_state.inventory:
        name = item["Food"].lower()
        for emoji in FOOD_EMOJIS.values():
            name = name.replace(emoji, "")
        name = name.strip()
        present.add("egg" if name == "eggs" else name)
    matched = [x for x in ingredients if ("egg" if x == "eggs" else x) in present]
    missing = [x for x in ingredients if x not in matched]
    pct = round(100 * len(matched) / len(ingredients)) if ingredients else 0
    return pct, matched, missing


# Recipes are ranked against the current virtual inventory.
# Only recipes with at least 50% of required ingredients available are shown.
RECIPE_CATALOG = [
    {"name":"🍊 Fresh Orange Juice","items":["orange"],"link":"https://www.youtube.com/results?search_query=fresh+orange+juice+recipe","time":"5 min"},
    {"name":"🍊 Orange & Apple Fruit Bowl","items":["orange","apple"],"link":"https://www.youtube.com/results?search_query=orange+apple+fruit+salad","time":"10 min"},
    {"name":"🍎 Apple Banana Fruit Bowl","items":["apple","banana"],"link":"https://www.youtube.com/results?search_query=apple+banana+fruit+bowl","time":"10 min"},
    {"name":"🍌 Banana Orange Smoothie","items":["banana","orange","milk"],"link":"https://www.youtube.com/results?search_query=banana+orange+smoothie","time":"5 min"},
    {"name":"🥗 Cucumber Tomato Salad","items":["cucumber","tomato","onion"],"link":"https://www.youtube.com/results?search_query=cucumber+tomato+salad","time":"10 min"},
    {"name":"🥕 Carrot Cucumber Salad","items":["carrot","cucumber","tomato"],"link":"https://www.youtube.com/results?search_query=carrot+cucumber+salad","time":"10 min"},
    {"name":"🍳 Tomato Onion Omelette","items":["egg","tomato","onion"],"link":"https://www.youtube.com/results?search_query=tomato+onion+omelette","time":"12 min"},
    {"name":"🥔 Potato Onion Hash","items":["potato","onion"],"link":"https://www.youtube.com/results?search_query=potato+onion+hash","time":"20 min"},
    {"name":"🥦 Broccoli Carrot Stir Fry","items":["broccoli","carrot","onion"],"link":"https://www.youtube.com/results?search_query=broccoli+carrot+stir+fry","time":"15 min"},
    {"name":"🫑 Bell Pepper Tomato Sauté","items":["bell_pepper","tomato","onion"],"link":"https://www.youtube.com/results?search_query=bell+pepper+tomato+saute","time":"15 min"},
    {"name":"🍄 Mushroom & Cheese Sauté","items":["mushroom","cheese","onion"],"link":"https://www.youtube.com/results?search_query=mushroom+cheese+saute","time":"15 min"},
    {"name":"🥛 Creamy Broccoli Soup","items":["broccoli","milk","onion"],"link":"https://www.youtube.com/results?search_query=creamy+broccoli+soup","time":"25 min"},
]

def get_recommended_recipes(min_match=50):
    recommendations = []
    for recipe in RECIPE_CATALOG:
        pct, available, missing = dynamic_recipe_match(recipe["items"])
        if pct >= min_match:
            recommendations.append({
                **recipe,
                "match_pct": pct,
                "available": available,
                "missing": missing
            })
    recommendations.sort(
        key=lambda item: (item["match_pct"], -len(item["missing"]), item["name"]),
        reverse=True
    )
    return recommendations

# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.markdown(
    '<div class="main-title">🧊 Smart Refrigerator</div>',
    unsafe_allow_html=True
)

    st.markdown(
    '<div class="subtitle">'
    'Intelligent Food Inventory • Freshness Tracking • Smart Recipes'
    '</div>',
    unsafe_allow_html=True
)

    # --------------------------------------------------------
    # IMAGE UPLOAD
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">📸 Refrigerator Scanner</div>',
        unsafe_allow_html=True
    )

    upload_col = st.container()

    with upload_col:

        uploaded_file = st.file_uploader(
            "Upload an image of your refrigerator",
            type=["jpg", "jpeg", "png"],
            help="Upload a clear image of the refrigerator interior."
        )


        if uploaded_file:
            image_bytes = uploaded_file.getvalue()
            image_hash = hashlib.md5(image_bytes).hexdigest()
            st.image(image_bytes, caption="Uploaded Refrigerator Image", use_container_width=True)

            if st.button("🔍 Analyze Refrigerator", type="primary", use_container_width=True, key="analyze_fridge_button"):
                try:
                    with st.spinner("Running YOLO detection..."):
                        counts, score_data, annotated, model_used = run_food_detection(image_bytes)
                    if not counts:
                        st.warning("No supported food items detected. Previous inventory is unchanged. Try a clearer image.")
                    else:
                        # Replace the previous scan's inventory with the latest scan.
                        st.session_state.inventory = inventory_from_detections(counts)
                        st.session_state.last_scan_hash = image_hash
                        st.session_state.last_scan_model = model_used
                        st.session_state.last_scan_count = sum(counts.values())
                        st.session_state.last_annotated_image = annotated
                        st.session_state.last_detection_confidences = score_data
                        st.success(f"Detected {sum(counts.values())} objects across {len(counts)} categories. Inventory updated.")
                        st.rerun()
                except FileNotFoundError as exc:
                    st.error(str(exc))
                except ImportError:
                    st.error("Ultralytics is not installed. Run: pip install ultralytics")
                except Exception as exc:
                    st.error(f"Detection failed: {exc}")

            if st.session_state.get("last_scan_hash") == image_hash:
                st.caption(f"Model: {st.session_state.last_scan_model} • Detected objects: {st.session_state.last_scan_count}")
                if st.session_state.last_annotated_image is not None:
                    st.image(st.session_state.last_annotated_image, caption="YOLO Detection Results", use_container_width=True)

    # --------------------------------------------------------
    # INVENTORY METRICS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">📊 Inventory Overview</div>',
        unsafe_allow_html=True
    )

    total_items = sum(
        item["Quantity"] for item in st.session_state.inventory
    )

    low_stock = sum(
        1 for item in st.session_state.inventory
        if item["Status"] == "Low Stock"
    )

    expiring = sum(
        1 for item in st.session_state.inventory
        if item["Status"] == "Expiring Soon"
    )

    categories = len(st.session_state.inventory)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-icon">📦</div>
                <div class="metric-title">Total Items</div>
                <div class="metric-value">{total_items}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-icon">⚠️</div>
                <div class="metric-title">Low Stock</div>
                <div class="metric-value">{low_stock}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-icon">⏰</div>
                <div class="metric-title">Expiring Soon</div>
                <div class="metric-value">{expiring}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-icon">🥗</div>
                <div class="metric-title">Food Categories</div>
                <div class="metric-value">{categories}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # TWO COLUMN SECTION
    # --------------------------------------------------------

    left, right = st.columns([1.15, 0.85])

    # --------------------------------------------------------
    # ALERTS
    # --------------------------------------------------------

    with left:


        today = date.today()
        alert_items = []
        for item in st.session_state.inventory:
            days_left = (item["Expiry"] - today).days
            if item["Status"] == "Low Stock":
                alert_items.append(("alert-orange", f"🟠 {item['Food']} is low in stock", f"{item['Quantity']} {item['Unit']} detected/recorded."))
            if days_left <= 1:
                alert_items.append(("alert-red", f"🔴 {item['Food']} is expiring soon", "Consider using it soon to reduce food waste."))
            elif days_left <= 3:
                alert_items.append(("alert-orange", f"🟠 {item['Food']} expires in {days_left} days", "Consider using it in an upcoming meal."))
        if alert_items:
            for css_class, title, message in alert_items:
                st.markdown(f'<div class="alert-card {css_class}"><b>{title}</b><br><span>{message}</span></div>', unsafe_allow_html=True)
        else:
            st.success("No low-stock or upcoming-expiry alerts based on current inventory.")

    # --------------------------------------------------------
    # RECENT INVENTORY
    # --------------------------------------------------------

    with right:

        st.markdown(
            '<div class="section-title">📦 Current Inventory</div>',
            unsafe_allow_html=True
        )

        for item in st.session_state.inventory[:6]:

            status = item["Status"]

            if status == "Available":
                status_text = "🟢 Available"
            elif status == "Low Stock":
                status_text = "🟠 Low Stock"
            else:
                status_text = "🔴 Expiring"

            st.markdown(
                f"""
                <div class="alert-card">
                    <b>{item["Food"]}</b>
                    <span style="float:right;">
                        {item["Quantity"]} {item["Unit"]}
                    </span>
                    <br>
                    <small>{status_text}</small>
                </div>
                """,
                unsafe_allow_html=True
            )

    # --------------------------------------------------------
    # LIVE SWIGGY INSTAMART REORDERING
    # --------------------------------------------------------

    render_swiggy_reordering()

    # --------------------------------------------------------
    # RECIPES
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">🍳 Recommended Recipes</div>',
        unsafe_allow_html=True
    )


    recommended = get_recommended_recipes(min_match=50)

    if not recommended:
        st.info(
            "No recipes currently reach the 50% ingredient-match threshold. "
            "Add more ingredients to your virtual inventory or scan another image."
        )
    else:
        cols = st.columns(3)
        for idx, recipe in enumerate(recommended[:6]):
            with cols[idx % 3]:
                available_text = " • ".join(x.replace("_", " ").title() for x in recipe["available"])
                missing_text = " • ".join(x.replace("_", " ").title() for x in recipe["missing"]) or "None"
                st.markdown(
                    f"""<div class="recipe-card">
                    <div class="recipe-name">{recipe["name"]}</div>
                    <div class="recipe-match">✓ {recipe["match_pct"]}% ingredient match</div>
                    <div class="recipe-ingredients"><b>Available:</b> {available_text}<br>
                    <b>Missing:</b> {missing_text}<br><b>Preparation:</b> {recipe["time"]}</div>
                    </div>""",
                    unsafe_allow_html=True
                )
                st.link_button("▶ Watch Recipe", recipe["link"], use_container_width=True)


# ============================================================
# INVENTORY PAGE
# ============================================================

elif page == "📦 Inventory":

    st.markdown(
        '<div class="main-title">📦 Food Inventory</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Track quantities, availability and expiry dates'
        '</div>',
        unsafe_allow_html=True
    )

    inventory_df = pd.DataFrame(st.session_state.inventory)
    st.caption("This is the latest detected inventory snapshot. Quantities are detected object counts, not measured weight or volume.")

    inventory_df["Expiry"] = inventory_df["Expiry"].apply(
        lambda x: x.strftime("%d %b %Y")
    )

    st.dataframe(
        inventory_df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        '<div class="section-title">➕ Add Item Manually</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        food = st.text_input("Food Name")

    with col2:
        quantity = st.number_input(
            "Quantity",
            min_value=1,
            value=1
        )

    with col3:
        unit = st.selectbox(
            "Unit",
            ["pcs", "kg", "g", "L", "pack"]
        )

    with col4:
        expiry = st.date_input(
            "Expiry Date",
            value=date.today() + timedelta(days=7)
        )

    if st.button(
        "➕ Add to Inventory",
        type="primary"
    ):

        if food:

            st.session_state.inventory.append(
                {
                    "Food": f"🍽️ {food}",
                    "Quantity": quantity,
                    "Unit": unit,
                    "Status": "Available",
                    "Expiry": expiry
                }
            )

            st.success(f"{food} added to inventory.")
            st.rerun()

        else:

            st.warning("Please enter a food name.")


# ============================================================
# RECIPES PAGE
# ============================================================

elif page == "🍳 Recipes":

    st.markdown(
        '<div class="main-title">🍳 Recipe Recommendations</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Recipes generated from your available ingredients'
        '</div>',
        unsafe_allow_html=True
    )

    st.info(
        "The recommendation engine matches available refrigerator "
        "ingredients with recipe requirements."
    )


    recommended = get_recommended_recipes(min_match=50)

    st.caption("Only recipes with at least 50% of their required ingredients available in your current virtual inventory are displayed. Results update after each successful scan or inventory edit.")

    if not recommended:
        st.info(
            "No recipes meet the 50% match requirement yet. "
            "Add ingredients to your inventory to unlock more recommendations."
        )
    else:
        st.success(f"{len(recommended)} recipe(s) match at least 50% of your current inventory.")
        for i in range(0, len(recommended), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j >= len(recommended):
                    break
                recipe = recommended[i + j]
                with col:
                    available_text = ", ".join(x.replace("_", " ").title() for x in recipe["available"]) or "None"
                    missing_text = ", ".join(x.replace("_", " ").title() for x in recipe["missing"]) or "None"
                    st.markdown(
                        f"""<div class="recipe-card">
                        <div class="recipe-name">{recipe["name"]}</div>
                        <div class="recipe-match">✓ {recipe["match_pct"]}% ingredient match</div>
                        <div class="recipe-ingredients">
                            <b>Available:</b> {available_text}<br><br>
                            <b>Missing:</b> {missing_text}<br>
                            <b>Preparation:</b> {recipe["time"]}
                        </div>
                        </div>""",
                        unsafe_allow_html=True
                    )
                    st.link_button("▶ Watch Recipe", recipe["link"], use_container_width=True)


# ============================================================
# DIET PLANNER PAGE
# ============================================================

elif page == "🍽️ Diet Planner":

    render_diet_planner()


# ============================================================
# SETTINGS PAGE
# ============================================================

elif page == "⚙️ Settings":

    st.markdown(
        '<div class="main-title">⚙️ Settings</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Configure Smart Refrigerator preferences'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("### ⚠️ Inventory Alerts")

    low_stock_threshold = st.slider(
        "Low-stock threshold",
        min_value=1,
        max_value=10,
        value=2
    )

    expiry_threshold = st.slider(
        "Expiry warning period (days)",
        min_value=1,
        max_value=14,
        value=3
    )

    st.markdown("### 🤖 AI Configuration")

    st.checkbox(
        "Enable automatic food detection",
        value=True
    )

    st.checkbox(
        "Enable recipe recommendations",
        value=True
    )

    st.checkbox(
        "Enable expiry alerts",
        value=True
    )

    st.markdown("### 📊 System Information")

    st.info("""
    **Model:** YOLO11n  
    **Task:** Food Object Detection  
    **Classes:** 14  
    **Application:** Smart Refrigerator  
    **Framework:** Streamlit + Python
    """)

    st.success("System configuration saved.")


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "🧊 Smart Refrigerator • AI-Powered Food Inventory Management "
    "• Academic Project"
)