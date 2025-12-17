import streamlit as st
import re
import json # Import the json module
import pandas as pd
# Removed asyncio and httpx imports as LLM is no longer used

# --- Page Configuration ---
st.set_page_config(page_title="DAZZLE PREMIUM Order Email Generator", layout="wide", initial_sidebar_state="collapsed")

# --- Custom CSS Styling (Award-quality, Handcrafted UI - Extended) ---
st.markdown("""
<style>
    /* --------------------------------------------------------- */
    /* Design System Variables */
    :root {
        --bg: #f6f8fa;
        --panel: #ffffff;
        --muted: #9aa5ad;
        --text: #12232b;
        --accent: #0f6fff;
        --accent-2: #243b55;
        --success: #16a34a;
        --warning: #f59e0b;
        --danger: #ef4444;
        --soft: rgba(17, 24, 39, 0.03);
        --glass: rgba(255,255,255,0.8);
        --radius: 10px;
        --card-radius: 12px;
        --shadow-1: 0 6px 18px rgba(18,35,43,0.06);
        --shadow-2: 0 10px 30px rgba(18,35,43,0.08);
    }

    /* Reset */
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body, .stApp { height: 100%; background: var(--bg); color: var(--text); font-family: Inter, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; }

    /* Global layout container tuning */
    .main .block-container { max-width: 1360px; margin: 28px auto; padding: 28px; background: linear-gradient(180deg, var(--panel) 0%, #fbfcfd 100%); border-radius: 14px; box-shadow: var(--shadow-1); }

    /* Typography scale */
    h1 { font-size: 34px; line-height: 1.06; font-weight: 700; color: #0b1720; margin-bottom: 6px; }
    .subtitle { font-size: 15px; color: var(--muted); margin-bottom: 20px; }
    h2 { font-size: 20px; font-weight: 700; color: #071524; margin: 20px 0 14px; }
    h3 { font-size: 16px; font-weight: 600; color: #0b1720; margin: 14px 0 10px; }
    h4 { font-size: 12px; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }

    p, label { color: #334155; font-size: 14px; line-height: 1.5; }

    /* Utility */
    .muted { color: var(--muted); }
    .small { font-size: 12px; }
    .kbd { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, 'Roboto Mono', monospace; background: #eef2f7; padding: 2px 6px; border-radius: 6px; font-size: 12px; }

    /* Top navigation / hero area */
    .app-hero { display:flex; align-items:center; justify-content:space-between; gap:20px; margin-bottom: 18px; }
    .app-hero .left { display:flex; gap:16px; align-items:center; }
    .brand-badge { display:flex; align-items:center; gap:10px; }
    .brand-badge .logo { width:48px; height:48px; border-radius:10px; background: linear-gradient(135deg, var(--accent), #5aa2ff); box-shadow: var(--shadow-2); display:flex; align-items:center; justify-content:center; color:white; font-weight:700; }
    .brand-badge .title { display:flex; flex-direction:column; }
    .brand-badge .title .name { font-weight:700; font-size:20px; letter-spacing: -0.3px; }
    .brand-badge .title .tag { font-size:12px; color:var(--muted); }

    .app-hero .actions { display:flex; gap:10px; align-items:center; }
    .search { display:flex; align-items:center; gap:8px; background:var(--soft); padding:8px 12px; border-radius:999px; border:1px solid rgba(17,24,39,0.03); }
    .search input { border: none; background: transparent; outline:none; width:220px; font-size:14px; color:var(--text); }
    .pill { background: linear-gradient(180deg,#fbfcff, #f4f8ff); border-radius:999px; padding:8px 12px; border:1px solid rgba(17,24,39,0.04); font-weight:600; color:var(--accent-2); }

    /* Panels and cards */
    .panel { background: var(--panel); border-radius: var(--card-radius); padding: 18px; border: 1px solid rgba(2,6,23,0.04); box-shadow: var(--shadow-1); }
    .panel.header { display:flex; align-items:center; justify-content:space-between; gap:18px; }

    .panel.grid { display:grid; grid-template-columns: 1fr 420px; gap: 22px; align-items:start; }

    /* Buttons */
    .btn { display:inline-flex; align-items:center; gap:8px; padding:10px 14px; border-radius:10px; border:none; cursor:pointer; font-weight:600; font-size:14px; }
    .btn.primary { background: linear-gradient(90deg,var(--accent), #4aa3ff); color:white; box-shadow: 0 8px 30px rgba(15,111,255,0.14); }
    .btn.ghost { background: transparent; border: 1px solid rgba(2,6,23,0.06); color:var(--accent-2); }
    .btn.warn { background: linear-gradient(90deg,#fff3e0,#fff1d6); color:var(--warning); border:1px solid rgba(245,158,11,0.08); }

    .btn:hover { transform: translateY(-2px); transition: transform 160ms ease; }

    .icon-circle { width:38px; height:38px; border-radius:9px; display:flex; align-items:center; justify-content:center; background: linear-gradient(180deg,#fff,#f5f7fb); border:1px solid rgba(2,6,23,0.04); }

    /* Form and textarea styling */
    .form-row { display:flex; flex-direction:column; gap:8px; margin-bottom:12px; }
    .label { font-size:13px; font-weight:700; color:#475569; }
    .input { width:100%; padding:12px 14px; border-radius:10px; border:1px solid #e6eef6; background: #fbfdff; font-size:14px; color:var(--text); }
    textarea.input { min-height: 160px; resize: vertical; }

    .helper { font-size:12px; color:var(--muted); }

    /* Data display */
    .data-row { display:flex; align-items:center; justify-content:space-between; gap:12px; padding:10px; border-radius:10px; border:1px solid rgba(2,6,23,0.04); background: linear-gradient(180deg,#ffffff,#fbfdff); }

    .items { display:flex; flex-direction:column; gap:10px; }
    .item { display:flex; gap:12px; align-items:flex-start; padding:12px; border-radius:10px; background: linear-gradient(180deg,#ffffff,#fbfcff); border:1px solid rgba(2,6,23,0.03); }
    .item .meta { display:flex; flex-direction:column; }
    .item .title { font-weight:700; color:#0b1720; }
    .item .meta .small { color:var(--muted); font-size:13px; }

    /* Status badges */
    .badge { display:inline-flex; align-items:center; gap:8px; padding:6px 10px; border-radius:999px; font-weight:700; font-size:13px; }
    .badge.success { background: rgba(16,185,129,0.12); color: var(--success); border:1px solid rgba(16,185,129,0.12); }
    .badge.warn { background: rgba(245,158,11,0.08); color: var(--warning); border:1px solid rgba(245,158,11,0.08); }
    .badge.info { background: rgba(14,165,233,0.08); color: #0369a1; border:1px solid rgba(14,165,233,0.08); }

    /* Message blocks */
    .message-block { border-radius: 10px; padding: 14px; border: 1px dashed rgba(2,6,23,0.04); background: linear-gradient(180deg,#fbfdff,#f7fbff); white-space: pre-wrap; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, 'Roboto Mono', monospace; }

    /* Table-like styles */
    .orders-table { width:100%; border-collapse: collapse; font-size: 14px; }
    .orders-table thead th { text-align:left; padding:12px; color:#55636f; font-weight:700; border-bottom: 1px solid rgba(2,6,23,0.04); }
    .orders-table tbody td { padding:12px; border-bottom: 1px solid rgba(2,6,23,0.03); }

    /* Micro-interactions */
    .hover-lift { transition: transform 160ms ease, box-shadow 160ms ease; }
    .hover-lift:hover { transform: translateY(-6px); box-shadow: var(--shadow-2); }

    @keyframes pulseSoft { 0% { box-shadow: 0 0 0 0 rgba(15,111,255,0.08);} 70% { box-shadow: 0 0 0 8px rgba(15,111,255,0);} 100% { box-shadow: 0 0 0 0 rgba(15,111,255,0);} }
    .pulse { animation: pulseSoft 2.6s infinite; }

    /* Accessibility */
    .sr-only { position:absolute; left:-10000px; top:auto; width:1px; height:1px; overflow:hidden; }

    /* Mobile responsive grid stacks */
    @media (max-width: 980px) {
        .panel.grid { grid-template-columns: 1fr; }
        .search input { width: 120px; }
        .main .block-container { padding: 18px; margin: 8px; }
    }

    /* Extended form helpers */
    .field-inline { display:flex; gap:10px; align-items:center; }
    .field-inline .input { flex:1; }
    .field-muted { color:#94a3b8; font-size:13px; }

    .chip { display:inline-flex; align-items:center; gap:8px; padding:6px 10px; border-radius:999px; background:#f1f5f9; border:1px solid rgba(2,6,23,0.03); font-weight:600; }

    /* Modal and tooltip (visual only) */
    .mod-backdrop { position:fixed; inset:0; background: rgba(2,6,23,0.35); display:none; align-items:center; justify-content:center; }
    .mod { width:720px; background:var(--panel); border-radius:12px; padding:22px; box-shadow: var(--shadow-2); }
    .tooltip { position:relative; display:inline-block; }
    .tooltip .tip { position:absolute; bottom:calc(100% + 8px); left:50%; transform:translateX(-50%); background:#0b1720; color:white; padding:8px 10px; border-radius:6px; font-size:12px; display:none; }
    .tooltip:hover .tip { display:block; }

    .input.error { border-color: rgba(239,68,68,0.12); box-shadow: 0 2px 8px rgba(239,68,68,0.06); }
    .input.success { border-color: rgba(16,185,129,0.12); box-shadow: 0 2px 8px rgba(16,185,129,0.06); }

    .mini-footer { display:flex; justify-content:space-between; gap:10px; align-items:center; border-top:1px solid rgba(2,6,23,0.04); padding-top:12px; margin-top:16px; color:var(--muted); font-size:13px; }

    .ic { width:18px; height:18px; display:inline-block; }
    .rule { height:1px; background: linear-gradient(90deg, transparent, rgba(2,6,23,0.04), transparent); margin: 12px 0; }

    .cols-3 { display:grid; grid-template-columns: repeat(3,1fr); gap:12px; }
    .cols-2 { display:grid; grid-template-columns: repeat(2,1fr); gap:12px; }

    .muted-block { background: linear-gradient(180deg,#fbfdff,#f6f9fb); border:1px solid rgba(2,6,23,0.03); padding:8px 10px; border-radius:8px; color:var(--muted); }
    .btn.large { padding:12px 18px; font-size:15px; border-radius:12px; }
    .soft-border { border: 1px solid rgba(2,6,23,0.03); border-radius:10px; background: linear-gradient(180deg,#fff,#fbfdff); }

    .stCode { overflow-x:auto; }

    @media (max-width: 560px) {
        h1 { font-size:22px; }
        .search input { width:90px; }
        .brand-badge .title .name { font-size:16px; }
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

st.markdown("""
<div class="app-hero panel header">
    <div class="left">
        <div class="brand-badge">
            <div class="logo">DP</div>
            <div class="title">
                <div class="name">Dazzle Premium</div>
                <div class="tag">Order Email Generator — Ship faster, communicate better</div>
            </div>
        </div>
        <div class="rule" style="width:1px; height:40px; background:transparent; margin-left:8px;"></div>
    </div>

    <div class="actions">
        <div class="search" title="Quickly find an order (visual)">
            <svg class="ic" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M21 21l-4.35-4.35" stroke="#6b7280" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <input placeholder="Find order or email..." />
        </div>
        <div class="pill">Premium</div>
        <button class="btn primary" onclick="window.scrollTo({ top: 400, behavior: 'smooth' })">Generate Email</button>
        <button class="btn ghost" onclick="window.scrollTo({ top: 900, behavior: 'smooth' })">Batch Orders</button>
    </div>
</div>
""", unsafe_allow_html=True)

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
