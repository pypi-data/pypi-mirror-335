from io import StringIO
from typing import Union, Any, Optional, Generator
from wowool.annotation import Concept, Annotation, Token, Sentence
import json
from wowool.io.provider import InputProvider
from wowool.io.provider import Factory
from wowool.diagnostic import Diagnostics
from wowool.analysis import (
    _filter_pass_thru_concept,
    Analysis,
    AnalysisInputProvider,
)
from wowool.analysis import APP_ID as APP_ID_ANALYSIS
from typing import cast
from wowool.document.apps.topics import convert_topics, Topic
from wowool.document.apps.themes import convert_themes, Theme
from wowool.document.apps.chunks import convert_chunks, Chunk

RESULTS = "results"
DIAGNOSTICS = "diagnostics"


def to_json_convert(obj):
    if isinstance(obj, set):
        return str(list(obj))
    return obj


STR_MISSING_ANALYSIS = "Document has not been processed by a Language"


class Document:
    """
    :class:`Document` is a class that stores the data related to a document. Instances of this class are returned from a Pipeline, a Language or a Domain object.
    """

    def __init__(
        self,
        data: Optional[Union[str, bytes, InputProvider]] = None,
        id: Optional[str] = None,
        provider_type: Optional[str] = None,
        encoding="utf8",
        metadata=None,
        **kwargs,
    ):
        """
        Initialize a :class:`Document` instance

        .. literalinclude:: ../../../../common/py/eot/wowool/init_document.py

        :param data: Data to be processed
        :type data: A ``str``, ``bytes``, or an :class:`InputProvider <wowool.io.InputProviders>`
        :param id: Unique identifier for the document. If not provided, and ``data`` is an :class:`InputProvider <wowool.io.InputProviders>`, then the ``id`` will be set automatically
        :type id: ``str``
        :param type: Document type. Defaults to ``'txt'``
        :type type: ``str``
        :param encoding: Encoding of the ``data``. Defaults to ``'utf8'``
        :type encoding: ``str``

        :return: An initialized document
        :rtype: :class:`Document`
        """

        if data is not None:
            if isinstance(data, InputProvider):
                assert id is None, "'id' cannot be set when using 'input_provider'"
                self.input_provider = data
            else:
                self.input_provider = Factory.create(
                    id=id,
                    data=data,
                    provider_type=provider_type,
                    encoding=encoding,
                    **kwargs,
                )

            assert isinstance(self.input_provider, InputProvider), f"{type(self.input_provider)} is not derived from InputProvider"
        else:
            assert id is not None, "'id' is required when 'input_provider' is None"

            self.input_provider = Factory.create(
                id=id,
                data=None,
                provider_type=provider_type,
                encoding=encoding,
                **kwargs,
            )

        assert self.input_provider, "could not create inputprovider."
        self._apps = {}
        self.kwargs = {**kwargs}
        self.metadata = metadata if metadata != None else {}

    @property
    def id(self) -> str:
        """
        :return: The unique identifier of the document
        :rtype: ``str``
        """
        return self.input_provider.id

    @property
    def text(self) -> Union[str, None]:
        """
        :return: The text data of the document
        :rtype: 'str | None'
        """
        return self.input_provider.text if self.input_provider else ""

    @property
    def analysis(self):
        """
        :return: The :class:`Analysis <wowool.analysis.Analysis>` of the document, containing the :class:`Sentences <wowool.annotation.sentence.Sentence>`, :class:`Tokens <wowool.annotation.token.Token>` and :class:`Concepts <wowool.annotation.concept.Concept>`, or ``None`` if the document has not been processed by a Language

        .. literalinclude:: ../../../../common/py/eot/wowool/init_document_analysis.py

        :rtype: :class:`Analysis <wowool.analysis.Analysis>`
        """
        return cast(Analysis, self.results(APP_ID_ANALYSIS))

    def app_ids(self):
        """
        Iterate over the application identifiers

        :return: A generator expression yielding application identifiers
        :rtype: ``str``
        """
        for app_id in self._apps:
            yield app_id

    def has(self, app_id: str) -> bool:
        return self.has_results(app_id)

    def has_results(self, app_id: str) -> bool:
        """
        :return: Whether the application, as identified by the given application identifier, is in the document
        :rtype: ``bool``
        """
        return app_id in self._apps

    def add_results(self, app_id: str, results):
        """
        Add the given application results to the document

        :param app_id: Application identifier
        :type app_id: ``str``
        :param results: Application results
        :type results: A JSON serializable object type
        """
        if app_id in self._apps:
            self._apps[app_id][RESULTS] = results
        else:
            self._apps[app_id] = {RESULTS: results}
        return results

    def results(self, app_id: str) -> Union[Any, None]:
        """
        :return: The results of the given application. See the different type of :ref:`application results <apps>`

        :param app_id: Application identifier
        :type app_id: ``str``
        :param defaults: The defaults result to create when the application identifier is not present
        :type default: Any JSON serializable object
        """
        if app_id in self._apps and RESULTS in self._apps[app_id]:
            return self._apps[app_id][RESULTS]

    def add_diagnostics(self, app_id: str, diagnostics: Diagnostics):
        """
        Add the given application diagnostics to the document

        :param app_id: Application identifier
        :type app_id: ``str``
        :param diagnostics: Application diagnostics
        :type diagnostics: :class:`Diagnostics <wowool.diagnostic.Diagnostics>`
        """
        if app_id in self._apps:
            self._apps[app_id][DIAGNOSTICS] = diagnostics
        else:
            self._apps[app_id] = {DIAGNOSTICS: diagnostics}

    def has_diagnostics(self, app_id: str = None) -> bool:
        """
        :param app_id: Application identifier
        :type app_id: ``str`` or ``None``
        :return: Whether the document contains diagnostics for the given application or any diagnostics if no application identifier is provided
        :rtype: ``bool``
        """
        if app_id is None:
            for app_id in self._apps:
                if DIAGNOSTICS in self._apps[app_id]:
                    return True
            return False
        else:
            if app_id in self._apps and DIAGNOSTICS in self._apps[app_id]:
                return True
            else:
                return False

    def diagnostics(self, app_id: str = None) -> Diagnostics:
        """
        :param app_id: Application identifier
        :type app_id: ``str`` or ``None``

        :return: The diagnostics of the given application. See the different type of :ref:`application results <apps>`
        :rtype: :class:`Diagnostics <wowool.diagnostic.Diagnostics>`
        """
        if app_id is None:
            diagnostics = Diagnostics()
            for _, app_data in self._apps.items():
                if DIAGNOSTICS in app_data:
                    diagnostics.extend(app_data[DIAGNOSTICS])
            return diagnostics
        else:
            if app_id in self._apps and DIAGNOSTICS in self._apps[app_id]:
                return self._apps[app_id][DIAGNOSTICS]
            else:
                raise ValueError(f"App '{app_id}' has no diagnostics")

    def to_json(self) -> dict:
        """
        :return: A dictionary representing a JSON object of the document
        :rtype: ``dict``
        """
        from json import JSONEncoder

        class Encoder(JSONEncoder):
            def default(self, obj):
                if isinstance(obj, set):
                    return str(list(obj))
                else:
                    return getattr(obj, "to_json")() if hasattr(obj, "to_json") else super().default(obj)

        document = {"id": self.id, "apps": self._apps}
        return json.loads(json.dumps(document, cls=Encoder))

    @staticmethod
    def from_json(document_json: dict):
        assert "id" in document_json, "Invalid Document json format"
        assert "apps" in document_json, "Invalid Document json format"

        doc = Document(id=document_json["id"])
        doc._apps = document_json["apps"]

        if APP_ID_ANALYSIS in doc._apps:
            analysis_ = doc._apps[APP_ID_ANALYSIS]
            assert isinstance(analysis_, dict), f"Expected dict, not '{type(analysis_)}'"
            # phforest : this should no be a assert, in case we have errors there will be no results.
            # assert RESULTS in analysis_, f"Missing {RESULTS} in {APP_ID_ANALYSIS}"
            if RESULTS in analysis_:
                analysis = Analysis.parse(analysis_[RESULTS])
                doc.input_provider = AnalysisInputProvider(analysis, doc.id)
                doc.add_results(APP_ID_ANALYSIS, analysis)

        for _, app_data in doc._apps.items():
            if DIAGNOSTICS in app_data:
                app_data[DIAGNOSTICS] = Diagnostics.from_json(app_data[DIAGNOSTICS])

        return doc

    def concepts(self, filter=_filter_pass_thru_concept):
        """
        Access the concepts in the analysis of the document

        :param filter: Optional filter to select or discard concepts
        :type filter: Functor accepting a :class:`Concept <wowool.annotation.concept.Concept>` and returning a ``bool``

        :return: A generator expression yielding the concepts in the processed document
        :rtype: :class:`Concepts <wowool.annotation.concept.Concept>`
        """
        return self.analysis.concepts(filter) if self.analysis else iter([])

    def __repr__(self):
        sz = len(self.text) if self.text else 0
        text = '"' + self.text[:50].strip().replace("\n", " ") + '"' if self.text else None
        return f"""<Document id="{self.id}" size={sz} text={text}>"""

    def __str__(self):
        with StringIO() as output:
            if self.analysis:
                output.write(str(self.analysis))
            else:
                output.write(self.__repr__())

            # print the rest of the applications.
            for app_id, app_data in self._apps.items():
                if app_id == APP_ID_ANALYSIS:
                    # we already have printed the self.analysis
                    continue

                if RESULTS in app_data:
                    output.write(f"{app_id}, {json.dumps(app_data[RESULTS], indent=2)}\n")
                elif DIAGNOSTICS in app_data:
                    output.write(f"{app_id}, {app_data[DIAGNOSTICS].to_json()}\n")

            return output.getvalue()

    @property
    def entities(self) -> Generator[Concept, Any, None]:
        """
        :return: The entities of the document
        :rtype: ``Generator``
        """
        if self.analysis:
            yield from self.analysis.entities
        else:
            raise ValueError(STR_MISSING_ANALYSIS)

    @property
    def tokens(self) -> Generator[Token, Any, None]:
        """
        :return: The tokens of the document
        :rtype: ``Generator``
        """
        if self.analysis:
            yield from self.analysis.tokens
        else:
            raise ValueError(STR_MISSING_ANALYSIS)

    @property
    def annotations(self) -> Generator[Annotation, Any, None]:
        """
        :return: The annotations of the document
        :rtype: ``list``
        """
        if self.analysis:
            yield from self.analysis.annotations
        else:
            raise ValueError(STR_MISSING_ANALYSIS)

    @property
    def sentences(self) -> Generator[Sentence, Any, None]:
        """
        :return: The annotations of the document
        :rtype: ``list``
        """

        if self.analysis:
            yield from self.analysis.sentences
        else:
            raise ValueError(STR_MISSING_ANALYSIS)

    @property
    def topics(self) -> list[Topic] | list:
        """
        :return: The topics of the document
        :rtype: ``list``
        """
        if self.has("wowool_topic_identifier"):
            return convert_topics(self.results("wowool_topic_identifier"))
        else:
            return []

    @property
    def categories(self) -> list[Theme] | list:
        """
        :return: The categories of the document
        :rtype: ``list``
        """
        if self.has("wowool_semantic_theme"):
            return convert_themes(self.results("wowool_semantic_theme"))
        else:
            return []

    @property
    def chunks(self) -> list[Chunk] | list:
        """
        :return: The chunks data of the document
        :rtype: ``list``
        """
        if self.has("wowool_chunks"):
            return convert_chunks(self.results("wowool_chunks"))
        else:
            return []

    @property
    def themes(self) -> list[Theme] | list:
        """
        :return: The categories of the document
        :rtype: ``list``
        """
        return self.categories

    @property
    def language(self):
        """
        :return: The language of the document
        :rtype: ``str``
        """
        if self.has("wowool_language_identifier"):
            return self.results("wowool_language_identifier")["language"]
        else:
            if self.has(APP_ID_ANALYSIS):
                language = self.results(APP_ID_ANALYSIS).language
                if "@" in language:
                    return language.split("@")[0]
                return self.results(APP_ID_ANALYSIS).language
            else:
                return None
