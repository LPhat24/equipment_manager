"""Shared UI styling utilities for the Lab Equipment Manager."""

import streamlit as st


def apply_full_width():
    """Inject CSS to make the main content area use full page width."""
    st.markdown(
        """
<style>
    .stMainBlockContainer {
        max-width: 100%;
        padding: 1rem 2rem;
    }
</style>
""",
        unsafe_allow_html=True,
    )
