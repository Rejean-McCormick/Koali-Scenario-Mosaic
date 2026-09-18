from pathlib import Path
import html as html_lib
import json
import re
import sys


R = Path(__file__).resolve().parents[1]
errors = []
capability_titles = json.loads((R / 'src/data/scenario-capability-titles.json').read_text(encoding='utf-8'))

LOCALES = {
    'en': {
        'alt': lambda sid, title: f'Abstract illustration for {sid}: {title}',
        'generic_body': 'The Koali point is continuity:',
        'generic_preview': 'same context moves across specialized capabilities',
        'article_pattern': r'^(A|An|The)\b',
        'article_limit': 30,
        'stopwords': {
            'the', 'a', 'an', 'to', 'and', 'of', 'with', 'from', 'through', 'each',
            'same', 'their', 'that', 'this', 'into', 'its', 'for', 'over', 'around',
            'behind', 'between', 'before', 'after', 'while', 'can', 'every',
            'multiple', 'without',
        },
    },
    'fr': {
        'alt': lambda sid, title: f'Illustration abstraite pour {sid} : {title}',
        'generic_body': 'Le point Koali est la continuité:',
        'generic_preview': 'le même contexte passe d’une capacité spécialisée à l’autre',
        'article_pattern': r"^(Un|Une|Le|La|Les|L[’'])\b",
        'article_limit': 40,
        'stopwords': {
            'le', 'la', 'les', 'un', 'une', 'de', 'des', 'du', 'et', 'à', 'au',
            'aux', 'avec', 'dans', 'chaque', 'même', 'leurs', 'leur', 'en', 'pour',
            'par', 'sur', 'entre', 'avant', 'après', 'sans', 'ses', 'son', 'sa',
            'ce', 'cette', 'ces', 'plusieurs', 'tous', 'toutes',
        },
    },
}


def scalar(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def field(text, name):
    match = re.search(rf'(?m)^{re.escape(name)}:\s*(.+)$', text)
    return scalar(match.group(1)) if match else ''


def sentences_from(summary):
    return [
        sentence for sentence in re.split(r'(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-Þ“"\'])', summary.strip())
        if sentence
    ]


def response_from(summary):
    sentences = sentences_from(summary)
    index = next((i for i, sentence in enumerate(sentences) if re.search(r'\bKoali\b', sentence)), -1)
    return ' '.join(sentences[index:]) if index > 0 else ''


def content_tokens(value, stopwords):
    return {
        word for word in re.findall(r"[\wÀ-ÿ’'-]+", value.casefold())
        if len(word) > 2 and word not in stopwords
    }


for locale, rules in LOCALES.items():
    source = R / 'src' / 'content' / 'scenarios' / locale
    titles = {}
    gaps = {}
    summaries = {}
    responses = {}
    opening_signatures = {}
    response_verbs = {}

    for path in sorted(source.glob('SCN-*.md')):
        text = path.read_text(encoding='utf-8')
        sid = path.stem
        title = field(text, 'title')
        gap = field(text, 'continuity_gap')
        summary = field(text, 'preview_summary')
        sentences = sentences_from(summary)
        response = response_from(summary)
        titles[sid] = title
        gaps[sid] = gap
        summaries[sid] = summary
        responses[sid] = response

        opening_words = re.findall(r"[\wÀ-ÿ’'-]+", sentences[0].casefold())[:3] if sentences else []
        opening_signature = ' '.join(opening_words)
        opening_signatures.setdefault(opening_signature, []).append(sid)
        response_verb = re.match(r"^Koali\s+([\wÀ-ÿ’'-]+)", response)
        if response_verb:
            response_verbs.setdefault(response_verb.group(1).casefold(), []).append(sid)

        if f'# {sid} — {title}' not in text:
            errors.append(f'{sid}/{locale}: H1 does not match title')
        if field(text, 'preview_image_alt') != rules['alt'](sid, title):
            errors.append(f'{sid}/{locale}: image alt does not match title')
        if not response:
            errors.append(f'{sid}/{locale}: preview summary has no distinct Koali response')
        if len(sentences) != 2:
            errors.append(f'{sid}/{locale}: public impact copy must contain exactly two sentences')
        elif re.search(r'\bKoali\b', sentences[0]) or not re.match(r'^Koali\b', sentences[1]):
            errors.append(f'{sid}/{locale}: use problem first, then a Koali response')
        word_count = len(summary.split())
        if not 30 <= word_count <= 50:
            errors.append(f'{sid}/{locale}: public impact copy has {word_count} words; expected 30–50')

        capability = capability_titles.get(sid, {}).get(locale, '')
        title_tokens = content_tokens(capability, rules['stopwords'])
        response_tokens = content_tokens(response, rules['stopwords'])
        title_reuse = len(title_tokens & response_tokens) / max(1, len(title_tokens))
        if title_reuse >= 0.45:
            errors.append(f'{sid}/{locale}: Koali response paraphrases capability title ({title_reuse:.0%} token reuse)')
        section_heading = '## With Koali' if locale == 'en' else '## Avec Koali'
        section_match = re.search(
            rf'(?ms)^{re.escape(section_heading)}\n\n(.*?)(?=\n## )',
            text,
        )
        section_copy = section_match.group(1).strip() if section_match else ''
        if section_copy != response:
            errors.append(f'{sid}/{locale}: {section_heading} does not match the authored Koali response')
        if rules['generic_body'] in text:
            errors.append(f'{sid}/{locale}: generic continuity paragraph remains')

    if len(titles) != 120:
        errors.append(f'{locale}: expected 120 scenarios, found {len(titles)}')

    for signature, ids in opening_signatures.items():
        if signature and len(ids) > 1:
            errors.append(f'{locale}: repeated three-word problem opening {signature!r}: {", ".join(ids)}')
    for verb, ids in response_verbs.items():
        if len(ids) > 12:
            errors.append(f'{locale}: repetitive Koali response verb {verb!r}: {len(ids)} uses')

    for label, values in (
        ('title', titles),
        ('continuity gap', gaps),
        ('public impact summary', summaries),
        ('Koali response', responses),
    ):
        groups = {}
        for sid, value in values.items():
            groups.setdefault(value.casefold(), []).append(sid)
        for ids in groups.values():
            if len(ids) > 1:
                errors.append(f'Duplicate {label}/{locale}: {", ".join(ids)}')

    article_starts = sum(
        1 for title in titles.values()
        if re.match(rules['article_pattern'], title)
    )
    if article_starts > rules['article_limit']:
        errors.append(f'{locale}: repetitive title openings ({article_starts})')

    preview = (R / 'preview' / locale / 'index.html').read_text(encoding='utf-8')
    match = re.search(r'<script type="application/json" data-mosaic-data>(.*?)</script>', preview, re.S)
    if not match:
        errors.append(f'{locale}: preview scenario data is missing')
    else:
        data = json.loads(match.group(1))
        if len(data) != 120:
            errors.append(f'{locale}: preview contains {len(data)} scenarios')
        for sid, title in titles.items():
            item = data.get(sid, {})
            if item.get('example') != title:
                errors.append(f'{sid}/{locale}: generated preview title is stale')
            if item.get('summary') != summaries[sid]:
                errors.append(f'{sid}/{locale}: generated preview impact copy is stale')
            if rules['generic_preview'] in item.get('summary', ''):
                errors.append(f'{sid}/{locale}: generic generated response remains')

            detail_path = R / 'preview' / locale / 'uses' / sid / 'index.html'
            detail = detail_path.read_text(encoding='utf-8') if detail_path.exists() else ''
            detail_title = re.search(r'<h1 data-preview-title>(.*?)</h1>', detail, re.S)
            detail_summary = re.search(
                r'<p class="preview-summary" data-preview-summary>(.*?)</p>',
                detail,
                re.S,
            )
            rendered_title = html_lib.unescape(detail_title.group(1)) if detail_title else ''
            rendered_summary = html_lib.unescape(detail_summary.group(1)) if detail_summary else ''
            if rendered_title != capability_titles.get(sid, {}).get(locale, ''):
                errors.append(f'{sid}/{locale}: detailed preview capability title is stale')
            if rendered_summary != summaries[sid]:
                errors.append(f'{sid}/{locale}: detailed preview impact copy is stale')

    print(
        f'{locale.upper()} editorial variety: {len(titles)} unique titles, '
        f'{len(gaps)} unique gaps, {len(summaries)} unique impact summaries'
    )
    print(f'{locale.upper()} article-led title openings: {article_starts} / 120')
    print(f'{locale.upper()} most-used Koali response verb: {max(map(len, response_verbs.values()))} / 120')

if errors:
    print('\nEDITORIAL VARIETY VALIDATION FAILED')
    for error in errors:
        print(f' - {error}')
    sys.exit(1)
print('English and French scenario copy is synchronized and free of exact narrative duplicates.')
