import json
from mutual_fund_parser import MutualFundDataParser

pdf = 'SEP2025_AA03366523_TXN.pdf'
parser = MutualFundDataParser()
df = parser.parse_from_pdf(pdf)
if df is None or df.empty:
    print('No data parsed')
else:
    j = parser.to_json_dict(df)
    print(json.dumps(j, indent=2, ensure_ascii=False)[:1000])
    print('\n..printed truncated JSON (first 1000 chars)')
