
import pandas as pd
from io import BytesIO
from datetime import datetime

def process_files(aspire_file, safaricom_file, key_file):
    # Load files
    aspire = pd.read_csv(aspire_file)
    safaricom = pd.read_csv(safaricom_file)
    key = pd.read_excel(key_file)

    # Standardize Safaricom column names
    new_columns = safaricom.columns[1:].tolist() + ['EXTRA']
    safaricom.columns = new_columns
    safaricom = safaricom.drop(columns='EXTRA')

    safaricom_cols = [
        'STORE_NAME', 'RECEIPT_NUMBER', 'ACCOUNT_TYPE_NAME', 'TRANSACTION_TYPE', 'START_TIMESTAMP',
        'TRANSACTION_PARTY_DETAILS', 'CREDIT_AMOUNT', 'DEBIT_AMOUNT', 'BALANCE', 'LINKED_TRANSACTION_ID'
    ]
    safaricom = safaricom[[col for col in safaricom_cols if col in safaricom.columns]]

    # Clean store names
    key.columns = ['Original_STORE_NAME', 'Clean_STORE_NAME']
    store_map = dict(zip(key['Original_STORE_NAME'], key['Clean_STORE_NAME']))
    safaricom['STORE_NAME'] = safaricom['STORE_NAME'].map(store_map).fillna(safaricom['STORE_NAME'])

    # Reconcile by matching REFERENCE NUMBER (RRN)
    aspire['REF_NO'] = aspire['REF_NO'].astype(str).str.replace(r'^0+', '', regex=True)
    safaricom['RECEIPT_NUMBER'] = safaricom['RECEIPT_NUMBER'].astype(str).str.replace(r'^0+', '', regex=True)

    merged = pd.merge(
        aspire,
        safaricom,
        left_on='REF_NO',
        right_on='RECEIPT_NUMBER',
        how='left',
        suffixes=('', '_saf')
    )
    merged['Match_Status'] = merged['RECEIPT_NUMBER'].notna().map({True: 'Matched', False: 'Unmatched'})

    # Create Excel output
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        aspire.to_excel(writer, sheet_name='Raw_Aspire', index=False)
        safaricom.to_excel(writer, sheet_name='Raw_Safaricom', index=False)
        merged.to_excel(writer, sheet_name='Reconciled', index=False)
    output.seek(0)
    return output
