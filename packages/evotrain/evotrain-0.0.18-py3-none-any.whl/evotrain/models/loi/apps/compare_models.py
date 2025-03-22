import json

# Let's add ../src to the path
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_image_comparison import image_comparison
from tbparse import SummaryReader

# Let's rewrite the app in a simpler way
# We want to make a list of folders in the results_dir
results_dir = "/data/users/Public/kalfasyan/share/outputs/pngs/models/"
results_dir = Path(results_dir)
model_dirs = list(results_dir.glob("*"))
og_model_dirs = Path("/vitodata/vegteam_vol2/models/cloudsen/60m/")
st.write(og_model_dirs)


def select_model_and_index(key=None):
    model_list = [i.name for i in model_dirs]
    selected_model = st.selectbox(
        "Select a model",
        model_list,
        key=key,
    )
    if not selected_model:
        st.warning("Please select a model.")
        return None, None

    index_list = list((results_dir / selected_model).glob("index_*"))
    index_list = [i.name for i in index_list]
    index_list.insert(0, selected_model)  # Add the model folder itself as an option
    selected_index = st.selectbox(
        f"Select index for {selected_model}", index_list, key=f"{key}_index"
    )

    return selected_model, selected_index


if __name__ == "__main__":
    model1, index1 = select_model_and_index(key="model1")
    model2, index2 = select_model_and_index(key="model2")

    # Inside og_model_dirs (subfolder with model name, no index subfolder)
    # we have a config.json file
    # Let's make an expander for the config.json files of the selected models
    if model1:
        config1_path = og_model_dirs / model1 / "version_0/config.json"
        if config1_path.exists():
            with st.expander(f"Config for {model1}"):
                with open(config1_path, "r") as f:
                    config1 = json.load(f)
                st.write(f"Config for {model1}")
                st.json(config1)
        else:
            st.warning(f"Config file not found for {model1} in {config1_path}")

    if model2:
        config2_path = og_model_dirs / model2 / "version_0/config.json"
        if config2_path.exists():
            with st.expander(f"Config for {model2}"):
                with open(config2_path, "r") as f:
                    config2 = json.load(f)
                st.write(f"Config for {model2}")
                st.json(config2)
        else:
            st.warning(f"Config file not found for {model2} in {config2_path}")

    if model1 and model2:
        st.write(f"Comparing {model1}, {index1} and {model2}, {index2}")

        # Products image comparison
        products = Path(
            "/data/users/Public/kalfasyan/share/outputs/pngs/products"
        ).glob("*")

        products = list([p.name for p in products])

        for prd, product in enumerate(products):
            img1_path = (
                Path("/data/users/Public/kalfasyan/share/outputs/pngs/models")
                / model1
                / (index1 if index1 != model1 else "")
                / f"{product}.png"
            ).as_posix()
            img2_path = (
                Path("/data/users/Public/kalfasyan/share/outputs/pngs/models")
                / model2
                / (index2 if index2 != model2 else "")
                / f"{product}.png"
            ).as_posix()
            if not Path(img1_path).exists():
                st.warning(f"Image not found for {model1} and {product}")
            if not Path(img2_path).exists():
                st.warning(f"Image not found for {model2} and {product}")
            if Path(img1_path).exists() and Path(img2_path).exists():
                image_comparison(
                    img1=img1_path,
                    img2=img2_path,
                    label1=f"{model1}_{index1 if index1 != model1 else 'main'}",
                    label2=f"{model2}_{index2 if index2 != model2 else 'main'}",
                    show_labels=True,
                    width=500,
                )
                st.caption(f"{product}")
                st.divider()

            # if prd > 10:
            #     break
