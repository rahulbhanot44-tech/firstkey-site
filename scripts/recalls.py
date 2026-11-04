"""Build recalls.json: Health Canada consumer product recalls for home equipment.

Source: Recalls and Safety Alerts, Government of Canada open data (Open Government Licence - Canada).
The FirstKey app downloads the small file this makes and matches it to the equipment people add.
"""
import html, json, re, urllib.request

SRC = 'https://recalls-rappels.canada.ca/sites/default/files/opendata-donneesouvertes/HCRSAMOpenData.json'
WORDS = ['furnace', 'boiler', 'water heater', 'hot water', 'air conditioner', 'air conditioning', 'heat pump',
         'ventilator', 'hrv', 'erv', 'sump pump', 'softener', 'dishwasher', 'washer', 'washing machine', 'dryer',
         'refrigerator', 'fridge', 'freezer', 'garage door', 'snow blower', 'snowblower', 'snow thrower',
         'smoke alarm', 'smoke detector', 'carbon monoxide', 'co alarm', 'generator', 'dehumidifier', 'humidifier',
         'range', 'oven', 'cooktop', 'stove', 'microwave', 'thermostat', 'fireplace', 'space heater', 'range hood']
PAT = re.compile(r'\b(' + '|'.join(re.escape(w) for w in WORDS) + r')s?\b', re.I)

def clean(s):
    s = html.unescape(re.sub(r'<[^>]+>', ' ', s or '')).replace('\u200b', '').replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', s).strip()

with urllib.request.urlopen(SRC, timeout=120) as r:
    rows = json.load(r)

out = []
for x in rows:
    if x.get('Organization') != 'Consumer product safety':
        continue
    title, product = clean(x.get('Title')), clean(x.get('Product'))
    if product == 'None':
        product = ''
    if not PAT.search(f'{title} {product}'):
        continue
    out.append({
        'id': x.get('NID'), 'title': title, 'product': product, 'issue': clean(x.get('Issue')),
        'date': x.get('Last updated') if x.get('Last updated') not in (None, 'None') else '',
        'url': x.get('URL'), 'what': clean(x.get('What you should do'))[:700],
    })
out.sort(key=lambda r: r['date'], reverse=True)
json.dump({'source': 'Health Canada Recalls and Safety Alerts (Open Government Licence - Canada)', 'count': len(out), 'recalls': out},
          open('recalls.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print(len(out), 'recalls kept')
