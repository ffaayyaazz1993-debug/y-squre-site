"""Static pages: about, contact, privacy, terms, disclaimer, editorial policy,
advertising. Plus robots.txt, sitemap.xml, favicon and the OG image."""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_lib import *  # noqa

PAGES = []


def simple(path, title, desc, h1, lede, blocks, active="", extra_script=""):
    b = head(title, desc, "/" + path, section=h1)
    b += header(active)
    b += crumbs([("/", "Home"), ("/" + path, h1)])
    b += '  <main id="main">\n' + ad("Advertisement", "ad-top")
    b += page_head(esc(h1), lede)
    b += f'    <div class="wrap" style="padding-top:26px">\n      <div class="prose">\n{blocks}\n      </div>\n    </div>\n  </main>\n'
    b += footer()
    PAGES.append((path, b))
    return b



# -------------------------------------------------------------------- account
# The brief asked for a Sign In slot in the masthead. There is no account
# system, so rather than ship a link to a page that does not exist -- or a
# fake login form that collects credentials it cannot use -- this states
# plainly what the slot is reserved for.
simple("account/index.html", "Account | Y-Square",
       "The Y-Square account area. There is no reader account or login service "
       "yet; this page records what the space is reserved for.",
       "Account",
       "Reader accounts are not switched on. This page records what the area is reserved for.",
       """            <p>Y-Square does not have reader accounts, and there is nothing to sign in to.
            No login form is shown here deliberately: a form that could not do anything
            would be worse than none.</p>

            <h2>What the account area is reserved for</h2>
            <p>The masthead carries a <strong>Sign In</strong> slot so the navigation does
            not have to be rebuilt when the service arrives. It is planned to cover:</p>
            <ul>
              <li>saved articles and reading lists,</li>
              <li>email alerts on the sections a reader follows,</li>
              <li>a newsletter archive, and</li>
              <li>an optional paid-research entitlement.</li>
            </ul>

            <h2>What we are not doing in the meantime</h2>
            <p>Y-Square does not ask for a password, does not run a newsletter sign-up that
            stores a profile behind it, and does not sell or share reader data. Nothing on
            this site requires an account to read.</p>

            <h2>Following sections without an account</h2>
            <p>Use the navigation to reach any region, market, macro, research or blog
            section directly. Every page is public and needs no sign-in.</p>

            <p><a href="/">Return to the front page</a> or browse
            <a href="/geopolitics/">geopolitical coverage</a> and
            <a href="/macro/">macroeconomic analysis</a>.</p>""")

# ---------------------------------------------------------------------- about
simple("about/index.html", "About Y-Square | Y-Square Research",
       "What Y-Square is, how its research is produced and labelled, and the editorial standards it holds itself to.",
       "About Y-Square",
       "An independent research practice working on macroeconomics, geopolitics and markets.",
       """            <p>Y-Square is an independent investment research and analysis practice. We
            publish work on macroeconomics, geopolitics and markets, and we do not manage
            money, sell products, or accept a commission for a view.</p>

            <h2>What we do</h2>
            <p>Our work starts from the aggregate economy and the state system rather than from
            a screen. We read primary sources, we state the assumptions behind a conclusion,
            and we name the conditions under which we would be wrong.</p>

            <h2>How we label things</h2>
            <p>Every article carries one of four labels, and the label tells you what kind of
            statement you are reading before you read it:</p>
            <ul>
              <li><strong>News</strong> &mdash; reporting on an event, attributed to its source.</li>
              <li><strong>Analysis</strong> &mdash; our interpretation of events or data.</li>
              <li><strong>Explainer</strong> &mdash; an explanation of a mechanism.</li>
              <li><strong>Research Note</strong> &mdash; a longer document with a stated method.</li>
            </ul>
            <p>We do not present opinion as reporting, and we do not present a source's claim
            as our own verification. Where we report what another outlet or an official body
            said, we say so in the sentence.</p>

            <h2>What we will not do</h2>
            <ul>
              <li>Publish a statistic we cannot source, or a quote we cannot attribute.</li>
              <li>Invent an event to fill a section.</li>
              <li>Present a forecast as a finding.</li>
              <li>Publish a headline designed to be more alarming than the evidence.</li>
            </ul>

            <h2>Independence</h2>
            <p>We accept advertising through Google AdSense, which is disclosed on every page
            and detailed on the <a href="/advertising/index.html">advertising</a> page.
            Advertisers do not see our editorial work before publication and have no input
            into it. We do not currently run paid research, and we do not take a commission on
            anything we cover.</p>

            <h2>Corrections</h2>
            <p>If something here is materially wrong, tell us and we will check it. Corrections
            are noted on the article with a timestamp rather than silently edited.</p>""")

# -------------------------------------------------------------------- contact
simple("contact/index.html", "Contact | Y-Square Research",
       "Contact Y-Square about questions, corrections, research requests or advertising. We reply to enquiries within two business days.",
       "Contact",
       "Questions, corrections, or a specific research request. We reply within two business days.",
       f"""            <p>We read everything that arrives. The fastest way to reach us is email.</p>

            <p style="margin:18px 0"><strong style="font-size:1.05rem">
            <a href="mailto:{EMAIL}">{EMAIL}</a></strong></p>

            <h2>What to include</h2>
            <ul>
              <li>For a <strong>correction</strong>, the article URL and what specifically is
              wrong. We will check primary sources and correct with a timestamp.</li>
              <li>For a <strong>question</strong> about published work, the article it relates
              to. General questions are answered when we can, but we are a small practice.</li>
              <li>For a <strong>research request</strong>, the market, asset class or region
              and the question you are trying to answer.</li>
            </ul>

            <h2>What we cannot do</h2>
            <ul>
              <li>Give investment advice or a recommendation to buy or sell.</li>
              <li>Comment on an individual holding or a personal financial situation.</li>
              <li>Provide data we have not verified, or a source we have not read.</li>
            </ul>
            <p>Y-Square is not a SEBI-registered investment adviser. Nothing we publish is a
            solicitation to buy or sell any security.</p>""")

# -------------------------------------------------------------------- privacy
# Body carried forward from the policy already live at /privacy.html.
PRIVACY = """            <h2>Summary</h2>
            <p>This site collects very little. We do not run accounts, we have no contact
            form that posts to us, we use no analytics of our own, and we embed no third-party
            media. What we do collect is: the email you use to contact us, the server logs
            our host keeps, the cookies Google AdSense sets, and the cookie choice you make
            on this site.</p>

            <h2>Who we are</h2>
            <p>Y-Square is an independent research practice. Contact:
            <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>

            <h2>What we collect directly</h2>
            <h3>Enquiry email</h3>
            <p>If you email us we keep your message and address so we can reply and retain the
            correspondence. We use it for that purpose only. We do not add correspondents to a
            mailing list, and we do not sell or share it.</p>

            <h3>Server logs</h3>
            <p>Our hosting provider records standard request logs, including IP address,
            timestamp, requested URL, user agent and referrer. These are generated by the
            hosting infrastructure, not by us, and are used for security and troubleshooting.</p>

            <h3>Your cookie choice</h3>
            <p>When you accept or decline cookies we store that single value
            (<code>ysq_consent</code>) in your browser's local storage so we do not ask you
            again on every page. It contains no identifier and never leaves your browser. You
            can clear it at any time using the &ldquo;Cookie choices&rdquo; link in the footer.</p>

            <h2>Advertising and Google</h2>
            <p>This site uses <strong>Google AdSense</strong> to display advertising.</p>
            <ul>
              <li>Google and its partners may use cookies and similar technologies to serve and
              measure ads.</li>
              <li>Google's use of advertising cookies enables it and its partners to serve ads
              to users based on their visits to this and other sites.</li>
              <li>You may opt out of personalised advertising by visiting
              <a href="https://www.google.com/settings/ads" rel="noopener nofollow"
              target="_blank">Google Ads Settings</a>.</li>
              <li>For how Google uses information from sites that use its services, see
              <a href="https://policies.google.com/technologies/partner-sites"
              rel="noopener nofollow" target="_blank">How Google uses data from sites that use
              our services</a>.</li>
            </ul>
            <p>Declining cookies on this site does not prevent you from reading anything here,
            and it does not stop Google serving ads under its own consent framework.</p>

            <h2>European regulations (GDPR)</h2>
            <p>Where the GDPR applies to you, we process personal data on the following bases:
            <strong>legitimate interests</strong> for responding to enquiries and securing the
            site, and <strong>consent</strong> for advertising cookies. You have the right to
            access, correct, erase, restrict, port and object to processing of your personal
            data, and to withdraw consent at any time. To exercise any of these, email
            <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>

            <h2>California (CCPA/CPRA)</h2>
            <p>California residents have the right to know what personal information is
            collected, to request deletion, to request correction, to opt out of sale or
            sharing of personal information, and to limit use of sensitive personal
            information. <strong>Y-Square does not sell or share personal information as those
            terms are defined by the CCPA.</strong> Advertising cookies are set by Google; to
            opt out of interest-based advertising, use the
            <a href="https://www.google.com/settings/ads" rel="noopener nofollow"
            target="_blank">Google Ads Settings</a> page.</p>
            <p>We honour the <strong>Global Privacy Control (GPC)</strong> signal. If your
            browser sends it, this site records a decline and does not show you the cookie
            banner again, because under CCPA section 7025 that signal is treated as a valid
            opt-out request.</p>

            <h2>What we do not collect</h2>
            <ul>
              <li>No user accounts, and no login.</li>
              <li>No contact form that stores your submission on this site.</li>
              <li>No analytics, tracking pixels or profiling tools of our own.</li>
              <li>No third-party videos, maps, fonts or social widgets embedded in articles.</li>
              <li>No sale or rental of personal data, in any form.</li>
            </ul>

            <h2>Children</h2>
            <p>This site is not directed at children and we do not knowingly collect personal
            data from anyone under 16.</p>

            <h2>Retention</h2>
            <p>Enquiry correspondence is retained only as long as needed to deal with the
            matter. Server logs are retained according to our host's configuration.</p>

            <h2>Changes to this policy</h2>
            <p>If this policy changes materially we will update the date below and, where the
            change affects how data is used, note it on the homepage.</p>

            <h2>Contact</h2>
            <p>Questions about this policy: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>"""
simple("privacy/index.html", "Privacy Policy | Y-Square Research",
       "What Y-Square collects, what it does not, and the choices you have under the GDPR and the CCPA, including how to opt out of advertising cookies.",
       "Privacy Policy", "Last updated 26 September 2026. Written to describe what actually "
       "happens on this site, not to satisfy a template.", PRIVACY)

# ---------------------------------------------------------------------- terms
simple("terms/index.html", "Terms of Use | Y-Square Research",
       "The terms governing use of the Y-Square website: no investment advice, no offer, market risk, and the limits of what this site provides.",
       "Terms of Use", "Last updated 26 September 2026.",
       f"""            <h2>1. What this site is</h2>
            <p>Y-Square publishes research, analysis and educational material. It is not a
            brokerage, not an investment adviser, and not a provider of personalised financial
            services. It is not a SEBI-registered investment adviser.</p>

            <h2>2. No advice, no offer</h2>
            <p>Nothing on this site is investment advice, a personal recommendation, or an
            offer or solicitation to buy or sell any security or financial instrument. Nothing
            takes account of your objectives, financial situation or needs.</p>

            <h2>3. Risk</h2>
            <p>Investments in securities markets are subject to market risks. You may lose some
            or all of the capital you invest. Past performance is not a guide to future
            results. Forecasts and scenarios are opinions, not guarantees, and may prove wrong.</p>

            <h2>4. Licence to read</h2>
            <p>You may read, link to and quote short extracts from this site with attribution
            and a link. You may not republish substantial portions of our work, resell it, or
            present it as your own.</p>

            <h2>5. Third-party links and advertising</h2>
            <p>This site contains advertising served by Google AdSense and may link to
            third-party sites. We do not control and are not responsible for third-party
            content, products or practices. See the <a href="/advertising/index.html">advertising
            page</a> and our <a href="/privacy/index.html">privacy policy</a>.</p>

            <h2>6. No warranty</h2>
            <p>The site is provided "as is" without warranties of any kind. We do not warrant
            that it will be uninterrupted, error-free, or that any information is complete or
            current. We may change, suspend or withdraw any part of it at any time.</p>

            <h2>7. Limitation of liability</h2>
            <p>To the extent permitted by law, Y-Square is not liable for any loss arising
            from use of, or reliance on, anything published here.</p>

            <h2>8. Governing law</h2>
            <p>These terms are governed by the laws of India, and the courts of India have
            jurisdiction.</p>

            <h2>9. Contact</h2>
            <p>Questions about these terms: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>""")

# ----------------------------------------------------------------- disclaimer
simple("disclaimer/index.html", "Investment Disclaimer | Y-Square Research",
       "The Y-Square investment risk disclaimer: market risk, no personal advice, no offer, regulatory status, and the limits of forecasts and opinion.",
       "Investment Disclaimer", "Last updated 26 September 2026.",
       f"""            <div class="notice">
              <p>{FOOTER_DISCLAIMER}</p>
            </div>

            <h2>Market risk</h2>
            <p>The value of investments and the income from them can fall as well as rise, and
            you may get back less than you put in. Past performance is not a reliable indicator
            of future results. The value of investments may also fall due to exchange rate
            movements if you hold them in a currency other than your own.</p>

            <h2>No personal advice</h2>
            <p>Content here is general, educational and informational. It is not tailored to
            your objectives, financial situation or needs, and taking it as such could be
            inappropriate. If you are unsure whether a course of action is suitable for you,
            take independent professional advice.</p>

            <h2>No offer</h2>
            <p>Nothing on this site is an offer, or a solicitation of an offer, to buy or sell
            any security, financial instrument or product, in any jurisdiction.</p>

            <h2>Regulatory status</h2>
            <p><strong>Y-Square is not a SEBI-registered investment adviser.</strong> We do not
            manage portfolios, do not receive transaction-based compensation, and do not give
            personalised investment recommendations.</p>

            <h2>Forecasts and opinion</h2>
            <p>Where we discuss scenarios, forecasts or expected outcomes, these are opinions
            about probability, not predictions of fact. They can be wrong. The conditions that
            would falsify a view are stated where we can state them, and readers should assume
            we have not succeeded in every case.</p>

            <h2>Sources</h2>
            <p>We cite primary sources in preference to commentary, and we attribute claims to
            their origin. We do not claim to have independently verified a claim we are
            reporting from another outlet. Data may be revised by its publisher after
            publication.</p>

            <h2>External links</h2>
            <p>Links to third-party sites are provided for context. We do not control them and
            are not responsible for their content.</p>""")

# ----------------------------------------------------------- editorial policy
simple("editorial-policy/index.html", "Editorial Policy | Y-Square Research",
       "How Y-Square selects, writes, labels, sources and corrects its work: what counts as reporting, what counts as analysis, and what we refuse to publish.",
       "Editorial Policy", "Last updated 26 September 2026. This is the standard we hold "
       "ourselves to, and the standard a reader can hold us to.",
       """            <h2>What we publish</h2>
            <p>Research and analysis on macroeconomics, geopolitics and markets. We do not
            publish investment recommendations, price targets, or sponsored content presented
            as editorial.</p>

            <h2>Labelling</h2>
            <p>Every article is labelled <strong>News</strong>, <strong>Analysis</strong>,
            <strong>Explainer</strong> or <strong>Research Note</strong>. The label appears
            before the headline, not in a footer, so a reader knows what kind of statement they
            are looking at before reading it. Analysis is never presented as reporting.</p>

            <h2>Sourcing</h2>
            <ul>
              <li>Primary sources are preferred: government statements, central banks,
              statistical agencies, international organisations and company filings.</li>
              <li>Secondary reporting is used for context and cross-checking, and is named.</li>
              <li>A claim made by another party is attributed in the sentence &mdash; "according
              to X" &mdash; not presented as our own finding.</li>
              <li>Official statements are distinguished from independent verification.</li>
            </ul>

            <h2>What we will not publish</h2>
            <ul>
              <li>Invented events, statistics, quotations or sources.</li>
              <li>Content republished from another publication.</li>
              <li>Headlines written to be more alarming than the evidence.</li>
              <li>Unattributed screenshots, or images we do not have the right to use.</li>
              <li>Forecasts presented as established fact.</li>
            </ul>

            <h2>Advertising and independence</h2>
            <p>Advertising is served by Google AdSense and is labelled. Advertisers have no
            prior sight of, or influence over, editorial content. We do not accept payment for
            coverage, and we do not publish advertorial as analysis.</p>

            <h2>Corrections</h2>
            <p>Errors are corrected on the article with a timestamped note, not silently
            removed. Send us the article URL and what is wrong. If we agree, the correction is
            made; if we disagree, we will say why.</p>

            <h2>Independence and conflicts</h2>
            <p>Y-Square does not manage client money and does not take a commission on anything
            it covers, so there is no position to recommend in any security discussed.</p>""")

# ----------------------------------------------------------------- advertising
simple("advertising/index.html", "Advertising | Y-Square Research",
       "Advertising on Y-Square, and how it is kept separate from editorial work.",
       "Advertising", "Last updated 26 September 2026.",
       f"""            <h2>We do advertise</h2>
            <p>Y-Square is supported by advertising served through <strong>Google AdSense</strong>.
            Ads are clearly separated from editorial content, labelled, and kept out of the
            reading column so they do not interrupt an article.</p>

            <h2>What we will not do</h2>
            <ul>
              <li>Accept payment for a favourable view, a placement, or a story.</li>
              <li>Publish advertorial, native advertising or sponsored posts as analysis.</li>
              <li>Give an advertiser editorial review rights, or show them a draft.</li>
              <li>Accept advertising for anything that would undermine the site's purpose.</li>
            </ul>

            <h2>Labels</h2>
            <p>Every ad container on the site is reserved and marked
            &ldquo;Advertisement&rdquo; before an ad is served into it. Analysis, explainers and
            research notes are never presented as advertising, and advertising is never
            presented as analysis.</p>

            <h2>Enquiries</h2>
            <p>For advertising enquiries: <a href="mailto:{EMAIL}">{EMAIL}</a> with
            &ldquo;Advertising&rdquo; in the subject line.</p>

            <h2>Your privacy</h2>
            <p>Advertising cookies are set by Google, not by us. See the
            <a href="/privacy/index.html">privacy policy</a> for what is collected and how to
            opt out, and the &ldquo;Cookie choices&rdquo; link in the footer to change your
            choice on this site.</p>""")

# ------------------------------------------------------------------- 404 page
# .htaccess sets `ErrorDocument 404 /404/index.html`, so the page must live at
# that path. It previously went to /404.html, which is why a bad URL returned a
# bare server 406 instead of this page. Serving a .html file directly also means
# the site would answer /404.html with HTTP 200, which is wrong for an error
# document.
PAGES.append(("404/index.html",
              head("Page not found | Y-Square", "The page you requested does not exist on this site. Use the links below to reach the homepage, the latest articles, or any section index.", "/404/",
                   noindex=True)
              + header("")
              + '  <main id="main">\n'
              + ad("Advertisement", "ad-top")
              + '    <div class="wrap" style="padding:60px 0 80px">\n'
                '      <div class="prose">\n'
                '        <h1>Page not found</h1>\n'
                '        <p class="lede">That URL does not exist on this site. It may have '
                'moved, or the link that brought you here may be wrong.</p>\n'
                '        <ul>\n'
                '          <li><a href="/">Homepage</a></li>\n'
                '          <li><a href="/latest/">Latest articles</a></li>\n'
                '          <li><a href="/geopolitics/">Geopolitics</a></li>\n'
                '          <li><a href="/macro/">Macroeconomics</a></li>\n'
                '          <li><a href="/markets/">Markets</a></li>\n'
                '          <li><a href="/blog/">Analysis and blog</a></li>\n'
                '          <li><a href="/sitemap.xml">Sitemap</a></li>\n'
                '        </ul>\n'
                '      </div>\n'
                '    </div>\n'
                '  </main>\n'
              + footer()))

if __name__ == "__main__":
    for path, c in PAGES:
        print(f"  {path:<32}{write(path, c):>7}B")
    print(f"\nstatic pages: {len(PAGES)}")
