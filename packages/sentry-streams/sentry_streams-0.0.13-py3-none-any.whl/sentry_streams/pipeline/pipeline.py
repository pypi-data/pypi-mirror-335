from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import (
    Any,
    Callable,
    Generic,
    Mapping,
    MutableMapping,
    MutableSequence,
    Optional,
    TypeVar,
    Union,
    cast,
)

from sentry_streams.modules import get_module
from sentry_streams.pipeline.batch import BatchBuilder
from sentry_streams.pipeline.function_template import (
    Accumulator,
    AggregationBackend,
    GroupBy,
    InputType,
    OutputType,
)
from sentry_streams.pipeline.window import MeasurementUnit, TumblingWindow, Window


class StepType(Enum):
    BRANCH = "branch"
    FILTER = "filter"
    FLAT_MAP = "flat_map"
    MAP = "map"
    REDUCE = "reduce"
    ROUTER = "router"
    SINK = "sink"
    SOURCE = "source"


class Pipeline:
    """
    A graph representing the connections between
    logical Steps.
    """

    def __init__(self) -> None:
        self.steps: MutableMapping[str, Step] = {}
        self.incoming_edges: MutableMapping[str, list[str]] = defaultdict(list)
        self.outgoing_edges: MutableMapping[str, list[str]] = defaultdict(list)
        self.sources: list[Source] = []

    def register(self, step: Step) -> None:
        assert step.name not in self.steps
        self.steps[step.name] = step

    def register_edge(self, _from: Step, _to: Step) -> None:
        self.incoming_edges[_to.name].append(_from.name)
        self.outgoing_edges[_from.name].append(_to.name)

    def register_source(self, step: Source) -> None:
        self.sources.append(step)


@dataclass
class Step:
    """
    A generic Step, whose incoming
    and outgoing edges are registered
    against a Pipeline.
    """

    name: str
    ctx: Pipeline

    def __post_init__(self) -> None:
        self.ctx.register(self)


@dataclass
class Source(Step):
    """
    A generic Source.
    """


@dataclass
class StreamSource(Source):
    """
    A Source which reads from Kafka.
    """

    stream_name: str
    step_type: StepType = StepType.SOURCE

    def __post_init__(self) -> None:
        super().__post_init__()
        self.ctx.register_source(self)


@dataclass
class WithInput(Step):
    """
    A generic Step representing a logical
    step which has inputs.
    """

    inputs: list[Step]

    def __post_init__(self) -> None:
        super().__post_init__()
        for input in self.inputs:
            self.ctx.register_edge(input, self)


@dataclass
class Sink(WithInput):
    """
    A generic Sink.
    """


@dataclass
class StreamSink(Sink):
    """
    A Sink which specifically writes to Kafka.
    """

    stream_name: str
    step_type: StepType = StepType.SINK


RoutingFuncReturnType = TypeVar("RoutingFuncReturnType")
TransformFuncReturnType = TypeVar("TransformFuncReturnType")


class TransformFunction(ABC, Generic[TransformFuncReturnType]):
    @property
    @abstractmethod
    def resolved_function(self) -> Callable[..., TransformFuncReturnType]:
        raise NotImplementedError()


@dataclass
class TransformStep(WithInput, TransformFunction[TransformFuncReturnType]):
    """
    A generic step representing a step performing a transform operation
    on input data.
    function: supports reference to a function using dot notation, or a Callable
    """

    function: Union[Callable[..., TransformFuncReturnType], str]
    step_type: StepType

    @property
    def resolved_function(self) -> Callable[..., TransformFuncReturnType]:
        """
        Returns a callable of the transform function defined, or referenced in the
        this class
        """
        if callable(self.function):
            return self.function

        fn_path = self.function
        mod, cls, fn = fn_path.rsplit(".", 2)

        module = get_module(mod)

        imported_cls = getattr(module, cls)
        imported_func = cast(Callable[..., TransformFuncReturnType], getattr(imported_cls, fn))
        function_callable = imported_func
        return function_callable


@dataclass
class Map(TransformStep[Any]):
    """
    A simple 1:1 Map, taking a single input to single output.
    """

    # We support both referencing map function via a direct reference
    # to the symbol and through a string.
    # The direct reference to the symbol allows for strict type checking
    # The string is likely to be used in cross code base pipelines where
    # the symbol is just not present in the current code base.
    step_type: StepType = StepType.MAP

    # TODO: Allow product to both enable and access
    # configuration (e.g. a DB that is used as part of Map)


@dataclass
class Filter(TransformStep[bool]):
    """
    A simple Filter, taking a single input and either returning it or None as output.
    """

    step_type: StepType = StepType.FILTER


@dataclass
class Branch(Step):
    """
    A Branch represents one branch in a pipeline, which is routed to
    by a Router.
    """

    step_type: StepType = StepType.BRANCH


@dataclass
class Router(WithInput, Generic[RoutingFuncReturnType]):
    """
    A step which takes a routing table of Branches and sends messages
    to those branches based on a routing function.
    Routing functions must only return a single output branch, routing
    to multiple branches simultaneously is not currently supported.
    """

    routing_function: Callable[..., RoutingFuncReturnType]
    routing_table: Mapping[RoutingFuncReturnType, Branch]
    step_type: StepType = StepType.ROUTER

    def __post_init__(self) -> None:
        super().__post_init__()
        for branch_step in self.routing_table.values():
            self.ctx.register_edge(self, branch_step)


class Reduce(WithInput, ABC, Generic[MeasurementUnit, InputType, OutputType]):
    """
    A generic Step for a Reduce (or Accumulator-based) operation
    """

    @property
    @abstractmethod
    def group_by(self) -> Optional[GroupBy]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def windowing(self) -> Window[MeasurementUnit]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def aggregate_fn(self) -> Callable[[], Accumulator[InputType, OutputType]]:
        raise NotImplementedError()


@dataclass
class Aggregate(Reduce[MeasurementUnit, InputType, OutputType]):
    """
    A Reduce step which performs windowed aggregations. Can be keyed or non-keyed on the
    input stream. Supports an Accumulator-style aggregation which can have a configurable
    storage backend, for flushing intermediate aggregates.
    """

    window: Window[MeasurementUnit]
    aggregate_func: Callable[[], Accumulator[InputType, OutputType]]
    aggregate_backend: Optional[AggregationBackend[OutputType]] = None
    group_by_key: Optional[GroupBy] = None
    step_type: StepType = StepType.REDUCE

    @property
    def group_by(self) -> Optional[GroupBy]:
        return self.group_by_key

    @property
    def windowing(self) -> Window[MeasurementUnit]:
        return self.window

    @property
    def aggregate_fn(self) -> Callable[[], Accumulator[InputType, OutputType]]:
        return self.aggregate_func


BatchInput = TypeVar("BatchInput")


@dataclass
class Batch(Reduce[MeasurementUnit, InputType, MutableSequence[InputType]]):
    """
    A step to Batch up the results of the prior step.

    Batch can be configured via batch size, which can be
    an event time duration or a count of events.
    """

    # TODO: Use concept of custom triggers to close window
    # by either size or time
    batch_size: MeasurementUnit
    step_type: StepType = StepType.REDUCE

    @property
    def group_by(self) -> Optional[GroupBy]:
        return None

    @property
    def windowing(self) -> Window[MeasurementUnit]:
        return TumblingWindow(self.batch_size)

    @property
    def aggregate_fn(self) -> Callable[[], Accumulator[InputType, OutputType]]:
        batch_acc = BatchBuilder[BatchInput]
        return cast(Callable[[], Accumulator[InputType, OutputType]], batch_acc)


@dataclass
class FlatMap(TransformStep[Any]):
    """
    A generic step for mapping and flattening (and therefore alerting the shape of) inputs to
    get outputs. Takes a single input to 0...N outputs.
    """

    step_type: StepType = StepType.FLAT_MAP
