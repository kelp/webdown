# Webdown Troubleshooting Guide

This guide helps you understand and handle common issues when using Webdown.

## Common Errors and Solutions

### Network Errors

#### Connection Errors

**Error Message**: "Failed to establish a connection to the URL: Connection refused"

**Possible Causes**:
- The website is down
- Your internet connection is unstable
- The website is blocking requests with our default User-Agent

**Solutions**:
1. Check if the website is accessible in your browser
2. Try again in a few minutes if the site might be temporarily down
3. Use a custom User-Agent with the `--user-agent` flag:
   ```bash
   webdown --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" https://example.com
   ```

#### Timeout Errors

**Error Message**: "Request timed out after X seconds"

**Possible Causes**:
- The website is slow to respond
- The website has large resources that take time to load
- Your internet connection is slow

**Solutions**:
1. Increase the timeout with the `--timeout` flag:
   ```bash
   webdown --timeout 60 https://example.com
   ```
2. Try again when your internet connection is more stable

### Invalid URL Errors

**Error Message**: "Invalid URL: The URL must begin with http:// or https://"

**Solution**:
Ensure your URL starts with either `http://` or `https://`. Webdown requires fully-formed URLs.

### CSS Selector Errors

**Error Message**: "Invalid CSS selector: Not a valid CSS selector" or "CSS selector did not match any elements"

**Possible Causes**:
- The CSS selector syntax is invalid
- The selector doesn't match any elements on the page
- The page structure has changed since you last used the selector

**Solutions**:
1. Check the syntax of your CSS selector
2. Use browser developer tools to verify your selector matches elements on the current page
3. Try a broader selector:
   ```bash
   webdown --css "main, article, .content" https://example.com
   ```

### Content Extraction Errors

**Error Message**: "Failed to extract content" or "No content found after extraction"

**Possible Causes**:
- The page uses JavaScript to render content (Webdown doesn't execute JavaScript)
- The CSS selector didn't match any content-containing elements
- The page structure is unusual

**Solutions**:
1. Try without a CSS selector to get the entire page
2. Use a browser developer tool to find a better CSS selector
3. For JavaScript-heavy sites, consider using a different tool that can execute JavaScript

## Large File Handling

When processing very large web pages (>10MB), Webdown automatically switches to streaming mode. You might notice:

- Progress reporting is less precise
- Memory usage is optimized but processing might be slower

This behavior is normal and helps handle large sites without excessive memory usage.

## Markdown Formatting Issues

### Table of Contents Problems

**Issue**: Table of contents links are not working correctly

**Possible Causes**:
- Special characters in headings
- Duplicate heading names
- Complex formatting in headings

**Solutions**:
1. Use the `--toc-depth` flag to limit TOC depth:
   ```bash
   webdown --toc --toc-depth 2 https://example.com
   ```
2. For files with many similar headings, try post-processing with a text editor

### Code Block Formatting

**Issue**: Code blocks are not formatted correctly

**Possible Causes**:
- The original HTML doesn't use standard code tags
- The code has special formatting that's lost in conversion

**Solutions**:
1. Use `--preserve-emphasis` to maintain more formatting:
   ```bash
   webdown --preserve-emphasis https://example.com
   ```
2. For Claude XML output, code blocks are automatically wrapped in `<answer>` tags with language information preserved

## Claude XML Specific Issues

### XML Validation Errors

**Issue**: Output XML is not recognized by Claude

**Possible Causes**:
- Unclosed XML tags in the content
- Malformed XML due to special characters
- Invalid HTML in the source document

**Solutions**:
1. Use the `--compact` option to reduce extraneous whitespace:
   ```bash
   webdown --claude-xml --compact https://example.com
   ```
2. Check if the source HTML has valid structure
3. For complex pages, try extracting specific sections with CSS selectors:
   ```bash
   webdown --claude-xml --css "main, article" https://example.com
   ```

## Getting Help

If you continue to experience issues not covered in this guide:

1. Check the [GitHub Issues](https://github.com/kelp-labs/webdown/issues) to see if your problem has been reported
2. If not, create a new issue with:
   - The command you ran
   - The complete error message
   - The URL you were trying to process (if not private)
   - Your operating system and Python version
