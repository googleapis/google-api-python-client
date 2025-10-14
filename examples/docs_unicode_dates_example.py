#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: Working with Google Docs API Unicode Date Characters

This example addresses GitHub issue #2547:
"Google doc dates returned as unicode (e.g., \\ue907)"

IMPORTANT: The \\ue907 character is INTENTIONAL API behavior, not a bug!

According to the Google Docs API documentation:
"TextRun.content: Any non-text elements in the run are replaced with the Unicode character U+E907."

This example shows:
1. How to identify these Unicode placeholder characters
2. How to extract the actual date/chip information from richLink properties
3. Best practices for working with Google Docs smart chips
"""

import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth import default


# Unicode character used by Google Docs API for non-text elements
DOCS_SMART_CHIP_PLACEHOLDER = '\ue907'  # U+E907


def analyze_document_with_smart_chips(doc_id, creds_file=None):
    """
    Analyze a Google Doc and properly handle smart chips (dates, etc.).
    
    This demonstrates the correct way to extract date information from 
    Google Docs when encountering the \\ue907 Unicode placeholder.
    
    Args:
        doc_id: Google Docs document ID
        creds_file: Optional path to service account credentials file
    """
    print(f"📄 Analyzing Google Docs document: {doc_id}")
    print("=" * 60)
    
    # Set up authentication
    scopes = ['https://www.googleapis.com/auth/documents.readonly']
    if creds_file and os.path.exists(creds_file):
        creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
    else:
        creds, project = default(scopes=scopes)
    
    # Build the Docs API service
    service = build('docs', 'v1', credentials=creds)
    
    try:
        # Get the document
        document = service.documents().get(
            documentId=doc_id,
            fields='body'  
        ).execute()
        
        # Access the document's content
        content = document.get('body', {}).get('content', [])
        
        print("🔍 Document Analysis Results:")
        print("-" * 40)
        
        element_count = 0
        smart_chip_count = 0
        
        # Process each element
        for element in content:
            if 'paragraph' in element:
                paragraph = element.get('paragraph', {})
                elements = paragraph.get('elements', [])
                
                for elem in elements:
                    element_count += 1
                    
                    # Check for textRun content (where Unicode placeholders appear)
                    if 'textRun' in elem:
                        text_run = elem['textRun']
                        content_text = text_run.get('content', '')
                        
                        print(f"\n📝 Element {element_count}:")
                        print(f"   Raw content: {repr(content_text)}")
                        
                        # Check for smart chip placeholder
                        if DOCS_SMART_CHIP_PLACEHOLDER in content_text:
                            smart_chip_count += 1
                            print(f"   🎯 SMART CHIP/DATE DETECTED!")
                            print(f"   📍 Found Unicode placeholder: U+E907 (\\ue907)")
                            print(f"   💡 This represents a non-text element (date, person, etc.)")
                            
                            # Show how to make it readable for display purposes
                            readable = content_text.replace(DOCS_SMART_CHIP_PLACEHOLDER, '[DATE/CHIP]')
                            print(f"   ✨ Display version: {repr(readable)}")
                        else:
                            print(f"   📝 Regular text content")
                    
                    # IMPORTANT: Check for rich links - this is where actual data lives!
                    if 'richLink' in elem:
                        rich_link = elem['richLink']
                        print(f"\n   🔗 RICH LINK FOUND - This may contain the actual date/chip data!")
                        print(f"       Rich Link ID: {rich_link.get('richLinkId', 'N/A')}")
                        
                        # Rich link properties contain the real information
                        if 'richLinkProperties' in rich_link:
                            props = rich_link['richLinkProperties']
                            title = props.get('title', 'N/A')
                            uri = props.get('uri', 'N/A')
                            
                            print(f"       📅 Title: {title}")  # ← ACTUAL DATE IS HERE!
                            print(f"       🔗 URI: {uri}")
                            
                            # Check if this looks like a date
                            date_keywords = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                                           'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
                                           '2024', '2025', 'monday', 'tuesday', 'wednesday']
                            
                            if any(keyword in title.lower() for keyword in date_keywords):
                                print(f"   🎉 SUCCESS! Found actual date information: '{title}'")
                            
                            # Check if it's a calendar event
                            if 'calendar.google.com' in uri or 'calendar' in uri.lower():
                                print(f"   📆 This appears to be a Google Calendar event!")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"📈 Total elements processed: {element_count}")
        print(f"🎯 Smart chips/dates found: {smart_chip_count}")
        
        if smart_chip_count > 0:
            print(f"\n💡 KEY INSIGHTS:")
            print(f"   • The \\ue907 character is NOT a bug - it's intentional API design")
            print(f"   • Look for 'richLink' properties to get actual date/chip information")
            print(f"   • The API replaces smart chips with placeholders for plain text extraction")
            print(f"   • Use Google Calendar API for detailed event information")
        
        print(f"\n🔧 TECHNICAL DETAILS:")
        print(f"   • Unicode Character: U+E907 (\\ue907)")
        print(f"   • API Behavior: Documented in TextRun.content specification")
        print(f"   • Purpose: Represents non-text elements (smart chips)")
        print(f"   • Workaround: Extract data from richLinkProperties")
        
    except Exception as e:
        print(f"❌ Error analyzing document: {e}")
        print(f"💡 Make sure you have proper authentication and document access")


def demonstrate_unicode_handling():
    """Demonstrate how to handle the Unicode characters from issue #2547."""
    print("\n🧪 UNICODE CHARACTER DEMONSTRATION")
    print("=" * 60)
    
    # Example content from GitHub issue #2547
    example_from_issue = '\ue907 | '
    
    print("📋 Example from GitHub Issue #2547:")
    print(f"   Original API response: {repr(example_from_issue)}")
    print(f"   Character breakdown:")
    print(f"     - '\\ue907' = Unicode U+E907 (smart chip placeholder)")
    print(f"     - ' | '     = Regular text")
    
    print(f"\n🔍 Character Analysis:")
    for i, char in enumerate(example_from_issue):
        if char == DOCS_SMART_CHIP_PLACEHOLDER:
            print(f"   Position {i}: '\\ue907' → Smart chip/date placeholder")
        else:
            print(f"   Position {i}: {repr(char)} → Regular text")
    
    print(f"\n✨ Making It Readable:")
    readable_version = example_from_issue.replace(DOCS_SMART_CHIP_PLACEHOLDER, '[DATE]')
    print(f"   Original:  {repr(example_from_issue)}")
    print(f"   Readable:  {repr(readable_version)}")
    
    print(f"\n💡 Best Practices:")
    print(f"   1. Don't try to 'decode' \\ue907 - it's just a placeholder")
    print(f"   2. Look for richLink properties in the same or adjacent elements")
    print(f"   3. Use context from surrounding text elements")
    print(f"   4. For calendar events, use Google Calendar API with event IDs")
    print(f"   5. Accept that some smart chip data may not be fully accessible via Docs API")


def suggest_next_steps():
    """Provide actionable next steps for developers facing this issue."""
    print(f"\n🚀 NEXT STEPS FOR DEVELOPERS")
    print("=" * 60)
    
    steps = [
        "1. 🔍 Accept that \\ue907 is intentional API behavior, not a bug",
        "2. 📋 Always check for 'richLink' elements when processing documents",
        "3. 🔗 Extract actual data from richLinkProperties.title and .uri",
        "4. 📅 Use Google Calendar API for detailed event information",
        "5. 👥 Use Google People API for person chip details",
        "6. 🏢 Use Google Places API for location chip information",
        "7. 📝 Implement context analysis of surrounding text elements",
        "8. 🧪 Test with various smart chip types (dates, people, places)",
        "9. 📚 Read the Google Docs API documentation on TextRun.content",
        "10. 💬 Educate users that this is expected API behavior"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print(f"\n📚 USEFUL RESOURCES:")
    print(f"   • GitHub Issue: https://github.com/googleapis/google-api-python-client/issues/2547")
    print(f"   • Google Docs API: https://developers.google.com/docs/api/reference/rest/v1/documents")
    print(f"   • Google Calendar API: https://developers.google.com/calendar/api")
    print(f"   • Unicode Private Use Areas: https://en.wikipedia.org/wiki/Private_Use_Areas")


if __name__ == "__main__":
    print("🔧 Google Docs API: Working with Smart Chip Unicode Characters")
    print("   Addressing GitHub Issue #2547")
    print()
    
    # Demonstrate how to handle the Unicode characters
    demonstrate_unicode_handling()
    
    # Provide actionable guidance
    suggest_next_steps()
    
    print(f"\n📖 USAGE EXAMPLE:")
    print("# To analyze an actual document:")
    print("# analyze_document_with_smart_chips('your-document-id-here')")
    print("# analyze_document_with_smart_chips('your-doc-id', '/path/to/credentials.json')")
    
    print(f"\n🎯 REMEMBER:")
    print("This is NOT a client library bug - it's intentional Google Docs API behavior!")
    print("Focus on extracting data from richLink properties, not decoding Unicode characters.")