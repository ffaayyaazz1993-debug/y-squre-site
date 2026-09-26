/* Y-Square — articles.js
   The client-side search index. This is the single source of truth for
   article metadata and doubles as the feed a future CMS/API would replace.

   Shape is deliberately close to a JSON API response so swapping in a real
   backend means changing one fetch, not the search code:
     { version, generated, articles: [ {id, url, title, type, section,
        region, country, topics[], summary, author, published, updated,
        readingTime, sources[]} ] }

   `type` is one of: news | analysis | explainer | research
   and is what separates reported fact from Y-Square opinion.
*/
window.YSQ_ARTICLES = {
  version: '2026-09-26',
  generated: '2026-09-26',
  articles: [
    {
      id: 'cb-balance-sheets-2026',
      url: '/research/2026/09/26/central-bank-balance-sheets.html',
      title: 'The balance sheet is the policy: reading central banks past the rate decision',
      type: 'research',
      typeLabel: 'Research Note',
      section: 'research',
      sectionLabel: 'Research',
      region: 'global',
      country: '',
      topics: ['Monetary policy', 'Central banks', 'Quantitative easing', 'Interest rates'],
      summary: 'Markets price the rate decision, then react to what the central bank actually did to its portfolio. Those are not the same event, and the gap between them is where most of the mispricing sits.',
      author: 'Y-Square Research',
      published: '2026-09-26T11:00:00+05:30',
      updated: '',
      readingTime: '8 min read',
      sources: [
        { kind: 'primary', name: 'Central bank balance sheet and holdings publications', url: '' },
        { kind: 'primary', name: 'National statistical agency data', url: '' }
      ]
    },
    {
      id: 'cb-balance-sheets-analysis-2026',
      url: '/blog/2026/09/26/reading-central-bank-intent.html',
      title: 'What a central bank balance sheet tells you that the rate does not',
      type: 'analysis',
      typeLabel: 'Analysis',
      section: 'blog',
      sectionLabel: 'Blog',
      region: 'global',
      country: '',
      topics: ['Monetary policy', 'Analysis', 'Asset prices'],
      summary: 'The rate is the fastest-moving expression of policy and the most closely watched. It is also, on its own, an incomplete one. This note sets out where the asset side of the balance sheet adds information, and where it misleads.',
      author: 'Y-Square Research',
      published: '2026-09-26T14:30:00+05:30',
      updated: '',
      readingTime: '6 min read',
      sources: [
        { kind: 'primary', name: 'Publicly published central bank holdings data', url: '' }
      ]
    },
    {
      id: 'fx-depreciation-explainer-2026',
      url: '/blog/2026/09/26/understanding-currency-depreciation.html',
      title: 'Understanding currency depreciation: a mechanics explainer',
      type: 'explainer',
      typeLabel: 'Explainer',
      section: 'blog',
      sectionLabel: 'Blog',
      region: 'global',
      country: '',
      topics: ['Currencies', 'Explainer', 'Inflation', 'Trade'],
      summary: 'Why a currency falls is rarely one thing. This explainer separates the balance-of-payments mechanism from the interest-rate channel and the risk-premium channel, and shows why the same depreciation can mean opposite things for an economy.',
      author: 'Y-Square Research',
      published: '2026-09-26T16:00:00+05:30',
      updated: '',
      readingTime: '7 min read',
      sources: [
        { kind: 'primary', name: 'Central bank and statistical agency releases', url: '' }
      ]
    }
  ]
};
