"""Basic tests for smart_prompt_eval package."""


def test_package_import() -> None:
    """Test that the package can be imported."""
    import smart_prompt_eval

    assert str(smart_prompt_eval.__version__) == "0.0.1"


def test_module_imports() -> None:
    """Test that utils and evals modules can be imported."""
    from smart_prompt_eval import evals, utils

    assert utils is not None
    assert evals is not None
