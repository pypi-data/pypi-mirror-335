import numpy as np
import natinterp3d


def test_natinterp3d():
    queries = np.random.randn(50, 3)
    keys = np.random.randn(100, 3)
    values = np.random.randn(100)

    res = natinterp3d.interpolate(queries, keys, values)
    assert res.shape == (50,)

    weights = natinterp3d.get_weights(queries, keys)
    assert weights.shape == (50, 100)

    res2 = natinterp3d.interpolate(queries, keys, values, parallel=False)
    assert np.allclose(res, res2)

    values2 = np.random.randn(100, 2)
    res3 = natinterp3d.interpolate(queries, keys, values2)
    assert res3.shape == (50, 2)

    weights2 = natinterp3d.get_weights(queries, keys, parallel=True)
    assert np.allclose(weights.toarray(), weights2.toarray())

    # Set up some function at 10000 random points
    np.random.seed(10)
    keys = np.random.randn(10000, 3)

    def func(x):
        x = x * 0.1
        return np.sin(x[:, 0]) + np.cos(x[:, 1]) + np.tan(x[:, 2])

    values = func(keys)
    queries = np.random.randn(100, 3)

    interp_values = natinterp3d.interpolate(queries, keys, values)
    actual_values = func(queries)
    assert np.mean(np.abs(interp_values - actual_values)) < 1e-3
