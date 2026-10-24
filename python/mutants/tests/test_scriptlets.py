import pytest

from traffic_agent.script.scriptlets import ScriptletContext, ScriptletEngine
from traffic_agent.sandbox.executor import SandboxExecutor


def test_load_and_apply_on_request():
    engine = ScriptletEngine()
    engine.load(
        "header-patch",
        "def on_request(ctx):\n"
        "    ctx.values['headers']['Authorization'] = 'Bearer abc'\n"
        "    return 'patched'\n",
    )
    ctx = ScriptletContext(values={"headers": {"Accept": "json"}})
    ret = engine.apply_on_request("header-patch", ctx)
    assert ret == "patched"
    assert ctx.values["headers"]["Authorization"] == "Bearer abc"


def test_on_response_hook():
    engine = ScriptletEngine()
    engine.load(
        "body-rewrite",
        "def on_response(ctx):\n"
        "    ctx.values['body'] = ctx.values['body'].replace('error', 'info')\n",
    )
    ctx = ScriptletContext(values={"body": "an error occurred"})
    engine.apply_on_response("body-rewrite", ctx)
    assert ctx.values["body"] == "an info occurred"


def test_hooks_are_optional():
    engine = ScriptletEngine()
    scriptlet = engine.load("empty", "x = 1\n")
    assert scriptlet.has_on_request is False
    assert scriptlet.has_on_response is False


def test_calling_missing_hook_raises():
    engine = ScriptletEngine()
    engine.load("empty", "x = 1")
    with pytest.raises(TypeError):
        engine.apply_on_request("empty", ScriptletContext())


def test_bad_source_is_rejected_at_load():
    engine = ScriptletEngine()
    with pytest.raises(ValueError) as exc:
        engine.load("broken", "def broken(:")
    assert "failed to load" in str(exc.value)


def test_forbidden_source_rejected():
    engine = ScriptletEngine()
    with pytest.raises(Exception):
        engine.load("evil", "import os\ndef on_request(ctx):\n    pass")


def test_listing_and_unloading():
    engine = ScriptletEngine()
    engine.load("a", "x=1")
    engine.load("b", "y=2")
    assert engine.names() == ["a", "b"]
    assert engine.unload("a") is True
    assert engine.names() == ["b"]
    assert engine.unload("a") is False


def test_unknown_scriptlet_raises():
    engine = ScriptletEngine()
    with pytest.raises(KeyError):
        engine.apply_on_request("missing", ScriptletContext())


def test_timeout_scriptlet_fails():
    engine = ScriptletEngine(SandboxExecutor(timeout_ms=120))
    with pytest.raises(Exception):
        engine.load("slow", "while True:\n    pass")
