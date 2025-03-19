from wowool.document.factory import Factory
from typing import Optional, Union
from pathlib import Path
from wowool.utility.path import expand_path
from wowool.document.factory import Factory as DocumentCollection


def make_document_collection(
    text: Optional[Union[list, str]] = None,
    file: Optional[Union[Path, str]] = None,
    cleanup: Optional[bool] = None,
    encoding="utf-8",
    pattern="**/*.txt",
    **kwargs,
):
    stripped = None
    if cleanup:
        stripped = lambda s: "".join(i for i in s if 31 < ord(i) < 127 or ord(i) == 0xD or ord(i) == 0xA)

    if file:
        options = {}
        options["encoding"] = encoding
        if cleanup:
            options["cleanup"] = stripped
        fn = expand_path(file)

        return DocumentCollection.glob(fn, stripped=stripped)
        # folder, pattern_ = Factory.split_path_on_wildcards(fn)
        # if folder.exists():
        #     if folder.is_dir():
        #         doc_collection.extend(Factory.glob(fn, pattern_))
        #     else:
        #         doc_collection.append(Factory.create(file, **options))
        # else:
        #     raise RuntimeError(f"File or folder not found. '{fn}'")
    if text:
        doc_collection = []
        if isinstance(text, str):
            doc_collection.append(Factory.create(text))
        elif isinstance(text, list):
            for text_ in text:
                doc_collection.append(Factory.create(text_))

    return doc_collection
