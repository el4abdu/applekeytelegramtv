#!/usr/bin/env python3
"""
Test script to verify the key extraction functionality
"""
import re

def extract_key_from_url(url):
    """Extract the Apple TV key from the URL"""
    match = re.search(r'code=([A-Z0-9]+)', url)
    if match:
        return match.group(1)
    return None

# Test URLs
test_urls = [
    "https://tv.apple.com/includes/commerce/authenticate?returnPath=/redeem?ctx=tv%26code=YE634R6H9EWN",
    "https://tv.apple.com/includes/commerce/redeem?ctx=tv&code=YE634R6H9EWN",
    "https://tv.apple.com/redeem?code=ABCDE12345XYZ",
    "https://tv.apple.com/something/else",
]

print("Testing key extraction from URLs:")
for url in test_urls:
    key = extract_key_from_url(url)
    print(f"URL: {url}")
    print(f"Extracted key: {key}")
    print("-" * 50)

# Test the specific example
example_url = "https://tv.apple.com/includes/commerce/redeem?ctx=tv&code=YE634R6H9EWN"
key = extract_key_from_url(example_url)
print(f"Example key extraction:")
print(f"URL: {example_url}")
print(f"Expected key: YE634R6H9EWN")
print(f"Extracted key: {key}")
print(f"Match: {'Yes' if key == 'YE634R6H9EWN' else 'No'}")

if __name__ == "__main__":
    print("\nThis test can be run with: python test_key_extraction.py") 