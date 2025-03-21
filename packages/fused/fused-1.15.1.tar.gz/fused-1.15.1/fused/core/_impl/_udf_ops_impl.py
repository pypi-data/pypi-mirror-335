import json
from pathlib import Path
from typing import Any, Callable, Optional

from fused.models._codegen import MetaJson
from fused.models.api import UdfJobStepConfig
from fused.models.udf._eval_result import UdfEvaluationResult
from fused.models.udf.output import Output
from fused.models.udf.udf import GeoPandasUdfV2, load_udf_from_response_data


def get_step_config_from_server(
    email_or_handle: Optional[str],
    slug: str,
    cache_key: Any,
    _is_public: bool = False,
) -> UdfJobStepConfig:
    from fused.api.api import FusedAPI

    # cache_key is unused
    api = FusedAPI()
    if _is_public:
        obj = api._get_public_udf(slug)
    else:
        obj = api._get_udf(email_or_handle, slug)
    udf = load_udf_from_response_data(obj)

    step_config = UdfJobStepConfig(udf=udf)
    return step_config


def get_github_udf_from_server(
    url: str,
    cache_key: Any,
):
    from fused.api.api import FusedAPI

    # cache_key is unused
    # TODO: Do this locally in fused-py
    api = FusedAPI(credentials_needed=False)
    obj = api._get_code_by_url(url)
    udf = load_udf_from_response_data(obj)

    step_config = UdfJobStepConfig(udf=udf)
    return step_config


def run_and_get_data(udf, *args, **kwargs):
    # TODO: This is a silly way to do this, because we have to pass parameters in such an odd way
    job = udf(*args, **kwargs)
    result = job.run_local()
    if isinstance(result, (Output, UdfEvaluationResult)):
        return result.data
    else:
        return result


def get_step_config_from_shared_token(token: str) -> UdfJobStepConfig:
    from fused.api.api import FusedAPI

    api = FusedAPI()
    obj = api._get_udf_by_token(token)
    udf = load_udf_from_response_data(obj)
    return UdfJobStepConfig(udf=udf)


def get_udf_from_file(path: Path) -> GeoPandasUdfV2:
    data = {
        "name": path.stem,
        "entrypoint": "udf",
        "type": "geopandas_v2",
        "code": path.read_bytes().decode("utf8"),
    }
    return GeoPandasUdfV2.model_validate(data)


def get_udf_from_code(code: str, name: Optional[str] = None) -> GeoPandasUdfV2:
    data = {
        "name": name or "udf",
        "entrypoint": "udf",
        "type": "geopandas_v2",
        "code": code,
    }
    return GeoPandasUdfV2.model_validate(data)


def get_udf_from_directory(load_callback: Callable[[str], bytes]) -> GeoPandasUdfV2:
    meta_contents = json.loads(load_callback("meta.json"))
    meta = MetaJson.model_validate(meta_contents)

    if len(meta.job_config.steps) != 1:
        raise ValueError(
            f"meta.json is not in expected format: {len(meta.job_config.steps)=}"
        )

    if meta.job_config.steps[0]["type"] != "udf":
        raise ValueError(
            f'meta.json is not in expected format: {meta.job_config.steps[0]["type"]=}'
        )

    # Load the source code into the UDF model
    udf_dict = meta.job_config.steps[0]["udf"]
    source_file_name = udf_dict["source"]

    code = load_callback(source_file_name).decode("utf-8")
    udf_dict["code"] = code
    del udf_dict["source"]

    # Do the same for headers
    for header_dict in udf_dict["headers"]:
        header_source_file_name = header_dict.get("source_file")
        if header_source_file_name:
            del header_dict["source_file"]
            header_code = load_callback(header_source_file_name).decode("utf-8")
            header_dict["source_code"] = header_code

    return GeoPandasUdfV2.model_validate(udf_dict)
