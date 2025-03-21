import sys
import time
import warnings
from functools import partial
from typing import (
    TYPE_CHECKING,
    Any,
    Coroutine,
    Dict,
    Literal,
    Optional,
    Union,
    overload,
)

from fused._options import options as OPTIONS

if TYPE_CHECKING:
    import geopandas as gpd
    import pandas as pd
    import xarray as xr

from fused._udf.decorators import _parse_ttl
from fused.models.api.udf_access_token import is_udf_token
from fused.models.udf._eval_result import UdfEvaluationResult
from fused.types import UdfRuntimeError
from fused.warnings import FusedDeprecationWarning, FusedIgnoredWarning, FusedWarning

from .core import (
    run_file,
    run_file_async,
    run_shared_file,
    run_shared_file_async,
    run_shared_tile,
    run_shared_tile_async,
    run_tile,
    run_tile_async,
)
from .core._impl._realtime_ops_impl import default_run_engine
from .core._impl._reimports import GeoPandasUdfV2, UdfAccessToken, UdfJobStepConfig

ResultType = Union["xr.Dataset", "pd.DataFrame", "gpd.GeoDataFrame"]


@overload
def run(
    udf: Union[str, None, UdfJobStepConfig, GeoPandasUdfV2, UdfAccessToken] = None,
    *args,
    x: Optional[int] = None,
    y: Optional[int] = None,
    z: Optional[int] = None,
    sync: Literal[True] = True,
    engine: Optional[Literal["remote", "local"]] = None,
    type: Optional[Literal["tile", "file"]] = None,
    max_retry: int = 0,
    cache_max_age: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    _include_log: Optional[bool] = False,
    _return_response: Literal[False] = False,
    **kw_parameters,
) -> ResultType:
    ...


@overload
def run(
    udf: Union[str, None, UdfJobStepConfig, GeoPandasUdfV2, UdfAccessToken] = None,
    *args,
    x: Optional[int] = None,
    y: Optional[int] = None,
    z: Optional[int] = None,
    sync: Literal[True] = True,
    engine: Optional[Literal["remote", "local"]] = None,
    type: Optional[Literal["tile", "file"]] = None,
    max_retry: int = 0,
    cache_max_age: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    _include_log: Optional[bool] = False,
    _return_response: Literal[True] = True,
    **kw_parameters,
) -> UdfEvaluationResult:
    ...


@overload
def run(
    udf: Union[str, None, UdfJobStepConfig, GeoPandasUdfV2, UdfAccessToken] = None,
    *args,
    x: Optional[int] = None,
    y: Optional[int] = None,
    z: Optional[int] = None,
    sync: Literal[False] = False,
    engine: Optional[Literal["remote", "local"]] = None,
    type: Optional[Literal["tile", "file"]] = None,
    max_retry: int = 0,
    cache_max_age: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    _include_log: Optional[bool] = False,
    _return_response: Literal[False] = False,
    **kw_parameters,
) -> Coroutine[ResultType, None, None]:
    ...


def run(
    udf: Union[str, None, UdfJobStepConfig, GeoPandasUdfV2, UdfAccessToken] = None,
    *args,
    x: Optional[int] = None,
    y: Optional[int] = None,
    z: Optional[int] = None,
    sync: bool = True,
    engine: Optional[Literal["remote", "local"]] = None,
    type: Optional[Literal["tile", "file"]] = None,
    max_retry: int = 0,
    cache_max_age: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    _include_log: Optional[bool] = False,
    _return_response: Optional[bool] = False,
    **kw_parameters,
) -> Union[
    ResultType,
    Coroutine[ResultType, None, None],
    UdfEvaluationResult,
    Coroutine[UdfEvaluationResult, None, None],
]:
    """
    Executes a user-defined function (UDF) with various execution and input options.

    This function supports executing UDFs in different environments (local or remote),
    with different types of inputs (tile coordinates, geographical bounding boxes, etc.), and
    allows for both synchronous and asynchronous execution. It dynamically determines the execution
    path based on the provided parameters.

    Args:
        udf (str, GeoPandasUdfV2 or UdfJobStepConfig): the UDF to execute.
            The UDF can be specified in several ways:
            - A string representing a UDF name or UDF shared token.
            - A UDF object.
            - A UdfJobStepConfig object for detailed execution configuration.
        x, y, z: Tile coordinates for tile-based UDF execution.
        sync: If True, execute the UDF synchronously. If False, execute asynchronously.
        engine: The execution engine to use ('remote' or 'local').
        type: The type of UDF execution ('tile' or 'file').
        max_retry: The maximum number of retries to attempt if the UDF fails.
            By default does not retry.
        cache_max_age: The maximum age when returning a result from the cache.
            Supported units are seconds (s), minutes (m), hours (h), and days (d) (e.g. “48h”, “10s”, etc.).
            Default is `None` so a UDF run with `fused.run()` will follow `cache_max_age` defined in `@fused.udf()` unless this value is changed.
        parameters: Additional parameters to pass to the UDF.
        **kw_parameters: Additional parameters to pass to the UDF.

    Raises:
        ValueError: If the UDF is not specified or is specified in more than one way.
        TypeError: If the first parameter is not of an expected type.
        Warning: Various warnings are issued for ignored parameters based on the execution path chosen.

    Returns:
        The result of the UDF execution, which varies based on the UDF and execution path.

    Examples:


        Run a UDF saved in the Fused system:
        ```py
        fused.run("username@fused.io/my_udf_name")
        ```

        Run a UDF saved in GitHub:
        ```py
        loaded_udf = fused.load("https://github.com/fusedio/udfs/tree/main/public/Building_Tile_Example")
        fused.run(loaded_udf, bbox=bbox)
        ```

        Run a UDF saved in a local directory:
        ```py
        loaded_udf = fused.load("/Users/local/dir/Building_Tile_Example")
        fused.run(loaded_udf, bbox=bbox)
        ```

    Note:
        This function dynamically determines the execution path and parameters based on the inputs.
        It is designed to be flexible and support various UDF execution scenarios.
    """
    from fused._optional_deps import HAS_GEOPANDAS, HAS_MERCANTILE, HAS_SHAPELY

    job_step: Optional[UdfJobStepConfig] = None
    token: Optional[str] = None
    udf_email: Optional[str] = None
    udf_name: Optional[str] = None

    if "token" in kw_parameters:
        token = kw_parameters.pop("token")
        if udf is not None:
            warnings.warn(
                "token parameter is being ignored in favor of the first positional parameter.",
                FusedIgnoredWarning,
            )
        else:
            udf = token
        warnings.warn(
            "The 'token' keyword is deprecated. You can pass the token as the first "
            "argument instead (i.e. replace 'fused.run(token=<token>)' with "
            "'fused.run(<token>)')",
            FusedDeprecationWarning,
        )

    elif "udf_email" in kw_parameters and "udf_name" in kw_parameters:
        udf_email = kw_parameters.pop("udf_email")
        udf_name = kw_parameters.pop("udf_name")
        if udf is not None:
            warnings.warn(
                "udf_email parameter is being ignored in favor of the first positional parameter.",
                FusedIgnoredWarning,
            )
        else:
            udf = f"{udf_email}/{udf_name}"
            warnings.warn(
                "The 'udf_email' and 'udf_name' keywords are deprecated. You can pass "
                "the email and name as the first argument instead (i.e. replace "
                "'fused.run(udf_email=<email>, udf_name=<name>)' with "
                "'fused.run(\"<email>/<name>\")')",
                FusedDeprecationWarning,
            )

    elif args:
        if len(args) > 1:
            raise TypeError(
                "run() takes from 0 to 2 positional arguments but 3 were given"
            )
        udf_name = args[0]
        udf = f"{udf}/{udf_name}"
        warnings.warn(
            "The separate 'udf_email' and 'udf_name' arguments are deprecated. You can "
            "pass the email and name as the first argument instead (i.e. replace "
            "'fused.run(<email>, <name>)' with 'fused.run(\"<email>/<name>\")')",
            FusedDeprecationWarning,
        )

    if udf is None:
        raise ValueError("No UDF specified")

    if isinstance(udf, UdfJobStepConfig):
        job_step = udf
        udf_storage = "local_job_step"
    elif isinstance(udf, GeoPandasUdfV2):
        job_step = UdfJobStepConfig(udf=udf)
        udf_storage = "local_job_step"
    elif isinstance(udf, UdfAccessToken):
        token = udf.token
        udf_storage = "token"
    elif isinstance(udf, str):
        if "/" in udf:
            udf_email, udf_name = udf.split("/", maxsplit=1)
            udf_storage = "saved"
        elif "@" in udf:
            udf_email = udf
            udf_storage = "saved"
        elif is_udf_token(udf):
            token = udf
            udf_storage = "token"
        else:
            # This will actually be the udf name, not the user's email
            udf_email = udf
            udf_storage = "saved"
    else:
        raise TypeError(
            "Could not detect UDF from first parameter. It should be a string, UdfJobStepConfig, or BaseUdf object."
        )

    if engine == "realtime":
        engine = "remote"
    elif engine == "batch":
        warnings.warn(
            "The 'batch' engine option is deprecated. Use fused.submit() instead.",
            FusedDeprecationWarning,
            stacklevel=2,
        )
    elif engine is None:
        if udf_storage in ["token", "saved"]:
            engine = "remote"
        else:
            engine = default_run_engine()
    elif engine not in ("local", "remote"):
        raise ValueError("Invalid engine specified. Must be 'local' or 'remote'.")

    local_tile_bbox: Optional["gpd.GeoDataFrame"] = None
    xyz_ignored = False
    if x is not None and y is not None and z is not None:
        if HAS_MERCANTILE and HAS_GEOPANDAS and HAS_SHAPELY:
            import geopandas as gpd
            import mercantile
            import shapely

            tile_bounds = mercantile.bounds(x, y, z)
            local_tile_bbox = gpd.GeoDataFrame(
                {"x": [x], "y": [y], "z": [z]},
                geometry=[shapely.box(*tile_bounds)],
                crs=4326,
            )
        else:
            xyz_ignored = True

    if x is not None and y is not None and z is not None:
        if type != "tile":
            if type is None:
                # by default we still interpret x/y/z (if all passed) as a tile run
                type = "tile"
            else:
                kw_parameters["x"] = x
                kw_parameters["y"] = y
                kw_parameters["z"] = z
    else:
        if type is None:
            type = "file"
        elif type != "file":
            raise ValueError(
                "x, y, z not specified but type is 'tile', which is an invalid configuration. You must specify x, y, and z."
            )
        if x is not None:
            kw_parameters["x"] = x
        if y is not None:
            kw_parameters["y"] = y
        if z is not None:
            kw_parameters["z"] = z

    parameters = {
        **kw_parameters,
        **(parameters if parameters is not None else {}),
        **{"_include_log": True},
    }
    cache_max_age = _parse_ttl(cache_max_age)

    dispatch_params = ("sync" if sync else "async", type, udf_storage, engine)
    # Saved UDF
    if dispatch_params == ("sync", "tile", "saved", "remote"):
        fn = partial(
            run_tile,
            udf_email,
            udf_name,
            x=x,
            y=y,
            z=z,
            cache_max_age=cache_max_age,
            **parameters,
        )
    elif dispatch_params == ("async", "tile", "saved", "remote"):
        fn = partial(
            run_tile_async,
            udf_email,
            udf_name,
            x=x,
            y=y,
            z=z,
            cache_max_age=cache_max_age,
            **parameters,
        )
    elif dispatch_params == ("sync", "file", "saved", "remote"):
        fn = partial(
            run_file,
            udf_email,
            udf_name,
            cache_max_age=cache_max_age,
            **parameters,
        )
    elif dispatch_params == ("async", "file", "saved", "remote"):
        fn = partial(
            run_file_async,
            udf_email,
            udf_name,
            cache_max_age=cache_max_age,
            **parameters,
        )

    # shared UDF token
    elif dispatch_params == ("sync", "tile", "token", "remote"):
        fn = partial(
            run_shared_tile,
            token,
            x=x,
            y=y,
            z=z,
            cache_max_age=cache_max_age,
            **parameters,
        )
    elif dispatch_params == ("async", "tile", "token", "remote"):
        fn = partial(
            run_shared_tile_async,
            token,
            x=x,
            y=y,
            z=z,
            cache_max_age=cache_max_age,
            **parameters,
        )
    elif dispatch_params == ("sync", "file", "token", "remote"):
        fn = partial(run_shared_file, token, cache_max_age=cache_max_age, **parameters)
    elif dispatch_params == ("async", "file", "token", "remote"):
        fn = partial(
            run_shared_file_async, token, cache_max_age=cache_max_age, **parameters
        )

    # Local job step, which includes locally held code
    elif dispatch_params == ("sync", "tile", "local_job_step", "remote"):
        fn = lambda: job_step.run_tile(
            x=x, y=y, z=z, cache_max_age=cache_max_age, **parameters
        )
    elif dispatch_params == ("async", "tile", "local_job_step", "remote"):
        fn = lambda: job_step.run_tile_async(
            x=x, y=y, z=z, cache_max_age=cache_max_age, **parameters
        )
    elif dispatch_params == ("sync", "file", "local_job_step", "remote"):
        fn = lambda: job_step.run_file(cache_max_age=cache_max_age, **parameters)
    elif dispatch_params == ("async", "file", "local_job_step", "remote"):
        fn = lambda: job_step.run_file_async(**parameters)
    elif dispatch_params == ("sync", "tile", "local_job_step", "local"):
        fn = lambda: job_step.run_local(
            local_tile_bbox, **parameters, _return_response=_return_response
        )
    elif dispatch_params == ("async", "tile", "local_job_step", "local"):
        fn = lambda: job_step.run_local(local_tile_bbox, **parameters)
    elif dispatch_params == ("sync", "file", "local_job_step", "local"):
        fn = lambda: job_step.run_local(**parameters, _return_response=_return_response)
    elif dispatch_params == ("async", "file", "local_job_step", "local"):
        fn = lambda: job_step.run_local(**parameters)
    elif dispatch_params == ("sync", "tile", "local_job_step", "batch"):
        fn = None
    elif dispatch_params == ("sync", "file", "local_job_step", "batch"):
        fn = lambda: job_step.set_udf(job_step.udf, parameters=parameters).run_remote()
    else:
        fn = ...

    if xyz_ignored and engine == "local":
        # This warning doesn't matter on realtime because we will just put the x/y/z into the URL
        warnings.warn(
            FusedIgnoredWarning(
                "x, y, z arguments will be ignored because the following packages were not all found: mercantile shapely geopandas"
            ),
        )

    # Ellipsis is the sentinal value for not found in the dictionary at all
    if fn is Ellipsis:
        if udf_storage == "token" and engine != "remote":
            raise ValueError("UDF tokens can only be called on the 'remote' engine.")
        elif udf_storage == "saved" and engine != "remote":
            raise ValueError(
                "Saved UDFs can only be called on the 'remote' engine. To use another engine, load the UDF locally first."
            )
        else:
            raise ValueError(
                f"Could not determine how to call with settings: {dispatch_params}"
            )
    if fn is None:
        raise ValueError(f"Call type is not yet implemented: {dispatch_params}")
    if not sync and udf_storage not in ["saved", "token"]:
        raise ValueError(
            "Asynchronous execution is only supported for saved UDFs specifed by name or token."
        )

    n_retries = 0
    while n_retries <= max_retry:
        try:
            udf_eval_result = fn()
            break
        except Exception as exc:
            if n_retries >= max_retry:
                raise exc
            delay = OPTIONS.run_retry_base_delay * (2**n_retries)
            n_retries += 1
            warnings.warn(
                f"UDF execution failed, retrying in {delay} seconds (error: {exc})",
                FusedWarning,
            )

            time.sleep(delay)
            continue

    # Nested and remote UDF calls will return UdfEvaluationResult.
    # merge the stdout/stderr from fused.run() into running environment,
    # unless _include_log=True, then return the UdfEvaluationResult object.
    if _return_response:
        return udf_eval_result
    if isinstance(udf_eval_result, UdfEvaluationResult):
        if udf_eval_result.stdout:
            sys.stdout.write(udf_eval_result.stdout)
        if udf_eval_result.stderr:
            sys.stderr.write(udf_eval_result.stderr)
        if udf_eval_result.error_message is not None:
            raise UdfRuntimeError(
                udf_eval_result.error_message,
                child_exception_class=udf_eval_result.exception_class,
            )
        if _include_log:
            return udf_eval_result
        else:
            return udf_eval_result.data
    return udf_eval_result
