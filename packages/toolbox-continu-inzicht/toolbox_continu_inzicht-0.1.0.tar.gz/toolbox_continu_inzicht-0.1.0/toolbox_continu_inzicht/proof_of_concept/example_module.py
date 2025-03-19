from pydantic.dataclasses import dataclass
from toolbox_continu_inzicht.base.data_adapter import DataAdapter
import pandas as pd
from typing import Optional, ClassVar


@dataclass(config={"arbitrary_types_allowed": True})
class ValuesDivideTwo:
    """
    Voorbeeld class die laat zien hoe de architectuur werkt door waardes delen door twee te doen

    Attributes
    ----------
    data_adapter: DataAdapter
        De data adapter die de input en output regelt
    df_in: Optional[pd.DataFrame] | None
        De input data
    df_out: Optional[pd.DataFrame] | None
        De output data
    input_schema: ClassVar[dict[str, str]]
        De input schema

    """

    data_adapter: DataAdapter
    df_in: Optional[pd.DataFrame] | None = None
    df_out: Optional[pd.DataFrame] | None = None

    input_schema: ClassVar[dict[str, str]] = {
        "value": "float",
    }

    def run(self, input: str, output: str):
        """Runt de funcies en stuur de df terug"""
        self.df_in = self.data_adapter.input(input, schema=self.input_schema)

        self.df_out = self.divide_two(self.df_in)
        self.data_adapter.output(output, self.df_out)

    @staticmethod
    def divide_two(dataframe: pd.DataFrame) -> pd.DataFrame:
        """Vermenigvuldigd de meetstation waardes met 2 als voorbeeld"""
        df = dataframe.copy(deep=True)
        df["value"] = df["value"] / 2
        return df


@dataclass(config={"arbitrary_types_allowed": True})
class ValuesTimesTwo:
    """
    Voorbeeld class die laat zien hoe de architectuur werkt door waardes keer twee te doen


    Attributes
    ----------
    data_adapter: DataAdapter
        De data adapter die de input en output regelt
    df_in: Optional[pd.DataFrame] | None
        De input data
    df_out: Optional[pd.DataFrame] | None
        De output data
    input_schema: ClassVar[dict[str, str]]
        De input schema

    """

    data_adapter: DataAdapter
    df_in: Optional[pd.DataFrame] | None = None
    df_out: Optional[pd.DataFrame] | None = None

    input_schema: ClassVar[dict[str, str]] = {
        "value": "float",
    }

    def run(self, input: str, output: str):
        """Runt de funcies en stuur de df terug"""

        self.df_in = self.data_adapter.input(input, self.input_schema)
        self.df_out = self.times_two(self.df_in)
        self.data_adapter.output(output, self.df_out)

    @staticmethod
    def times_two(dataframe: pd.DataFrame) -> pd.DataFrame:
        """Deelt de meetstation waardes door 2 als voorbeeld"""
        df = dataframe.copy(deep=True)
        df["value"] = df["value"] * 2
        return df
