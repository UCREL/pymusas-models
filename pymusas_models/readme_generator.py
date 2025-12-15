'''
The majority of this code has been taken from the spaCy codebase:
https://github.com/explosion/spaCy/blob/29afbdb91e5fecf513125a85f1ac1d165f40bc93/spacy/cli/package.py

This code is used to generate the spaCy model's release README file.
'''

from typing import Any, Dict, List, cast

from wasabi import MarkdownRenderer


def generate_readme(meta: Dict[str, Any]) -> str:
    """
    Generate a Markdown-formatted README text from a model meta.json. Used
    within the GitHub release notes and as content for README.md file added
    to model packages.
    """
    md = MarkdownRenderer()
    name = f"{meta['name']}"
    version = meta["version"]
    pipeline = ", ".join([md.code(p) for p in meta.get("pipeline", [])])
    components = ", ".join([md.code(p) for p in meta.get("components", [])])
    vecs = meta.get("vectors", {})
    vectors = f"{vecs.get('keys', 0)} keys, {vecs.get('vectors', 0)} unique vectors ({vecs.get('width', 0)} dimensions)"
    author = meta.get("author") or "n/a"
    model_size = meta.get("size") or "n/a"
    notes = meta.get("notes", "")
    license_name = meta.get("license")
    sources = _format_sources(meta.get("sources"))
    description = meta.get("description")
    label_scheme = _format_label_scheme(cast(Dict[str, Any], meta.get("labels")))
    accuracy = _format_accuracy(cast(Dict[str, Any], meta.get("performance")))
    table_data = [
        (md.bold("Name"), md.code(name)),
        (md.bold("Version"), md.code(version)),
        (md.bold("spaCy"), md.code(meta["spacy_version"])),
        (md.bold("Default Pipeline"), pipeline),
        (md.bold("Components"), components),
        (md.bold("Vectors"), vectors),
        (md.bold("Sources"), sources or "n/a"),
        (md.bold("License"), md.code(license_name) if license_name else "n/a"),
        (md.bold("Author"), md.link(author, meta["url"]) if "url" in meta else author),
        (md.bold("Model size"), model_size),
    ]
    # Put together Markdown body
    if description:
        md.add(description)
    md.add(md.table(table_data, ["Feature", "Description"]))
    if label_scheme:
        md.add(md.title(3, "Label Scheme"))
        md.add(label_scheme)
    if accuracy:
        md.add(md.title(3, "Accuracy"))
        md.add(accuracy)
    if notes:
        md.add(notes)
    return cast(str, md.text)  # type: ignore


def _format_sources(data: Any) -> str:
    if not data or not isinstance(data, list):
        return "n/a"
    sources = []
    for source in data:
        if not isinstance(source, dict):
            source = {"name": source}
        name = source.get("name")
        if not name:
            continue
        url = source.get("url")
        author = source.get("author")
        result = name if not url else "[{}]({})".format(name, url)
        if author:
            result += " ({})".format(author)
        sources.append(result)
    return "<br />".join(sources)


def _format_accuracy(data: Dict[str, Any], exclude: List[str] = ["speed"]) -> str:
    if not data:
        return ""
    md = MarkdownRenderer()
    scalars = [(k, v) for k, v in data.items() if isinstance(v, (int, float))]
    scores = [
        (md.code(acc.upper()), f"{score * 100:.2f}")
        for acc, score in scalars
        if acc not in exclude
    ]
    md.add(md.table(scores, ["Type", "Score"]))
    return cast(str, md.text)  # type: ignore


def _format_label_scheme(data: Dict[str, Any]) -> str:
    if not data:
        return ""
    md = MarkdownRenderer()
    n_labels = 0
    n_pipes = 0
    label_data = []
    for pipe, labels in data.items():
        if not labels:
            continue
        col1 = md.bold(md.code(pipe))
        col2 = ", ".join(
            [md.code(str(label).replace("|", "\\|")) for label in labels]
        )  # noqa: W605
        label_data.append((col1, col2))
        n_labels += len(labels)
        n_pipes += 1
    if not label_data:
        return ""
    label_info = f"View label scheme ({n_labels} labels for {n_pipes} components)"
    md.add("<details>")
    md.add(f"<summary>{label_info}</summary>")
    md.add(md.table(label_data, ["Component", "Labels"]))
    md.add("</details>")
    return cast(str, md.text)  # type: ignore
