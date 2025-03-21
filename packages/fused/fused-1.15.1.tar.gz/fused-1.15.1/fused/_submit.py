import concurrent.futures
import time
from typing import TYPE_CHECKING, Literal, Optional, Union, overload

from requests.exceptions import ReadTimeout

from fused._optional_deps import HAS_PANDAS, PD_DATAFRAME
from fused._run import ResultType
from fused._run import run as fused_run
from fused.models.udf.udf import GeoPandasUdfV2
from fused.types import UdfRuntimeError

if TYPE_CHECKING:
    import pandas as pd


class Future:
    # or `Job`, `JobResult`, `Task`, ...

    def __init__(self, future):
        self._future: concurrent.futures.Future = future

    def done(self):
        return self._future.done()

    def result(self):
        response = self._future.result()
        if isinstance(response, Exception):
            raise response
        if response.error_message is not None:
            raise self.exception()
        return response.data

    def exception(self):
        response = self._future.result()
        if isinstance(response, Exception):
            return response
        if response.error_message is not None:
            return UdfRuntimeError(
                response.error_message,
                child_exception_class=response.exception_class,
            )
        return self._future.exception()

    def get_logs(self):
        response = self._future.result()
        if isinstance(response, ReadTimeout):
            return str(response)
        out = ""
        if response.stdout:
            out += "stdout\n------\n" + response.stdout
        if response.stderr:
            out += "\nstderr\n------\n" + response.stderr
        return out

    def status(self):
        if self._future.running():
            return "running"
        elif self._future.done():
            exc = self.exception()
            if exc:
                if isinstance(
                    exc, ReadTimeout
                ) or "504 Server Error: Gateway Timeout" in str(exc):
                    return "timeout"
                return "error"
            return "success"  # or "finished"?
        else:
            return "pending"

    def __repr__(self):
        return f"<fused.Future [status: {('done - ' if self.done() else '') + self.status()}]>"


class JobPool:
    # or `Futures`, `PoolRunner`, etc

    """
    Pool of UDF runs. Don't use this class directly, use `fused.submit` instead.
    """

    # TODO add cancel support
    # TODO add retry support

    def __init__(
        self,
        udf,
        arg_list,
        kwargs=None,
        engine="remote",
        max_workers=None,
        max_retry=2,
    ):
        self.udf = udf
        self.arg_list = arg_list
        self.n_jobs = len(self.arg_list)
        self._kwargs = kwargs or {}
        self.engine = engine
        max_workers = min(max_workers or 32, 1024)
        self._pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self._max_retry = max_retry

    def _start_jobs(self):
        def _run(args):
            # currently we have to add a small delay between starting the UDF runs
            # to avoid overloading the server
            time.sleep(0.01)
            try:
                return fused_run(
                    self.udf,
                    engine=self.engine,
                    _return_response=True,
                    max_retry=self._max_retry,
                    **args,
                    **self._kwargs,
                )
            except Exception as exc:
                # ReadTime or HTTPError can happen on time-out or other server error
                return exc

        self._futures = [
            Future(self._pool.submit(_run, args)) for args in self.arg_list
        ]

    def done(self):
        return all(fut.done() for fut in self._futures)

    def _get_status(self):
        return [f.done() for f in self._futures]

    def _get_progress(self):
        percentage = round(sum(self._get_status()) / self.n_jobs * 100)
        return percentage, f"{sum(self._get_status())}/{self.n_jobs}"

    def wait(self):
        from tqdm.auto import tqdm

        t = tqdm(total=self.n_jobs, bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt}")
        while not self.done():
            n_done = sum(self._get_status())
            t.update(n_done - t.n)
        t.update(self.n_jobs - t.n)
        t.close()

    def results(self, return_exceptions=False):
        results = []
        for fut in self._futures:
            try:
                results.append(fut.result())
            except Exception:
                if return_exceptions:
                    results.append(fut.exception())
                else:
                    raise
        return results

    def __getitem__(self, idx: int) -> Future:
        return self._futures[idx]

    def __len__(self):
        return self.n_jobs

    def __repr__(self):
        # TODO we could provide a more informative repr in notebooks (e.g. showing
        # a table of the individual jobs and their status?)
        return f"<JobPool with {self.n_jobs} jobs [status: {self._get_progress()[1]} done]>"

    def get_status_df(self):
        if not HAS_PANDAS:
            raise ImportError("pandas is required to use this method")

        import pandas as pd

        results_df = pd.DataFrame(self.arg_list)
        results_df["status"] = [f.status() for f in self._futures]
        results_df["result"] = "<pending>"
        for i, fut in enumerate(self._futures):
            if results_df["status"].iloc[i] not in ("running", "pending"):
                try:
                    res = fut.result()
                except Exception:
                    res = fut.exception()
                results_df.at[i, "result"] = res

        return results_df

    def get_results_df(self, ignore_exceptions=False):
        if not HAS_PANDAS:
            raise ImportError("pandas is required to use this method")

        import pandas as pd

        results = self.results(return_exceptions=True)
        results_df = pd.DataFrame(self.arg_list)
        results_df["status"] = [f.status() for f in self._futures]
        results_df["result"] = results
        if ignore_exceptions:
            mask = [not isinstance(r, Exception) for r in results]
            results_df = results_df[mask]
        return results_df

    def collect(self, ignore_exceptions=True):
        if not HAS_PANDAS:
            raise ImportError("pandas is required to use this method")

        import pandas as pd

        results = self.results(return_exceptions=ignore_exceptions)
        results = dict(
            res
            for res in zip(range(self.n_jobs), results)
            if not isinstance(res[1], Exception)
        )

        results_pandas = all(isinstance(res, pd.DataFrame) for res in results.values())
        if results_pandas:
            results_df = pd.concat(results)
        else:
            results_df = pd.DataFrame({"result": pd.Series(results)})
            results_df.index = pd.MultiIndex.from_product([results_df.index])

        args_df = pd.DataFrame(self.arg_list)
        mask = [not isinstance(r, Exception) for r in results]
        args_df = args_df[mask]

        # combine concatenated results with arguments as prepended index levels
        assert len(results_df.index.levels[0]) == len(args_df)
        args_index = pd.MultiIndex.from_frame(args_df)
        args_codes = [c.take(results_df.index.codes[0]) for c in args_index.codes]
        new_idx = pd.MultiIndex(
            levels=list(args_index.levels) + results_df.index.levels[1:],
            codes=args_codes + results_df.index.codes[1:],
            names=list(args_df.columns) + results_df.index.names[1:],
        )
        results_df.index = new_idx
        return results_df


def _validate_arg_list(arg_list, udf):
    if HAS_PANDAS and isinstance(arg_list, PD_DATAFRAME):
        return arg_list.to_dict(orient="records")

    if not len(arg_list):
        raise ValueError("arg_list must be a non-empty list")
    if not isinstance(arg_list[0], dict):
        if not isinstance(udf, GeoPandasUdfV2):
            raise ValueError(
                "arg_list must be a list of dictionaries. A simple list to pass "
                "as first positional argument is only supported for UDF objects."
            )
        name = udf._parameter_list[0]
        arg_list = [{name: arg} for arg in arg_list]

    return arg_list


@overload
def submit(
    udf,
    arg_list,
    /,
    *,
    engine: Optional[Literal["remote", "local"]] = "remote",
    max_workers: Optional[int] = None,
    max_retry: int = 2,
    debug_mode: Literal[False] = False,
    collect: Literal[False] = False,
    **kwargs,
) -> JobPool:
    ...


@overload
def submit(
    udf,
    arg_list,
    /,
    *,
    engine: Optional[Literal["remote", "local"]] = "remote",
    max_workers: Optional[int] = None,
    max_retry: int = 2,
    debug_mode: Literal[True] = True,
    collect: bool = True,
    **kwargs,
) -> ResultType:
    ...


@overload
def submit(
    udf,
    arg_list,
    /,
    *,
    engine: Optional[Literal["remote", "local"]] = "remote",
    max_workers: Optional[int] = None,
    max_retry: int = 2,
    debug_mode: Literal[False] = False,
    collect: Literal[True] = True,
    **kwargs,
) -> "pd.DataFrame":
    ...


def submit(
    udf,
    arg_list,
    /,
    *,
    engine: Optional[Literal["remote", "local"]] = "remote",
    max_workers: Optional[int] = None,
    max_retry: int = 2,
    debug_mode: bool = False,
    collect: bool = True,
    **kwargs,
) -> Union[JobPool, ResultType, "pd.DataFrame"]:
    """
    Executes a user-defined function (UDF) multiple times for a list of input
    parameters, and return immediately a "lazy" JobPool object allowing
    to inspect the jobs and wait on the results.

    See `fused.run` for more details on the UDF execution.

    Args:
        udf: the UDF to execute.
            See `fused.run` for more details on how tos specify the UDF.
        arg_list: a list of input parameters for the UDF. Can be specified as:
            - a list of values for parametrizing over a single parameter, i.e.
              the first parameter of the UDF
            - a list of dictionaries for parametrizing over multiple parameters
            - A DataFrame for parametrizing over multiple parameters where each
              row is a set of parameters

        engine: The execution engine to use. Defaults to 'remote'.
        max_workers: The maximum number of workers to use. Defaults to 32.
        max_retry: The maximum number of retries for failed jobs. Defaults to 2.
        debug_mode: If True, executes only the first item in arg_list directly using
            `fused.run()`, useful for debugging UDF execution. Default is False.
        collect: If True, waits for all jobs to complete and returns the collected DataFrame
            containing the results. If False, returns a JobPool object, which is non-blocking
            and allows you to inspect the individual results and logs.
            Default is True.

    Returns:
        JobPool

    Examples:

        Run a UDF multiple times for the values 0 to 9 passed to as the first
        positional argument of the UDF:
        ```py
        pool = fused.submit("username@fused.io/my_udf_name", range(10))
        ```

        Being explicit about the parameter name:
        ```py
        pool = fused.submit(udf, [dict(n=i) for i in range(10)])
        ```

    """
    arg_list = _validate_arg_list(arg_list, udf)

    if debug_mode:
        return fused_run(udf, engine=engine, **arg_list[0], **kwargs)

    job_pool = JobPool(
        udf,
        arg_list,
        kwargs,
        engine=engine,
        max_workers=max_workers,
        max_retry=max_retry,
    )
    job_pool._start_jobs()

    if collect:
        job_pool.wait()
        return job_pool.collect()
    else:
        return job_pool
