import torch
from torch.distributed import ReduceOp, all_reduce, is_initialized
from torch.optim.lr_scheduler import StepLR

# TODO: add scaling params to Net init and model config
# TODO: add missing params in hparams so we can check in tb while training
# TODO: add scaling_params...
# TODO: add mIoU metric for training
# TODO: add proper val loss training
# TODO: split segmentation head in 2 heads
# TODO: modify the dataloader to only scale the DEM and let the model handle the rest


def compute_iou(preds, true_labels, num_classes=9):
    # Step 2: Flatten the predictions and true labels
    preds = preds.view(-1)  # Shape: (batch * y * x)
    true_labels = true_labels.view(-1)  # Shape: (batch * y * x)

    # Step 3: Compute IoU for each class
    iou_per_class = []
    for cls in range(num_classes):
        # True Positive (intersection)
        intersection = ((preds == cls) & (true_labels == cls)).sum().item()
        # Union (total area of both predictions and targets for this class)
        union = ((preds == cls) | (true_labels == cls)).sum().item()

        if union == 0:
            iou_per_class.append(float("nan"))  # Ignore this class if union is zero
        else:
            iou_per_class.append(intersection / union)

    # Step 4: Compute the mean IoU, ignoring NaNs
    mean_iou = torch.tensor(iou_per_class).nanmean().item()

    return mean_iou, iou_per_class


def compute_class_fraction_accuracy(preds, true_labels, num_classes=9):
    # Step 2: Calculate the fraction of each class in predictions and targets
    batch_size = preds.size(0)
    pred_fractions = torch.zeros(batch_size, num_classes, device=preds.device)
    target_fractions = torch.zeros(batch_size, num_classes, device=true_labels.device)

    for cls in range(num_classes):
        # For each batch, count pixels belonging to the current class
        pred_fractions[:, cls] = (preds == cls).float().sum(dim=(1, 2)) / (
            preds.size(1) * preds.size(2)
        )
        target_fractions[:, cls] = (true_labels == cls).float().sum(dim=(1, 2)) / (
            true_labels.size(1) * true_labels.size(2)
        )

    # Step 3: Compute class-wise absolute differences (accuracy metric)
    class_accuracies = 1 - torch.abs(
        pred_fractions - target_fractions
    )  # Shape: (batch_size, num_classes)

    # Step 4: Calculate the mean accuracy per class across the batch
    mean_class_accuracy = class_accuracies.mean(dim=0)  # Shape: (num_classes,)

    # Step 5: Calculate overall accuracy by averaging across classes and batch
    overall_accuracy = mean_class_accuracy.mean().item()

    return overall_accuracy, mean_class_accuracy


def get_label_stats(outputs, targets, label):
    # Convert predictions and targets to class labels
    preds = torch.argmax(outputs, dim=1)
    true_labels = torch.argmax(targets, dim=1)

    # Accumulate true positives, false positives, and false negatives
    tp = ((preds == label) & (true_labels == label)).sum()
    fp = ((preds == label) & (true_labels != label)).sum()
    fn = ((preds != label) & (true_labels == label)).sum()

    return tp, fp, fn


# def compute_metrics(outputs, targets, num_classes=len([0, 1, 2, 3]), suffix=""):
#     # Handle suffix
#     suffix = f"_{suffix}" if suffix else ""

#     preds = torch.argmax(outputs, dim=1)  # Shape: (batch, y, x)
#     true_labels = torch.argmax(targets, dim=1)  # Shape: (batch, y, x)

#     # Compute IoU and class fraction accuracy
#     mean_iou, iou_per_class = compute_iou(preds, true_labels, num_classes)
#     overall_accuracy, mean_class_accuracy = compute_class_fraction_accuracy(
#         preds, true_labels, num_classes
#     )

#     # Create a dictionary of metrics
#     metrics = {
#         f"mean_iou{suffix}": mean_iou,
#         f"overall_accuracy{suffix}": overall_accuracy,
#     }

#     for cls, acc in enumerate(mean_class_accuracy):
#         metrics[f"class_accuracy_{NET_LABELS[cls]}{suffix}"] = acc.item()

#     for cls, iou in enumerate(iou_per_class):
#         metrics[f"class_iou_{NET_LABELS[cls]}{suffix}"] = iou

#     return metrics
