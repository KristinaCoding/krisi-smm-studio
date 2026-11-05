"""krisi.site SMM Studio v1.0 — local, fictional-data prototype."""
import csv
import io
import sqlite3
from datetime import date
from pathlib import Path

import streamlit as st
from guided_smm import sidebar, guide, home, help_page
from content_planner import render_content_planner
from social_inbox import init_inbox, render_social_inbox
from analytics_visuals import render_analytics_dashboard

DB = Path(__file__).with_name('smm_studio.db')
PLATFORMS = ['Instagram', 'Facebook', 'TikTok', 'LinkedIn', 'Pinterest', 'YouTube', 'Discord', 'Reddit', 'Twitch']


def connect():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    return c


def init_db():
    with connect() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS brands (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, client_alias TEXT NOT NULL, notes TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, brand_id INTEGER NOT NULL REFERENCES brands(id), platform TEXT NOT NULL, publish_date TEXT NOT NULL, caption TEXT NOT NULL, hashtags TEXT DEFAULT '', asset_ref TEXT DEFAULT '', status TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS campaigns (id INTEGER PRIMARY KEY, brand_id INTEGER NOT NULL REFERENCES brands(id), title TEXT NOT NULL, goal TEXT NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL, status TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS metrics (id INTEGER PRIMARY KEY, brand_id INTEGER NOT NULL REFERENCES brands(id), platform TEXT NOT NULL, period TEXT NOT NULL, impressions INTEGER NOT NULL, engagements INTEGER NOT NULL, followers INTEGER NOT NULL, notes TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS referrals (id INTEGER PRIMARY KEY, brand_id INTEGER NOT NULL REFERENCES brands(id), platform TEXT NOT NULL, reference TEXT NOT NULL, category TEXT NOT NULL, priority TEXT NOT NULL, status TEXT NOT NULL, notes TEXT DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        ''')


def rows(query, params=()):
    with connect() as c:
        return [dict(r) for r in c.execute(query, params).fetchall()]


def write(query, params):
    with connect() as c:
        c.execute(query, params)


def show_table(records, empty='No records yet.'):
    if records:
        st.dataframe(records, use_container_width=True, hide_index=True)
    else:
        st.info(empty)


def brand_choices():
    return {f"{r['name']} (#{r['id']})": r['id'] for r in rows('SELECT id,name FROM brands ORDER BY name')}


def brand_select(label='Brand'):
    choices = brand_choices()
    if not choices:
        st.warning('Create a fictional brand in Brands first.')
        st.stop()
    selected = st.selectbox(label, list(choices))
    return choices[selected]


def export_csv(records, filename):
    if not records:
        return
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=list(records[0]))
    writer.writeheader()
    writer.writerows(records)
    st.download_button('Download CSV', stream.getvalue().encode('utf-8-sig'), file_name=filename, mime='text/csv')


st.set_page_config(page_title='krisi.site SMM Studio', page_icon='📅', layout='wide')
init_db()
init_inbox(connect)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');
:root {color-scheme: dark;}
html,body,[data-testid="stAppViewContainer"],.stApp {background:#120d11!important;color:#efe4d9;}
[data-testid="stHeader"] {background:rgba(18,13,17,.88)!important;}
[data-testid="stSidebar"] {background:#1c1219!important;border-right:1px solid #6b4a45;}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {color:#e8d6c7;}
[data-testid="stSidebar"] [role="radiogroup"] label {padding:.52rem .7rem;border-radius:.3rem;}
[data-testid="stSidebar"] .smm-nav-group {color:#c9a979;font-size:.69rem;letter-spacing:.15em;font-weight:700;margin:1.25rem 0 .35rem;}
[data-testid="stSidebar"] button {text-align:left;justify-content:flex-start;}
.block-container {max-width:1420px;padding-top:2rem;padding-bottom:5rem;}
html,body,p,label,input,textarea,button {font-family:'DM Sans',sans-serif;}
h1,h2,h3,h4 {font-family:'Playfair Display',Georgia,serif!important;color:#f1e1d1!important;}
h2,h3 {margin-top:1.4rem;}
.krisi-hero {border:1px solid #826044;background:radial-gradient(ellipse at 85% 10%,#4b2236 0%,transparent 50%),linear-gradient(130deg,#27141e,#150e14);padding:clamp(1.6rem,4vw,3.5rem);margin-bottom:1.5rem;}
.krisi-eyebrow {color:#d0a975;font-size:.72rem;letter-spacing:.24em;font-weight:700;}
.krisi-hero h1 {font-size:clamp(2.3rem,5vw,4.2rem);margin:1rem 0 .7rem;line-height:1.13;}
.krisi-hero h1 em {color:#d1ac7c;font-weight:500;}
.krisi-hero p {color:#d6c1b5;font-size:1.02rem;max-width:680px;}
.krisi-hero-footer {border-top:1px solid #654637;padding-top:1rem;margin-top:2rem;display:flex;gap:1rem;justify-content:space-between;flex-wrap:wrap;color:#c9a979;font-size:.68rem;letter-spacing:.12em;}
[data-testid="stMetric"] {background:linear-gradient(135deg,#2c1924,#21141b);border:1px solid #78563e;padding:1.2rem 1.4rem;border-radius:3px;}
[data-testid="stMetricLabel"] {color:#d5b895!important;}
[data-testid="stMetricValue"] {color:#f3e6da!important;font-family:'Playfair Display',Georgia,serif;}
[data-testid="stForm"] {background:#21151c;border:1px solid #72503d;border-radius:4px;padding:1.5rem;}
[data-testid="stDataFrame"] {border:1px solid #78563e;border-radius:3px;}
div.stButton > button,div.stDownloadButton > button,div[data-testid="stFormSubmitButton"] button {background:#6a2a40;border:1px solid #c29a65;color:#fff2e4;border-radius:3px;font-weight:600;}
div.stButton > button:hover,div.stDownloadButton > button:hover,div[data-testid="stFormSubmitButton"] button:hover {background:#873950;color:white;border-color:#e3bf88;}
input,textarea {color:#f3e6dc!important;}
[data-testid="stAlert"] {border-radius:3px;}
@media(max-width:700px) {.block-container {padding-left:1rem;padding-right:1rem;}.krisi-hero-footer {flex-direction:column;}}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<div class="krisi-hero">
  <div class="krisi-eyebrow">KRISI.SITE &nbsp; / &nbsp; CREATIVE OPERATIONS</div>
  <h1>Social Media <em>Studio</em></h1>
  <p>A thoughtful workspace for brands, editorial planning, campaigns and insights.</p>
  <div class="krisi-hero-footer"><span>● LOCAL PROTOTYPE</span><span>VERSION 2.0 PREVIEW · DARK ACADEMIA</span></div>
</div>
""", unsafe_allow_html=True)
st.caption('Private local prototype · Fictional demonstration information only · No automatic publishing')
section = sidebar()
if section not in ('Home', 'Guides & Help'):
    guide(section)

if section == 'Home':
    home(rows)

elif section == 'Guides & Help':
    help_page()

elif section == 'Dashboard':
    st.header('Dashboard')
    counts = [rows(f'SELECT COUNT(*) AS n FROM {table}')[0]['n'] for table in ('brands', 'posts', 'campaigns', 'referrals')]
    cols = st.columns(4)
    for col, label, n in zip(cols, ['Brands', 'Planned posts', 'Campaigns', 'Moderation referrals'], counts):
        col.metric(label, n)
    st.subheader('Upcoming content')
    show_table(rows('''SELECT b.name AS brand,p.platform,p.publish_date,p.caption,p.status FROM posts p JOIN brands b ON b.id=p.brand_id WHERE p.publish_date>=? ORDER BY p.publish_date LIMIT 15''', (date.today().isoformat(),)))

elif section == 'Social Inbox':
    render_social_inbox(rows, write, export_csv)

elif section == 'Content Planner':
    render_content_planner(rows, write, export_csv)

elif section == 'Brands':
    st.header('Client & Brand Manager')
    with st.form('brand_form', clear_on_submit=True):
        name = st.text_input('Brand name', placeholder='Demo Nature Club')
        alias = st.text_input('Client alias', placeholder='Fictional Client')
        notes = st.text_area('Notes (optional)')
        submit = st.form_submit_button('Create brand')
    if submit:
        if not name.strip() or not alias.strip():
            st.error('Brand name and client alias are required.')
        else:
            try:
                write('INSERT INTO brands(name,client_alias,notes) VALUES(?,?,?)', (name.strip(), alias.strip(), notes.strip()))
                st.success('Brand created.'); st.rerun()
            except sqlite3.IntegrityError:
                st.error('That brand name already exists.')
    show_table(rows('SELECT id,name,client_alias,notes FROM brands ORDER BY id DESC'))

elif section in ('Content Calendar', 'Content Library'):
    st.header(section)
    st.caption('The calendar stores planned dates; the library stores captions, hashtags and creative asset references. Nothing is published automatically.')
    with st.form('post_form', clear_on_submit=True):
        brand_id = brand_select()
        platform = st.selectbox('Platform', PLATFORMS)
        planned = st.date_input('Planned publication date', value=date.today())
        caption = st.text_area('Caption / draft copy')
        hashtags = st.text_input('Hashtags (optional)')
        asset = st.text_input('Creative asset reference (filename or internal note, optional)')
        status = st.selectbox('Content status', ['Idea', 'Draft', 'Awaiting approval', 'Approved', 'Published manually'])
        submit = st.form_submit_button('Save content')
    if submit:
        if not caption.strip():
            st.error('Enter a caption or draft.')
        else:
            write('INSERT INTO posts(brand_id,platform,publish_date,caption,hashtags,asset_ref,status) VALUES(?,?,?,?,?,?,?)', (brand_id,platform,planned.isoformat(),caption.strip(),hashtags.strip(),asset.strip(),status))
            st.success('Content saved.'); st.rerun()
    st.subheader('Saved content')
    records = rows('''SELECT p.id,b.name AS brand,p.platform,p.publish_date,p.caption,p.hashtags,p.asset_ref,p.status FROM posts p JOIN brands b ON b.id=p.brand_id ORDER BY p.publish_date DESC,p.id DESC''')
    show_table(records)
    export_csv(records, 'smm_content.csv')
    if records:
        with st.expander('Update a content status'):
            ids = [r['id'] for r in records]
            pid = st.selectbox('Content ID', ids)
            new_status = st.selectbox('New status', ['Idea', 'Draft', 'Awaiting approval', 'Approved', 'Published manually'], key='update_post_status')
            if st.button('Update content status'):
                write('UPDATE posts SET status=? WHERE id=?', (new_status,pid)); st.success('Updated.'); st.rerun()

elif section == 'Campaigns':
    st.header('Campaign Manager')
    with st.form('campaign_form', clear_on_submit=True):
        brand_id = brand_select()
        title = st.text_input('Campaign title')
        goal = st.text_area('Campaign goal')
        start = st.date_input('Start date', value=date.today())
        end = st.date_input('End date', value=date.today())
        status = st.selectbox('Status', ['Planned', 'Active', 'Completed', 'Paused'])
        submit = st.form_submit_button('Create campaign')
    if submit:
        if not title.strip() or not goal.strip() or end < start:
            st.error('Enter a title and goal, and ensure the end date is not before the start date.')
        else:
            write('INSERT INTO campaigns(brand_id,title,goal,start_date,end_date,status) VALUES(?,?,?,?,?,?)', (brand_id,title.strip(),goal.strip(),start.isoformat(),end.isoformat(),status))
            st.success('Campaign saved.'); st.rerun()
    show_table(rows('''SELECT c.id,b.name AS brand,c.title,c.goal,c.start_date,c.end_date,c.status FROM campaigns c JOIN brands b ON b.id=c.brand_id ORDER BY c.id DESC'''))

elif section == 'Analytics & Reports':
    st.header('Analytics & Reports')
    st.caption('Enter metrics manually from authorized sources. These are not live platform analytics.')
    with st.form('metrics_form', clear_on_submit=True):
        brand_id = brand_select()
        platform = st.selectbox('Platform', PLATFORMS)
        period = st.text_input('Reporting period', value=date.today().strftime('%Y-%m'))
        impressions = st.number_input('Impressions', min_value=0, step=1)
        engagements = st.number_input('Engagements', min_value=0, step=1)
        followers = st.number_input('Followers at end of period', min_value=0, step=1)
        notes = st.text_area('Notes')
        submit = st.form_submit_button('Save metrics')
    if submit:
        if not period.strip():
            st.error('Reporting period is required.')
        else:
            write('INSERT INTO metrics(brand_id,platform,period,impressions,engagements,followers,notes) VALUES(?,?,?,?,?,?,?)', (brand_id,platform,period.strip(),int(impressions),int(engagements),int(followers),notes.strip()))
            st.success('Metrics saved.'); st.rerun()
    records = rows('''SELECT m.id,b.name AS brand,m.platform,m.period,m.impressions,m.engagements,m.followers,m.notes FROM metrics m JOIN brands b ON b.id=m.brand_id ORDER BY m.id DESC''')
    render_analytics_dashboard(records, export_csv)

elif section == 'Moderation Coordination':
    st.header('Moderation Coordination')
    st.info('This module tracks manual referrals only. Detailed moderation evidence and decisions remain in the separate Trust & Safety Studio. No automatic data synchronization is implemented.')
    with st.form('referral_form', clear_on_submit=True):
        brand_id = brand_select()
        platform = st.selectbox('Platform', PLATFORMS)
        reference = st.text_input('Internal case reference (no private URLs or personal information)')
        category = st.selectbox('Issue category', ['Spam', 'Harassment', 'Impersonation', 'Policy question', 'Other'])
        priority = st.selectbox('Priority', ['Low', 'Normal', 'High'])
        status = st.selectbox('Referral status', ['Open', 'Referred to Trust & Safety', 'Resolved'])
        notes = st.text_area('Coordination notes (non-sensitive)')
        submit = st.form_submit_button('Save referral')
    if submit:
        if not reference.strip():
            st.error('Provide a fictional internal reference.')
        else:
            write('INSERT INTO referrals(brand_id,platform,reference,category,priority,status,notes) VALUES(?,?,?,?,?,?,?)', (brand_id,platform,reference.strip(),category,priority,status,notes.strip()))
            st.success('Referral saved.'); st.rerun()
    records = rows('''SELECT r.id,b.name AS brand,r.platform,r.reference,r.category,r.priority,r.status,r.notes FROM referrals r JOIN brands b ON b.id=r.brand_id ORDER BY r.id DESC''')
    show_table(records)
    export_csv(records, 'smm_moderation_referrals.csv')
    if records:
        with st.expander('Update referral status'):
            rid = st.selectbox('Referral ID', [r['id'] for r in records])
            status = st.selectbox('New referral status', ['Open', 'Referred to Trust & Safety', 'Resolved'], key='update_referral_status')
            if st.button('Update referral'):
                write('UPDATE referrals SET status=? WHERE id=?', (status,rid)); st.success('Updated.'); st.rerun()
