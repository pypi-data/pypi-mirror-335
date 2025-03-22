from femtum_sdk.database.adapter.tags_adapter import ApplyTagsToDataframe
import pandas as pd
from femtum_sdk.database.grpc.result_pb2 import (
    SpectrumResult,
)


def SweepResulToDataframe(
    item: SpectrumResult,
    with_tags: bool = False,
) -> pd.DataFrame:
    dataframeDict = {
        "Powers": list(map(float, item.Data.PowersArray)),
        "Wavelengths": list(map(float, item.Data.WavelengthsArray)),
    }

    dataframe = pd.DataFrame(dataframeDict)

    if with_tags is True:
        dataframe = ApplyTagsToDataframe(dataframe, item.Tags)

    return dataframe
