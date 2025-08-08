import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Truemed Tools", layout="centered")

# Header
st.title("Truemed Tools")

# Link to Loom video
st.markdown("""
### 📹 How to Use This Tool
[Watch the tutorial video](https://www.loom.com/share/f147c759c8b54ff18cb652a6becfd380?sid=7046d406-5ab6-4b86-b1b5-e09522102357)
""")

st.markdown("""
**This tool helps you generate bulk tag updates for use with the
[Power Tools Bulk Edit Tags](https://apps.shopify.com/power-tools-bulk-edit-tags) app. Please start by installing the app in Shopify.**

**Next, go to [app.truemed.com](https://app.truemed.com), navigate to the Products tab, and download your products list as a CSV.**

---
""")

# Tag selection
tag_choice = st.radio(
    "Which Truemed tag do you want to apply?",
    options=["truemed-eligible", "truemed-ineligible"],
    index=0
)

# Show widget snippet above Output Format
st.markdown("---")
st.subheader("💡 Shopify Theme Code Snippet")

if tag_choice == "truemed-eligible":
    st.markdown("""
```html
<!-- Display widget only if product has 'truemed-eligible' tag -->
{% if product.tags contains 'truemed-eligible' %}
<div id="truemed-instructions" style="font-size: 14px;" icon-height="12" data-public-id="YOUR_PUBLIC_QUALIFICATION_ID"></div>
<script src="https://static.truemed.com/widgets/product-page-widget.min.js" defer></script>
{% endif %}
```
    """)
else:
    st.markdown("""
```html
<!-- Display widget unless product has 'truemed-ineligible' tag -->
{% unless product.tags contains "truemed-ineligible" %}
<div id="truemed-instructions" style="font-size: 14px;" icon-height="12" data-public-id="YOUR_PUBLIC_QUALIFICATION_ID"></div>
<script src="https://static.truemed.com/widgets/product-page-widget.min.js" defer></script>
{% endunless %}
```
    """)

st.info("⚠️ Make sure to update `YOUR_PUBLIC_QUALIFICATION_ID` in the code snippet above with your actual public qualification ID from Truemed.")

# Output format section
st.markdown("""
### 📄 Expected CSV Format
- `Item Name`: Shopify product **handle**
- `Status`: either `eligible` or `ineligible`

---

### ✅ Output Format (one line per product):
```
product-handle, add, truemed-eligible
```
""")

st.info("After generating your tag lines, navigate to 'Bulk Edit Tags' in the Power Tools app, scroll to the section 'Bulk Add and Delete using a list of products', and paste in the output you downloaded or copied above.")

# Upload CSV
uploaded_file = st.file_uploader("📄 Upload your Truemed Eligibility CSV", type=["csv"])

# Main logic
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        df['Item Name'] = df['Item Name'].astype(str).str.strip()
        df['Status'] = df['Status'].astype(str).str.lower().str.strip()

        # Filter by tag choice
        if tag_choice == "truemed-eligible":
            # Check for both approved_with_lmn and pre_approved statuses
            filtered_df = df[df['Status'].isin(['approved_with_lmn', 'pre_approved'])]
        else:
            # For truemed-ineligible, check for ineligible status
            filtered_df = df[df['Status'] == 'ineligible']
        
        handles = filtered_df['Item Name'].dropna().unique().tolist()

        if not handles:
            if tag_choice == "truemed-eligible":
                st.warning("No products with status 'approved_with_lmn' or 'pre_approved' found.")
            else:
                st.warning("No products with status 'ineligible' found.")
        else:
            # Create one line per handle
            lines = [f"{handle}, add, {tag_choice}" for handle in handles]
            output_text = "\n".join(lines)

            st.success(f"✅ Generated {len(lines)} Power Tools tag lines:")
            st.code(output_text, language="text")

            st.download_button(
                label="⬇️ Download as .txt",
                data=output_text.encode("utf-8"),
                file_name=f"{tag_choice}-tags.txt",
                mime="text/plain"
            )

    except Exception as e:
        st.error(f"❌ Failed to process CSV: {e}")
else:
    st.info("Please upload your CSV to begin.")
