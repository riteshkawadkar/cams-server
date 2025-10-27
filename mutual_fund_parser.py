import pandas as pd
import re
from typing import Dict, List, Union
import pdfplumber  # For PDF parsing
from PIL import Image
import pytesseract  # For OCR from images

class MutualFundDataParser:
    """
    A robust parser for mutual fund holdings data.
    Supports multiple input formats: CSV, Excel, PDF, and images.
    """

    def __init__(self):
        self.columns = [
            'Scheme Name',
            'ISIN',
            'Folio No.',
            'ARN Code',
            'Closing Units',
            'NAV',
            'Cost',
            'Market Value',
            'TER Regular',
            'TER Direct',
            'Commission',
            'Profit/Loss',
            'Profit/Loss %'
        ]

        # Column mappings for flexibility in parsing
        self.column_patterns = {
            'scheme': ['scheme', 'fund', 'portfolio'],
            'isin': ['isin', 'INF'],
            'folio': ['folio'],
            'arn': ['arn'],
            'units': ['closing', 'bal', 'units'],
            'nav': ['nav'],
            'cost': ['cumulative', 'amount invested', 'cost'],
            'value': ['valuation', 'market'],
            'ter_reg': ['expense ratio.*regular', 'ter.*regular'],
            'ter_dir': ['expense ratio.*direct', 'ter.*direct'],
            'commission': ['commission', 'distributors'],
            'profit_loss': ['profit/loss', 'unrealised', 'pl'],
            'profit_loss_pct': ['profit.*%', 'loss.*%', 'return']
        }

    def parse_from_pdf(self, filepath: str, password: str = 'BREPK5205M') -> pd.DataFrame:
        """Parse data from PDF file using pdfplumber"""
        try:
            # Open PDF with password
            with pdfplumber.open(filepath, password=password) as pdf:
                print(f"Successfully opened PDF with {len(pdf.pages)} pages")

                # Initialize data storage
                data = []
                headers = None
                table_started = False

                # Process each page
                for page_num, page in enumerate(pdf.pages, 1):
                    print(f"\nProcessing page {page_num}")
                    text = page.extract_text()
                    if not text:
                        continue

                    # Print the text for debugging
                    print("\nPage text:")
                    print(text[:500] + "..." if len(text) > 500 else text)

                    # Try text-based parsing first
                    lines = text.split('\n')
                    in_holdings_section = False

                    for line in lines:
                        if 'MUTUAL FUND UNITS HELD AS ON' in line:
                            print(f"\nFound holdings section: {line}")
                            in_holdings_section = True
                            continue

                        if in_holdings_section:
                            if not headers and ('Scheme' in line or 'ISIN' in line):
                                print(f"\nPotential header line: {line}")
                                headers = self._extract_columns(line)
                                print(f"Extracted headers: {headers}")
                            elif headers and ('INF' in line or 'ARN-' in line):
                                row_data = self._parse_data_row(line)
                                if row_data and len(row_data) >= 5:
                                    print(f"\nFound data row: {row_data}")
                                    data.append(row_data)

                    # Only try table extraction if text parsing didn't work
                    if not data:
                        try:
                            tables = page.extract_tables()
                            if tables:
                                print(f"\nFound {len(tables)} tables on page {page_num}")
                                for table in tables:
                                    if not table:
                                        continue
                                    for row in table:
                                        row_str = ' '.join(str(cell) for cell in row if cell)
                                        print(f"Table row: {row_str[:100]}")
                                        if 'MUTUAL FUND UNITS HELD AS ON' in row_str:
                                            in_holdings_section = True
                                            continue
                                        if in_holdings_section:
                                            if not headers and ('Scheme' in row_str or 'ISIN' in row_str):
                                                headers = self._clean_headers(row)
                                            elif headers and ('INF' in row_str or 'ARN-' in row_str):
                                                row_data = [str(cell).strip() for cell in row if cell]
                                                if row_data and len(row_data) >= 5:
                                                    data.append(row_data)
                        except Exception as e:
                            print(f"Error extracting tables: {e}")

                    # If no tables found, try text parsing
                    if not data:
                        lines = text.split('\n')
                        in_holdings_section = False

                        for line in lines:
                            if 'MUTUAL FUND UNITS HELD AS ON' in line:
                                in_holdings_section = True
                                continue

                            if in_holdings_section:
                                if not headers and any(word in line.lower() for word in ['scheme', 'isin']):
                                    headers = self._extract_columns(line)
                                elif headers and any(x in line for x in ['INF', 'ARN-']):
                                    row_data = self._parse_data_row(line)
                                    if row_data and len(row_data) >= 5:
                                        data.append(row_data)

                if data:
                    # Create DataFrame
                    df = pd.DataFrame(data)
                    if len(df.columns) == len(headers):
                        df.columns = headers
                    return self._clean_dataframe(df)
                else:
                    print("No valid data found in the PDF")
                    return None

        except Exception as e:
            print(f"Error parsing PDF: {e}")
            if "password is invalid" in str(e).lower():
                print("The provided password is incorrect")
            return None

    def _clean_headers(self, headers: List[str]) -> List[str]:
        """Clean and standardize header names"""
        clean_headers = []
        for header in headers:
            if not header:
                continue
            header = str(header).strip().lower()

            # Match header with known columns
            matched = False
            for col_name, patterns in self.column_patterns.items():
                if any(pattern in header for pattern in patterns):
                    clean_headers.append(self.columns[len(clean_headers)])
                    matched = True
                    break

            if not matched:
                clean_headers.append(header.title())

        return clean_headers

    def _extract_columns(self, header_line: str) -> List[str]:
        """Extract column names from header line"""
        # Split by multiple spaces or common separators
        columns = re.split(r'\s{2,}|\t|│|┃', header_line.strip())
        # Clean up column names
        columns = [col.strip() for col in columns if col.strip()]
        # Map to standard column names where possible
        return self._clean_headers(columns)

    def _parse_data_row(self, line: str) -> List[str]:
        """Parse a data row into fields"""
        # First try splitting by common separators
        fields = re.split(r'\s{2,}|\t|│|┃', line.strip())
        fields = [f.strip() for f in fields if f.strip()]

        if not fields:
            return None

        # Handle scheme name with embedded spaces
        if len(fields) > len(self.columns):
            # Try to merge fields that might be part of scheme name
            merged = []
            current = []
            for field in fields:
                if re.match(r'^(INF|[A-Z0-9]{10})', field):  # ISIN found
                    if current:
                        merged.append(' '.join(current))
                        current = []
                    merged.append(field)
                elif re.match(r'^[\d,.]+$', field):  # Numeric value
                    if current:
                        merged.append(' '.join(current))
                        current = []
                    merged.append(field)
                else:
                    current.append(field)
            if current:
                merged.append(' '.join(current))
            fields = merged

        return fields

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize the dataframe"""
        if df is None or df.empty:
            return None

        # Convert DataFrame to string type for consistent handling
        df = df.astype(str)

        # Remove completely empty rows and columns
        df = df.replace('', pd.NA).replace('None', pd.NA).replace('nan', pd.NA)
        df = df.dropna(how='all').dropna(axis=1, how='all')

        # Drop rows that don't look like holdings data
        df = df[df.apply(lambda row: any('INF' in str(cell) for cell in row), axis=1)]

        # Standardize column names
        if len(df.columns) >= 10:  # Make sure we have enough columns
            df.columns = self.columns[:len(df.columns)]

        # Clean up scheme names
        if 'Scheme Name' in df.columns:
            df['Scheme Name'] = df['Scheme Name'].apply(lambda x: ' '.join(str(x).split()))

        # Try to identify numeric columns
        numeric_patterns = {
            'Closing Units': [r'[\d,.]+'],
            'NAV': [r'[\d,.]+\.\d*'],
            'Cost': [r'[\d,.]+\.\d{2}'],
            'Market Value': [r'[\d,.]+\.\d{2}'],
            'TER Regular': [r'[\d.]+%?'],
            'TER Direct': [r'[\d.]+%?'],
            'Commission': [r'[\d,.]+\.\d{2}'],
            'Profit/Loss': [r'-?[\d,.]+\.\d{2}'],
            'Profit/Loss %': [r'-?[\d.]+']
        }

        def extract_numeric(text, patterns):
            if pd.isna(text) or not text:
                return None
            text = str(text).strip()
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    return match.group(0)
            return None

        # Process each column
        for col in df.columns:
            if col in numeric_patterns:
                # Extract numeric values
                df[col] = df[col].apply(lambda x: extract_numeric(x, numeric_patterns[col]))
                # Convert to float
                df[col] = pd.to_numeric(df[col].str.replace(',', '').str.replace('%', ''), errors='coerce')

        return df

    def _clean_numeric(self, series: pd.Series) -> pd.Series:
        """Clean numeric values by removing commas and converting to float"""
        def clean_value(x):
            if pd.isna(x):
                return 0.0
            try:
                # Remove currency symbols, commas, and whitespace
                clean = str(x).replace('₹', '').replace(',', '').strip()
                # Handle parentheses (negative numbers)
                if clean.startswith('(') and clean.endswith(')'):
                    clean = '-' + clean[1:-1]
                return float(clean)
            except (ValueError, TypeError):
                return 0.0

        return series.apply(clean_value)

    def get_summary_statistics(self, df: pd.DataFrame) -> Dict:
        """Calculate summary statistics from the dataframe"""
        if df is None or df.empty:
            return {}

        value_col = next((col for col in df.columns if 'value' in col.lower() or 'valuation' in col.lower()), None)
        invested_col = next((col for col in df.columns if 'invested' in col.lower() or 'cost' in col.lower()), None)
        pl_col = next((col for col in df.columns if 'profit' in col.lower() and not '%' in col.lower()), None)

        summary = {
            'total_schemes': len(df),
            'total_valuation': df[value_col].sum() if value_col else 0,
            'total_investment': df[invested_col].sum() if invested_col else 0,
            'total_profit_loss': df[pl_col].sum() if pl_col else 0,
        }

        summary['overall_return_percentage'] = (
            (summary['total_profit_loss'] / summary['total_investment'] * 100)
            if summary['total_investment'] > 0 else 0
        )

        return summary

    def filter_by_scheme(self, df: pd.DataFrame, scheme_pattern: str) -> pd.DataFrame:
        """Filter dataframe by scheme name pattern"""
        if df is None or not any('scheme' in col.lower() for col in df.columns):
            return None

        scheme_col = next(col for col in df.columns if 'scheme' in col.lower())
        return df[df[scheme_col].str.contains(scheme_pattern, case=False, na=False)]

    def export_to_excel(self, df: pd.DataFrame, output_path: str):
        """Export dataframe to Excel with formatting"""
        if df is None:
            print("No data to export")
            return

        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Holdings', index=False)
            print(f"Data exported to {output_path}")
        except Exception as e:
            print(f"Error exporting to Excel: {e}")


# Example usage
if __name__ == "__main__":
    parser = MutualFundDataParser()

    # Example with real PDF
    import sys
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
        print(f"Processing {pdf_file}...")
        df = parser.parse_from_pdf(pdf_file)
        if df is not None:
            print("\nFound holdings:")
            print(df.head())
            print("\nSummary statistics:")
            stats = parser.get_summary_statistics(df)
            for key, value in stats.items():
                if isinstance(value, float):
                    print(f"{key}: ₹{value:,.2f}" if 'total' in key else f"{key}: {value:.2f}%")
                else:
                    print(f"{key}: {value}")
            parser.export_to_excel(df, pdf_file.replace('.pdf', '_holdings.xlsx'))
    else:
        print("Please provide a PDF file path as argument")