# krisi.site SMM Studio v1.0

A local Streamlit + SQLite freelance SMM workspace. Separate from Biology Studio and Trust & Safety Studio.

## Setup (Windows / PyCharm)
1. Extract this ZIP and open the extracted folder as a new PyCharm project.
2. Open the terminal and run `python -m pip install -r requirements.txt`.
3. Run `python -m streamlit run app.py`.
4. Open the local URL Streamlit prints (usually http://localhost:8501).

If another Streamlit app is already using port 8501, run `python -m streamlit run app.py --server.port 8502`.

## First test
1. In Brands, create `Demo Nature Club`, client alias `Fictional Client`.
2. In Content Calendar, save an Instagram draft caption for that brand.
3. In Campaigns, create `Autumn Awareness` with a goal and dates.
4. In Analytics & Reports, enter fictional numbers and download the CSV.
5. In Moderation Coordination, save a fictional referral `DEMO-001` and update its status.

## Scope and safeguards
- Local prototype only, **not** production-secure or multi-user.
- Use fictional or non-sensitive test data; do not enter real client credentials, private messages, or moderation evidence.
- No direct publishing, scheduling automation, live analytics, API connections, account permissions, or moderation actions.
- A planned publication date is an internal calendar record only.
- Moderation Coordination records manual referral metadata only; there is **no automatic synchronization** with Trust & Safety Studio.
- CSV reports are exported from manually entered data.
- SQLite data is stored in `smm_studio.db` next to `app.py`. Back up that file and the project folder when finished.


## v1.1 Dark Academia interface
The Streamlit appearance now matches the Trust & Safety Studio Dark Academia design. Existing SQLite tables, data entry forms, status updates, manual analytics, CSV exports and moderation referral workflows are preserved. This is a local prototype, not a live social media integration. To preserve existing records, stop the app, back up `smm_studio.db`, and copy it into the new project folder.
