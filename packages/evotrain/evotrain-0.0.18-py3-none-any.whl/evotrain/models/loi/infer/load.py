def load_model_files(
    model_path: str,
    idx=-1,
    load_last=False,
    model_config_only=False,
    classes=list(range(4)),
):
    """
    Load model from model path and return model, model_class_mapping, config
    """
    # HACK putting this _inside_ the function to avoid torch import error in OpenEO UDF
    import json
    from pathlib import Path

    import torch
    from loguru import logger

    from evotrain.models.loi import natural_sort

    from ..train.model import CloudNet

    model_path = Path(model_path)
    with open(model_path / "config.json", "r") as file:
        model_config = json.load(file)
    input_bands = [band[4:] for band in model_config["bands_config"]["s2_bands"]]
    model_config["bands_config"]["s2_bands"] = input_bands

    if model_config["data_config"]["classify_snow"]:
        model_class_mapping = model_config["labels_config"][
            "cloudsen12_mergedclouds_extrasnow"
        ]
    else:
        model_class_mapping = model_config["labels_config"]["cloudsen12"]

    model_checkpoint_path = model_path / "checkpoints"
    logger.debug(f"Model checkpoint path: {model_checkpoint_path}")

    assert model_checkpoint_path.exists(), (
        f"Model checkpoint path {model_checkpoint_path} does not exist"
    )

    if load_last:
        model_checkpoint = model_checkpoint_path / "last.ckpt"
    else:
        available_checkpoints = natural_sort(model_checkpoint_path.glob("ep*.ckpt"))
        logger.debug(f"Available checkpoints: {available_checkpoints}")
        model_checkpoint = available_checkpoints[idx]
        logger.debug(f"Loading model from {model_checkpoint}")

    model_state_dict = torch.load(
        model_checkpoint,
        map_location="cpu",
        weights_only=True,  # NOTE define weights for better understanding
    )["state_dict"]
    logger.info(f"Model state dict loaded from {model_checkpoint}")

    if model_config_only:
        logger.info("Returning model configuration only")
        return model_config

    logger.info("Initializing CloudNet model")
    model = CloudNet(
        bands=model_config["bands_config"]["s2_bands"],
        classes=classes,
        arch=model_config["dl_model_config"]["arch"],
        backbone=model_config["dl_model_config"]["backbone"],
        activation=model_config["dl_model_config"]["activation"],
        loss=model_config["dl_model_config"]["loss"],
        learning_rate=model_config["dl_model_config"]["learning_rate"],
        class_weights_list=model_config["dl_model_config"]["class_weights_list"],
        sample_weights=model_config["dl_model_config"]["sample_weights"],
        label_smoothing_factor=model_config["dl_model_config"][
            "label_smoothing_factor"
        ],
        dropout_rate=model_config["dl_model_config"]["dropout_rate"],
        config=model_config,
        architecture_version=model_config["dl_model_config"]["architecture_version"],
        mlp_hidden_layers=model_config["dl_model_config"]["mlp_hidden_layers"],
        head_filters_settings=model_config["dl_model_config"]["head_filters_settings"],
        bands_head=model_config["dl_model_config"]["bands_head"],
    )
    model.load_state_dict(model_state_dict, strict=False)
    logger.info("Model state dict loaded successfully")

    model.eval()
    logger.info("Model set to evaluation mode")
    return model, model_class_mapping, model_config


def load_s3_model_files(
    model_path: str, idx=-1, load_last=False, model_config_only=False
):
    """
    Load model from model path and return model, model_class_mapping, config
    """
    import torch
    from loguru import logger
    from veg_workflows.aws import (
        AWS_LCFM_OUTPUT_BUCKET,
        download_checkpoint,
        get_key_from_s3_uri,
        get_s3_api,
    )

    from evotrain.models.loi import natural_sort

    from ..train.model import CloudNet

    s3_vegaws = get_s3_api(bucket=AWS_LCFM_OUTPUT_BUCKET)
    model_name = model_path.split("/")[-2]

    model_key = get_key_from_s3_uri(model_path)
    model_config = s3_vegaws.read_json(f"{model_key}/config.json")
    input_bands = [band[4:] for band in model_config["bands_config"]["s2_bands"]]
    model_config["bands_config"]["s2_bands"] = input_bands

    if model_config["data_config"]["classify_snow"]:
        model_class_mapping = model_config["labels_config"][
            "cloudsen12_mergedclouds_extrasnow"
        ]
    else:
        model_class_mapping = model_config["labels_config"]["cloudsen12"]

    if not model_path.endswith("/"):
        model_path += "/"

    model_checkpoint_path = model_path + "checkpoints/"
    logger.debug(f"Model checkpoint path: {model_checkpoint_path}")

    if load_last:
        model_checkpoint = model_checkpoint_path + "/last.ckpt"
    else:
        _ep_checkpoints = s3_vegaws.list_files(
            get_key_from_s3_uri(model_checkpoint_path)
        )

        available_checkpoints = natural_sort(_ep_checkpoints)
        for i, checkpoint in enumerate(available_checkpoints):
            available_checkpoints[i] = f"s3://{AWS_LCFM_OUTPUT_BUCKET}/{checkpoint}"

        logger.info(f"Available checkpoints: {available_checkpoints}")
        model_checkpoint = available_checkpoints[idx]
        checkpoint_name = model_checkpoint.rsplit("/")[-1]
        checkpoint_localpth = download_checkpoint(
            checkpoint_name,
            model_name=model_name,
            tgt_path=f"/tmp/{checkpoint_name}",
        )  # download method already checks if file exists
        logger.info(f"Loading model from {model_checkpoint}")

    model_state_dict = torch.load(
        checkpoint_localpth, map_location="cpu", weights_only=True
    )["state_dict"]

    if model_config_only:
        logger.info("Returning model configuration only")
        return model_config

    logger.info("Initializing CloudNet model")
    model = CloudNet(
        bands=model_config["bands_config"]["s2_bands"],
        classes=list(range(4)),
        arch=model_config["dl_model_config"]["arch"],
        backbone=model_config["dl_model_config"]["backbone"],
        activation=model_config["dl_model_config"]["activation"],
        loss=model_config["dl_model_config"]["loss"],
        learning_rate=model_config["dl_model_config"]["learning_rate"],
        class_weights_list=model_config["dl_model_config"]["class_weights_list"],
        sample_weights=model_config["dl_model_config"]["sample_weights"],
        label_smoothing_factor=model_config["dl_model_config"][
            "label_smoothing_factor"
        ],
        dropout_rate=model_config["dl_model_config"]["dropout_rate"],
        config=model_config,
        architecture_version=model_config["dl_model_config"]["architecture_version"],
        mlp_hidden_layers=model_config["dl_model_config"]["mlp_hidden_layers"],
        head_filters_settings=model_config["dl_model_config"]["head_filters_settings"],
        bands_head=model_config["dl_model_config"]["bands_head"],
    )
    model.load_state_dict(model_state_dict, strict=False)
    logger.info("Model state dict loaded successfully")

    model.eval()
    logger.info("Model set to evaluation mode")
    return model, model_class_mapping, model_config
