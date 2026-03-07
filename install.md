# Running the Documentation Site Locally

This site is built with [Jekyll](https://jekyllrb.com/) using the [Minimal Mistakes](https://mmistakes.github.io/minimal-mistakes/) theme.

## Clone the Repository

```bash
git clone https://github.com/OceanDataTools/openrvdas-docs.git
cd openrvdas-docs
```

## Prerequisites

1. **Install Ruby** (Homebrew is recommended on macOS):
   ```bash
   brew install ruby
   ```

2. **Add Ruby to your PATH** by adding the following to your `~/.zshrc` or `~/.bash_profile`:
   ```bash
   export PATH="/usr/local/opt/ruby/bin:$PATH"
   ```
   Then reload your shell:
   ```bash
   source ~/.zshrc
   ```

3. **Install Bundler**:
   ```bash
   gem install bundler
   ```

## Install Dependencies

From the root of this repository, install all required gems:

```bash
bundle install
```

## Serve the Site

```bash
bundle exec jekyll serve
```

Then open your browser to [http://localhost:4000](http://localhost:4000).

To have Jekyll automatically regenerate the site when files change, add the `--livereload` flag:

```bash
bundle exec jekyll serve --livereload
```

> **Note:** Changes to `_config.yml` require a server restart to take effect.

### Incremental Builds

For faster rebuilds during development, use the `--incremental` flag:

```bash
bundle exec jekyll serve --incremental
```

## Repository Structure

```
.
├── _config.yml          # Site configuration (title, theme, plugins, navigation)
├── _docs/               # Main documentation pages (rendered as the /docs/ collection)
├── _pages/              # Standalone pages (about, doc index, archives, 404)
├── _data/               # Navigation and other structured data
├── assets/              # CSS, JavaScript, and images
├── Gemfile              # Ruby gem dependencies
└── README.md            # Project landing page
```

## Contributing

Documentation source files are Markdown (`.md`) files located in `_docs/` and `_pages/`. Each file begins with a YAML front matter block that sets the title, layout, and navigation options.

To add or update a documentation page:

1. Edit or create a `.md` file in `_docs/`.
2. Ensure the front matter includes at minimum a `title` and `permalink`.
3. Run the site locally to preview your changes before submitting a pull request.
