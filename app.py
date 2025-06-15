
import streamlit as st
from helpers import process_files

st.set_page_config(page_title="Mpesa Reconciliation App", layout="centered")

st.title("📊 Mpesa Reconciliation App")
st.markdown("Upload Aspire CSV, Safaricom CSV, and Store Key Excel File")

aspire_file = st.file_uploader("Upload Aspire CSV", type=["csv"])
safaricom_file = st.file_uploader("Upload Safaricom CSV", type=["csv"])
key_file = st.file_uploader("Upload Key Excel File", type=["xlsx"])

if aspire_file and safaricom_file and key_file:
    with st.spinner("Processing..."):
        output = process_files(aspire_file, safaricom_file, key_file)
        st.success("✅ Reconciliation Complete")
        st.download_button("📥 Download Reconciled Report", data=output, file_name="mpesa_reconciliation.xlsx")
