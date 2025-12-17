import streamlit as st
import re
import json # Import the json module
import pandas as pd
# Removed asyncio and httpx imports as LLM is no longer used

# --- Page Configuration ---
st.set_page_config(page_title="DAZZLE PREMIUM Order Email Generator", layout="wide", initial_sidebar_state="collapsed")

# --- Custom CSS Styling (Alive & Handcrafted) ---
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    html, body, .stApp {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
        background: #f8f9fa;
        color: #2c3e50;
    }

    .main .block-container {
        max-width: 1280px;
        padding: 3rem 2.5rem;
        background: white;
        margin: 0 auto;
    }

    /* Typography - Warm & Real */
    h1 {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a1a;
        margin: 0 0 0.2rem 0;
        letter-spacing: -0.5px;
    }

    .subtitle {
        font-size: 1rem;
        color: #7f8c8d;
        font-weight: 400;
        margin: 0 0 2rem 0;
        letter-spacing: 0.3px;
    }

    h2 {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a1a1a;
        margin: 1.5rem 0 0.8rem 0;
    }

    h3 {
        font-size: 1.15rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 1rem 0 0.6rem 0;
    }

    h4 {
        font-size: 0.8rem;
        font-weight: 700;
        color: #7f8c8d;
        margin: 1rem 0 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }

    p {
        font-size: 0.95rem;
        color: #555;
        line-height: 1.6;
    }

    /* Buttons - Warm & Interactive */
    .stButton button {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.65rem 1.3rem;
        font-weight: 600;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.23, 1, 0.320, 1);
        box-shadow: 0 2px 8px rgba(44, 62, 80, 0.15);
    }

    .stButton button:hover {
        background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%);
        box-shadow: 0 4px 16px rgba(44, 62, 80, 0.25);
        transform: translateY(-2px);
    }

    .stButton button:active {
        transform: translateY(0);
    }

    /* Input Fields - Inviting */
    .stTextInput > div > div > input,
    .stTextArea > div > textarea {
        background-color: #fafbfc !important;
        border: 1.5px solid #e0e6ed !important;
        border-radius: 7px !important;
        padding: 0.9rem !important;
        font-size: 0.95rem !important;
        color: #2c3e50 !important;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > textarea::placeholder {
        color: #bdc3c7 !important;
        font-weight: 400;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > textarea:focus {
        border-color: #34495e !important;
        box-shadow: 0 0 0 3px rgba(44, 62, 80, 0.08) !important;
        outline: none !important;
        background-color: white !important;
    }

    /* Status Cards - Expressive */
    .success-card {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-left: 4px solid #22c55e;
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 1.2rem;
        color: #166534;
        font-size: 0.9rem;
        font-weight: 500;
        box-shadow: 0 2px 6px rgba(34, 197, 94, 0.1);
    }

    .warning-card {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border-left: 4px solid #f59e0b;
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 1.2rem;
        color: #92400e;
        font-size: 0.9rem;
        font-weight: 500;
        box-shadow: 0 2px 6px rgba(245, 158, 11, 0.1);
    }

    .info-card {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-left: 4px solid #0ea5e9;
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 1.2rem;
        color: #0c2340;
        font-size: 0.9rem;
        font-weight: 500;
        box-shadow: 0 2px 6px rgba(14, 165, 233, 0.1);
    }

    /* Data Display Boxes - Prominent */
    .data-display-box {
        background: #f8f9fa;
        border: 1.5px solid #e0e6ed;
        border-radius: 7px;
        padding: 1rem;
        margin-bottom: 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.9rem;
        transition: all 0.2s ease;
    }

    .data-display-box:hover {
        border-color: #34495e;
        background: white;
    }

    .data-display-box span:first-child {
        color: #2c3e50;
        word-break: break-all;
        flex: 1;
        font-weight: 500;
    }

    /* Copy Button - Actionable */
    .copy-button {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-size: 0.8rem;
        font-weight: 600;
        cursor: pointer;
        margin-left: 0.8rem;
        white-space: nowrap;
        transition: all 0.25s ease;
        box-shadow: 0 2px 6px rgba(44, 62, 80, 0.1);
    }

    .copy-button:hover {
        background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%);
        box-shadow: 0 3px 10px rgba(44, 62, 80, 0.15);
        transform: translateY(-1px);
    }

    /* Extracted Data Card - Clean but Warm */
    .extracted-data-card {
        background: linear-gradient(135deg, #f8f9fa 0%, white 100%);
        border: 1.5px solid #e0e6ed;
        border-radius: 7px;
        padding: 1.2rem;
        margin-top: 1.2rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }

    .field-row {
        display: flex;
        gap: 1.2rem;
        margin-bottom: 0.8rem;
        font-size: 0.9rem;
        align-items: center;
    }

    .field-label {
        font-weight: 700;
        color: #7f8c8d;
        min-width: 110px;
        text-transform: uppercase;
        font-size: 0.72rem;
        letter-spacing: 0.3px;
    }

    .field-value-display {
        color: #2c3e50;
        flex: 1;
        background: white;
        padding: 0.5rem 0.8rem;
        border-radius: 5px;
        border: 1px solid #e0e6ed;
        font-weight: 500;
    }

    /* Order Items - Readable */
    .order-item {
        background: linear-gradient(135deg, white 0%, #f8f9fa 100%);
        border: 1.5px solid #e0e6ed;
        border-radius: 6px;
        padding: 0.9rem;
        margin-bottom: 0.7rem;
        font-size: 0.85rem;
        transition: all 0.2s ease;
    }

    .order-item:hover {
        border-color: #34495e;
        box-shadow: 0 2px 8px rgba(44, 62, 80, 0.1);
    }

    .item-detail {
        display: flex;
        gap: 0.8rem;
        margin-bottom: 0.5rem;
        align-items: flex-start;
    }

    .item-detail .label {
        font-weight: 700;
        color: #7f8c8d;
        min-width: 75px;
        text-transform: uppercase;
        font-size: 0.68rem;
        letter-spacing: 0.2px;
    }

    .item-detail .value {
        color: #2c3e50;
        font-weight: 500;
    }

    /* Code Block - Readable */
    .stCode {
        background: #f5f7fa !important;
        border: 1.5px solid #e0e6ed !important;
        border-radius: 6px !important;
        padding: 1.2rem !important;
        line-height: 1.6;
    }

    .stCode code {
        color: #2c3e50 !important;
        font-weight: 500;
    }

    /* Tabs - Natural */
    [data-baseweb="tab"] {
        font-weight: 600;
        color: #7f8c8d;
    }

    [data-baseweb="tab"][aria-selected="true"] {
        color: #2c3e50;
    }

    /* Expander - Inviting */
    .st-expander {
        border: 1.5px solid #e0e6ed !important;
        border-radius: 6px !important;
        overflow: hidden;
        background: white !important;
        margin-bottom: 1.2rem;
    }

    [data-testid="stExpanderDetails"] {
        background: #f8f9fa !important;
    }

    /* Divider - Subtle */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #e0e6ed, transparent);
        margin: 2rem 0;
    }

    /* Section Spacing */
    [data-testid="column"] {
        gap: 2rem;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 2rem 1.5rem;
        }
        h1 {
            font-size: 1.8rem;
        }
        .field-row {
            flex-direction: column;
            gap: 0.4rem;
        }
        .data-display-box {
            flex-direction: column;
            align-items: flex-start;
        }
        .copy-button {
            margin-left: 0;
            margin-top: 0.8rem;
            width: 100%;
        }
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

st.markdown("""<h1>✨ Dazzle Premium</h1>""", unsafe_allow_html=True)
st.markdown("""<p class='subtitle'>Order Email Generator — Ship faster, communicate better</p>""", unsafe_allow_html=True)
st.divider()

# Tabs for different sections
tab1, tab2 = st.tabs(["📧 Email Generator", "📦 Batch Orders"])

with tab1:
    st.markdown("<h2 style='margin-top: 0;'>Generate Professional Emails</h2>", unsafe_allow_html=True)
    
    # Create two columns
    col_left, col_right = st.columns([1.15, 0.95], gap="large")

    with col_left:
        st.markdown("<h3>Order Details</h3>", unsafe_allow_html=True)

        raw_text_input = st.text_area(
            "Paste Order Export",
            height=240,
            value=st.session_state.raw_text,
            placeholder="Paste your complete Shopify order export here...",
            key="raw_text_input_main",
            label_visibility="collapsed"
        )

        st.markdown("<h4 style='margin-top: 1.2rem;'>Choose Email Type</h4>", unsafe_allow_html=True)
        col_buttons = st.columns(4, gap="small")
        
        with col_buttons[0]:
            if st.button("✓ Confirmation", use_container_width=True, key="btn_confirm"):
                if raw_text_input:
                    st.session_state.raw_text = raw_text_input
                    st.session_state.parsed_data = parse_shopify_export(raw_text_input)
                    st.session_state.missing_info_flags = st.session_state.parsed_data["missing_info"]
                    subject, message = generate_standard_email(st.session_state.parsed_data)
                    st.session_state.generated_subject = subject
                    st.session_state.generated_email_body = message
                    st.session_state.current_step = "generate_standard"
                    st.rerun()
                else:
                    st.warning("Please paste order details first")
        
        with col_buttons[1]:
            if st.button("⚠️ High-Risk", use_container_width=True, key="btn_highrisk"):
                if raw_text_input:
                    st.session_state.raw_text = raw_text_input
                    st.session_state.parsed_data = parse_shopify_export(raw_text_input)
                    st.session_state.missing_info_flags = st.session_state.parsed_data["missing_info"]
                    subject, message = generate_high_risk_email(st.session_state.parsed_data)
                    st.session_state.generated_subject = subject
                    st.session_state.generated_email_body = message
                    st.session_state.current_step = "generate_high_risk"
                    st.rerun()
                else:
                    st.warning("Please paste order details first")
        
        with col_buttons[2]:
            if st.button("↩️ Return", use_container_width=True, key="btn_return"):
                if raw_text_input:
                    st.session_state.raw_text = raw_text_input
                    st.session_state.parsed_data = parse_shopify_export(raw_text_input)
                    st.session_state.missing_info_flags = st.session_state.parsed_data["missing_info"]
                    subject, message = generate_return_email(st.session_state.parsed_data)
                    st.session_state.generated_subject = subject
                    st.session_state.generated_email_body = message
                    st.session_state.current_step = "generate_return"
                    st.rerun()
                else:
                    st.warning("Please paste order details first")
        
        with col_buttons[3]:
            if st.button("🔍 Verify", use_container_width=True, key="btn_medium"):
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
                    st.warning("Please paste order details first")

    with col_right:
        st.markdown("<h3>Email Preview</h3>", unsafe_allow_html=True)

        if st.session_state.generated_email_body:
            # Status indicator
            if st.session_state.missing_info_flags and st.session_state.current_step == "generate_standard":
                st.markdown(f"""<div class="warning-card">⚠️ <strong>Missing:</strong> {", ".join(st.session_state.missing_info_flags)}</div>""", unsafe_allow_html=True)
            elif st.session_state.current_step == "generate_high_risk":
                st.markdown("""<div class="warning-card"><strong>🚨 High-Risk Email</strong></div>""", unsafe_allow_html=True)
            elif st.session_state.current_step == "generate_return":
                st.markdown("""<div class="info-card"><strong>↩️ Return Request</strong></div>""", unsafe_allow_html=True)
            elif st.session_state.current_step == "generate_medium_risk":
                st.markdown("""<div class="warning-card"><strong>🔍 Verification Required</strong></div>""", unsafe_allow_html=True)
            else:
                st.markdown("""<div class="success-card"><strong>✓ Ready to send</strong></div>""", unsafe_allow_html=True)

            st.markdown("<h4>To</h4>", unsafe_allow_html=True)
            st.markdown(f"""
                <div class="data-display-box">
                    <span>{st.session_state.parsed_data.get('email_address', 'N/A')}</span>
                    <button class="copy-button" id="copyEmailBtn" onclick="copyToClipboard(
                        '{st.session_state.parsed_data.get('email_address', 'N/A').replace("'", "\\'")}', 'copyEmailBtn'
                    )">Copy</button>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("<h4>Subject</h4>", unsafe_allow_html=True)
            st.markdown(f"""
                <div class="data-display-box">
                    <span>{st.session_state.generated_subject}</span>
                    <button class="copy-button" id="copySubjectBtn" onclick="copyToClipboard(
                        '{st.session_state.generated_subject.replace("'", "\\'")}', 'copySubjectBtn'
                    )">Copy</button>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("<h4>Message</h4>", unsafe_allow_html=True)
            st.code(st.session_state.generated_email_body, language="text")
            
            js_safe_email_body = json.dumps(st.session_state.generated_email_body)
            st.markdown(f"""
                <div style="text-align: right; margin: -0.8rem 0 1.2rem 0;">
                    <button class="copy-button" id="copyBodyBtn" onclick="copyToClipboard(
                        {js_safe_email_body}, 'copyBodyBtn'
                    )">Copy Message</button>
                </div>
            """, unsafe_allow_html=True)

            # Show extracted data in an expander
            with st.expander("👁️ View extracted data"):
                if st.session_state.current_step == "generate_standard":
                    st.markdown(f"""
                        <div class="extracted-data-card">
                            <div class="field-row">
                                <span class="field-label">Name</span>
                                <span class="field-value-display">{st.session_state.parsed_data.get('customer_name', '[Not found]')}</span>
                            </div>
                            <div class="field-row">
                                <span class="field-label">Order #</span>
                                <span class="field-value-display">{st.session_state.parsed_data.get('order_number', '[Not found]')}</span>
                            </div>
                            <div class="field-row">
                                <span class="field-label">Phone</span>
                                <span class="field-value-display">{st.session_state.parsed_data.get('phone_number', '[Not found]')}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    if st.session_state.parsed_data.get("items"):
                        st.markdown("<h4 style='margin-top: 1rem;'>Items Ordered</h4>", unsafe_allow_html=True)
                        for idx, item in enumerate(st.session_state.parsed_data["items"], 1):
                            st.markdown(f"""
                                <div class="order-item">
                                    <div class="item-detail"><span class="label">Item {idx}</span></div>
                                    <div class="item-detail"><span class="label">Product</span> <span class="value">{item.get('product_name', 'N/A')}</span></div>
                                    <div class="item-detail"><span class="label">Code</span> <span class="value">{item.get('style_code', 'N/A')}</span></div>
                                    <div class="item-detail"><span class="label">Size</span> <span class="value">{item.get('size', 'Not found')}</span></div>
                                    <div class="item-detail"><span class="label">Qty</span> <span class="value">{item.get('quantity', 1)}</span></div>
                                </div>
                            """, unsafe_allow_html=True)

            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
            if st.button("🔄 New order", use_container_width=True, key="btn_reset"):
                reset_app_state()
        else:
            st.markdown("""<p style='color: #bdc3c7; text-align: center; padding: 3rem 1rem; font-size: 1.05rem;'>Paste an order on the left &rarr;</p>""", unsafe_allow_html=True)

with tab2:
    st.markdown("<h2 style='margin-top: 0;'>Batch Processing</h2>", unsafe_allow_html=True)

    raw_text = st.text_area(
        "Paste Shopify Orders",
        height=300,
        placeholder="Paste the Shopify orders page text here...",
        key="batch_orders_textarea"
    )

    def parse_orders(text):
        rows = []
        warnings = []

        if "Select gid://shopify/Order/" not in text:
            return pd.DataFrame(), ["No Shopify order blocks found"]

        blocks = text.split("Select gid://shopify/Order/")[1:]

        for block in blocks:
            order = name = amount = None

            order_match = re.search(r"#\d+", block)
            if order_match:
                order = order_match.group(0)

            amount_match = re.search(r"\$[\d,]+\.\d{2}", block)
            if amount_match:
                amount = float(
                    amount_match.group(0).replace("$", "").replace(",", "")
                )

            name_match = re.search(r"\d+\sitems?\s*\n([^\n]+)", block)
            if name_match:
                candidate = name_match.group(1).strip()
                if "$" not in candidate and len(candidate) > 1:
                    name = candidate

            if order and name and amount is not None:
                rows.append({
                    "Order Number": order,
                    "Customer Name": name,
                    "Amount ($)": amount
                })
            else:
                warnings.append("One order skipped due to incomplete parsing")

        return pd.DataFrame(rows), warnings

    if st.button("Parse Orders", use_container_width=True, key="btn_parse"):
        df, warnings = parse_orders(raw_text)

        if df.empty:
            st.error("No valid orders could be extracted.")
        else:
            st.subheader("Extracted Orders")
            st.dataframe(df, use_container_width=True)

            st.download_button(
                "⬇️ Download as CSV",
                df.to_csv(index=False),
                file_name="shopify_orders.csv",
                mime="text/csv",
                use_container_width=True
            )

        if warnings:
            st.warning(f"{len(warnings)} order(s) skipped — check your data format")
