from pathlib import Path

def natural_sort(filenames):
    """
    Sorts a list of filenames in natural order.
    """

    def natural_key(filename):
        """
        Extracts the natural key from a filename.
        """
        key = []
        part = ""
        if isinstance(filename, Path):
            filename = filename.as_posix()
        for char in filename:
            if char.isdigit():
                part += char
            else:
                if part:
                    key.append(int(part))
                    part = ""
                key.append(char)
        if part:
            key.append(int(part))
        return key

    return sorted(filenames, key=natural_key)