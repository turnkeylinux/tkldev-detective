from libtklint.classifier import FileClassifier, FileItem, register_classifier
from os.path import isfile


@register_classifier
class ShebangClassifier(FileClassifier):
    WEIGHT = 10

    def classify(self, item: FileItem):
        if isfile(item.abspath):
            with open(item.abspath, "r") as fob:
                shebang = fob.read(512).splitlines()[0].strip().split()[0].strip()

            if shebang.startswith("#!"):
                item.add_tags(self, [f"shebang:{shebang[2:]}"])
