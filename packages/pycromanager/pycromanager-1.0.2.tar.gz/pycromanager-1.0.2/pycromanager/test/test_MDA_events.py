from pycromanager import multi_d_acquisition_events
import numpy as np
import pytest

x = np.arange(0, 5)
y = np.arange(0, -5, -1)
z = np.arange(0, 5)

xy = np.hstack([x[:, None], y[:, None]])
xyz = np.hstack([x[:, None], y[:, None], z[:, None]])

labels = [f'Pos{i}' for i in range(5)]

def test_xy_positions():
    expected = [
        {"axes": {"position": 0}, "x": 0, "y": 0},
        {"axes": {"position": 1}, "x": 1, "y": -1},
        {"axes": {"position": 2}, "x": 2, "y": -2},
        {"axes": {"position": 3}, "x": 3, "y": -3},
        {"axes": {"position": 4}, "x": 4, "y": -4},
    ]
    events = multi_d_acquisition_events(xy_positions=xy)
    assert events == expected

def test_xy_positions_with_labels():
    expected = [
        {"axes": {"position": _p}, "x": _x, "y": _y}
        for (_p, _x, _y) in zip(labels, x, y)
    ]

    events = multi_d_acquisition_events(xy_positions=xy, position_labels=labels)
    assert events == expected

def test_unequal_xy_positions_labels():
    with pytest.raises(ValueError):
        multi_d_acquisition_events(xy_positions=xy, position_labels=labels[:-1])

def test_xyz_positions():
    expected = [
        {"axes": {"position": 0, "z": 0}, "x": 0, "y": 0, "z": 0},
        {"axes": {"position": 1, "z": 0}, "x": 1, "y": -1, "z": 1},
        {"axes": {"position": 2, "z": 0}, "x": 2, "y": -2, "z": 2},
        {"axes": {"position": 3, "z": 0}, "x": 3, "y": -3, "z": 3},
        {"axes": {"position": 4, "z": 0}, "x": 4, "y": -4, "z": 4},
    ]
    assert expected == multi_d_acquisition_events(xyz_positions=xyz)

def test_xyz_positions_with_labels():
    expected = [
        {"axes": {"position": _p, "z": 0}, "x": _x, "y": _y, "z": _z}
        for (_p, _x, _y, _z) in zip(labels, x, y, z)
    ]

    assert expected == multi_d_acquisition_events(xyz_positions=xyz, position_labels=labels)

def test_unequal_xyz_positions_labels():
    with pytest.raises(ValueError):
        multi_d_acquisition_events(xyz_positions=xyz, position_labels=labels[:-1])

def test_xyz_relative_z():
    expected = [
        {"axes": {"position": 0, "z": 0}, "x": 0, "y": 0, "z": -1},
        {"axes": {"position": 0, "z": 1}, "x": 0, "y": 0, "z": 0},
        {"axes": {"position": 0, "z": 2}, "x": 0, "y": 0, "z": 1},
        {"axes": {"position": 1, "z": 0}, "x": 1, "y": -1, "z": 0},
        {"axes": {"position": 1, "z": 1}, "x": 1, "y": -1, "z": 1},
        {"axes": {"position": 1, "z": 2}, "x": 1, "y": -1, "z": 2},
        {"axes": {"position": 2, "z": 0}, "x": 2, "y": -2, "z": 1},
        {"axes": {"position": 2, "z": 1}, "x": 2, "y": -2, "z": 2},
        {"axes": {"position": 2, "z": 2}, "x": 2, "y": -2, "z": 3},
        {"axes": {"position": 3, "z": 0}, "x": 3, "y": -3, "z": 2},
        {"axes": {"position": 3, "z": 1}, "x": 3, "y": -3, "z": 3},
        {"axes": {"position": 3, "z": 2}, "x": 3, "y": -3, "z": 4},
        {"axes": {"position": 4, "z": 0}, "x": 4, "y": -4, "z": 3},
        {"axes": {"position": 4, "z": 1}, "x": 4, "y": -4, "z": 4},
        {"axes": {"position": 4, "z": 2}, "x": 4, "y": -4, "z": 5},
    ]
    assert expected == multi_d_acquisition_events(xyz_positions=xyz, z_start=-1, z_end=1, z_step=1)


def test_xy_absolute_z():
    expected = [
        {"axes": {"position": 0, "z": 0}, "x": 0, "y": 0, "z": -1},
        {"axes": {"position": 0, "z": 1}, "x": 0, "y": 0, "z": 0},
        {"axes": {"position": 0, "z": 2}, "x": 0, "y": 0, "z": 1},
        {"axes": {"position": 1, "z": 0}, "x": 1, "y": -1, "z": -1},
        {"axes": {"position": 1, "z": 1}, "x": 1, "y": -1, "z": 0},
        {"axes": {"position": 1, "z": 2}, "x": 1, "y": -1, "z": 1},
        {"axes": {"position": 2, "z": 0}, "x": 2, "y": -2, "z": -1},
        {"axes": {"position": 2, "z": 1}, "x": 2, "y": -2, "z": 0},
        {"axes": {"position": 2, "z": 2}, "x": 2, "y": -2, "z": 1},
        {"axes": {"position": 3, "z": 0}, "x": 3, "y": -3, "z": -1},
        {"axes": {"position": 3, "z": 1}, "x": 3, "y": -3, "z": 0},
        {"axes": {"position": 3, "z": 2}, "x": 3, "y": -3, "z": 1},
        {"axes": {"position": 4, "z": 0}, "x": 4, "y": -4, "z": -1},
        {"axes": {"position": 4, "z": 1}, "x": 4, "y": -4, "z": 0},
        {"axes": {"position": 4, "z": 2}, "x": 4, "y": -4, "z": 1},
    ]
    assert expected == multi_d_acquisition_events(xy_positions=xy, z_start=-1, z_end=1, z_step=1)

def test_xy_xyz_positions():
    with pytest.raises(ValueError):
        multi_d_acquisition_events(xy_positions=xy, xyz_positions=xyz)

def test_z_range_inputs():
    with pytest.raises(ValueError):
        multi_d_acquisition_events(z_start=0, z_end=5)

def test_z_range_inputs_1():
    with pytest.raises(ValueError):
        multi_d_acquisition_events(z_start=0, z_step=5)

def test_time_points():
    expected = [
        {"axes": {"time": 0}, "min_start_time": 0},
        {"axes": {"time": 1}, "min_start_time": 10},
        {"axes": {"time": 2}, "min_start_time": 20},
        {"axes": {"time": 3}, "min_start_time": 30},
        {"axes": {"time": 4}, "min_start_time": 40},
    ]
    assert expected == multi_d_acquisition_events(num_time_points=5, time_interval_s=10)

    expected = [
        {"axes": {"time": 0}, "min_start_time": 0},
        {"axes": {"time": 1}, "min_start_time": 10},
        {"axes": {"time": 2}, "min_start_time": 20},
        {"axes": {"time": 3}, "min_start_time": 30},
        {"axes": {"time": 4}, "min_start_time": 40},
    ]
    assert expected == multi_d_acquisition_events(num_time_points=5, time_interval_s=[0, 10, 10, 10, 10])

    expected = [
        {"axes": {"time": 0}, "min_start_time": 0},
        {"axes": {"time": 1}, "min_start_time": 10},
        {"axes": {"time": 2}, "min_start_time": 30},
        {"axes": {"time": 3}, "min_start_time": 30},
        {"axes": {"time": 4}, "min_start_time": 40},
    ]
    assert expected == multi_d_acquisition_events(num_time_points=5, time_interval_s=[0, 10, 20, 0, 10])

    expected = [
        {"axes": {"time": 0}, "min_start_time": 0},
        {"axes": {"time": 1}, "min_start_time": 10},
        {"axes": {"time": 2}, "min_start_time": 20},
        {"axes": {"time": 3}, "min_start_time": 30},
        {"axes": {"time": 4}, "min_start_time": 20},
    ]
    assert expected == multi_d_acquisition_events(num_time_points=5, time_interval_s=[0, 10, 10, 10, -10])

def test_order():
    expected = [
        {
            "axes": {"position": 0, "time": 0, "z": 0},
            "x": 0,
            "y": 0,
            "min_start_time": 0,
            "z": -1,
        },
        {
            "axes": {"position": 0, "time": 0, "z": 1},
            "x": 0,
            "y": 0,
            "min_start_time": 0,
            "z": 0,
        },
        {
            "axes": {"position": 0, "time": 1, "z": 0},
            "x": 0,
            "y": 0,
            "min_start_time": 10,
            "z": -1,
        },
        {
            "axes": {"position": 0, "time": 1, "z": 1},
            "x": 0,
            "y": 0,
            "min_start_time": 10,
            "z": 0,
        },
        {
            "axes": {"position": 1, "time": 0, "z": 0},
            "x": 1,
            "y": -1,
            "min_start_time": 0,
            "z": -1,
        },
        {
            "axes": {"position": 1, "time": 0, "z": 1},
            "x": 1,
            "y": -1,
            "min_start_time": 0,
            "z": 0,
        },
        {
            "axes": {"position": 1, "time": 1, "z": 0},
            "x": 1,
            "y": -1,
            "min_start_time": 10,
            "z": -1,
        },
        {
            "axes": {"position": 1, "time": 1, "z": 1},
            "x": 1,
            "y": -1,
            "min_start_time": 10,
            "z": 0,
        },
    ]
    xy_small = xy[:2, :]
    assert expected == multi_d_acquisition_events(
        num_time_points=2,
        time_interval_s=10,
        xy_positions=xy_small,
        order="ptz",
        z_start=-1,
        z_end=0,
        z_step=1,
    )


def test_channels():
    expected = [
        {
            "axes": {"position": 0, "channel": "BF"},
            "x": 0,
            "y": 0,
            "config_group": ["your-channel-group", "BF"],
            "exposure": 15.5,
        },
        {
            "axes": {"position": 0, "channel": "GFP"},
            "x": 0,
            "y": 0,
            "config_group": ["your-channel-group", "GFP"],
            "exposure": 200,
        },
        {
            "axes": {"position": 1, "channel": "BF"},
            "x": 1,
            "y": -1,
            "config_group": ["your-channel-group", "BF"],
            "exposure": 15.5,
        },
        {
            "axes": {"position": 1, "channel": "GFP"},
            "x": 1,
            "y": -1,
            "config_group": ["your-channel-group", "GFP"],
            "exposure": 200,
        },
        {
            "axes": {"position": 2, "channel": "BF"},
            "x": 2,
            "y": -2,
            "config_group": ["your-channel-group", "BF"],
            "exposure": 15.5,
        },
        {
            "axes": {"position": 2, "channel": "GFP"},
            "x": 2,
            "y": -2,
            "config_group": ["your-channel-group", "GFP"],
            "exposure": 200,
        },
        {
            "axes": {"position": 3, "channel": "BF"},
            "x": 3,
            "y": -3,
            "config_group": ["your-channel-group", "BF"],
            "exposure": 15.5,
        },
        {
            "axes": {"position": 3, "channel": "GFP"},
            "x": 3,
            "y": -3,
            "config_group": ["your-channel-group", "GFP"],
            "exposure": 200,
        },
        {
            "axes": {"position": 4, "channel": "BF"},
            "x": 4,
            "y": -4,
            "config_group": ["your-channel-group", "BF"],
            "exposure": 15.5,
        },
        {
            "axes": {"position": 4, "channel": "GFP"},
            "x": 4,
            "y": -4,
            "config_group": ["your-channel-group", "GFP"],
            "exposure": 200,
        },
    ]
    channel_group = "your-channel-group"
    channels = ["BF", "GFP"]
    channel_exposures_ms = [15.5, 200]
    assert expected == multi_d_acquisition_events(
        xy_positions=xy,
        channels=channels,
        channel_group=channel_group,
        channel_exposures_ms=channel_exposures_ms,
    )
