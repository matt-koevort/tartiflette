import pytest

from tartiflette import TartifletteError
from tartiflette.language.ast import Location
from tartiflette.language.parsers.lark import parse_to_document
from tartiflette.validation.rules import UniqueInputFieldNamesRule
from tartiflette.validation.validate import validate_sdl


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sdl,expected",
    [
        (
            """
            input AnInput
            type Query {
              field(arg: AnInput = { f: true }): String
            }
            """,
            [],
        ),
        (
            """
            input AnInput
            type Query {
              field(
                arg1: AnInput = { f: true },
                arg2: AnInput = { f: true },
              ): String
            }
            """,
            [],
        ),
        (
            """
            input AnInput
            type Query {
              field(
                arg: AnInput = { f1: "value", f2: "value", f3: "value" }
              ): String
            }
            """,
            [],
        ),
        (
            """
            input AnInput
            type Query {
              field(arg: AnInput = {
                deep: {
                  deep: {
                    id: 1
                  }
                  id: 1
                }
                id: 1
              }): String
            }
            """,
            [],
        ),
        (
            """
            input AnInput
            type Query {
              field(arg: AnInput = { f1: "value", f1: "value" }): String
            }
            """,
            [
                TartifletteError(
                    message="There can be only one input field named < f1 >.",
                    locations=[
                        Location(line=4, column=38, line_end=4, column_end=40),
                        Location(line=4, column=51, line_end=4, column_end=53),
                    ],
                )
            ],
        ),
        (
            """
            input AnInput
            type Query {
              field(
                arg: AnInput = { f1: "value", f1: "value", f1: "value" }
              ): String
            }
            """,
            [
                TartifletteError(
                    message="There can be only one input field named < f1 >.",
                    locations=[
                        Location(line=5, column=34, line_end=5, column_end=36),
                        Location(line=5, column=47, line_end=5, column_end=49),
                    ],
                ),
                TartifletteError(
                    message="There can be only one input field named < f1 >.",
                    locations=[
                        Location(line=5, column=34, line_end=5, column_end=36),
                        Location(line=5, column=60, line_end=5, column_end=62),
                    ],
                ),
            ],
        ),
        (
            """
            input AnInput
            type Query {
              field(arg: AnInput = { f1: {f2: "value", f2: "value" }}): String
            }
            """,
            [
                TartifletteError(
                    message="There can be only one input field named < f2 >.",
                    locations=[
                        Location(line=4, column=43, line_end=4, column_end=45),
                        Location(line=4, column=56, line_end=4, column_end=58),
                    ],
                )
            ],
        ),
        (
            """
            input AnInput
            type Query {
              field(arg: AnInput = { f1: {f2: "value", f2: "value" }}): String
              anotherField(
                arg: AnInput = { fa: {fb: "value", fb: "value" }}
              ): String
            }
            """,
            [
                TartifletteError(
                    message="There can be only one input field named < f2 >.",
                    locations=[
                        Location(line=4, column=43, line_end=4, column_end=45),
                        Location(line=4, column=56, line_end=4, column_end=58),
                    ],
                ),
                TartifletteError(
                    message="There can be only one input field named < fb >.",
                    locations=[
                        Location(line=6, column=39, line_end=6, column_end=41),
                        Location(line=6, column=52, line_end=6, column_end=54),
                    ],
                ),
            ],
        ),
        (
            """
            input AnInput
            type Query {
              field(arg: AnInput = { f1: {f2: "value", f2: "value" }}): String
              anotherField(
                arg: AnInput = { fa: {fb: "value", fb: "value" }, fa: true }
              ): String
            }
            """,
            [
                TartifletteError(
                    message="There can be only one input field named < f2 >.",
                    locations=[
                        Location(line=4, column=43, line_end=4, column_end=45),
                        Location(line=4, column=56, line_end=4, column_end=58),
                    ],
                ),
                TartifletteError(
                    message="There can be only one input field named < fb >.",
                    locations=[
                        Location(line=6, column=39, line_end=6, column_end=41),
                        Location(line=6, column=52, line_end=6, column_end=54),
                    ],
                ),
                TartifletteError(
                    message="There can be only one input field named < fa >.",
                    locations=[
                        Location(line=6, column=34, line_end=6, column_end=36),
                        Location(line=6, column=67, line_end=6, column_end=69),
                    ],
                ),
            ],
        ),
    ],
)
async def test_unique_input_field_names(sdl, expected):
    assert (
        validate_sdl(parse_to_document(sdl), rules=[UniqueInputFieldNamesRule])
        == expected
    )
