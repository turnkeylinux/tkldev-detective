from libtkldet.classifier import FileClassifier, FileItem, register_classifier
from os.path import isfile


@register_classifier
class ShebangClassifier(FileClassifier):
    WEIGHT = 10

    def classify(self, item: FileItem):
        if isfile(item.abspath):
            with open(item.abspath, "rb") as fob:
                shebang = b''
                head = fob.read(512)

                if b'\n' in head:
                    shebang = head.split(b'\n')[0].strip()
                    if shebang:
                        shebang = shebang.split()[0].strip()
            shebang = str(shebang)

            if shebang.startswith("#!"):
                item.add_tags(self, [f"shebang:{shebang[2:]}"])
