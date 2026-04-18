import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

if not st.session_state.get('authenticated'):
    st.warning('Please log in from the Home page')
    st.stop()

SideBarLinks()

API_BASE = 'http://web-api:4000'
user_id = st.session_state.get('user_id', 1)

st.title('Moderate Reviews')
st.write('#### Approve or reject user-submitted reviews')
st.write('')


def moderate(review_id: int, moderation_status: str, notes: str | None = None):
    payload = {
        'moderation_status': moderation_status,
        'admin_user_id': user_id,
    }
    if notes:
        payload['notes'] = notes
    try:
        r = requests.put(
            f'{API_BASE}/admin/reviews/{review_id}/moderate',
            json=payload,
            timeout=10,
        )
        if r.status_code == 200:
            st.success(
                f'Review {review_id} {moderation_status}.'
            )
            st.rerun()
        else:
            st.error(f'Failed: {r.status_code} - {r.text}')
    except Exception as e:
        st.error(f'Request failed: {e}')


tab_pending, tab_flagged = st.tabs(['Pending', 'Flagged'])

# ---- Pending tab ----
with tab_pending:
    st.subheader('Reviews awaiting moderation')
    pending = []
    try:
        r = requests.get(
            f'{API_BASE}/reviews/', params={'status': 'pending'}, timeout=5
        )
        if r.status_code == 200:
            pending = r.json() or []
        else:
            st.error(f'Could not load pending reviews: {r.status_code}')
    except Exception as e:
        st.error(f'Could not load pending reviews: {e}')

    if not pending:
        st.info('No pending reviews.')
    else:
        for rev in pending:
            rid = rev.get('review_id')
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(
                        f"**{rev.get('review_title','(no title)')}** "
                        f"by {rev.get('username','?')} on "
                        f"*{rev.get('movie_title','?')}*"
                    )
                    st.caption(f"Review id: {rid} | {rev.get('review_date','')}")
                    st.write(rev.get('review_body', ''))
                with c2:
                    if st.button('Approve', key=f'approve_p_{rid}',
                                 type='primary', use_container_width=True):
                        moderate(rid, 'approved')
                    if st.button('Reject', key=f'reject_p_{rid}',
                                 use_container_width=True):
                        moderate(rid, 'rejected')

# ---- Flagged tab ----
with tab_flagged:
    st.subheader('Reviews flagged by users')
    flagged = []
    try:
        r = requests.get(f'{API_BASE}/admin/reviews/flagged', timeout=5)
        if r.status_code == 200:
            flagged = r.json() or []
        else:
            st.error(f'Could not load flagged reviews: {r.status_code}')
    except Exception as e:
        st.error(f'Could not load flagged reviews: {e}')

    if not flagged:
        st.info('No flagged reviews pending moderation.')
    else:
        for rev in flagged:
            rid = rev.get('review_id')
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(
                        f"**{rev.get('review_title','(no title)')}** "
                        f"by {rev.get('review_author','?')} on "
                        f"*{rev.get('movie_title','?')}*"
                    )
                    st.caption(
                        f"Review id: {rid} | flagged by "
                        f"{rev.get('flagged_by','?')}: "
                        f"{rev.get('flag_reason','(no reason)')}"
                    )
                    st.write(rev.get('review_body', ''))
                with c2:
                    if st.button('Approve', key=f'approve_f_{rid}',
                                 type='primary', use_container_width=True):
                        moderate(rid, 'approved')
                    if st.button('Reject', key=f'reject_f_{rid}',
                                 use_container_width=True):
                        moderate(rid, 'rejected')
