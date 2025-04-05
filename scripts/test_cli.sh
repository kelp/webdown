#\!/bin/bash
# Comprehensive CLI testing script for webdown
# Tests all flags and options with a real website

set -e  # Exit immediately if a command exits with a non-zero status
set -u  # Treat unset variables as an error when substituting

# Create a directory for test outputs
TEST_DIR="$(mktemp -d)/webdown_cli_tests"
mkdir -p "$TEST_DIR"
echo "Running tests with output in $TEST_DIR"

# Helper function to run a test
run_test() {
    local test_name="$1"
    local cmd="$2"
    local output_file="${3:-$TEST_DIR/${test_name}.md}"

    echo "Testing: $test_name"
    echo "Command: $cmd"

    # Create command with redirect if not explicitly provided
    if [[ "$cmd" \!= *">"* && "$cmd" \!= *"-o"* ]]; then
        cmd="$cmd > \"$output_file\""
    fi

    # Run the command
    eval "$cmd"

    # For curl tests, check the downloaded file directly
    if [[ "$test_name" == download_html* ]]; then
        if [[ -s "$TEST_DIR/test.html" || -s "$TEST_DIR/example.html" ]]; then
            echo "✅ Test passed: HTML file downloaded successfully"
            return 0
        else
            echo "❌ Test failed: HTML file is empty or missing"
            return 1
        fi
    fi

    # For tests that specify their own output file with -o option
    if [[ "$test_name" == *"_to_file" ]]; then
        # Get the output file path
        if [[ "$test_name" == "url_to_file" ]]; then
            check_file="$TEST_DIR/url_output.md"
        elif [[ "$test_name" == "file_to_file" ]]; then
            check_file="$TEST_DIR/file_output.md"
        else
            check_file=""
        fi

        if [[ -n "$check_file" && -s "$check_file" ]]; then
            echo "✅ Test passed: Output file created with content"
            word_count=$(wc -w < "$check_file")
            echo "   Word count: $word_count"
            return 0
        else
            echo "❌ Test failed: Output file is empty or missing"
            echo "Looking for: $check_file"
            ls -la "$TEST_DIR"
            return 1
        fi
    # For tests that output to the default output file
    elif [[ -s "$output_file" ]]; then
        echo "✅ Test passed: Output file created with content"
        # Count words in the file to verify it has reasonable content
        word_count=$(wc -w < "$output_file")
        echo "   Word count: $word_count"
        return 0
    else
        echo "❌ Test failed: Output file is empty or missing"
        echo "Looking for: $output_file"
        ls -la "$TEST_DIR"
        return 1
    fi
}

# Use a reliable website with stable content
TEST_URL="https://httpbin.org/html"
TEST_URL2="https://example.com"

# Test conversion of website to HTML file for later file-based tests
run_test "download_html" "curl -s $TEST_URL -o \"$TEST_DIR/test.html\""
run_test "download_html2" "curl -s $TEST_URL2 -o \"$TEST_DIR/example.html\""

# ---------------------------------------------
# URL-based tests for all command-line options
# ---------------------------------------------

# Basic URL to markdown conversion
run_test "basic_url" "./scripts/run.sh webdown -u $TEST_URL > \"$TEST_DIR/basic_url.md\""

# URL to file with output option
run_test "url_to_file" "./scripts/run.sh webdown -u $TEST_URL -o \"$TEST_DIR/url_output.md\""

# With progress bar
run_test "progress_bar" "./scripts/run.sh webdown -u $TEST_URL -p > \"$TEST_DIR/progress_bar.md\""

# CSS selector options
run_test "css_selector" "./scripts/run.sh webdown -u $TEST_URL -s \"body\" > \"$TEST_DIR/css_selector.md\""

# Table of contents
run_test "table_of_contents" "./scripts/run.sh webdown -u $TEST_URL -t > \"$TEST_DIR/table_of_contents.md\""

# No links
run_test "no_links" "./scripts/run.sh webdown -u $TEST_URL -L > \"$TEST_DIR/no_links.md\""

# No images
run_test "no_images" "./scripts/run.sh webdown -u $TEST_URL -I > \"$TEST_DIR/no_images.md\""

# Compact output
run_test "compact_output" "./scripts/run.sh webdown -u $TEST_URL -c > \"$TEST_DIR/compact_output.md\""

# Width setting
run_test "width_setting" "./scripts/run.sh webdown -u $TEST_URL -w 40 > \"$TEST_DIR/width_setting.md\""

# Claude XML output
run_test "claude_xml" "./scripts/run.sh webdown -u $TEST_URL --claude-xml" "$TEST_DIR/claude_xml.xml"

# Claude XML without metadata
run_test "claude_xml_no_metadata" "./scripts/run.sh webdown -u $TEST_URL --claude-xml --no-metadata" "$TEST_DIR/claude_xml_no_metadata.xml"

# Claude XML without date
run_test "claude_xml_no_date" "./scripts/run.sh webdown -u $TEST_URL --claude-xml --no-date" "$TEST_DIR/claude_xml_no_date.xml"

# Combination of multiple options
run_test "url_multi_options" "./scripts/run.sh webdown -u $TEST_URL -t -c -w 50 -s \"body\" > \"$TEST_DIR/url_multi_options.md\""

# ---------------------------------------------
# File-based tests for all command-line options
# ---------------------------------------------

# Basic file to markdown conversion
run_test "basic_file" "./scripts/run.sh webdown -f \"$TEST_DIR/test.html\" > \"$TEST_DIR/basic_file.md\""

# File to file with output option
run_test "file_to_file" "./scripts/run.sh webdown -f \"$TEST_DIR/test.html\" -o \"$TEST_DIR/file_output.md\""

# CSS selector options
run_test "file_css_selector" "./scripts/run.sh webdown -f \"$TEST_DIR/test.html\" -s \"body\" > \"$TEST_DIR/file_css_selector.md\""

# Table of contents
run_test "file_table_of_contents" "./scripts/run.sh webdown -f \"$TEST_DIR/test.html\" -t > \"$TEST_DIR/file_table_of_contents.md\""

# No links
run_test "file_no_links" "./scripts/run.sh webdown -f \"$TEST_DIR/test.html\" -L > \"$TEST_DIR/file_no_links.md\""

# No images
run_test "file_no_images" "./scripts/run.sh webdown -f \"$TEST_DIR/test.html\" -I > \"$TEST_DIR/file_no_images.md\""

# Compact output
run_test "file_compact_output" "./scripts/run.sh webdown -f \"$TEST_DIR/test.html\" -c > \"$TEST_DIR/file_compact_output.md\""

# Width setting
run_test "file_width_setting" "./scripts/run.sh webdown -f \"$TEST_DIR/test.html\" -w 40 > \"$TEST_DIR/file_width_setting.md\""

# Claude XML output
run_test "file_claude_xml" "./scripts/run.sh webdown -f \"$TEST_DIR/test.html\" --claude-xml" "$TEST_DIR/file_claude_xml.xml"

# Claude XML without metadata
run_test "file_claude_xml_no_metadata" "./scripts/run.sh webdown -f \"$TEST_DIR/test.html\" --claude-xml --no-metadata" "$TEST_DIR/file_claude_xml_no_metadata.xml"

# Claude XML without date
run_test "file_claude_xml_no_date" "./scripts/run.sh webdown -f \"$TEST_DIR/test.html\" --claude-xml --no-date" "$TEST_DIR/file_claude_xml_no_date.xml"

# Combination of multiple options
run_test "file_multi_options" "./scripts/run.sh webdown -f \"$TEST_DIR/test.html\" -t -c -w 50 -s \"body\" > \"$TEST_DIR/file_multi_options.md\""

# ---------------------------------------------
# Version test
# ---------------------------------------------
VERSION=$(./scripts/run.sh webdown --version)
echo "Version test: $VERSION"
if [[ "$VERSION" == *"webdown"* && "$VERSION" == *"0.7.0"* ]]; then
    echo "✅ Version test passed"
else
    echo "❌ Version test failed"
fi

# ---------------------------------------------
# Help test
# ---------------------------------------------
HELP=$(./scripts/run.sh webdown --help)
echo "Help test: ${#HELP} characters"
if [[ "$HELP" == *"webdown"* && "$HELP" == *"--url"* && "$HELP" == *"--file"* ]]; then
    echo "✅ Help test passed"
else
    echo "❌ Help test failed"
fi

# ---------------------------------------------
# Additional test with example.com
# ---------------------------------------------
run_test "example_url" "./scripts/run.sh webdown -u $TEST_URL2 > \"$TEST_DIR/example_url.md\""
run_test "example_file" "./scripts/run.sh webdown -f \"$TEST_DIR/example.html\" > \"$TEST_DIR/example_file.md\""

# ---------------------------------------------
# Test auto-fixing URLs
# ---------------------------------------------
run_test "autofix_url" "./scripts/run.sh webdown -u example.com > \"$TEST_DIR/autofix_url.md\""

# ---------------------------------------------
# Summary
# ---------------------------------------------
echo "All tests completed successfully\!"
echo "Test outputs saved to $TEST_DIR"
echo "Tests completed at $(date)"
