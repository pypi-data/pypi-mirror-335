# Femtum SDK - Python

[![NuGet](https://img.shields.io/nuget/v/Femtum.SDK.svg)](https://www.nuget.org/packages/Femtum.SDK)

### Installation

To install the Femtum SDK, use the following command:

##### pip

```bash
pip install femtum-sdk
```

##### poetry

```bash
poetry add femtum-sdk
```

### Usage

Here is a basic example of how to use the Femtum SDK:

1. Start the SDK Server
2. Use SDK in your code

```python
# Find results by page and get sweep data

from femtum_sdk.adapter.analysis_pandas_adapter import SweepResulToDataframe
from femtum_sdk.core.result_pb2 import (
    FindResultByIdRequest,
    ListByPageResultsRequest,
    OptionalSweepResult,
    ResultsFilterRequest,
    ResultsPage,
)

from femtum_sdk import FemtumSdk
from femtum_sdk.core.tag_pb2 import Tag

# Make sure the API server is running before running next steps
with FemtumSdk() as sdk:
    page: ResultsPage = sdk.trimming.result.ListByPage(
        ListByPageResultsRequest(
            PageSize=10,
            PageNumber=1,
            Filters=ResultsFilterRequest(
                WaferName="MyWafer",
                ReticleName="MyReticle",
                DieName="MyDie",
                CircuitName="MyCircuit",
                Tags=[Tag(Key="ShotNumber", Value="6")],
            ),
        )
    )

    items = list(page.Items)
    print(items)

    firstResultWithData: OptionalSweepResult = sdk.trimming.result.FindSweepById(
        FindResultByIdRequest(Id=page.Items[0].Id)
    )
    result = firstResultWithData.Result

    print(result.WavelengthsArray)
    print(result.WavelengthsArray)
    print(result.PowersArray)

    dataframe = SweepResulToDataframe(result)
    print(dataframe)

```

#### With Specified SDK server url

```python
with FemtumSdk(hostUrl=api_server.get_grpc_url()) as sdk:
  request = FindResultDataRequestDto()
  result: SpectrumProviderSweepResultArray = (
      sdk.analysis.FindSpectrumProviderSweepResults(request)
  )

  print(result.Items)
```
