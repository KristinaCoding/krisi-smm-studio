"""Content Planner v2: filtered calendar, queue and manual approval tracking."""
import calendar
from datetime import date, timedelta
import streamlit as st

STATUSES = ["Idea", "Draft", "Awaiting approval", "Approved", "Published manually"]
PLATFORMS = ["Instagram", "Facebook", "TikTok", "LinkedIn", "Pinterest", "YouTube", "Discord", "Reddit", "Twitch"]

def render_content_planner(rows, write, export_csv):
    st.header("Content Planner")
    st.caption("Plan posts, filter your calendar, and track approvals. No automatic social publishing.")
    records = rows("""SELECT p.id, p.brand_id, b.name AS brand, p.platform,
                             p.publish_date, p.caption, p.hashtags, p.asset_ref, p.status
                      FROM posts p JOIN brands b ON b.id=p.brand_id
                      ORDER BY p.publish_date, p.id""")
    brands = sorted({r["brand"] for r in records})
    c1, c2, c3 = st.columns(3)
    with c1:
        brand = st.selectbox("Brand filter", ["All brands"] + brands, key="planner_brand")
    with c2:
        platform = st.selectbox("Platform filter", ["All platforms"] + PLATFORMS, key="planner_platform")
    with c3:
        status = st.selectbox("Status filter", ["All statuses"] + STATUSES, key="planner_status")
    filtered = [r for r in records
                if (brand == "All brands" or r["brand"] == brand)
                and (platform == "All platforms" or r["platform"] == platform)
                and (status == "All statuses" or r["status"] == status)]
    c1, c2, c3 = st.columns(3)
    c1.metric("Matching posts", len(filtered))
    c2.metric("Awaiting approval", sum(r["status"] == "Awaiting approval" for r in filtered))
    c3.metric("Approved", sum(r["status"] == "Approved" for r in filtered))

    st.subheader("Monthly calendar")
    today = date.today()
    selected_month = st.date_input("Choose a month", value=today.replace(day=1), key="planner_month")
    year, month = selected_month.year, selected_month.month
    st.caption(f"{calendar.month_name[month]} {year} · Each entry is a planned post, not a published post.")
    weeks = calendar.Calendar(firstweekday=0).monthdatescalendar(year, month)
    headers = st.columns(7)
    for col, dayname in zip(headers, ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        col.markdown(f"**{dayname}**")
    for week in weeks:
        cols = st.columns(7)
        for col, day in zip(cols, week):
            with col:
                if day.month != month:
                    st.caption(str(day.day))
                    continue
                st.markdown(f"**{day.day}**" + (" · Today" if day == today else ""))
                day_posts = [r for r in filtered if r["publish_date"] == day.isoformat()]
                for item in day_posts[:3]:
                    caption = item["caption"].replace("\n", " ")
                    st.caption(f"{item['platform']} · {item['status']}\n\n{caption[:35]}")
                if len(day_posts) > 3:
                    st.caption(f"+{len(day_posts)-3} more")
    st.subheader("Upcoming queue")
    upcoming = [r for r in filtered if r["publish_date"] >= today.isoformat() and r["status"] != "Published manually"]
    upcoming.sort(key=lambda r: (r["publish_date"], r["id"]))
    if upcoming:
        st.dataframe([{k: r[k] for k in ("id", "brand", "platform", "publish_date", "caption", "status")}
                      for r in upcoming[:30]], use_container_width=True, hide_index=True)
    else:
        st.info("No upcoming posts match these filters.")

    st.subheader("Review and update a post")
    if not filtered:
        st.info("Create a post in Content Library or Content Calendar to manage it here.")
    else:
        labels = {r["id"]: f"#{r['id']} · {r['brand']} · {r['platform']} · {r['publish_date']}" for r in filtered}
        with st.form("planner_update"):
            post_id = st.selectbox("Choose post", list(labels), format_func=lambda x: labels[x])
            item = next(r for r in filtered if r["id"] == post_id)
            next_status = st.selectbox("Approval status", STATUSES, index=STATUSES.index(item["status"]) if item["status"] in STATUSES else 0)
            next_date = st.date_input("Planned date", value=date.fromisoformat(item["publish_date"]))
            save = st.form_submit_button("Save changes")
        if save:
            write("UPDATE posts SET status=?, publish_date=? WHERE id=?",
                  (next_status, next_date.isoformat(), post_id))
            st.success("Post updated.")
            st.rerun()
    if filtered:
        export_csv(filtered, "smm_planner_filtered.csv")
