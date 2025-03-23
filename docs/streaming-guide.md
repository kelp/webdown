# Automatic Streaming for Large Web Pages

Webdown includes built-in support for handling large web pages through an automatic streaming mechanism. This guide explains how streaming works and when it's activated.

## Understanding Streaming Mode

For most web pages, Webdown downloads the entire HTML content at once before processing it. However, for very large web pages, this approach could use excessive memory and potentially cause issues on systems with limited resources.

To address this, Webdown automatically switches to a streaming mode when handling large web pages.

## The 10MB Threshold

Webdown uses a fixed 10MB threshold to determine when to activate streaming mode:

1. When requesting a web page, Webdown first checks its size
2. If the page size is less than 10MB, the entire page is downloaded at once
3. If the page size is 10MB or larger, streaming mode is activated

## How Streaming Works

When streaming mode is activated:

1. Webdown downloads the page in chunks rather than all at once
2. Each chunk is processed as it's received
3. Progress is reported based on the amount of data downloaded
4. Memory usage remains controlled even for extremely large pages

The streaming implementation uses Python's requests library with `stream=True` and processes the response in iterations.

## Progress Reporting in Streaming Mode

When streaming large pages, you'll notice the progress bar behaves slightly differently:

- For regular downloads, the progress bar shows both the download and processing phases
- In streaming mode, the progress bar primarily reflects the download progress

Example terminal output for a streaming download:
```
Downloading and processing https://example.com/largepage
[████████████████████] 100% | 15.8 MB | 00:04 remaining
Converting to Markdown... Done!
```

## Technical Implementation

The streaming functionality is implemented through these key components:

1. **Size checking**: Before downloading, Webdown sends a HEAD request to determine the content size
2. **Threshold decision**: Based on the 10MB threshold, Webdown decides whether to stream
3. **Chunked download**: For streaming, content is downloaded in reasonable chunks (8KB by default)
4. **Incremental processing**: Each chunk is decoded and added to the processing buffer

This implementation balances memory efficiency with processing speed.

## Common Questions

### Why is 10MB the fixed threshold?

The 10MB threshold was chosen based on:
- Testing with a wide range of web pages
- Balancing memory usage and performance
- Ensuring compatibility with most systems

This threshold works well for the vast majority of web pages while protecting against memory issues with extremely large pages.

### Does streaming affect the output quality?

No. The streaming mode only changes how the content is downloaded and processed internally. The final Markdown or Claude XML output is identical regardless of whether streaming was used.

### Is streaming slower than regular downloading?

Streaming can be slightly slower for pages just above the threshold because of the additional processing overhead. However, for very large pages, streaming is often more efficient and prevents potential out-of-memory errors.

### Can I disable streaming?

No, the streaming feature is automatically activated based on the page size and cannot be disabled. This design decision ensures Webdown remains robust when handling pages of any size.

## Use Cases for Large Page Handling

The automatic streaming capability makes Webdown suitable for:

1. **Documentation sites**: Handling large technical documentation
2. **Academic papers**: Processing lengthy scientific publications
3. **Legal documents**: Converting extensive legal texts
4. **Data-heavy reports**: Working with pages containing large tables or datasets

## Limitations

While streaming handles large pages well, be aware of these limitations:

1. Progress reporting is less precise in streaming mode
2. For extremely large pages (100MB+), processing may still take significant time
3. Some websites might not report their content size correctly, affecting the streaming decision
