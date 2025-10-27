import pandas as pd
import re
from typing import Dict, List, Union, Optional
import pdfplumber  # For PDF parsing
import tabula  # For table extraction
import PyPDF2  # For text extraction
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
        """Parse data from PDF using multiple methods"""
        df = None

        # Try pdfplumber first
        df = self._parse_with_pdfplumber(filepath, password)

        # If pdfplumber fails, try tabula
        if df is None or df.empty:
            df = self._parse_with_tabula(filepath, password)

        # If tabula fails, try PyPDF2
        if df is None or df.empty:
            df = self._parse_with_pypdf2(filepath, password)

        return df if df is not None else pd.DataFrame()

    def _parse_with_pdfplumber(self, filepath: str, password: str) -> Optional[pd.DataFrame]:
        """Parse PDF using pdfplumber library"""
        try:
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

                if data:
                    # Create DataFrame
                    df = pd.DataFrame(data)
                    if len(df.columns) == len(headers):
                        df.columns = headers
                    return self._clean_dataframe(df)
                return None
        except Exception as e:
            print(f"pdfplumber parsing failed: {e}")
            return None

    def _parse_with_tabula(self, filepath: str, password: str) -> Optional[pd.DataFrame]:
        """Parse PDF using tabula library"""
        try:
            tables = tabula.read_pdf(filepath, pages='all', multiple_tables=True,
                                   password=password)
            if tables:
                df = pd.concat(tables, ignore_index=True)
                print(f"Extracted data using tabula")
                return df
        except Exception as e:
            print(f"tabula parsing failed: {e}")
            return None

    def _parse_with_pypdf2(self, filepath: str, password: str) -> Optional[pd.DataFrame]:
        """Parse PDF using PyPDF2 library"""
        try:
            with open(filepath, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                if reader.is_encrypted:
                    reader.decrypt(password)
                text = ''
                for page in reader.pages:
                    text += page.extract_text()
                # Parse text content
                lines = text.split('\n')
                data = []
                headers = None
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
        if df is None or df.empty:
            print("No data to export")
            return

        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Holdings', index=False)

                # Get workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Holdings']

                # Auto-adjust columns
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter

                    # Find maximum length in column
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(cell.value)
                        except:
                            pass

                    # Set width (limit to 60 to avoid too wide columns)
                    adjusted_width = min(max_length + 2, 60)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

                print(f"Data exported to {output_path}")
        except Exception as e:
            print(f"Error exporting to Excel: {e}")

    def export_to_json(self, df: pd.DataFrame, output_path: str, include_summary: bool = True):
        """Export holdings data and summary to JSON"""
        if df is None or df.empty:
            print("No data to export")
            return

        try:
            # Convert DataFrame to dict format
            holdings_data = df.to_dict(orient='records')

            # Calculate summary statistics
            summary_stats = self.get_summary_statistics(df)

            # Build JSON dict using helper so API and other callers can reuse
            json_data = self.to_json_dict(df)

            # Write to JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                import json
                json.dump(json_data, f, indent=2, ensure_ascii=False)

            print(f"Data exported to {output_path}")
        except Exception as e:
            print(f"Error exporting to JSON: {e}")

    def to_json_dict(self, df: pd.DataFrame) -> dict:
        """Return a JSON-serializable dict for the holdings and summary.

        This method centralizes the JSON structure so external callers (for example
        an API) can obtain the payload without writing to disk.
        """
        # Convert DataFrame to dict format
        holdings_data = df.to_dict(orient='records')

        # Calculate summary statistics
        summary_stats = self.get_summary_statistics(df)

        # Helper to clean folio and numeric conversion
        def clean_folio(val):
            try:
                s = str(val)
                # remove newlines and stray soft-hyphen-like or NBSP chars
                s = re.sub(r"[\n\r\u00AD\u2011\u00A0]", '', s)
                s = s.strip()
                return s
            except Exception:
                return str(val)

        json_data = {
            'date': df.get('Date', pd.Timestamp.now().strftime('%Y-%m-%d')),
            'portfolio_summary': {
                'total_schemes': summary_stats.get('total_schemes', 0),
                'total_valuation': round(summary_stats.get('total_valuation', 0), 2),
                'total_investment': round(summary_stats.get('total_investment', 0), 2),
                'total_profit_loss': round(summary_stats.get('total_profit_loss', 0), 2),
                'overall_return_percentage': round(summary_stats.get('overall_return_percentage', 0), 2)
            },
            'holdings': []
        }

        for holding in holdings_data:
            try:
                commission_raw = holding.get('Commission', 0)
                # ensure commission is numeric and not NaN
                commission = 0.0
                if commission_raw is not None and pd.notna(commission_raw) and str(commission_raw).strip().lower() not in ['nan', 'none']:
                    commission = float(str(commission_raw).replace(',', ''))

                h = {
                    'scheme_name': holding.get('Scheme Name'),
                    'isin': holding.get('ISIN'),
                    'folio_no': clean_folio(holding.get('Folio No.')),
                    'arn_code': holding.get('ARN Code'),
                    'units': round(float(holding.get('Closing Units', 0) or 0), 3),
                    'nav': round(float(holding.get('NAV', 0) or 0), 4),
                    'cost': round(float(holding.get('Cost', 0) or 0), 2),
                    'current_value': round(float(holding.get('Market Value', 0) or 0), 2),
                    'ter_regular': float(holding.get('TER Regular', 0) or 0),
                    'ter_direct': float(holding.get('TER Direct', 0) or 0),
                    'commission': round(commission, 2),
                    'profit_loss': round(float(holding.get('Profit/Loss', 0) or 0), 2),
                    'profit_loss_percentage': round(float(holding.get('Profit/Loss %', 0) or 0), 2)
                }
                json_data['holdings'].append(h)
            except Exception:
                # skip problematic rows but continue
                continue

        return json_data


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

            # Export to both Excel and JSON
            excel_path = pdf_file.replace('.pdf', '_holdings.xlsx')
            json_path = pdf_file.replace('.pdf', '_holdings.json')
            parser.export_to_excel(df, excel_path)
            parser.export_to_json(df, json_path)
    else:
        print("Please provide a PDF file path as argument")

    # module-level to_json_dict removed; using class method