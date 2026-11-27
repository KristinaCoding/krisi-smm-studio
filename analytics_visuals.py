"""Dark Academia visual reporting for manually entered SMM metrics."""
import pandas as pd
import streamlit as st

def render_analytics_dashboard(records, export_csv):
    st.markdown("### Performance overview")
    st.caption("Visual summaries of manually entered records — not live social-platform analytics.")
    if not records:
        st.info("Add a metrics record above to see charts and comparisons.")
        return
    brands = sorted({r["brand"] for r in records})
    platforms = sorted({r["platform"] for r in records})
    periods = sorted({r["period"] for r in records})
    a, b, c = st.columns(3)
    with a:
        brand = st.selectbox("Client / brand", ["All brands"] + brands, key="analytics_brand")
    with b:
        platform = st.selectbox("Platform", ["All platforms"] + platforms, key="analytics_platform")
    with c:
        period = st.selectbox("Reporting period", ["All periods"] + periods, key="analytics_period")
    filtered = [r for r in records
                if (brand == "All brands" or r["brand"] == brand)
                and (platform == "All platforms" or r["platform"] == platform)
                and (period == "All periods" or r["period"] == period)]
    if not filtered:
        st.info("No records match your filters.")
        return
    df = pd.DataFrame(filtered)
    totals = df[["impressions", "engagements"]].sum()
    impressions = int(totals["impressions"])
    engagements = int(totals["engagements"])
    rate = 100 * engagements / impressions if impressions else None
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Impressions", f"{impressions:,}")
    k2.metric("Engagements", f"{engagements:,}")
    k3.metric("Engagement / impressions", f"{rate:.2f}%" if rate is not None else "N/A")
    k4.metric("Records", len(filtered))
    st.caption("Engagement / impressions is a calculated ratio, not a platform-defined engagement rate. Duplicate or overlapping records can inflate totals.")
    left, right = st.columns(2)
    with left:
        st.markdown("#### Platform comparison")
        platform_data = df.groupby("platform", as_index=True)[["impressions", "engagements"]].sum().sort_values("impressions", ascending=False)
        st.bar_chart(platform_data, use_container_width=True)
    with right:
        st.markdown("#### Performance by reporting period")
        period_data = df.groupby("period", as_index=True)[["impressions", "engagements"]].sum().sort_index()
        st.line_chart(period_data, use_container_width=True)
        st.caption("Periods are sorted by their entered text labels; use YYYY-MM for chronological order.")
    st.markdown("#### Followers by platform")
    st.caption("Latest recorded follower count per brand and platform (not summed across periods).")
    latest = df.sort_values(["period", "id"]).drop_duplicates(["brand", "platform"], keep="last")
    follower_data = latest.assign(channel=latest["brand"] + " · " + latest["platform"]).set_index("channel")[["followers"]]
    st.bar_chart(follower_data, use_container_width=True)
    with st.expander("View filtered source records and export"):
        st.dataframe(df, use_container_width=True, hide_index=True)
        export_csv(filtered, "smm_analytics_filtered.csv")
