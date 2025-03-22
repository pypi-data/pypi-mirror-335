from evotrain.labels import WorldCoverLabelsColors

# NET_LABELS = [10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100]
NET_LABELS = [50]

mapping = WorldCoverLabelsColors.id_to_class_name_mapping()
NET_LABELS_MAPPING = {key: mapping[key] for key in NET_LABELS if key in mapping}

if __name__ == "__main__":
    print(NET_LABELS_MAPPING)
