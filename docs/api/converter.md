# Core API Reference

This page documents the main API functions and classes provided by Webdown.

## Main Functions

::: webdown.converter
    options:
      show_root_heading: false
      show_root_toc_entry: false
      show_root_full_path: false
      show_object_full_path: false
      members:
        - convert_url_to_markdown
        - html_to_markdown
        - markdown_to_claude_xml
      show_docstring_attributes: true
      show_docstring_description: true
      show_docstring_examples: true
      extra:
        show_docstring_other_sections: true

## Configuration Classes

::: webdown.config.WebdownConfig
    options:
      show_bases: false
      members: true

::: webdown.config.DocumentOptions
    options:
      show_bases: false
      members: true

## HTML Parsing

::: webdown.html_parser
    options:
      show_root_heading: false
      show_root_toc_entry: false
      members:
        - fetch_url
        - fetch_url_with_progress
        - extract_content_with_css
      show_docstring_attributes: true
      show_docstring_description: true

## Markdown Conversion

::: webdown.markdown_converter
    options:
      show_root_heading: false
      show_root_toc_entry: false
      members:
        - html_to_markdown
        - get_html2text_options
      show_docstring_attributes: true
      show_docstring_description: true

## XML Conversion

::: webdown.xml_converter
    options:
      show_root_heading: false
      show_root_toc_entry: false
      members:
        - markdown_to_claude_xml
        - process_section
      show_docstring_attributes: true
      show_docstring_description: true

## Crawler

::: webdown.crawler
    options:
      show_root_heading: false
      show_root_toc_entry: false
      members:
        - crawl
        - crawl_from_sitemap
        - CrawlerConfig
      show_docstring_attributes: true
      show_docstring_description: true

## Link Extraction

::: webdown.link_extractor
    options:
      show_root_heading: false
      show_root_toc_entry: false
      members:
        - ScopeType
        - extract_links
        - normalize_url
        - filter_links_by_scope
        - parse_sitemap
      show_docstring_attributes: true
      show_docstring_description: true

## Output Management

::: webdown.output_manager
    options:
      show_root_heading: false
      show_root_toc_entry: false
      members:
        - CrawlResult
        - CrawledPage
        - url_to_filepath
        - write_manifest
      show_docstring_attributes: true
      show_docstring_description: true

## Error Handling

::: webdown.error_utils
    options:
      show_root_heading: false
      show_root_toc_entry: false
      members:
        - handle_validation_error
        - get_friendly_error_message
        - format_error_for_cli
        - handle_request_exception
      show_docstring_attributes: true
      show_docstring_description: true

## Exceptions

::: webdown.converter.WebdownError
    options:
      show_bases: true

## Validation

::: webdown.validation
    options:
      show_root_heading: false
      show_root_toc_entry: false
      members:
        - validate_url
        - validate_css_selector
        - validate_body_width
        - validate_numeric_parameter
        - validate_string_parameter
        - validate_boolean_parameter
      show_docstring_attributes: true
      show_docstring_description: true
