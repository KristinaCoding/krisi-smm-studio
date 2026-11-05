"""Manual social inbox and task tracking for fictional SMM workflows."""
from datetime import date
import streamlit as st

PLATFORMS = ["Instagram", "Facebook", "TikTok", "LinkedIn", "Pinterest", "YouTube", "Discord", "Reddit", "Twitch"]
STATUSES = ["New", "In Progress", "Resolved"]
PRIORITIES = ["Low", "Normal", "High"]
TYPES = ["Comment", "Message", "Mention", "Review", "Other"]

def init_inbox(connect):
    with connect() as db:
        db.execute("""
        CREATE TABLE IF NOT EXISTS social_inbox (
            id INTEGER PRIMARY KEY,
            brand_id INTEGER NOT NULL REFERENCES brands(id),
            platform TEXT NOT NULL,
            item_type TEXT NOT NULL,
            reference TEXT NOT NULL,
            summary TEXT NOT NULL,
            assigned_to TEXT NOT NULL DEFAULT '',
            priority TEXT NOT NULL DEFAULT 'Normal',
            status TEXT NOT NULL DEFAULT 'New',
            due_date TEXT,
            notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")

def render_social_inbox(rows, write, export_csv):
    st.header("Social Inbox & Tasks")
    st.caption("Manual work queue only · No social network connection, message fetching or replies.")
    brands = rows("SELECT id, name FROM brands ORDER BY name")
    if not brands:
        st.info("Create a fictional brand in Brands before adding inbox items.")
        return
    labels = {b["id"]: b["name"] for b in brands}
    with st.expander("＋ Add inbox item or follow-up task", expanded=False):
        with st.form("inbox_new", clear_on_submit=True):
            brand_id = st.selectbox("Brand", list(labels), format_func=lambda x: labels[x])
            platform = st.selectbox("Platform", PLATFORMS)
            item_type = st.selectbox("Interaction type", TYPES)
            reference = st.text_input("Fictional internal reference", placeholder="DEMO-001")
            summary = st.text_area("Short non-sensitive summary")
            c1, c2 = st.columns(2)
            with c1:
                priority = st.selectbox("Priority", PRIORITIES, index=1)
                assigned = st.text_input("Assigned to (alias or role)")
            with c2:
                status = st.selectbox("Status", STATUSES)
                due = st.date_input("Follow-up date", value=date.today())
            notes = st.text_area("Internal notes (no personal information)")
            save = st.form_submit_button("Save inbox item")
        if save:
            if not reference.strip() or not summary.strip():
                st.error("Reference and summary are required.")
            else:
                write("""INSERT INTO social_inbox
                         (brand_id, platform, item_type, reference, summary,
                          assigned_to, priority, status, due_date, notes)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                      (brand_id, platform, item_type, reference.strip(), summary.strip(),
                       assigned.strip(), priority, status, due.isoformat(), notes.strip()))
                st.success("Inbox item saved.")
                st.rerun()
    records = rows("""SELECT i.id, i.brand_id, b.name AS brand, i.platform,
                             i.item_type, i.reference, i.summary, i.assigned_to,
                             i.priority, i.status, i.due_date, i.notes, i.created_at
                      FROM social_inbox i JOIN brands b ON b.id=i.brand_id
                      ORDER BY CASE i.priority WHEN 'High' THEN 0 WHEN 'Normal' THEN 1 ELSE 2 END,
                               i.created_at DESC, i.id DESC""")
    c1, c2, c3 = st.columns(3)
    c1.metric("New", sum(r["status"] == "New" for r in records))
    c2.metric("In progress", sum(r["status"] == "In Progress" for r in records))
    c3.metric("Resolved", sum(r["status"] == "Resolved" for r in records))
    f1, f2, f3 = st.columns(3)
    with f1:
        brand_filter = st.selectbox("Filter brand", ["All"] + sorted({r["brand"] for r in records}))
    with f2:
        platform_filter = st.selectbox("Filter platform", ["All"] + PLATFORMS)
    with f3:
        status_filter = st.selectbox("Filter status", ["All"] + STATUSES)
    filtered = [r for r in records if
                (brand_filter == "All" or r["brand"] == brand_filter) and
                (platform_filter == "All" or r["platform"] == platform_filter) and
                (status_filter == "All" or r["status"] == status_filter)]
    st.subheader("Inbox queue")
    if filtered:
        columns = ("id", "brand", "platform", "item_type", "reference", "summary",
                   "assigned_to", "priority", "status", "due_date")
        st.dataframe([{k: r[k] for k in columns} for r in filtered],
                     use_container_width=True, hide_index=True)
        export_csv([{k: r[k] for k in columns} for r in filtered], "smm_inbox_filtered.csv")
    else:
        st.info("No items match your filters.")
    if filtered:
        st.subheader("Manage a follow-up")
        options = {r["id"]: f"#{r['id']} · {r['brand']} · {r['reference']}" for r in filtered}
        with st.form("inbox_edit"):
            selected = st.selectbox("Inbox item", list(options), format_func=lambda x: options[x])
            item = next(r for r in filtered if r["id"] == selected)
            next_status = st.selectbox("Update status", STATUSES, index=STATUSES.index(item["status"]))
            next_priority = st.selectbox("Update priority", PRIORITIES, index=PRIORITIES.index(item["priority"]))
            next_assignee = st.text_input("Assigned to", value=item["assigned_to"])
            next_notes = st.text_area("Coordination notes", value=item["notes"])
            update = st.form_submit_button("Save follow-up")
        if update:
            write("""UPDATE social_inbox
                     SET status=?, priority=?, assigned_to=?, notes=?
                     WHERE id=?""",
                  (next_status, next_priority, next_assignee.strip(), next_notes.strip(), selected))
            st.success("Follow-up updated.")
            st.rerun()
    st.info("For safety escalation, create a separate manual reference in Moderation Coordination. No information is automatically transferred to Trust & Safety Studio.")
