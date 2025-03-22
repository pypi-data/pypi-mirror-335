from pathlib import Path

import numpy as np
import streamlit as st

colors = dict(
    # Cloudsen12 colors
    SURFACE=[0, 255, 0],  # green
    CLOUDS=[255, 255, 255],  # white
    THIN_CLOUDS=[0, 255, 255],  # cyan
    SHADOWS=[105, 105, 105],  # darker gray
    SNOW=[255, 0, 255],  # magenta
    # Sentinel-2 L2A SCL colors
    NA=[0, 0, 0],  # black
    SATURATED_DEFECTIVE=[255, 0, 0],  # red
    DARK_FEATURES_SHADOWS=[205, 205, 205],  # gray
    CLOUD_SHADOWS=[105, 105, 105],  # darker gray
    VEGETATION=[0, 255, 0],  # green
    NOT_VEGETATED=[255, 255, 0],  # yellow
    WATER=[0, 0, 255],  # blue
    UNCLASSIFIED=[0, 0, 0],  # black
    CLOUDS_MEDIUM_PROB=[255, 170, 0],  # orange
    CLOUDS_HIGH_PROB=[255, 255, 255],  # white
    THIN_CIRRUS=[0, 255, 255],  # cyan
    SNOW_ICE=[255, 0, 255],  # magenta
)
colors_scl_minimal = dict(
    # Sentinel-2 L2A SCL colors (ignoring some classes)
    NA=[0, 0, 0],  # black
    SATURATED_DEFECTIVE=[0, 0, 0],  # red
    DARK_FEATURES_SHADOWS=[0, 255, 0],  # green
    CLOUD_SHADOWS=[105, 105, 105],  # darker gray
    VEGETATION=[0, 255, 0],  # green
    NOT_VEGETATED=[0, 255, 0],  # green
    WATER=[0, 255, 0],  # blue
    UNCLASSIFIED=[0, 0, 0],  # black
    CLOUDS_MEDIUM_PROB=[255, 255, 255],  # orange
    CLOUDS_HIGH_PROB=[255, 255, 255],  # white
    THIN_CIRRUS=[0, 255, 255],  # cyan
    SNOW_ICE=[255, 0, 255],  # magenta
)

scl = {
    "NA": 0,
    "SATURATED_DEFECTIVE": 1,
    "DARK_FEATURES_SHADOWS": 2,
    "CLOUD_SHADOWS": 3,
    "VEGETATION": 4,
    "NOT_VEGETATED": 5,
    "WATER": 6,
    "UNCLASSIFIED": 7,
    "CLOUDS_MEDIUM_PROB": 8,
    "CLOUDS_HIGH_PROB": 9,
    "THIN_CIRRUS": 10,
    "SNOW_ICE": 11,
}

# Define the colors for saving geotiff and plotting
cloudsen12_colors_rgb = {
    0: np.array(colors["SURFACE"]),
    1: np.array(colors["CLOUDS"]),
    2: np.array(colors["THIN_CLOUDS"]),
    3: np.array(colors["SHADOWS"]),
}


def mask_to_rgb(mask, colors, normalize_colors=True):
    """
    Convert mask to RGB using the given colors (class labels to colors mapping).
    The mask is a 2D array where each pixel contains the class label.
    The colors is a dictionary containing the colors for each class label.

    Args:
    mask (np.ndarray): Mask to convert
    colors (dict): Dictionary containing the colors for each class

    Returns:
    np.ndarray: RGB mask
    """
    if normalize_colors:
        colors = {k: np.array(v) / 255 for k, v in colors.items()}
    mask_rgb = np.zeros((mask.shape[0], mask.shape[1], 3))
    for i, color in colors.items():
        mask_rgb[mask == i] = color
    return mask_rgb


if __name__ == "__main__":
    with st.spinner("Importing libraries..."):
        from PIL import Image
        from streamlit_image_comparison import image_comparison
        from streamlit_image_coordinates import streamlit_image_coordinates
        from veg_workflows.collections import veg_collections
        from compare_models import inv_model_to_names, model_to_names, path_models

        raise NotImplementedError(
            "This script needs to be updated to use the new model inference functions"
        )
        # from lcfm_clouds.inference.model_inference import (
        #     load_model_files,
        #     process_product,
        # )

    tab1, tab2 = st.tabs(["Perform inference", "Crop & Save"])

    with tab1:
        with st.form(key="form2"):
            # user selects a model
            model_list = list(model_to_names.values())
            # Get index of the default model: 2407251716_BASELINE_mobilenet_v2
            default_model_idx = model_list.index("2407251716_BASELINE_mobilenet_v2") + 1

            selected_model = st.selectbox(
                "model selection",
                ["Select a model"] + model_list,
                index=default_model_idx,
                label_visibility="hidden",
            )
            selected_model = inv_model_to_names[selected_model]

            collection_name = "lcfm_10percent"  # 'lcfm_10percent'
            with st.spinner("Loading the collection..."):
                # user selects a product
                collection = getattr(veg_collections, collection_name)
                # collection = veg_collections.lcfm_10percent
                df_coll = collection.df

            with st.spinner("Reading a list of products..."):
                products = df_coll.product_id.unique().tolist()
                selected_product = st.selectbox(
                    "Select a product",
                    tuple(["Select a product"]) + tuple(products),
                    index=0,
                )

            # FORM SUBMIT
            submitted_form2 = st.form_submit_button("Run")

        if submitted_form2:
            if selected_product == "Select a product":
                st.error("Please select a product")
                st.stop()

            with st.spinner("Loading the model..."):
                model_path = Path(path_models) / selected_model / Path("version_0/")
                model, _, model_config = load_model_files(
                    model_path.as_posix() + "/", load_last=False
                )
                # if we have merged clouds and added snow
                if model_config["data"].get("merge_clouds_add_snow", False):
                    cloudsen12_colors_rgb[2] = np.array(colors["SHADOWS"])
                    cloudsen12_colors_rgb[3] = np.array(colors["SNOW"])
                # if we have the add_snow_class flag (i.e. didn't merge clouds)
                if model_config["data"].get("add_snow_class", False):
                    cloudsen12_colors_rgb[3] = np.array(colors["SNOW"])

            # SCL colors in RGB
            scl_cloudsen12_colors_rgb = {
                v: np.array(colors_scl_minimal[k]) for k, v in scl.items()
            }
            scl_colors_rgb = {v: np.array(colors[k]) for k, v in scl.items()}

            with st.expander("Collection dataframe"):
                st.dataframe(df_coll, width=550)

            with st.spinner("Processing the product..."):
                out, out_argmax, rgb_img, scl_array, data_array = process_product(
                    s2_product_id=selected_product,
                    collection_name=collection,
                    s2grid=veg_collections.s2grid,
                    model=model,
                    config=model_config,
                    export_pngs=False,
                    export_tifs=False,
                    export_s2grid_metadata=False,
                    production=False,
                )
            # TODO: after applying the offset, there's some saturation in the RGB images

            # Let's save the data_array as a nc file
            # data_array.to_netcdf('pages/data_array.nc')

            rgb_img = np.moveaxis(rgb_img.data, 0, -1)
            rgb_img = (rgb_img * 255).astype(np.uint8)
            rgb_img = Image.fromarray(rgb_img)
            # st.image(rgb_img, caption="RGB image")
            # rgb_img.save('pages/rgb.jpeg')
            # Save a resized images (downscale to 600x600)
            # first assert the image is square and has a size of 1372x1372
            assert rgb_img.size[0] == rgb_img.size[1] == 1372, (
                "The image is not 1372x1372"
            )
            rgb_img_resized = rgb_img.resize((600, 600))
            rgb_img_resized.save("pages/rgb.jpeg")

            out_argmax_rgb = mask_to_rgb(
                out_argmax, cloudsen12_colors_rgb, normalize_colors=True
            )
            # st.image(out_argmax_rgb, caption="Output argmax image (rgb)")
            out_argmax_rgb = Image.fromarray((out_argmax_rgb * 255).astype(np.uint8))
            out_argmax_rgb.save("pages/out_argmax_rgb.jpeg")

            image_comparison(
                img1=rgb_img,
                img2=out_argmax_rgb,
                label1="RGB image",
                label2="Output argmax image (rgb)",
                show_labels=True,
            )

    with tab2:
        image_path = Path("pages/rgb.jpeg")

        if image_path.exists():
            coords_and_dims = streamlit_image_coordinates(
                image_path,
                key="pxlimage",
                use_column_width="never",
            )

            with st.expander("RGB/SCL comparison"):
                image_comparison(
                    img1=Image.open(image_path),
                    img2=Image.open("pages/out_argmax_rgb.jpeg"),
                    label1="RGB image",
                    label2="Output argmax image (rgb)",
                    show_labels=True,
                    width=400,
                )

            with st.expander("coordinates"):
                st.write(coords_and_dims)
                # The coordinates are in the center of the crop
                # for the resized image (600x600), but we need to
                # adjust them for the original image (1372x1372)
                if coords_and_dims:
                    x = coords_and_dims["x"] * 1372 // 600
                    y = coords_and_dims["y"] * 1372 // 600
                    st.write(
                        f"Adjusted coordinates (original resolution): \nx: {x}, y: {y}"
                    )

            # crop parameters
            cropcol1, cropcol2 = st.columns(2)
            with cropcol1:
                crop_h = st.number_input("Crop height", value=64)
            with cropcol2:
                crop_w = st.number_input("Crop width", value=64)

            rgb_img = Image.open(image_path)
            # TODO: We need to load the original image here (data array rgb) and make the crop
            if coords_and_dims:
                x, y = coords_and_dims["x"], coords_and_dims["y"]

                crop = rgb_img.crop(
                    (x - crop_w // 2, y - crop_h // 2, x + crop_w // 2, y + crop_h // 2)
                )
                # if the crop is smaller than the desired size, we need to pad it
                if crop.size[0] < crop_w or crop.size[1] < crop_h:
                    new_crop = Image.new("RGB", (crop_w, crop_h))
                    new_crop.paste(crop, (0, 0))
                    crop = new_crop
                la, ca, ra = st.columns(3)
                with ca:
                    st.image(crop, caption=f"Cropped image {crop.size}")

            st.divider()

            with st.form(key="cropsave"):
                tmp_fname = st.text_input("Enter filename", value="crop123")

                # let's add a radio button with the list : ["SURFACE", "CLOUDS", "THIN_CLOUDS", "SHADOWS", "SNOW", ""]
                # and let the user select the class of the crop
                radio = st.radio(
                    "Select the class of the crop",
                    ["", "SURFACE", "CLOUDS", "THIN_CLOUDS", "SHADOWS", "SNOW"],
                )

                submitted_cropsave = st.form_submit_button("Save crop")
                if submitted_cropsave:
                    fname = f"{radio}_{tmp_fname}"
                    crop.save(f"pages/{fname}.jpeg")
                    st.info(f"crop saved as {fname}")
