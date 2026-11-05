"""Guided, accessible navigation for KRISI Social Media Studio v2."""
from datetime import date
import html
import streamlit as st

GROUPS = {
    "OVERVIEW": ["Home"],
    "CLIENTS & PLANNING": ["Brands", "Content Calendar", "Content Library", "Campaigns"],
    "PERFORMANCE & SAFETY": ["Analytics & Reports", "Moderation Coordination"],
    "SUPPORT": ["Guides & Help"],
}
GUIDES = {
    "Brands": ("Create your client workspace", "Add a fictional brand and client alias first. Every post, campaign and report belongs to a brand.", "Content Calendar"),
    "Content Calendar": ("Plan upcoming content", "Choose a brand and platform, write a draft, set its date, then track its approval status. Saving a post does not publish it.", "Content Library"),
    "Content Library": ("Organize creative work", "Save captions, hashtags and asset references. Use status updates to move drafts through approval.", "Campaigns"),
    "Campaigns": ("Coordinate campaigns", "Create a campaign with a clear goal, dates and status. Track related content in the calendar.", "Analytics & Reports"),
    "Analytics & Reports": ("Understand performance", "Record authorized platform metrics manually and export CSV reports. No live social analytics are connected.", "Moderation Coordination"),
    "Moderation Coordination": ("Track safety referrals", "Keep non-sensitive internal references and follow-up statuses here. Handle detailed reviews in your separate Trust & Safety Studio.", "Home"),
}

def navigate(page):
    st.session_state["smm_page"] = page
    st.rerun()

def sidebar():
    pages = [page for group in GROUPS.values() for page in group]
    if st.session_state.get("smm_page") not in pages:
        st.session_state["smm_page"] = "Home"
    st.sidebar.markdown("### KRISI · SMM Studio")
    st.sidebar.caption("Your creative operations workspace")
    for group, items in GROUPS.items():
        st.sidebar.markdown(f"<div class='smm-nav-group'>{group}</div>", unsafe_allow_html=True)
        for page in items:
            active = st.session_state["smm_page"] == page
            label = ("◆ " if active else "◇ ") + page
            if st.sidebar.button(label, key="nav_" + page, use_container_width=True, type="primary" if active else "secondary"):
                navigate(page)
    st.sidebar.divider()
    st.sidebar.caption("Local prototype · Manual planning and reporting · No automatic publishing")
    return st.session_state["smm_page"]

def guide(page):
    if page not in GUIDES:
        return
    title, description, next_page = GUIDES[page]
    with st.expander("✦ How to use this section", expanded=False):
        st.markdown(f"**{title}**")
        st.write(description)
        if st.button("Continue to " + next_page, key="guide_" + page):
            navigate(next_page)

def home(rows):
    st.header("Your workspace")
    st.caption("A clear starting point for today's client and content work.")
    tables = ["brands", "posts", "campaigns", "referrals"]
    counts = [rows(f"SELECT COUNT(*) AS n FROM {t}")[0]["n"] for t in tables]
    cols = st.columns(4)
    for col, label, value in zip(cols, ["Brands", "Content items", "Campaigns", "Safety referrals"], counts):
        col.metric(label, value)
    st.subheader("Continue working")
    if counts[0] == 0:
        target, message = "Brands", "Start by creating your first fictional client brand."
    elif counts[1] == 0:
        target, message = "Content Calendar", "Your brand is ready. Plan your first content draft."
    else:
        target, message = "Content Calendar", "Review upcoming content and update approval statuses."
    st.info(message)
    if st.button("Go to " + target, key="home_next", type="primary"):
        navigate(target)
    st.subheader("Upcoming content")
    upcoming = rows("""SELECT b.name AS brand,p.platform,p.publish_date,p.caption,p.status
                       FROM posts p JOIN brands b ON b.id=p.brand_id
                       WHERE p.publish_date>=? ORDER BY p.publish_date LIMIT 12""", (date.today().isoformat(),))
    if upcoming:
        st.dataframe(upcoming, use_container_width=True, hide_index=True)
    else:
        st.caption("No upcoming posts yet. Create a draft in Content Calendar.")
    st.subheader("Quick actions")
    cols = st.columns(3)
    for col, label, target in zip(cols, ["Plan content", "Manage clients", "View reports"], ["Content Calendar", "Brands", "Analytics & Reports"]):
        with col:
            if st.button(label, key="quick_" + target, use_container_width=True):
                navigate(target)
    with st.expander("Your SMM workflow"):
        st.markdown("**1. Brands** → **2. Content Calendar** → **3. Content Library & approval** → **4. Campaigns** → **5. Analytics & Reports**")
        st.caption("Moderation Coordination supports the workflow with manual, non-sensitive referrals.")

def help_page():
    st.header("Guides & Help")
    st.write("Use this guide to understand each part of your Studio.")
    for page, (title, description, next_page) in GUIDES.items():
        with st.expander(page):
            st.markdown(f"**{title}**")
            st.write(description)
            if st.button("Open " + page, key="help_" + page):
                navigate(page)
    st.warning("This version is a local fictional-data prototype. It does not publish, fetch messages, or sync analytics from social networks.")
