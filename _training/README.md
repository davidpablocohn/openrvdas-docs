# Deck script source

`openrvdas_tech_deck.md` is the source of truth for the OpenRVDAS tutorial deck
script. Edit it, then rebuild:

```bash
./_training/build_deck.py            # -> _training/openrvdas_tech_deck.html
./_training/build_deck.py --check    # list slides and flag empty blocks
```

The generated HTML is gitignored; the Markdown is what gets reviewed.

## Editing

- **Reorder slides** by moving a `## Slide title` block. Numbers, the contents
  list and the slide/section counts are all generated, so nothing needs
  renumbering.
- **Add a slide** by pasting a new `## Title` block with `ON SLIDE` and `SAY`
  under it, in the section where it belongs.
- **Tags** go on the heading: `## Read the stderr  {gotcha}` — one of
  `demo`, `gotcha`, `drill`, `ref`.
- `--check` lists every slide in order and flags any missing an `ON SLIDE` or
  `SAY` block, which is the quickest way to see what a reshuffle actually did.

Inside `ON SLIDE` and `SAY`: paragraphs, `-` bullets, `1.` numbered lists,
``` fences, ```mermaid diagrams, ```svg fences for hand-drawn inline SVG, `|` tables, `code`, `**bold**`, `*italic*`,
`{{demo}}` for an inline tag pill, a trailing `\` for a hard line break, and a
line starting with `NOTE:` for a presenter note.

Jekyll ignores directories beginning with an underscore, so nothing here is
published to the documentation site.
