import streamlit as st
from contextlib import contextmanager


def page_config(st, title):
  st.set_page_config(layout="wide", page_icon="📊")
  st.title(title)

class LayoutElements:
  @staticmethod
  @contextmanager
  def custom_sidebar():
    with st.sidebar:
      yield

      if st.button("Clear all cache"):
        st.cache_data.clear()

def load_custom_font():
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Dosis:wght@400&display=swap');
        body {
            font-family: 'Dosis', sans-serif;
        }
    </style>
    """


class FormElements:
  @staticmethod
  def periodicity_field(
    label,
    keys=("Année", "Mois"),
    options=("Année", "Mois")
  ):
    k_mapper = dict(zip(options, keys))
    return st.radio(
      label=label,
      options=options,
      format_func=lambda x: k_mapper.get(x, "default")
    )
