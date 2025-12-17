import streamlit as st
import re
import json # Import the json module
# Removed asyncio and httpx imports as LLM is no longer used

# --- Page Configuration ---
st.set_page_config(page_title="DAZZLE PREMIUM Order Email Generator", layout="wide", initial_sidebar_state="collapsed")

# --- Custom CSS Styling (Inspired by Material Design & Apple Aesthetics) ---
# Using Google Fonts (Inter for body, Montserrat for headings)
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Montserrat:wght@700&display=swap" rel="stylesheet">
<style>
    /* CSS Variables for consistent theming */
    :root {
        --primary-blue: #007AFF; /* Apple-like blue */
        --primary-blue-dark: #0056B3; /* Darker shade for hover */
        --light-blue-bg: #F0F8FF; /* Very light blue for soft backgrounds */
        --text-dark: #1C1C1E; /* Darker, more Apple-like text */
        --text-medium: #636366;
        --text-light: #AEAEB2;
        --border-color: #E0E0E0; /* Lighter, subtle border */
        --bg-light: #F2F2F7; /* Apple-like light gray background */
        --card-bg: #FFFFFF;

        /* Feedback colors - slightly adjusted for consistency */
        --success-bg: #E6F7EA; /* Lighter green */
        --success-text: #28A745;
        --warning-bg: #FFF8E6; /* Lighter yellow */
        --warning-text: #FFC107;
        --error-bg: #FFEBEB; /* Lighter red */
        --error-text: #DC3545;

        /* Shadows - refined for more depth on hover/active, very subtle */
        --shadow-sm: rgba(0, 0, 0, 0.02) 0px 1px 1px; /* Even lighter shadow */
        --shadow-md: rgba(0, 0, 0, 0.04) 0px 2px 4px; /* Lighter md shadow */
        --shadow-lg: rgba(0, 0, 0, 0.06) 0px 4px 8px; /* Lighter lg shadow */
    }

    /* General Body and App Styling */
    html, body, .stApp {
        font-family: 'Inter', sans-serif;
        color: var(--text-dark);
        background-color: var(--bg-light);
    }
    .main .block-container {
        padding-top: 0.8rem; /* Further reduced padding */
        padding-bottom: 0.8rem; /* Further reduced padding */
        max-width: 750px; /* Further reduced max width for content */
        margin: 0 auto; /* Center content */
    }

    /* Headings */
    h1, h2, h3, h4 {
        font-family: 'Montserrat', sans-serif;
        color: var(--text-dark);
        font-weight: 700;
        margin-top: 1rem; /* Reduced margin */
        margin-bottom: 0.4rem; /* Reduced margin */
    }
    h1 { font-size: 1.8rem; text-align: center; margin-bottom: 1rem; color: var(--primary-blue); } /* Reduced size */
    h2 { font-size: 1.5rem; }
    h3 { font-size: 1rem; }
    h4 { font-size: 0.9rem; color: var(--text-medium); margin-top: 0.5rem; } /* Reduced size, softer color */

    /* Input Fields (Text, Text Area) */
    .stTextInput > div > div > input,
    .stTextArea > div > textarea {
        border: 1px solid var(--border-color);
        border-radius: 6px; /* Reduced roundedness */
        padding: 0.5rem 0.7rem; /* Reduced padding */
        font-size: 0.8rem; /* Reduced font size */
        box-shadow: var(--shadow-sm);
        transition: border-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        background-color: #f0f8ff;
    }
    .stTextArea > div > textarea { /* Specific distinct styling for the text area */
        border: 1px solid var(--primary-blue); /* Distinct blue border */
        box-shadow: 0 0 0 1.5px rgba(0, 122, 255, 0.1), var(--shadow-md); /* Subtle blue glow + distinct shadow */
        background-color: #f0f8ff; /* Ensure white background */
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > textarea:focus {
        border-color: var(--primary-blue);
        box-shadow: 0 0 0 2px rgba(0, 122, 255, 0.2), var(--shadow-md); /* Softer, blue focus ring + deeper shadow */
        outline: none;
    }

    /* Buttons */
    .stButton button {
        background-color: var(--primary-blue);
        color: white;
        font-weight: 600;
        padding: 0.5rem 0.9rem; /* Reduced padding */
        font-size: 0.85rem; /* Reduced font size */
        border-radius: 6px; /* Reduced roundedness */
        border: none;
        box-shadow: var(--shadow-md);
        transition: background-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out, transform 0.1s ease-in-out;
        cursor: pointer;
    }
    .stButton button:hover {
        background-color: var(--primary-blue-dark);
        box-shadow: var(--shadow-lg);
        transform: translateY(-0.5px); /* Subtle lift */
    }
    .stButton button:active {
        transform: translateY(0);
        box-shadow: var(--shadow-sm);
    }

    /* Custom Card Styles for Data Display */
    .info-card, .success-card, .warning-card, .error-card {
        padding: 0.7rem 0.9rem; /* Reduced padding */
        border-radius: 8px; /* Reduced roundedness */
        margin-bottom: 0.8rem; /* Reduced margin */
        gap: 0.5rem; /* Reduced gap */
        font-size: 0.8rem; /* Reduced font size */
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border-color);
        background-color: var(--card-bg);
    }
    .info-card:hover, .success-card:hover, .warning-card:hover, .error-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-0.5px);
    }
    .info-card { color: var(--primary-blue); background-color: var(--light-blue-bg); border-color: rgba(0, 122, 255, 0.06); }
    .success-card { color: var(--success-text); background-color: var(--success-bg); border-color: rgba(40, 167, 69, 0.06); }
    .warning-card { color: var(--warning-text); background-color: var(--warning-bg); border-color: rgba(255, 193, 7, 0.06); }
    .error-card { color: var(--error-text); background-color: var(--error-bg); border-color: rgba(220, 53, 69, 0.06); }
    .info-card span, .success-card span, .warning-card span, .error-card span {
        font-size: 0.9rem; /* Adjusted icon size */
    }

    /* Specific Data Display Boxes (Email, Subject, Phone) */
    .data-display-box {
        background-color: var(--light-blue-bg);
        padding: 0.6rem 0.8rem; /* Reduced padding */
        border-radius: 6px; /* Reduced roundedness */
        margin-bottom: 0.6rem; /* Reduced margin */
        font-size: 0.8rem; /* Reduced font size */
        gap: 5px; /* Reduced gap */
        box-shadow: var(--shadow-sm);
        border: 1px solid rgba(0,0,0,0.03);
    }
    .data-display-box:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-0.5px);
    }

    /* Copy Button within Data Display */
    .copy-button {
        background-color: var(--primary-blue);
        color: white;
        border-radius: 5px; /* Reduced roundedness */
        padding: 0.3rem 0.6rem; /* Reduced padding */
        font-size: 0.7rem; /* Reduced font size */
        box-shadow: var(--shadow-sm);
    }
    .copy-button:hover {
        background-color: var(--primary-blue-dark);
        box-shadow: var(--shadow-md);
    }

    /* Extracted Data Review Cards */
    .extracted-data-card {
        background-color: var(--card-bg);
        border-radius: 8px; /* Reduced roundedness */
        padding: 0.9rem; /* Reduced padding */
        margin-bottom: 0.9rem; /* Reduced margin */
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color);
    }
    .extracted-data-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-1px);
    }
    .extracted-data-card h3 {
        margin-bottom: 0.6rem;
        font-size: 1rem;
        gap: 0.3rem;
    }
    .extracted-data-card .field-row {
        gap: 0.6rem;
        margin-bottom: 0.4rem;
    }
    .extracted-data-card .field-label {
        min-width: 80px; /* Adjusted min-width */
        font-size: 0.8rem;
    }
    .extracted-data-card .field-value-display {
        font-size: 0.8rem;
        padding: 0.3rem 0.6rem;
        border-radius: 5px;
    }
    .extracted-data-card .edit-icon {
        font-size: 0.8rem;
    }

    /* Order Items List */
    .order-item {
        background-color: var(--card-bg);
        border-radius: 6px; /* Reduced roundedness */
        padding: 0.6rem; /* Reduced padding */
        margin-bottom: 0.3rem; /* Reduced margin */
        gap: 0.2rem; /* Reduced gap */
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border-color);
    }
    .order-item:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-0.5px);
    }
    .order-item .item-detail {
        gap: 0.3rem;
    }
    .order-item .item-detail .label {
        min-width: 50px; /* Adjusted min-width */
        font-size: 0.75rem;
    }
    .order-item .item-detail .value {
        font-size: 0.75rem;
    }

    /* Code Block Styling (for email body) */
    .stCode {
        background-color: var(--bg-light);
        border-radius: 8px; /* Reduced roundedness */
        padding: 0.9rem; /* Reduced padding */
        font-size: 0.8rem; /* Reduced font size */
        line-height: 1.4; /* Reduced line height */
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border-color);
    }

    /* Responsive Adjustments */
    @media (max-width: 768px) {
        h1 { font-size: 1.6rem; margin-bottom: 0.8rem; }
        h2 { font-size: 1.2rem; }
        .main .block-container { padding: 0.6rem 0.4rem; }
        .extracted-data-card .field-label { min-width: auto; margin-bottom: 0.1rem; }
        .copy-button { width: 100%; margin-top: 0.3rem; }
        .info-card, .success-card, .warning-card, .error-card { padding: 0.5rem 0.7rem; font-size: 0.75rem; }
        .stButton button { padding: 0.4rem 0.7rem; font-size: 0.8rem; }
        .extracted-data-card { padding: 0.7rem; }
        .extracted-data-card h3 { font-size: 0.9rem; }
        .order-item { padding: 0.4rem; }
    }
</style>
""", unsafe_allow_html=True)

# --- JavaScript for Copy to Clipboard Functionality ---
# This script is injected once and provides a JS function to copy text.
st.markdown("""
<script>
function copyToClipboard(text, elementId) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    try {
        document.execCommand('copy');
        const element = document.getElementById(elementId);
        if (element) {
            element.innerText = 'Copied!';
            setTimeout(() => { element.innerText = 'Copy'; }, 1500); // Reset text after 1.5s
        }
    } catch (err) {
        console.error('Failed to copy text: ', err);
    }
    document.body.removeChild(textarea);
}
</script>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if "current_step" not in st.session_state:
    st.session_state.current_step = "input"  # input, generate_standard, generate_high_risk, generate_return
if "raw_text" not in st.session_state:
    st.session_state.raw_text = ""
if "parsed_data" not in st.session_state:
    st.session_state.parsed_data = {}
if "generated_email_body" not in st.session_state:
    st.session_state.generated_email_body = ""
if "generated_subject" not in st.session_state:
    st.session_state.generated_subject = ""
if "missing_info_flags" not in st.session_state: # Re-added for regex parser
    st.session_state.missing_info_flags = []


# --- Helper Functions ---

def parse_shopify_export(raw_text_input):
    """
    Parses the raw Shopify order export text to extract key information.
    This function uses multiple, redundant regex patterns and fallback strategies
    to maximize extraction success without human intervention.
    """
    data = {
        "customer_name": "[Customer Name Not Found]",
        "email_address": "[Email Not Found]",
        "phone_number": "[Phone Not Found]",
        "order_number": "[Order # Not Found]",
        "items": [],
        "missing_info": []
    }

    # Normalize input: remove extra spaces, ensure consistent line breaks
    normalized_text = re.sub(r'\s+', ' ', raw_text_input).strip() # Replace multiple spaces with single
    lines = [line.strip() for line in raw_text_input.split('\n') if line.strip()]

    # --- Extract Customer Name (Redundancy Level 1: Multiple Patterns) ---
    name_found = False
    
    # Attempt 1: From "Order confirmation email was sent to [Name] ([email])"
    email_sent_match = re.search(r"Order confirmation email was sent to (.*?) \([\w\.-]+@[\w\.-]+\.[\w\.-]+\)", raw_text_input, re.IGNORECASE)
    if email_sent_match:
        data["customer_name"] = email_sent_match.group(1).strip()
        name_found = True

    # Attempt 2: From "Customer" or "Contact information" sections
    if not name_found:
        for i, line in enumerate(lines):
            # Look for "Customer" or "Contact information" labels
            if re.search(r"Customer\s*$", line, re.IGNORECASE) or re.search(r"Contact information\s*$", line, re.IGNORECASE):
                # Try to find the name on the next line
                if i + 1 < len(lines):
                    potential_name = lines[i+1].split('\n')[0].strip()
                    # Ensure it doesn't look like an email or phone number
                    if "@" not in potential_name and not re.search(r"^\+?\d", potential_name):
                        data["customer_name"] = potential_name
                        name_found = True
                        break
            # Attempt 3: From "Shipping address" or "Billing address" sections
            elif (re.search(r"Shipping address\s*$", line, re.IGNORECASE) or \
                  re.search(r"Billing address\s*$", line, re.IGNORECASE)):
                # Try to find the name on the next line
                if i + 1 < len(lines):
                    potential_name = lines[i+1].split('\n')[0].strip()
                    if "@" not in potential_name and not re.search(r"^\+?\d", potential_name):
                        data["customer_name"] = potential_name
                        name_found = True
                        break
    
    if not name_found or data["customer_name"] == "[Customer Name Not Found]":
        data["missing_info"].append("Customer Name")


    # --- Extract Email Address (Redundancy Level 1: Multiple Patterns) ---
    # Attempt 1: General email pattern
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.[\w\.-]+", raw_text_input)
    if email_match:
        data["email_address"] = email_match.group(0).strip()
    else:
        # Attempt 2: Look for "Email:" label explicitly
        email_label_match = re.search(r"Email:\s*([\w\.-]+@[\w\.-]+\.[\w\.-]+)", raw_text_input, re.IGNORECASE)
        if email_label_match:
            data["email_address"] = email_label_match.group(1).strip()
        else:
            data["missing_info"].append("Email Address")

    # --- Extract Phone Number (Redundancy Level 1: Multiple Patterns) ---
    # Attempt 1: Flexible US phone number regex (common formats)
    phone_match = re.search(r"(\+1[\s\-()]?\d{3}[\s\-()]?\d{3}[\s\-()]?\d{4}|\d{3}[\s\-()]?\d{3}[\s\-()]?\d{4})", raw_text_input)
    if phone_match:
        data["phone_number"] = phone_match.group(0).strip()
    else:
        # Attempt 2: Look for "Phone:" label explicitly
        phone_label_match = re.search(r"(?:Phone|Tel|Contact):\s*(\+?\d[\d\s\-\(\).]{7,})", raw_text_input, re.IGNORECASE)
        if phone_label_match:
            data["phone_number"] = phone_label_match.group(1).strip()
        else:
            data["missing_info"].append("Phone Number")

    # --- Extract Order Number (Redundancy Level 1: Multiple Patterns) ---
    # Attempt 1: dazzlepremium# followed by digits
    order_number_match = re.search(r"dazzlepremium#(\d+)", raw_text_input, re.IGNORECASE)
    if order_number_match:
        data["order_number"] = order_number_match.group(1).strip()
    else:
        # Attempt 2: General "Order #" or "Order Number" followed by digits
        order_number_match_general = re.search(r"(?:Order #|Order Number|Invoice #)\s*(\d+)", raw_text_input, re.IGNORECASE)
        if order_number_match_general:
            data["order_number"] = order_number_match_general.group(1).strip()
        else:
            data["missing_info"].append("Order Number")

    # --- Extract Items (Redundancy Level 2: Layered Heuristics) ---
    # Strategy: Find lines that look like product names, then parse details from surrounding lines.
    
    product_lines_info = []
    # Heuristic 1: Lines containing " - " and ending with a style code (e.g., "Product Name - STYLECODE")
    for i, line in enumerate(lines):
        # This regex looks for product names followed by " - " and a style code,
        # ensuring it's not a line containing keywords like SKU, discount, etc.
        if re.search(r" - [A-Z0-9\-]+$", line) and \
           not any(kw in line.lower() for kw in ["sku", "discount", "subtotal", "shipping", "tax", "total", "paid", "balance"]):
            product_lines_info.append({"line": line, "index": i})
    
    # Heuristic 2: Lines containing a price and a quantity (e.g., "$57.00 x 1")
    # This helps identify product lines that might not have a style code in their main name
    # This is a fallback if Heuristic 1 didn't find anything, or to capture additional items.
    if not product_lines_info: # If no products found by Heuristic 1, try this
        for i, line in enumerate(lines):
            if re.search(r"\$\d+\.\d{2}\s*x\s*\d+", line) and \
               not any(kw in line.lower() for kw in ["sku", "discount", "subtotal", "shipping", "tax", "total", "paid", "balance"]):
                # Try to infer product name from the line above if it looks like a product description
                if i > 0 and " - " in lines[i-1] and not any(kw in lines[i-1].lower() for kw in ["sku", "discount", "subtotal"]):
                    product_lines_info.append({"line": lines[i-1], "index": i-1})
                else: # Fallback: use the line itself as product name, but this is less reliable
                    # This might pick up non-product lines, so it's a last resort
                    product_lines_info.append({"line": line.split('$')[0].strip(), "index": i})


    processed_indices = set() # To avoid processing the same product line multiple times

    for prod_info in product_lines_info:
        line_idx = prod_info["index"]
        if line_idx in processed_indices:
            continue # Skip if already processed

        product_name = "Unknown Product"
        style_code = "N/A"
        size = "Size Not Found" # Default to "Size Not Found"
        quantity = 1

        # Extract product name and style code from the identified product line
        if " - " in prod_info["line"]:
            parts = prod_info["line"].rsplit(" - ", 1)
            product_name = parts[0].strip()
            style_code = parts[1].strip()
        else:
            product_name = prod_info["line"] # Use full line as product name if no " - "

        # Look for size and quantity in the next few lines (Redundancy Level 3: Iterative Scan)
        found_size_for_item = False
        found_quantity_for_item = False

        for offset in range(1, 6): # Scan up to 5 lines after the product line
            if line_idx + offset >= len(lines):
                break # Reached end of document

            potential_detail_line = lines[line_idx + offset].strip()
            
            # Attempt to extract Quantity
            if not found_quantity_for_item:
                qty_match = re.search(r"x\s*(\d+)", potential_detail_line, re.IGNORECASE)
                if qty_match:
                    quantity = int(qty_match.group(1))
                    found_quantity_for_item = True
            
            # Attempt to extract Size (more flexible patterns)
            if not found_size_for_item:
                # Pattern 1: Common letter sizes (S, M, L, XL, etc.) or "One Size"
                size_match = re.search(r"\b(XS|S|M|L|XL|XXL|XXXL|One Size|OS)\b", potential_detail_line, re.IGNORECASE)
                
                # Pattern 2: Sizes like "M / YLW" or "16 / BS" (size is the first part before /)
                if not size_match:
                    match_slash_size = re.search(r"(\b\d{1,2}\b|\b[A-Z]{1,3}\b)\s*/\s*[A-Z0-9]+", potential_detail_line, re.IGNORECASE)
                    if match_slash_size:
                        size = match_slash_size.group(1).strip() # Capture the first group (the actual size part)
                        found_size_for_item = True
                        
                # Pattern 3: Standalone numeric sizes, but ONLY if the line doesn't contain "SKU" or "$"
                if not size_match: # Only attempt if size not found by previous patterns
                    if "SKU" not in potential_detail_line.upper() and "$" not in potential_detail_line:
                        # Very strict: must be just the number or number/number on the line
                        # Ensures it's a standalone size, not part of a larger number or price.
                        numeric_size_match = re.search(r"^\s*(?:US|EU)?\s*(\d{1,3}(?:/\d{1,2})?)\s*$", potential_detail_line, re.IGNORECASE)
                        if numeric_size_match:
                            size = numeric_size_match.group(1).strip()
                            found_size_for_item = True
                        # No need for the broader search here, the strict one is safer given the context.
                        # If it's not a standalone size line, it's probably not a size.

                if size_match and not found_size_for_item: # Only assign if size hasn't been found yet
                    size = size_match.group(0).strip()
                    found_size_for_item = True
            
            # If both size and quantity are found, we can stop scanning for this item's details.
            if found_size_for_item and found_quantity_for_item:
                break 

            # If we hit a line that signifies end of product details (e.g., another product, subtotal, discount)
            # This is a strong signal to stop.
            if any(kw in potential_detail_line.lower() for kw in ["subtotal", "discount", "shipping", "tax", "total", "paid", "balance"]) or \
               (re.search(r" - [A-Z0-9\-]+$", potential_detail_line) and potential_detail_line != prod_info["line"]):
                break # Stop scanning for details for this item

        # Special handling for "Sock" products: assign "One Size" if no explicit size was found
        # and the product name contains "sock".
        if size == "Size Not Found" and "sock" in product_name.lower():
            size = "One Size"

        data["items"].append({
            "product_name": product_name,
            "style_code": style_code,
            "size": size,
            "quantity": quantity
        })
        processed_indices.add(line_idx) # Mark the main product line as processed

    if not data["items"]:
        data["missing_info"].append("Order Items")
    
    # Add "Item Sizes" to missing_info if any item still has "Size Not Found" after all attempts
    for item in data["items"]:
        if item["size"] == "Size Not Found" and "Item Sizes" not in data["missing_info"]:
            data["missing_info"].append("Item Sizes")


    return data


def generate_standard_email(parsed_data):
    """Generates the standard order confirmation email."""
    customer_name = parsed_data.get("customer_name", "[Customer Name Not Found]")
    order_number = parsed_data.get("order_number", "[Order # Not Found]")
    items = parsed_data.get("items", [])

    order_details_list = []
    # Check if there's more than one item to decide on item numbering
    if len(items) > 1:
        for idx, item in enumerate(items):
            item_detail = (
                f"- Item {idx+1}:\n" # Display item count only if multiple items
                f"•\u2060  \u2060Product: {item.get('product_name', 'N/A')}\n"
                f"•\u2060  \u2060Style Code: {item.get('style_code', 'N/A')}\n"
                f"•\u2060  \u2060Size: {item.get('size', 'Size Not Found')}" # Use 'Size Not Found' default
            )
            # Only add quantity if it's greater than 1
            if item.get('quantity', 1) > 1:
                item_detail += f"\n•\u2060  \u2060Quantity: {item.get('quantity', 1)}"
            order_details_list.append(item_detail)
    elif len(items) == 1: # Only one item, no "Item 1:" prefix
        item = items[0]
        item_detail = (
            f"•\u2060  \u2060Product: {item.get('product_name', 'N/A')}\n"
            f"•\u2060  \u2060Style Code: {item.get('style_code', 'N/A')}\n"
            f"•\u2060  \u2060Size: {item.get('size', 'Size Not Found')}" # Use 'Size Not Found' default
        )
        # Only add quantity if it's greater than 1
        if item.get('quantity', 1) > 1:
            item_detail += f"\n•\u2060  \u2060Quantity: {item.get('quantity', 1)}"
        order_details_list.append(item_detail)
    
    order_details = "\n\n".join(order_details_list) if order_details_list else "No items found."

    subject = f"Final Order Confirmation of dazzlepremium#{order_number}"
    message = f"""Hello {customer_name},

This is DAZZLE PREMIUM Support confirming Order {order_number}

- Please reply YES to confirm just this order only.
- Kindly also reply YES to the SMS sent automatically to your inbox.

Order Details:
{order_details}

For your security, we use two-factor authentication. If this order wasn’t placed by you, text us immediately at 410-381-0000 to cancel.

Note: Any order confirmed after 3:00 pm will be scheduled for the next business day.

If you have any questions our US-based team is here Monday–Saturday, 10 AM–6 PM.
Thank you for choosing DAZZLE PREMIUM!"""

    return subject, message

def generate_high_risk_email(parsed_data):
    """Generates the high-risk order cancellation email."""
    customer_name = parsed_data.get("customer_name", "[Customer Name Not Found]")

    subject = f"Important: Your DAZZLE PREMIUM Order - Action Required"
    message = f"""Hello {customer_name},

We hope this message finds you well.

We regret to inform you that your recent order has been automatically cancelled as it was flagged as a high-risk transaction by our system. This is a standard security measure to help prevent unauthorized or fraudulent activity.

If you would still like to proceed with your order, we’d be happy to assist you in placing it manually. To do so, we kindly ask that you transfer the payment via Cash App.

Once the payment is received, we will immediately process your order and provide confirmation along along with tracking details.

If you have any questions or need assistance, feel free to reply to this email.

Thank you,
DAZZLE PREMIUM Support"""
    return subject, message

def generate_return_email(parsed_data):
    """Generates the return mail template."""
    customer_name = parsed_data.get("customer_name", "[Customer Name Not Found]") # Get the customer name

    subject = f"DAZZLE PREMIUM: Your Return Request Instructions"
    message = f"""Dear {customer_name},
Thank you for reaching out to us regarding your return request. To 
ensure a smooth and successful return process, please carefully follow 
the steps below:
1. Go to your local post office or any shipping carrier (USPS, FedEx, UPS, DHL).

2. Create and pay for the return shipping label.
(Please note: You are responsible for the return shipping cost.)

3. Ship the item to the following address:

Dazzle Premium 
3500 East-West Highway 
Suite 1032 
Hyattsville, MD 20782 
+1 (301) 942-0000 

4. Email us the tracking number after you ship the package by replying to this email.

Once we receive the returned item in its original condition with the 
tags intact and complete our inspection, we will process your refund.
If you have any questions, feel free to reply to this email.
"""
    return subject, message


def generate_medium_risk_email(parsed_data):
    """Generates the medium-risk order verification email."""
    customer_name = parsed_data.get("customer_name", "[Customer Name Not Found]")
    order_number = parsed_data.get("order_number", "[Order # Not Found]")
    items = parsed_data.get("items", [])

    # Build order details (similar to standard)
    order_details_list = []
    for item in items:
        item_detail = (
            f"• Product: {item.get('product_name', 'N/A')}\n"
            f"• Style Code: {item.get('style_code', 'N/A')}\n"
            f"• Size: {item.get('size', 'Size Not Found')}"
        )
        order_details_list.append(item_detail)
    order_details = "\n".join(order_details_list) if order_details_list else "No items found."

    subject = f"Verification Required for dazzlepremium#{order_number}"
    message = f"""Hello {customer_name},

Thank you for shopping with DAZZLE PREMIUM. Our system has flagged your recent order (#{order_number}) for additional verification. For your security and to prevent fraudulent activity, we are unable to ship this order until it has been manually reviewed and confirmed.

Order Details:
{order_details}

To complete verification, please reply to this email with:
- Your Order Number
- A valid photo ID (you may cover sensitive information, but your name must be visible)
- A picture of the payment card used (you may cover all digits except the last 4)

Once we receive this information, our fraud prevention team will promptly review it and proceed with shipping.

For your security: If you did not place this order, please text us immediately at 410-381-0000 so we can cancel and secure your account.

Note: Any order confirmed after 3:00 PM will be scheduled for the next business day.

If you have any questions, our US-based team is available Monday–Saturday, 10 AM–6 PM.

We truly value your safety and appreciate your cooperation.

Thank you for choosing DAZZLE PREMIUM!
"""
    return subject, message

def reset_app_state():
    """Resets all session state variables to their initial values."""
    st.session_state.current_step = "input"
    st.session_state.raw_text = ""
    st.session_state.parsed_data = {}
    st.session_state.generated_email_body = ""
    st.session_state.generated_subject = ""
    st.session_state.missing_info_flags = [] # Reset this too
    st.rerun() # Rerun to clear the UI immediately

# --- Main Application Logic ---

st.markdown("""<h1 style='text-align: center;'>📦 DAZZLE PREMIUM Order Email Generator</h1>""", unsafe_allow_html=True)

# Create two columns for the main layout
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("1. Paste Shopify Order Export")
    st.markdown("""
        <div class="info-card">
            <span style="font-size: 1.2rem;">📄</span>
            Paste the full text from your Shopify order export summary below.
            We'll automatically extract all the necessary details.
        </div>
    """, unsafe_allow_html=True)

    raw_text_input = st.text_area(
        "Full Order Export Text",
        height=400,
        value=st.session_state.raw_text,
        placeholder="Paste your Shopify order details here...",
        key="raw_text_input_main" # Add a key to avoid potential conflicts
    
    )

    col_buttons_input = st.columns(4) # Changed to 4 columns to add Medium-Risk button
    with col_buttons_input[0]:
        if st.button("Confirmation Email", use_container_width=True):
            if raw_text_input:
                st.session_state.raw_text = raw_text_input
                st.session_state.parsed_data = parse_shopify_export(raw_text_input)
                st.session_state.missing_info_flags = st.session_state.parsed_data["missing_info"] # Re-assign missing flags
                
                subject, message = generate_standard_email(st.session_state.parsed_data)
                st.session_state.generated_subject = subject
                st.session_state.generated_email_body = message
                st.session_state.current_step = "generate_standard" # Keep track of which email type was generated
                st.rerun()
            else:
                st.warning("Please paste the order export text to generate an email.")
    with col_buttons_input[1]:
        if st.button("High-Risk", use_container_width=True): # Shorter button text
            if raw_text_input:
                st.session_state.raw_text = raw_text_input
                st.session_state.parsed_data = parse_shopify_export(raw_text_input)
                st.session_state.missing_info_flags = st.session_state.parsed_data["missing_info"] # Re-assign missing flags
                
                subject, message = generate_high_risk_email(st.session_state.parsed_data)
                st.session_state.generated_subject = subject
                st.session_state.generated_email_body = message
                st.session_state.current_step = "generate_high_risk" # Keep track of which email type was generated
                st.rerun()
            else:
                st.warning("Please paste the order export text to generate a high-risk email.")
    with col_buttons_input[2]: # Return email (unchanged)
        if st.button("Return Email", use_container_width=True):
            if raw_text_input:
                st.session_state.raw_text = raw_text_input
                st.session_state.parsed_data = parse_shopify_export(raw_text_input) # Parse to get customer name
                st.session_state.missing_info_flags = st.session_state.parsed_data["missing_info"] # Re-assign missing flags
                
                subject, message = generate_return_email(st.session_state.parsed_data)
                st.session_state.generated_subject = subject
                st.session_state.generated_email_body = message
                st.session_state.current_step = "generate_return"
                st.rerun()
            else:
                st.warning("Please paste the order export text to generate a return email.")
    with col_buttons_input[3]: # New Medium-Risk button
        if st.button("Medium-Risk", use_container_width=True):
            if raw_text_input:
                st.session_state.raw_text = raw_text_input
                st.session_state.parsed_data = parse_shopify_export(raw_text_input)
                st.session_state.missing_info_flags = st.session_state.parsed_data["missing_info"]
                subject, message = generate_medium_risk_email(st.session_state.parsed_data)
                st.session_state.generated_subject = subject
                st.session_state.generated_email_body = message
                st.session_state.current_step = "generate_medium_risk"
                st.rerun()
            else:
                st.warning("Please paste the order export text to generate a medium-risk email.")
    
    # Placed Reset All button below the main generation buttons for clarity
    st.button("🔄 Reset All", on_click=reset_app_state, use_container_width=True)


with col_right:
    st.subheader("2. Your Generated Email")
    
    # Conditionally display content based on whether an email has been generated
    if st.session_state.generated_email_body:
        # Display info/warning/success cards (MOVED TO TOP)
        if st.session_state.missing_info_flags and st.session_state.current_step == "generate_standard":
            missing_text = ", ".join(st.session_state.missing_info_flags)
            st.markdown(f"""
                <div class="warning-card">
                    <span style="font-size: 1.2rem;">⚠️</span>
                    <strong>Missing Information:</strong> Could not automatically extract: {missing_text}.
                    Please verify the generated email and manually add/correct these details.
                </div>
            """, unsafe_allow_html=True)
        elif st.session_state.current_step == "generate_high_risk":
            st.markdown("""
                <div class="warning-card">
                    <span style="font-size: 1.2rem;">🚨</span>
                    This is the email for high-risk order cancellations. Please review carefully before sending.
                </div>
            """, unsafe_allow_html=True)
        elif st.session_state.current_step == "generate_return":
            st.markdown("""
                <div class="info-card">
                    <span style="font-size: 1.2rem;">↩️</span>
                    This is the return mail template. Ensure the customer name is correct.
                </div>
            """, unsafe_allow_html=True)
        elif st.session_state.current_step == "generate_medium_risk":
            st.markdown("""
                <div class="warning-card">
                    <span style="font-size: 1.2rem;">🟡</span>
                    This is the email for medium-risk order verification. Please review before sending.
                </div>
            """, unsafe_allow_html=True)
        else: # For standard with no missing info
            st.markdown("""
                <div class="success-card">
                    <span style="font-size: 1.2rem;">✅</span>
                    Email generated successfully! Ready to copy and send.
                </div>
            """, unsafe_allow_html=True)

        # Display recipient email
        st.markdown("<h4>📧 Recipient Email:</h4>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class="data-display-box">
                <span>{st.session_state.parsed_data.get('email_address', 'N/A')}</span>
                <button class="copy-button" id="copyEmailBtn" onclick="copyToClipboard(
                    '{st.session_state.parsed_data.get('email_address', 'N/A').replace("'", "\\'")}', 'copyEmailBtn'
                )">Copy</button>
            </div>
        """, unsafe_allow_html=True)

        # Display email subject
        st.markdown("<h4>📨 Subject:</h4>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class="data-display-box">
                <span>{st.session_state.generated_subject}</span>
                <button class="copy-button" id="copySubjectBtn" onclick="copyToClipboard(
                    '{st.session_state.generated_subject.replace("'", "\\'")}', 'copySubjectBtn'
                )">Copy</button>
            </div>
        """, unsafe_allow_html=True)

        # Display email body
        st.markdown("<h4>📝 Email Body:</h4>", unsafe_allow_html=True)
        st.code(st.session_state.generated_email_body, language="text")
        
        js_safe_email_body = json.dumps(st.session_state.generated_email_body)
        st.markdown(f"""
            <div style="text-align: right; margin-top: -0.8rem; margin-bottom: 0.8rem;">
                <button class="copy-button" id="copyBodyBtn" onclick="copyToClipboard(
                    {js_safe_email_body}, 'copyBodyBtn'
                )">Copy Email Body</button>
            </div>
        """, unsafe_allow_html=True)

        # Display extracted information card (only for standard email, or if user wants to see it for others)
        if st.session_state.current_step == "generate_standard":
            st.markdown(f"""
                <div class="extracted-data-card">
                    <h3><span style="font-size: 1.2rem;">🔍</span> Additional Order Details</h3>
                    <div class="field-row">
                        <span class="field-label">Customer Name:</span>
                        <span class="field-value-display">{st.session_state.parsed_data.get('customer_name', '[Not Found]')}</span>
                    </div>
                    <div class="field-row">
                        <span class="field-label">Order Number:</span>
                        <span class="field-value-display">{st.session_state.parsed_data.get('order_number', '[Not Found]')}</span>
                    </div>
                    <div class="field-row">
                        <span class="field-label">Phone:</span>
                        <span class="field-value-display">{st.session_state.parsed_data.get('phone_number', '[Not Found]')}</span>
                    </div>
                    <h4>Order Items:</h4>
            """, unsafe_allow_html=True)

            if st.session_state.parsed_data.get("items"):
                for item in st.session_state.parsed_data["items"]:
                    st.markdown(f"""
                        <div class="order-item">
                            <div class="item-detail"><span class="label">Product:</span> <span class="value">{item.get('product_name', 'N/A')}</span></div>
                            <div class="item-detail"><span class="label">Style Code:</span> <span class="value">{item.get('style_code', 'N/A')}</span></div>
                            <div class="item-detail"><span class="label">Size:</span> <span class="value">{item.get('size', 'Size Not Found')}</span></div>
                            <div class="item-detail"><span class="label">Quantity:</span> <span class="value">{item.get('quantity', 1)}</span></div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""<div class="info-card">No items extracted.</div>""", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True) # Close extracted-data-card

        # Always show "Start New Order" button on the right side if an email has been generated
        st.button("🔁 Start New Order", on_click=reset_app_state, use_container_width=True)
    else:
        # Placeholder message when no email has been generated yet, now using custom card style
        st.markdown("""
            <div class="info-card" style="min-height: 500px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
                <span style="font-size: 2.2rem; margin-bottom: 0.7rem;">✨</span>
                <p style="font-size: 1rem; font-weight: 600;">Your generated email will appear here.</p>
                <p style="color: var(--text-medium); font-size: 0.85rem;">Paste your order details on the left and click 'Generate Email' to see the magic!</p>
            </div>
        """, unsafe_allow_html=True)
