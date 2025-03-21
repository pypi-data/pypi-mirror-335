from ommx.v1 import Instance, DecisionVariable, Polynomial, Function
from dimod.sym import Sense
import dimod
import pytest

from ommx_dwave_adapter import OMMXLeapHybridCQMAdapter, OMMXDWaveAdapterError


def test_instance_to_cqm_model():
    # simple knapsack problem
    p = [10, 13, 18, 31, 7, 15]
    w = [11, 25, 20, 35, 10, 33]
    W = 47
    N = len(p)

    x = [
        DecisionVariable.binary(
            id=i,
            name="x",
            subscripts=[i],
        )
        for i in range(N)
    ]
    constraints = [Function(sum(w[i] * x[i] for i in range(N))) <= W]
    instance = Instance.from_components(
        decision_variables=x,
        objective=sum(p[i] * x[i] for i in range(N)),
        constraints=constraints,
        sense=Instance.MAXIMIZE,
    )
    adapter = OMMXLeapHybridCQMAdapter(instance)
    model = adapter.solver_input
    assert model.vartype(x[0].id) == dimod.BINARY
    assert list(model.variables) == [var.id for var in x]

    assert model.objective.quadratic == {}
    # MAXIMIZE check: dwave only minimizes, so all coefficients must have had their sign changed
    assert model.objective.linear == {x[i].id: -p[i] for i in range(N)}
    assert model.objective.offset == 0.0

    assert model.constraints[0].sense == Sense.Le
    assert model.constraints[0].lhs.offset == -W
    assert model.constraints[0].lhs.linear == {x[i].id: w[i] for i in range(N)}
    assert model.constraints[0].rhs == 0


def test_error_on_unsupported_function():
    decision_variables = [
        DecisionVariable.of_type(
            kind=DecisionVariable.BINARY, id=0, lower=0, upper=1, name="x"
        ),
        DecisionVariable.of_type(
            kind=DecisionVariable.INTEGER,
            id=1,
            lower=-20.0,
            upper=20.0,
            name="y",
            subscripts=[],
        ),
        DecisionVariable.of_type(
            kind=DecisionVariable.CONTINUOUS,
            id=2,
            lower=-30,
            upper=30,
            name="z",
            subscripts=[0],
        ),
        DecisionVariable.of_type(
            kind=DecisionVariable.CONTINUOUS,
            id=3,
            # TODO dwave doesn't accept -inf, +inf. how to handle this? should the adapter convert?
            lower=float("-1e30"),
            upper=float("1e30"),
            name="w",
            subscripts=[1, 2],
        ),
    ]
    objective = Polynomial(terms={(0, 1, 2): 2.0, (1, 2): 3.0, (2,): 4.0, (): 5.0})

    instance = Instance.from_components(
        decision_variables=decision_variables,
        objective=objective,
        constraints=[],
        sense=Instance.MINIMIZE,
    )
    with pytest.raises(OMMXDWaveAdapterError):
        OMMXLeapHybridCQMAdapter(instance)


def test_decode():
    p = [10, 13, 18, 31, 7, 15]
    w = [11, 25, 20, 35, 10, 33]
    W = 47
    N = len(p)

    x = [
        DecisionVariable.binary(
            id=i,
            name="x",
            subscripts=[i],
        )
        for i in range(N)
    ]
    constraints = [Function(sum(w[i] * x[i] for i in range(N))) <= W]
    instance = Instance.from_components(
        decision_variables=x,
        objective=sum(p[i] * x[i] for i in range(N)),
        constraints=constraints,
        sense=Instance.MAXIMIZE,
    )
    adapter = OMMXLeapHybridCQMAdapter(instance)
    cqm = adapter.sampler_input

    # using ExactCQM solver as a testable stand-in
    dimod_sampleset = dimod.ExactCQMSolver().sample_cqm(cqm)
    dimod_sampleset.resolve()

    sampleset = adapter.decode_to_sampleset(dimod_sampleset)
    assert sampleset.raw.sense == Instance.MAXIMIZE
    best = sampleset.best_feasible()
    assert best.objective == 41
    assert best.raw.state.entries[0] == pytest.approx(1)
    assert best.raw.state.entries[1] == pytest.approx(0)
    assert best.raw.state.entries[2] == pytest.approx(0)
    assert best.raw.state.entries[3] == pytest.approx(1)
    assert best.raw.state.entries[4] == pytest.approx(0)
    assert best.raw.state.entries[5] == pytest.approx(0)
