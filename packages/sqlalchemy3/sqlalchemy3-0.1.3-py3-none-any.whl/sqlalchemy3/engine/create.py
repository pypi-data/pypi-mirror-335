# engine/create.py
# Copyright (C) 2005-2024 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php

from __future__ import annotations

import inspect
import typing
from typing import Any
from typing import Callable
from typing import cast
from typing import Dict
from typing import List
from typing import Optional
from typing import overload
from typing import Type
from typing import Union

from . import base
from . import url as _url
from .interfaces import DBAPIConnection
from .mock import create_mock_engine
from .. import event
from .. import exc
from .. import util
from ..pool import _AdhocProxiedConnection
from ..pool import ConnectionPoolEntry
from ..sql import compiler
from ..util import immutabledict

if typing.TYPE_CHECKING:
    from .base import Engine
    from .interfaces import _ExecuteOptions
    from .interfaces import _ParamStyle
    from .interfaces import IsolationLevel
    from .url import URL
    from ..log import _EchoFlagType
    from ..pool import _CreatorFnType
    from ..pool import _CreatorWRecFnType
    from ..pool import _ResetStyleArgType
    from ..pool import Pool
    from ..util.typing import Literal


@overload
def create_engine(
    url: Union[str, URL],
    *,
    connect_args: Dict[Any, Any] = ...,
    convert_unicode: bool = ...,
    creator: Union[_CreatorFnType, _CreatorWRecFnType] = ...,
    echo: _EchoFlagType = ...,
    echo_pool: _EchoFlagType = ...,
    enable_from_linting: bool = ...,
    execution_options: _ExecuteOptions = ...,
    future: Literal[True],
    hide_parameters: bool = ...,
    implicit_returning: Literal[True] = ...,
    insertmanyvalues_page_size: int = ...,
    isolation_level: IsolationLevel = ...,
    json_deserializer: Callable[..., Any] = ...,
    json_serializer: Callable[..., Any] = ...,
    label_length: Optional[int] = ...,
    logging_name: str = ...,
    max_identifier_length: Optional[int] = ...,
    max_overflow: int = ...,
    module: Optional[Any] = ...,
    paramstyle: Optional[_ParamStyle] = ...,
    pool: Optional[Pool] = ...,
    poolclass: Optional[Type[Pool]] = ...,
    pool_logging_name: str = ...,
    pool_pre_ping: bool = ...,
    pool_size: int = ...,
    pool_recycle: int = ...,
    pool_reset_on_return: Optional[_ResetStyleArgType] = ...,
    pool_timeout: float = ...,
    pool_use_lifo: bool = ...,
    plugins: List[str] = ...,
    query_cache_size: int = ...,
    use_insertmanyvalues: bool = ...,
    **kwargs: Any,
) -> Engine: ...


@overload
def create_engine(url: Union[str, URL], **kwargs: Any) -> Engine: ...


@util.deprecated_params(
    strategy=(
        "1.4",
        "The :paramref:`_sa.create_engine.strategy` keyword is deprecated, "
        "and the only argument accepted is 'mock'; please use "
        ":func:`.create_mock_engine` going forward.  For general "
        "customization of create_engine which may have been accomplished "
        "using strategies, see :class:`.CreateEnginePlugin`.",
    ),
    empty_in_strategy=(
        "1.4",
        "The :paramref:`_sa.create_engine.empty_in_strategy` keyword is "
        "deprecated, and no longer has any effect.  All IN expressions "
        "are now rendered using "
        'the "expanding parameter" strategy which renders a set of bound'
        'expressions, or an "empty set" SELECT, at statement execution'
        "time.",
    ),
    implicit_returning=(
        "2.0",
        "The :paramref:`_sa.create_engine.implicit_returning` parameter "
        "is deprecated and will be removed in a future release. ",
    ),
)
def create_engine(url: Union[str, _url.URL], **kwargs: Any) -> Engine:
    """
    创建数据库的链接引擎
    engine = create_engine("postgresql+psycopg2://scott:tiger@localhost/test")
    engine = create_engine(
        "mysql+mysqldb://scott:tiger@hostname/dbname",
        pool_recycle=3600,
        echo=True,
    )
    echo = True  是否打印所有执行的sql语句
    future = False  是否使用2.0的特性
    pool_size = 5  连接池的大小
    pool_recycle = -1  多久之后对线程池中的线程进行一次连接的回收（重置）
    max_overflow = 10  控制在连接池达到最大数量时可以创建的连接数
    pool_timeout = 30  从连接池获取连接的超时时间
    pool_pre_ping = False  是否在连接池中获取连接之前进行连接的检查
    pool_use_lifo = True  是否使用后进先出的方式回收线程连接，默认使用先进先出
    """

    if "strategy" in kwargs:
        strat = kwargs.pop("strategy")
        if strat == "mock":
            # this case is deprecated
            return create_mock_engine(url, **kwargs)  # type: ignore
        else:
            raise exc.ArgumentError("unknown strategy: %r" % strat)

    kwargs.pop("empty_in_strategy", None)

    # create url.URL object
    u = _url.make_url(url)

    u, plugins, kwargs = u._instantiate_plugins(kwargs)

    entrypoint = u._get_entrypoint()
    _is_async = kwargs.pop("_is_async", False)
    if _is_async:
        dialect_cls = entrypoint.get_async_dialect_cls(u)
    else:
        dialect_cls = entrypoint.get_dialect_cls(u)

    if kwargs.pop("_coerce_config", False):

        def pop_kwarg(key: str, default: Optional[Any] = None) -> Any:
            value = kwargs.pop(key, default)
            if key in dialect_cls.engine_config_types:
                value = dialect_cls.engine_config_types[key](value)
            return value

    else:
        pop_kwarg = kwargs.pop  # type: ignore

    dialect_args = {}
    # consume dialect arguments from kwargs
    for k in util.get_cls_kwargs(dialect_cls):
        if k in kwargs:
            dialect_args[k] = pop_kwarg(k)

    dbapi = kwargs.pop("module", None)
    if dbapi is None:
        dbapi_args = {}

        if "import_dbapi" in dialect_cls.__dict__:
            dbapi_meth = dialect_cls.import_dbapi

        elif hasattr(dialect_cls, "dbapi") and inspect.ismethod(
            dialect_cls.dbapi
        ):
            util.warn_deprecated(
                "The dbapi() classmethod on dialect classes has been "
                "renamed to import_dbapi().  Implement an import_dbapi() "
                f"classmethod directly on class {dialect_cls} to remove this "
                "warning; the old .dbapi() classmethod may be maintained for "
                "backwards compatibility.",
                "2.0",
            )
            dbapi_meth = dialect_cls.dbapi
        else:
            dbapi_meth = dialect_cls.import_dbapi

        for k in util.get_func_kwargs(dbapi_meth):
            if k in kwargs:
                dbapi_args[k] = pop_kwarg(k)
        dbapi = dbapi_meth(**dbapi_args)

    dialect_args["dbapi"] = dbapi

    dialect_args.setdefault("compiler_linting", compiler.NO_LINTING)
    enable_from_linting = kwargs.pop("enable_from_linting", True)
    if enable_from_linting:
        dialect_args["compiler_linting"] ^= compiler.COLLECT_CARTESIAN_PRODUCTS

    for plugin in plugins:
        plugin.handle_dialect_kwargs(dialect_cls, dialect_args)

    # create dialect
    dialect = dialect_cls(**dialect_args)

    # assemble connection arguments
    (cargs_tup, cparams) = dialect.create_connect_args(u)
    cparams.update(pop_kwarg("connect_args", {}))
    cargs = list(cargs_tup)  # allow mutability

    # look for existing pool or create
    pool = pop_kwarg("pool", None)
    if pool is None:

        def connect(
            connection_record: Optional[ConnectionPoolEntry] = None,
        ) -> DBAPIConnection:
            if dialect._has_events:
                for fn in dialect.dispatch.do_connect:
                    connection = cast(
                        DBAPIConnection,
                        fn(dialect, connection_record, cargs, cparams),
                    )
                    if connection is not None:
                        return connection

            return dialect.connect(*cargs, **cparams)

        creator = pop_kwarg("creator", connect)

        poolclass = pop_kwarg("poolclass", None)
        if poolclass is None:
            poolclass = dialect.get_dialect_pool_class(u)
        pool_args = {"dialect": dialect}

        # consume pool arguments from kwargs, translating a few of
        # the arguments
        for k in util.get_cls_kwargs(poolclass):
            tk = _pool_translate_kwargs.get(k, k)
            if tk in kwargs:
                pool_args[k] = pop_kwarg(tk)

        for plugin in plugins:
            plugin.handle_pool_kwargs(poolclass, pool_args)

        pool = poolclass(creator, **pool_args)
    else:
        pool._dialect = dialect

    if (
        hasattr(pool, "_is_asyncio")
        and pool._is_asyncio is not dialect.is_async
    ):
        raise exc.ArgumentError(
            f"Pool class {pool.__class__.__name__} cannot be "
            f"used with {'non-' if not dialect.is_async else ''}"
            "asyncio engine",
            code="pcls",
        )

    # create engine.
    if not pop_kwarg("future", True):
        raise exc.ArgumentError(
            "The 'future' parameter passed to "
            "create_engine() may only be set to True."
        )

    engineclass = base.Engine

    engine_args = {}
    for k in util.get_cls_kwargs(engineclass):
        if k in kwargs:
            engine_args[k] = pop_kwarg(k)

    # internal flags used by the test suite for instrumenting / proxying
    # engines with mocks etc.
    _initialize = kwargs.pop("_initialize", True)

    # all kwargs should be consumed
    if kwargs:
        raise TypeError(
            "Invalid argument(s) %s sent to create_engine(), "
            "using configuration %s/%s/%s.  Please check that the "
            "keyword arguments are appropriate for this combination "
            "of components."
            % (
                ",".join("'%s'" % k for k in kwargs),
                dialect.__class__.__name__,
                pool.__class__.__name__,
                engineclass.__name__,
            )
        )

    engine = engineclass(pool, dialect, u, **engine_args)

    if _initialize:
        do_on_connect = dialect.on_connect_url(u)
        if do_on_connect:

            def on_connect(
                dbapi_connection: DBAPIConnection,
                connection_record: ConnectionPoolEntry,
            ) -> None:
                assert do_on_connect is not None
                do_on_connect(dbapi_connection)

            event.listen(pool, "connect", on_connect)

        builtin_on_connect = dialect._builtin_onconnect()
        if builtin_on_connect:
            event.listen(pool, "connect", builtin_on_connect)

        def first_connect(
            dbapi_connection: DBAPIConnection,
            connection_record: ConnectionPoolEntry,
        ) -> None:
            c = base.Connection(
                engine,
                connection=_AdhocProxiedConnection(
                    dbapi_connection, connection_record
                ),
                _has_events=False,
                # reconnecting will be a reentrant condition, so if the
                # connection goes away, Connection is then closed
                _allow_revalidate=False,
                # dont trigger the autobegin sequence
                # within the up front dialect checks
                _allow_autobegin=False,
            )
            c._execution_options = util.EMPTY_DICT

            try:
                dialect.initialize(c)
            finally:
                # note that "invalidated" and "closed" are mutually
                # exclusive in 1.4 Connection.
                if not c.invalidated and not c.closed:
                    # transaction is rolled back otherwise, tested by
                    # test/dialect/postgresql/test_dialect.py
                    # ::MiscBackendTest::test_initial_transaction_state
                    dialect.do_rollback(c.connection)

        # previously, the "first_connect" event was used here, which was then
        # scaled back if the "on_connect" handler were present.  now,
        # since "on_connect" is virtually always present, just use
        # "connect" event with once_unless_exception in all cases so that
        # the connection event flow is consistent in all cases.
        event.listen(
            pool, "connect", first_connect, _once_unless_exception=True
        )

    dialect_cls.engine_created(engine)
    if entrypoint is not dialect_cls:
        entrypoint.engine_created(engine)

    for plugin in plugins:
        plugin.engine_created(engine)

    return engine


def engine_from_config(
    configuration: Dict[str, Any], prefix: str = "sqlalchemy3.", **kwargs: Any
) -> Engine:
    """Create a new Engine instance using a configuration dictionary.

    The dictionary is typically produced from a config file.

    The keys of interest to ``engine_from_config()`` should be prefixed, e.g.
    ``sqlalchemy.url``, ``sqlalchemy.echo``, etc.  The 'prefix' argument
    indicates the prefix to be searched for.  Each matching key (after the
    prefix is stripped) is treated as though it were the corresponding keyword
    argument to a :func:`_sa.create_engine` call.

    The only required key is (assuming the default prefix) ``sqlalchemy.url``,
    which provides the :ref:`database URL <database_urls>`.

    A select set of keyword arguments will be "coerced" to their
    expected type based on string values.    The set of arguments
    is extensible per-dialect using the ``engine_config_types`` accessor.

    :param configuration: A dictionary (typically produced from a config file,
        but this is not a requirement).  Items whose keys start with the value
        of 'prefix' will have that prefix stripped, and will then be passed to
        :func:`_sa.create_engine`.

    :param prefix: Prefix to match and then strip from keys
        in 'configuration'.

    :param kwargs: Each keyword argument to ``engine_from_config()`` itself
        overrides the corresponding item taken from the 'configuration'
        dictionary.  Keyword arguments should *not* be prefixed.

    """

    options = {
        key[len(prefix) :]: configuration[key]
        for key in configuration
        if key.startswith(prefix)
    }
    options["_coerce_config"] = True
    options.update(kwargs)
    url = options.pop("url")
    return create_engine(url, **options)


@overload
def create_pool_from_url(
    url: Union[str, URL],
    *,
    poolclass: Optional[Type[Pool]] = ...,
    logging_name: str = ...,
    pre_ping: bool = ...,
    size: int = ...,
    recycle: int = ...,
    reset_on_return: Optional[_ResetStyleArgType] = ...,
    timeout: float = ...,
    use_lifo: bool = ...,
    **kwargs: Any,
) -> Pool: ...


@overload
def create_pool_from_url(url: Union[str, URL], **kwargs: Any) -> Pool: ...


def create_pool_from_url(url: Union[str, URL], **kwargs: Any) -> Pool:
    """Create a pool instance from the given url.

    If ``poolclass`` is not provided the pool class used
    is selected using the dialect specified in the URL.

    The arguments passed to :func:`_sa.create_pool_from_url` are
    identical to the pool argument passed to the :func:`_sa.create_engine`
    function.

    .. versionadded:: 2.0.10
    """

    for key in _pool_translate_kwargs:
        if key in kwargs:
            kwargs[_pool_translate_kwargs[key]] = kwargs.pop(key)

    engine = create_engine(url, **kwargs, _initialize=False)
    return engine.pool


_pool_translate_kwargs = immutabledict(
    {
        "logging_name": "pool_logging_name",
        "echo": "echo_pool",
        "timeout": "pool_timeout",
        "recycle": "pool_recycle",
        "events": "pool_events",  # deprecated
        "reset_on_return": "pool_reset_on_return",
        "pre_ping": "pool_pre_ping",
        "use_lifo": "pool_use_lifo",
    }
)
