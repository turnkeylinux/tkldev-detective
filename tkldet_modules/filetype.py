from libtkldet.classifier import FileClassifier, FileItem, register_classifier
from os.path import splitext, isfile


@register_classifier
class FiletypeClassifier(FileClassifier):
    WEIGHT = 10

    def classify(self, item: FileItem):
        if isfile(item.abspath) and "." in item.value:
            item.add_tags(self, [f"ext:{splitext(item.value)[1][1:]}"])
