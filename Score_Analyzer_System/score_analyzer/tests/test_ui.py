import components.ui as ui


def test_inject_css_hides_sidebar_for_auth_views(monkeypatch):
    captured = {}

    def fake_markdown(css, unsafe_allow_html=True):
        captured["css"] = css

    monkeypatch.setattr(ui.st, "markdown", fake_markdown)

    ui.inject_css(background_image=None, show_sidebar=False)

    assert "display: none !important" in captured["css"]
