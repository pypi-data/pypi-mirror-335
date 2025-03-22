import json
from asyncio import sleep
from pathlib import Path
from unittest.mock import patch

import pytest

from panel_gwalker import GraphicWalker
from panel_gwalker._utils import _raw_fields


@pytest.fixture
def default_appearance():
    return "light"


def _get_params(gwalker):
    return {
        "object": gwalker.object,
        "field_specs": gwalker.field_specs,
        "appearance": gwalker.appearance,
        "config": gwalker.config,
        "spec": gwalker.spec,
        "kernel_computation": gwalker.kernel_computation,
    }


def test_constructor(data, default_appearance):
    gwalker = GraphicWalker(object=data)
    assert gwalker.object is data
    assert not gwalker.field_specs
    assert not gwalker.config
    assert gwalker.appearance == default_appearance
    assert gwalker.theme_key == "g2"


def test_process_parameter_change(data, default_appearance):
    gwalker = GraphicWalker(object=data)
    params = _get_params(gwalker)

    gwalker._process_param_change(params)
    assert params["field_specs"] == gwalker.calculated_field_specs()
    assert params["appearance"] == default_appearance
    assert not params["config"]


def test_process_parameter_change_with_fields(data, default_appearance):
    field_specs = [
        {
            "fid": "t_county",
            "name": "t_county",
            "semanticType": "nominal",
            "analyticType": "dimension",
        },
    ]
    gwalker = GraphicWalker(object=data, field_specs=field_specs)
    params = _get_params(gwalker)

    gwalker._process_param_change(params)
    assert params["field_specs"] is field_specs
    assert params["appearance"] == default_appearance
    assert not params["config"]


def test_process_parameter_change_with_config(data, default_appearance):
    config = {"a": "b"}
    gwalker = GraphicWalker(object=data, config=config)
    params = _get_params(gwalker)

    gwalker._process_param_change(params)
    assert params["field_specs"]
    assert params["appearance"] == default_appearance
    assert params["config"] is config


def test_process_parameter_change_with_appearance(data):
    appearance = "dark"
    gwalker = GraphicWalker(object=data, appearance=appearance)
    params = _get_params(gwalker)
    result = gwalker._process_param_change(params)
    assert result["appearance"] == appearance


@pytest.mark.xfail(reason="Don't know how to implement this")
def test_process_parameter_change_resetting_kernel_computation(data):
    gwalker = GraphicWalker(object=data, kernel_computation=True)
    gwalker.kernel_computation = False
    params = {"kernel_computation": gwalker.kernel_computation}
    result = gwalker._process_param_change(params)
    assert result["object"] is gwalker.object


def test_kernel_computation(data):
    gwalker = GraphicWalker(object=data, kernel_computation=True)
    gwalker.param.kernel_computation.constant = False
    gwalker.kernel_computation = True

    params = _get_params(gwalker)
    assert "object" not in gwalker._process_param_change(params)

    gwalker.kernel_computation = False
    params = _get_params(gwalker)
    assert "object" in gwalker._process_param_change(params)


def test_calculated_fields(data):
    gwalker = GraphicWalker(object=data)
    assert gwalker.calculated_field_specs() == _raw_fields(data)


def test_process_spec(data, tmp_path: Path):
    """If the spec is a string, it can be either a file path, a url path, or a JSON string."""

    def _process_spec(spec):
        gwalker = GraphicWalker(object=data, spec=spec, _debug=True)
        params = _get_params(gwalker)
        return gwalker._process_param_change(params)["spec"]

    # Test with None
    assert _process_spec(None) is None

    # Test with dict
    dict_spec = {"key": "value"}
    _process_spec(dict_spec) == dict_spec

    # Test with list
    list_spec = [{"key": "value"}]
    assert _process_spec(list_spec) == list_spec

    # Test with a URL (assuming we are just checking format, not accessing the URL)
    url = "https://cdn.jsdelivr.net/gh/panel-extensions/panel-graphic-walker@main/examples/bikesharing_dashboard/bikesharing_dashboard.json"
    assert isinstance(_process_spec(url), list)

    # Test with a JSON string
    json_string = '{"key": "value"}'
    result = _process_spec(json_string)
    assert result == {"key": "value"}, f"Expected JSON object, got {result}"

    # Test with a file Path
    json_data = {"file_key": "file_value"}
    tmp_file = tmp_path / "data.json"

    with open(tmp_file, "w") as file:
        json.dump(json_data, file)

    result = _process_spec(tmp_file)
    assert result == json_data, f"Expected JSON content from file, got {result}"

    # Test with a file path string
    tmp_file_str = str(tmp_file.absolute())
    result = _process_spec(tmp_file_str)
    assert result == json_data, f"Expected JSON content from file, got {result}"


async def _mock_export(self, *args, **kwargs):
    return {"args": args, "kwargs": kwargs}


def test_can_create_export_settings(data):
    gwalker = GraphicWalker(object=data)
    assert gwalker.export_controls(width=400)


@pytest.mark.asyncio
async def test_export(data):
    with patch.object(GraphicWalker, "export_chart", _mock_export):
        gwalker = GraphicWalker(object=data)
        assert await gwalker.export_chart()


@pytest.mark.asyncio
async def test_export_button(data):
    with patch.object(GraphicWalker, "export_chart", _mock_export):
        gwalker = GraphicWalker(object=data)
        button = gwalker.export_controls(width=400)
        assert not button.value
        button.param.trigger("run")
        await sleep(0.01)
        assert button.value


@pytest.mark.asyncio
async def test_can_save(data, tmp_path, export=_mock_export):
    with patch.object(GraphicWalker, "export_chart", _mock_export):
        gwalker = GraphicWalker(object=data)
        path = tmp_path / "spec.json"
        await gwalker.save_chart(path=path)
        assert path.exists()


@pytest.mark.asyncio
async def test_save_button(data, tmp_path: Path):
    with patch.object(GraphicWalker, "export_chart", _mock_export):
        gwalker = GraphicWalker(object=data)

        save_path = tmp_path / "spec.json"
        button = gwalker.save_controls(save_path=save_path, width=400)
        button.param.trigger("run")
        await sleep(0.1)
        assert save_path.exists()


def test_page_size(data):
    gwalker = GraphicWalker(object=data, page_size=50)
    assert gwalker.page_size == 50


def test_clone(data):
    gwalker = GraphicWalker(object=data)
    clone = gwalker.clone(
        renderer="chart",
        index=1,
    )
    assert clone.object is data
    assert clone.renderer == "chart"
    assert clone.index == 1


def test_clone_to_chart(data):
    gwalker = GraphicWalker(object=data, kernel_computation=True)
    chart = gwalker.chart(1, width=400)
    assert chart.object is data
    assert chart.renderer == "chart"
    assert not chart.kernel_computation
    assert chart.index == 1
    assert chart.width == 400


def test_clone_to_explorer(data):
    gwalker = GraphicWalker(object=data, renderer="profiler", page_size=50)
    explorer = gwalker.explorer(width=400)
    assert explorer.object is data
    assert explorer.renderer == "explorer"
    assert explorer.page_size == 50
    assert explorer.width == 400


def test_clone_to_profiler(data):
    gwalker = GraphicWalker(object=data)
    viewer = gwalker.profiler(page_size=50, width=400)
    assert viewer.object is data
    assert viewer.renderer == "profiler"
    assert viewer.page_size == 50
    assert viewer.width == 400


def test_clone_to_viewer(data):
    gwalker = GraphicWalker(object=data)
    viewer = gwalker.viewer(width=400)
    assert viewer.object is data
    assert viewer.renderer == "viewer"
    assert viewer.width == 400


def test_page_size_enabled(data):
    walker = GraphicWalker(object=data, renderer="explorer")
    assert not walker.is_enabled("page_size")()
    walker.renderer = "profiler"
    assert walker.is_enabled("page_size")()


def test_is_disabled(data):
    walker = GraphicWalker(object=data, renderer="profiler")
    for parameter in walker.param:
        assert walker.is_disabled(parameter)() == (not walker.is_enabled(parameter)())
