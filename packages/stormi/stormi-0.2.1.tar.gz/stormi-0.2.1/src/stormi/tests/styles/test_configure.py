import matplotlib as mpl

from stormi.styles.configure import configure_matplotlib_style


def test_configure_matplotlib_style_basic():
    """Test that configure_matplotlib_style sets default style."""
    mpl.rcParams.update(mpl.rcParamsDefault)

    configure_matplotlib_style()

    assert mpl.rcParams != mpl.rcParamsDefault


def test_configure_matplotlib_style_override():
    """Test that configure_matplotlib_style correctly applies overrides."""
    mpl.rcParams.update(mpl.rcParamsDefault)

    test_override = {
        "figure.figsize": (10, 8),
        "lines.linewidth": 3.0,
    }

    configure_matplotlib_style(override_defaults=test_override)

    assert list(mpl.rcParams["figure.figsize"]) == [10.0, 8.0]
    assert mpl.rcParams["lines.linewidth"] == 3.0


def test_configure_matplotlib_style_latex_disabled(monkeypatch):
    """Test that usetex is disabled when latex is not available."""
    mpl.rcParams.update(mpl.rcParamsDefault)

    monkeypatch.setattr(
        "shutil.which", lambda cmd: None if cmd == "latex" else "/path/to/cmd"
    )

    configure_matplotlib_style()

    assert mpl.rcParams["text.usetex"] is False
