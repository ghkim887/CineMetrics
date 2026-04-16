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

st.title('Manage My Reviews')
st.write('Edit or delete reviews you\'ve written.')

# ---- Load reviews ----
reviews = []
try:
    resp = requests.get(f'{API_BASE}/reviews/', params={'user_id': user_id}, timeout=5)
    if resp.status_code == 200:
        reviews = resp.json() or []
    else:
        st.error(f'Failed to load your reviews (status {resp.status_code})')
except Exception as e:
    st.error(f'Could not fetch reviews: {e}')

if not reviews:
    st.info('You haven\'t written any reviews yet.')
    if st.button('Write your first review', type='primary'):
        st.switch_page('pages/11_Write_Review.py')
    st.stop()

# ---- Pending deletion confirmation state ----
pending_delete = st.session_state.get('pending_delete_review_id')
editing_id = st.session_state.get('editing_review_id')

for rev in reviews:
    review_id = rev.get('review_id') or rev.get('id')
    with st.container(border=True):
        top_l, top_r = st.columns([4, 2])
        with top_l:
            st.markdown(f"### {rev.get('review_title', 'Untitled')}")
            st.caption(f"*{rev.get('movie_title', '')}* — {rev.get('review_date', '')}")

        with top_r:
            bc1, bc2 = st.columns(2)
            with bc1:
                if st.button('Edit', key=f'edit_{review_id}', use_container_width=True):
                    st.session_state['editing_review_id'] = review_id
                    editing_id = review_id
            with bc2:
                if st.button('Delete', key=f'del_{review_id}', use_container_width=True):
                    st.session_state['pending_delete_review_id'] = review_id
                    pending_delete = review_id

        # ---- Edit form ----
        if editing_id == review_id:
            with st.form(f'edit_form_{review_id}'):
                new_title = st.text_input('Review Title',
                                          value=rev.get('review_title', ''),
                                          max_chars=200)
                new_body = st.text_area('Your Review',
                                        value=rev.get('review_body', ''),
                                        height=200)
                save_col, cancel_col = st.columns(2)
                with save_col:
                    save = st.form_submit_button('Save Changes', type='primary',
                                                 use_container_width=True)
                with cancel_col:
                    cancel = st.form_submit_button('Cancel', use_container_width=True)

                if save:
                    payload = {
                        'review_title': new_title.strip(),
                        'review_body': new_body.strip(),
                    }
                    try:
                        r = requests.put(f'{API_BASE}/reviews/{review_id}',
                                         json=payload, timeout=5)
                        if r.status_code in (200, 204):
                            st.success('Review updated.')
                            st.session_state.pop('editing_review_id', None)
                            st.rerun()
                        else:
                            st.error(f'Update failed (status {r.status_code}): {r.text}')
                    except Exception as e:
                        st.error(f'Could not update review: {e}')
                elif cancel:
                    st.session_state.pop('editing_review_id', None)
                    st.rerun()
        else:
            st.write(rev.get('review_body', ''))

        # ---- Delete confirmation ----
        if pending_delete == review_id:
            st.warning('Are you sure you want to delete this review? This cannot be undone.')
            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button('Yes, delete it', key=f'confirm_del_{review_id}',
                             type='primary', use_container_width=True):
                    try:
                        r = requests.delete(f'{API_BASE}/reviews/{review_id}', timeout=5)
                        if r.status_code in (200, 204):
                            st.success('Review deleted.')
                            st.session_state.pop('pending_delete_review_id', None)
                            st.rerun()
                        else:
                            st.error(f'Delete failed (status {r.status_code}): {r.text}')
                    except Exception as e:
                        st.error(f'Could not delete review: {e}')
            with cc2:
                if st.button('Cancel', key=f'cancel_del_{review_id}',
                             use_container_width=True):
                    st.session_state.pop('pending_delete_review_id', None)
                    st.rerun()
