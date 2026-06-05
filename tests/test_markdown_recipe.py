from app.core.markdown import render_markdown


def test_render_markdown_supports_recipe_formatting():
    html = str(
        render_markdown(
            "## Filling\n"
            "- Butter\n"
            "- Jam\n"
            "\n"
            "Use **cold** dough and `rest` overnight."
        )
    )

    assert "<h2>Filling</h2>" in html
    assert "<li>Butter" in html
    assert "<strong>cold</strong>" in html
    assert "<code>rest</code>" in html


def test_render_markdown_supports_recipe_tables_quotes_and_ordered_steps():
    html = str(
        render_markdown(
            "# Reverse-Roasted Steak\n"
            "\n"
            "## Step 1: Sear the Steak\n"
            "1. Preheat the oven.\n"
            "2. Sear the steak:\n"
            "   - 60 seconds on each flat side\n"
            "   - 30 seconds on each edge\n"
            "\n"
            "> The goal is to build crust.\n"
            "\n"
            "---\n"
            "\n"
            "| Desired Doneness | Time |\n"
            "|------------------|------|\n"
            "| Medium | 8 minutes |\n"
            "| Well-Done | 12 minutes |\n"
        )
    )

    assert "<h1>Reverse-Roasted Steak</h1>" in html
    assert "<ol>" in html
    assert "<ul>" in html
    assert "<blockquote><p>The goal is to build crust.</p></blockquote>" in html
    assert "<hr>" in html
    assert '<table class="markdown-table">' in html
    assert '<th class="align-left">Desired Doneness</th>' in html
    assert '<td class="align-left">8 minutes</td>' in html


def test_render_markdown_supports_table_alignment_markers():
    html = str(
        render_markdown(
            "| Name | Temp | Time |\n"
            "|:-----|:----:|-----:|\n"
            "| Medium | 140°F | 8 min |\n"
        )
    )

    assert 'class="align-left"' in html
    assert 'class="align-center"' in html
    assert 'class="align-right"' in html


def test_render_markdown_escapes_raw_html():
    html = str(render_markdown("<script>alert('x')</script> **safe**"))

    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "<strong>safe</strong>" in html
