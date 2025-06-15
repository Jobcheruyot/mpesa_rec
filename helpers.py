
import pandas as pd
from io import BytesIO

def process_files(aspire_file, safaricom_file, key_file):
    # Load input files
    aspire = pd.read_csv(aspire_file)
    safaricom = pd.read_csv(safaricom_file)
    key = pd.read_excel(key_file)

    # Validate required columns
    if 'TRANSACTION_ID' not in aspire.columns:
        raise KeyError("Aspire file must contain a column named 'TRANSACTION_ID'")
    if 'RECEIPT_NUMBER' not in safaricom.columns:
        raise KeyError("Safaricom file must contain a column named 'RECEIPT_NUMBER'")
    if 'STORE_NAME' not in safaricom.columns:
        raise KeyError("Safaricom file must contain a column named 'STORE_NAME'")

    # Clean store names using the key file
    key.columns = ['Original_STORE_NAME', 'Clean_STORE_NAME']
    store_map = dict(zip(key['Original_STORE_NAME'], key['Clean_STORE_NAME']))
    safaricom['STORE_NAME'] = safaricom['STORE_NAME'].map(store_map).fillna(safaricom['STORE_NAME'])

    # Normalize transaction IDs
    aspire['TRANSACTION_ID'] = aspire['TRANSACTION_ID'].astype(str).str.replace(r'^0+', '', regex=True)
    safaricom['RECEIPT_NUMBER'] = safaricom['RECEIPT_NUMBER'].astype(str).str.replace(r'^0+', '', regex=True)

    # Merge
    merged = pd.merge(
        aspire,
        safaricom,
        left_on='TRANSACTION_ID',
        right_on='RECEIPT_NUMBER',
        how='left',
        suffixes=('', '_saf')
    )
    merged['Match_Status'] = merged['RECEIPT_NUMBER'].notna().map({True: 'Matched', False: 'Unmatched'})

    # Output to Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        aspire.to_excel(writer, sheet_name='Aspire', index=False)
        safaricom.to_excel(writer, sheet_name='Safaricom', index=False)
        merged.to_excel(writer, sheet_name='Reconciled', index=False)
    output.seek(0)
    return output
