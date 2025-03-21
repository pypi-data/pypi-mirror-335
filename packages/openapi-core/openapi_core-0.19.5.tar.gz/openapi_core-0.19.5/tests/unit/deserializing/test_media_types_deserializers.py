from xml.etree.ElementTree import Element

import pytest
from jsonschema_path import SchemaPath

from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.deserializing.media_types import media_type_deserializers
from openapi_core.deserializing.media_types.factories import (
    MediaTypeDeserializersFactory,
)
from openapi_core.deserializing.styles import style_deserializers_factory


class TestMediaTypeDeserializer:
    @pytest.fixture
    def deserializer_factory(self):
        def create_deserializer(
            mimetype,
            schema=None,
            encoding=None,
            parameters=None,
            media_type_deserializers=media_type_deserializers,
            extra_media_type_deserializers=None,
        ):
            return MediaTypeDeserializersFactory(
                style_deserializers_factory,
                media_type_deserializers,
            ).create(
                mimetype,
                schema=schema,
                parameters=parameters,
                encoding=encoding,
                extra_media_type_deserializers=extra_media_type_deserializers,
            )

        return create_deserializer

    @pytest.mark.parametrize(
        "mimetype,parameters,value,expected",
        [
            (
                "text/plain",
                {"charset": "iso-8859-2"},
                b"\xb1\xb6\xbc\xe6",
                "ąśźć",
            ),
            (
                "text/plain",
                {"charset": "utf-8"},
                b"\xc4\x85\xc5\x9b\xc5\xba\xc4\x87",
                "ąśźć",
            ),
            ("text/plain", {}, b"\xc4\x85\xc5\x9b\xc5\xba\xc4\x87", "ąśźć"),
            ("text/plain", {}, "somestr", "somestr"),
            ("text/html", {}, "somestr", "somestr"),
        ],
    )
    def test_plain_valid(
        self, deserializer_factory, mimetype, parameters, value, expected
    ):
        deserializer = deserializer_factory(mimetype, parameters=parameters)

        result = deserializer.deserialize(value)

        assert result == expected

    @pytest.mark.parametrize(
        "mimetype",
        [
            "application/json",
            "application/vnd.api+json",
        ],
    )
    def test_json_valid(self, deserializer_factory, mimetype):
        parameters = {"charset": "utf-8"}
        deserializer = deserializer_factory(mimetype, parameters=parameters)
        value = b'{"test": "test"}'

        result = deserializer.deserialize(value)

        assert type(result) is dict
        assert result == {"test": "test"}

    @pytest.mark.parametrize(
        "mimetype",
        [
            "application/json",
            "application/vnd.api+json",
        ],
    )
    def test_json_empty(self, deserializer_factory, mimetype):
        deserializer = deserializer_factory(mimetype)
        value = b""

        with pytest.raises(DeserializeError):
            deserializer.deserialize(value)

    @pytest.mark.parametrize(
        "mimetype",
        [
            "application/json",
            "application/vnd.api+json",
        ],
    )
    def test_json_empty_object(self, deserializer_factory, mimetype):
        deserializer = deserializer_factory(mimetype)
        value = b"{}"

        result = deserializer.deserialize(value)

        assert result == {}

    @pytest.mark.parametrize(
        "mimetype",
        [
            "application/xml",
            "application/xhtml+xml",
        ],
    )
    def test_xml_empty(self, deserializer_factory, mimetype):
        deserializer = deserializer_factory(mimetype)
        value = b""

        with pytest.raises(DeserializeError):
            deserializer.deserialize(value)

    @pytest.mark.parametrize(
        "mimetype",
        [
            "application/xml",
            "application/xhtml+xml",
        ],
    )
    def test_xml_default_charset_valid(self, deserializer_factory, mimetype):
        deserializer = deserializer_factory(mimetype)
        value = b"<obj>text</obj>"

        result = deserializer.deserialize(value)

        assert type(result) is Element

    @pytest.mark.parametrize(
        "mimetype",
        [
            "application/xml",
            "application/xhtml+xml",
        ],
    )
    def test_xml_valid(self, deserializer_factory, mimetype):
        parameters = {"charset": "utf-8"}
        deserializer = deserializer_factory(mimetype, parameters=parameters)
        value = b"<obj>text</obj>"

        result = deserializer.deserialize(value)

        assert type(result) is Element

    def test_octet_stream_empty(self, deserializer_factory):
        mimetype = "application/octet-stream"
        deserializer = deserializer_factory(mimetype)
        value = b""

        result = deserializer.deserialize(value)

        assert result == b""

    @pytest.mark.parametrize(
        "mimetype",
        [
            "image/gif",
            "image/png",
        ],
    )
    def test_octet_stream_implicit(self, deserializer_factory, mimetype):
        deserializer = deserializer_factory(mimetype)
        value = b""

        result = deserializer.deserialize(value)

        assert result == value

    def test_octet_stream_simple(self, deserializer_factory):
        mimetype = "application/octet-stream"
        schema_dict = {}
        schema = SchemaPath.from_dict(schema_dict)
        deserializer = deserializer_factory(mimetype, schema=schema)
        value = b"test"

        result = deserializer.deserialize(value)

        assert result == b"test"

    def test_urlencoded_form_empty(self, deserializer_factory):
        mimetype = "application/x-www-form-urlencoded"
        schema_dict = {}
        schema = SchemaPath.from_dict(schema_dict)
        deserializer = deserializer_factory(mimetype, schema=schema)
        value = b""

        result = deserializer.deserialize(value)

        assert result == {}

    def test_urlencoded_form_simple(self, deserializer_factory):
        mimetype = "application/x-www-form-urlencoded"
        schema_dict = {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                },
            },
        }
        schema = SchemaPath.from_dict(schema_dict)
        encoding_dict = {
            "name": {
                "style": "form",
            },
        }
        encoding = SchemaPath.from_dict(encoding_dict)
        deserializer = deserializer_factory(
            mimetype, schema=schema, encoding=encoding
        )
        value = b"name=foo+bar"

        result = deserializer.deserialize(value)

        assert result == {
            "name": "foo bar",
        }

    def test_urlencoded_complex(self, deserializer_factory):
        mimetype = "application/x-www-form-urlencoded"
        schema_dict = {
            "type": "object",
            "properties": {
                "prop": {
                    "type": "array",
                    "items": {
                        "type": "integer",
                    },
                },
            },
        }
        schema = SchemaPath.from_dict(schema_dict)
        deserializer = deserializer_factory(mimetype, schema=schema)
        value = b"prop=a&prop=b&prop=c"

        result = deserializer.deserialize(value)

        assert result == {
            "prop": ["a", "b", "c"],
        }

    def test_urlencoded_content_type(self, deserializer_factory):
        mimetype = "application/x-www-form-urlencoded"
        schema_dict = {
            "type": "object",
            "properties": {
                "prop": {
                    "type": "array",
                    "items": {
                        "type": "integer",
                    },
                },
            },
        }
        schema = SchemaPath.from_dict(schema_dict)
        encoding_dict = {
            "prop": {
                "contentType": "application/json",
            },
        }
        encoding = SchemaPath.from_dict(encoding_dict)
        deserializer = deserializer_factory(
            mimetype, schema=schema, encoding=encoding
        )
        value = b'prop=["a","b","c"]'

        result = deserializer.deserialize(value)

        assert result == {
            "prop": ["a", "b", "c"],
        }

    def test_urlencoded_deepobject(self, deserializer_factory):
        mimetype = "application/x-www-form-urlencoded"
        schema_dict = {
            "type": "object",
            "properties": {
                "color": {
                    "type": "object",
                    "properties": {
                        "R": {
                            "type": "integer",
                        },
                        "G": {
                            "type": "integer",
                        },
                        "B": {
                            "type": "integer",
                        },
                    },
                },
            },
        }
        schema = SchemaPath.from_dict(schema_dict)
        encoding_dict = {
            "color": {
                "style": "deepObject",
                "explode": True,
            },
        }
        encoding = SchemaPath.from_dict(encoding_dict)
        deserializer = deserializer_factory(
            mimetype, schema=schema, encoding=encoding
        )
        value = b"color[R]=100&color[G]=200&color[B]=150"

        result = deserializer.deserialize(value)

        assert result == {
            "color": {
                "R": "100",
                "G": "200",
                "B": "150",
            },
        }

    def test_multipart_form_empty(self, deserializer_factory):
        mimetype = "multipart/form-data"
        schema_dict = {}
        schema = SchemaPath.from_dict(schema_dict)
        deserializer = deserializer_factory(mimetype, schema=schema)
        value = b""

        result = deserializer.deserialize(value)

        assert result == {}

    def test_multipart_form_simple(self, deserializer_factory):
        mimetype = "multipart/form-data"
        schema_dict = {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "format": "binary",
                },
                "param2": {
                    "type": "string",
                    "format": "binary",
                },
            },
        }
        schema = SchemaPath.from_dict(schema_dict)
        encoding_dict = {
            "param1": {
                "contentType": "application/octet-stream",
            },
        }
        encoding = SchemaPath.from_dict(encoding_dict)
        parameters = {
            "boundary": "===============2872712225071193122==",
        }
        deserializer = deserializer_factory(
            mimetype, schema=schema, parameters=parameters, encoding=encoding
        )
        value = (
            b"--===============2872712225071193122==\n"
            b"Content-Type: text/plain\nMIME-Version: 1.0\n"
            b'Content-Disposition: form-data; name="param1"\n\ntest\n'
            b"--===============2872712225071193122==\n"
            b"Content-Type: text/plain\nMIME-Version: 1.0\n"
            b'Content-Disposition: form-data; name="param2"\n\ntest2\n'
            b"--===============2872712225071193122==--\n"
        )

        result = deserializer.deserialize(value)

        assert result == {
            "param1": b"test",
            "param2": b"test2",
        }

    def test_multipart_form_array(self, deserializer_factory):
        mimetype = "multipart/form-data"
        schema_dict = {
            "type": "object",
            "properties": {
                "file": {
                    "type": "array",
                    "items": {},
                },
            },
        }
        schema = SchemaPath.from_dict(schema_dict)
        parameters = {
            "boundary": "===============2872712225071193122==",
        }
        deserializer = deserializer_factory(
            mimetype, schema=schema, parameters=parameters
        )
        value = (
            b"--===============2872712225071193122==\n"
            b"Content-Type: text/plain\nMIME-Version: 1.0\n"
            b'Content-Disposition: form-data; name="file"\n\ntest\n'
            b"--===============2872712225071193122==\n"
            b"Content-Type: text/plain\nMIME-Version: 1.0\n"
            b'Content-Disposition: form-data; name="file"\n\ntest2\n'
            b"--===============2872712225071193122==--\n"
        )

        result = deserializer.deserialize(value)

        assert result == {
            "file": [b"test", b"test2"],
        }

    def test_custom_simple(self, deserializer_factory):
        deserialized = "x-custom"

        def custom_deserializer(value):
            return deserialized

        custom_mimetype = "application/custom"
        extra_media_type_deserializers = {
            custom_mimetype: custom_deserializer,
        }
        deserializer = deserializer_factory(
            custom_mimetype,
            extra_media_type_deserializers=extra_media_type_deserializers,
        )
        value = b"{}"

        result = deserializer.deserialize(
            value,
        )

        assert result == deserialized
