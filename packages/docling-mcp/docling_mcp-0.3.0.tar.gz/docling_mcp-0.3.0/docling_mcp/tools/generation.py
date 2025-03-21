import hashlib

from docling_core.types.doc.document import (
    ContentLayer,
    DoclingDocument,
    GroupItem,
)
from docling_core.types.doc.labels import (
    DocItemLabel,
    GroupLabel,
    # PictureClassificationLabel,
    # TableCellLabel
)

from docling_mcp.docling_cache import get_cache_dir
from docling_mcp.shared import local_document_cache, local_stack_cache, mcp


def hash_string_md5(input_string: str) -> str:
    """Creates an md5 hash-string from the input string."""
    return hashlib.md5(input_string.encode()).hexdigest()


@mcp.tool()
def create_new_docling_document(prompt: str) -> str:
    """
    Creates a new Docling document from a provided prompt string.

    This function generates a new document in the local document cache with the
    provided prompt text. The document is assigned a unique key derived from an MD5
    hash of the prompt text.

    Args:
        prompt (str): The prompt text to include in the new document.

    Returns:
        str: A confirmation message containing the document key and original prompt.

    Note:
        The document is stored in the local_document_cache with a key generated
        from the MD5 hash of the prompt string, ensuring uniqueness and retrievability.

    Example:
        create_new_docling_document("Analyze the impact of climate change on marine ecosystems")
    """
    doc = DoclingDocument(name="Generated Document")

    item = doc.add_text(
        label=DocItemLabel.TEXT,
        text=f"prompt: {prompt}",
        content_layer=ContentLayer.FURNITURE,
    )

    document_key = hash_string_md5(prompt)

    local_document_cache[document_key] = doc
    local_stack_cache[document_key] = [item]

    return f"document-key: {document_key} for prompt:`{prompt}`"


@mcp.tool()
def export_docling_document_to_markdown(document_key: str) -> str:
    """
    Exports a document from the local document cache to markdown format.

    This tool converts a Docling document that exists in the local cache into
    a markdown formatted string, which can be used for display or further processing.

    Args:
        document_key (str): The unique identifier for the document in the local cache.

    Returns:
        str: A string containing the markdown representation of the document,
             along with a header identifying the document key.

    Raises:
        ValueError: If the specified document_key does not exist in the local cache.

    Example:
        export_docling_document_to_markdown("doc123")
    """
    if document_key not in local_document_cache:
        doc_keys = ", ".join(local_document_cache.keys())
        raise ValueError(
            f"document-key: {document_key} is not found. Existing document-keys are: {doc_keys}"
        )

    markdown = local_document_cache[document_key].export_to_markdown()

    return f"Markdown export for document with key: {document_key}\n\n{markdown}\n\n"


@mcp.tool()
def save_docling_document(document_key: str) -> str:
    """
    Saves a document from the local document cache to disk in both markdown and JSON formats.

    This tool takes a document that exists in the local cache and saves it to the specified
    cache directory with filenames based on the document key. Both markdown and JSON versions
    of the document are saved.

    Args:
        document_key (str): The unique identifier for the document in the local cache.

    Returns:
        str: A confirmation message indicating where the document was saved.

    Raises:
        ValueError: If the specified document_key does not exist in the local cache.

    Example:
        save_docling_document("doc123")
    """
    if document_key not in local_document_cache:
        doc_keys = ", ".join(local_document_cache.keys())
        raise ValueError(
            f"document-key: {document_key} is not found. Existing document-keys are: {doc_keys}"
        )

    cache_dir = get_cache_dir()

    local_document_cache[document_key].save_as_markdown(
        filename=cache_dir / f"{document_key}.md", text_width=72
    )
    local_document_cache[document_key].save_as_json(
        filename=cache_dir / f"{document_key}.json"
    )

    filename = cache_dir / f"{document_key}.md"

    return f"document saved at {filename}"


@mcp.tool()
def add_title_to_docling_document(document_key: str, title: str) -> str:
    """
    Adds or updates the title of a document in the local document cache.

    This tool modifies an existing document that has already been processed
    and stored in the local cache. It requires that the document already exists
    in the cache before a title can be added.

    Args:
        document_key (str): The unique identifier for the document in the local cache.
        title (str): The title text to add to the document.

    Returns:
        str: A confirmation message indicating the title was updated successfully.

    Raises:
        ValueError: If the specified document_key does not exist in the local cache.

    Example:
        add_title_to_docling_document("doc123", "Research Paper on Climate Change")
    """
    if document_key not in local_document_cache:
        doc_keys = ", ".join(local_document_cache.keys())
        raise ValueError(
            f"document-key: {document_key} is not found. Existing document-keys are: {doc_keys}"
        )

    if len(local_stack_cache[document_key]) == 0:
        raise ValueError(
            f"Stack size is zero for document with document-key: {document_key}. Abort document generation"
        )

    parent = local_stack_cache[document_key][-1]

    if isinstance(parent, GroupItem):
        if parent.label == GroupLabel.LIST or parent.label == GroupLabel.ORDERED_LIST:
            raise ValueError(
                "A list is currently opened. Please close the list before adding a title!"
            )

    item = local_document_cache[document_key].add_title(text=title)
    local_stack_cache[document_key][-1] = item

    return f"updated title for document with key: {document_key}"


@mcp.tool()
def add_section_heading_to_docling_document(
    document_key: str, section_heading: str, section_level: int
) -> str:
    """
    Adds a section heading to an existing document in the local document cache.

    This tool inserts a section heading with the specified heading text and level
    into a document that has already been processed and stored in the local cache.
    Section levels typically represent heading hierarchy (e.g., 1 for H1, 2 for H2).

    Args:
        document_key (str): The unique identifier for the document in the local cache.
        section_heading (str): The text to use for the section heading.
        section_level (int): The level of the heading (1-6, where 1 is the highest level).

    Returns:
        str: A confirmation message indicating the heading was added successfully.

    Raises:
        ValueError: If the specified document_key does not exist in the local cache.

    Example:
        add_section_heading_to_docling_document("doc123", "Introduction", 1)
    """
    if document_key not in local_document_cache:
        doc_keys = ", ".join(local_document_cache.keys())
        raise ValueError(
            f"document-key: {document_key} is not found. Existing document-keys are: {doc_keys}"
        )

    if len(local_stack_cache[document_key]) == 0:
        raise ValueError(
            f"Stack size is zero for document with document-key: {document_key}. Abort document generation"
        )

    parent = local_stack_cache[document_key][-1]

    if isinstance(parent, GroupItem):
        if parent.label == GroupLabel.LIST or parent.label == GroupLabel.ORDERED_LIST:
            raise ValueError(
                "A list is currently opened. Please close the list before adding a section-heading!"
            )

    item = local_document_cache[document_key].add_heading(
        text=section_heading, level=section_level
    )
    local_stack_cache[document_key][-1] = item

    return f"added section-heading of level {section_level} for document with key: {document_key}"


@mcp.tool()
def add_paragraph_to_docling_document(document_key: str, paragraph: str) -> str:
    """
    Adds a paragraph of text to an existing document in the local document cache.

    This tool inserts a new paragraph under the specified section header and level
    into a document that has already been processed and stored in the cache.

    Args:
        document_key (str): The unique identifier for the document in the local cache.
        paragraph (str): The text content to add as a paragraph.

    Returns:
        str: A confirmation message indicating the paragraph was added successfully.

    Raises:
        ValueError: If the specified document_key does not exist in the local cache.

    Example:
        add_paragraph_to_docling_document("doc123", "This is a sample paragraph text.", 2)
    """
    if document_key not in local_document_cache:
        doc_keys = ", ".join(local_document_cache.keys())
        raise ValueError(
            f"document-key: {document_key} is not found. Existing document-keys are: {doc_keys}"
        )

    if len(local_stack_cache[document_key]) == 0:
        raise ValueError(
            f"Stack size is zero for document with document-key: {document_key}. Abort document generation"
        )

    parent = local_stack_cache[document_key][-1]

    if isinstance(parent, GroupItem):
        if parent.label == GroupLabel.LIST or parent.label == GroupLabel.ORDERED_LIST:
            raise ValueError(
                "A list is currently opened. Please close the list before adding a paragraph!"
            )

    item = local_document_cache[document_key].add_text(
        label=DocItemLabel.TEXT, text=paragraph
    )
    local_stack_cache[document_key][-1] = item

    return f"added paragraph for document with key: {document_key}"


@mcp.tool()
def open_list_in_docling_document(document_key: str) -> str:
    """
    Opens a new list group in an existing document in the local document cache.

    This tool creates a new list structure within a document that has already been
    processed and stored in the local cache. It requires that the document already exists
    and that there is at least one item in the document's stack cache.

    Args:
        document_key (str): The unique identifier for the document in the local cache.

    Returns:
        str: A confirmation message indicating the list was successfully opened.

    Raises:
        ValueError: If the specified document_key does not exist in the local cache.

    Example:
        open_list_docling_document(document_key="doc123")
    """
    if document_key not in local_document_cache:
        doc_keys = ", ".join(local_document_cache.keys())
        raise ValueError(
            f"document-key: {document_key} is not found. Existing document-keys are: {doc_keys}"
        )

    if len(local_stack_cache[document_key]) == 0:
        raise ValueError(
            f"Stack size is zero for document with document-key: {document_key}. Abort document generation"
        )

    item = local_document_cache[document_key].add_group(label=GroupLabel.LIST)
    local_stack_cache[document_key].append(item)

    return f"opened a new list for document with key: {document_key}"


@mcp.tool()
def close_list_in_docling_document(document_key: str) -> str:
    """
    Closes a list group in an existing document in the local document cache.

    This tool closes a previously opened list structure within a document.
    It requires that the document exists and that there is more than one item
    in the document's stack cache.

    Args:
        document_key (str): The unique identifier for the document in the local cache.

    Returns:
        str: A confirmation message indicating the list was successfully closed.

    Raises:
        ValueError: If the specified document_key does not exist in the local cache.

    Example:
        close_list_docling_document(document_key="doc123")
    """
    if document_key not in local_document_cache:
        doc_keys = ", ".join(local_document_cache.keys())
        raise ValueError(
            f"document-key: {document_key} is not found. Existing document-keys are: {doc_keys}"
        )

    if len(local_stack_cache[document_key]) <= 1:
        raise ValueError(
            f"Stack size is zero for document with document-key: {document_key}. Abort document generation"
        )

    local_stack_cache[document_key].pop()

    return f"closed list for document with key: {document_key}"


@mcp.tool()
def add_listitem_to_list_in_docling_document(
    document_key: str, listitem_text: str, listmarker_text: str
) -> str:
    """
    Adds a list item to an open list in an existing document in the local document cache.

    This tool inserts a new list item with the specified text and marker into an
    open list within a document. It requires that the document exists and that
    there is at least one item in the document's stack cache.

    Args:
        document_key (str): The unique identifier for the document in the local cache.
        listitem_text (str): The content text for the list item.
        listmarker_text (str): The marker text to use for the list item (e.g., "-", "1.", "•").

    Returns:
        str: A confirmation message indicating the list item was successfully added.

    Raises:
        ValueError: If the specified document_key does not exist in the local cache.

    Example:
        add_listitem_to_docling_document(document_key="doc123", listitem_text="First item in the list", listmarker_text="-")
    """
    if document_key not in local_document_cache:
        doc_keys = ", ".join(local_document_cache.keys())
        raise ValueError(
            f"document-key: {document_key} is not found. Existing document-keys are: {doc_keys}"
        )

    if len(local_stack_cache[document_key]) == 0:
        raise ValueError(
            f"Stack size is zero for document with document-key: {document_key}. Abort document generation"
        )

    parent = local_stack_cache[document_key][-1]

    if isinstance(parent, GroupItem):
        if parent.label != GroupLabel.LIST and parent.label != GroupLabel.ORDERED_LIST:
            raise ValueError(
                "No list is currently opened. Please open a list before adding list-items!"
            )
    else:
        raise ValueError(
            "No list is currently opened. Please open a list before adding list-items!"
        )

    local_document_cache[document_key].add_list_item(
        text=listitem_text, marker=listmarker_text, parent=parent
    )

    return f"added listitem to list in document with key: {document_key}"
