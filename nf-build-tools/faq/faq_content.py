# -*- coding: utf-8 -*-
"""The /faqs copy, as data.

One source for both the visible page and the FAQPage JSON-LD, because the brief
requires them to match exactly and generating both from the same object is the
only way that stays true after the next edit.

4 Sep, third cut. It ran to 33 questions across six categories, which made a
simple business look complicated and turned the page into a policy manual.
Alex: "one question = one genuinely distinct thing somebody needs to
understand", not every sentence of the business model getting its own
accordion. Four categories, sixteen questions, answers held to roughly 60-120
words, with the detail pushed out to the pages that actually prove it.

What was folded in rather than cut:
  access codes, cups-to-kilos, venue pricing, rent vs buy, milk coolers and
  machine sizing all now live inside the four Buying answers
  certifications, "are you against certification", "more sustainable than
  normal coffee" and "does it save a forest" are one comparison answer
  the four origins are a visual row under Coffee & Conservation, not a question
  used grounds and sustainability reporting are single sentences
"""

ORIGINS_ROW = [
    ("Batang Toru", "Tapanuli, North Sumatra", "/origins/batang-toru"),
    ("Batang Gadis", "Mandailing, North Sumatra", "/origins/batang-gadis"),
    ("Gayo Lues", "Aceh", "/origins/gayo-lues"),
    ("Arakan Mountains", "Magway, Myanmar", "/origins/arakan-mountains"),
]

# The two external citations. UNVERIFIED: this session has no network access,
# so these are written from knowledge and must be opened and confirmed before
# the page is published.
SRC_RA = "https://www.rainforest-alliance.org/resource-item/2020-sustainable-agriculture-standard/"
SRC_FT = "https://www.fairtrade.net/standard/minimum-price-info"

CATEGORIES = [
    {
        "n": "01", "id": "why-nofilter", "cls": "The why", "plate": "Agroforest · the forest edge",
        "title": "Why NoFilter?",
        "strap": "Why we care, and why the landscape changes the equation.",
        "img": "https://nofilter-shared.netlify.app/sabar-agroforest.jpg",
        "alt": "Agroforestry coffee under canopy where the farmed land meets standing forest",
        "open": True,
        "items": [
            {
                "id": "why-nofilter-exists",
                "q": "Why does NoFilter exist?",
                "a": """
<p>Most of us buy coffee based on two things: what does it cost, and does it taste good?</p>
<p>We started NoFilter because we think there's another question worth asking: where could that coffee spend be most useful?</p>
<p>We work with farmers and conservation organisations around globally important forests that still have a huge amount to lose. Sometimes we join an existing project; sometimes we help build the coffee programme through infrastructure, processing, finance and market access.</p>
<p>Then we buy the coffee and put a share of every sale back into conservation there.</p>
<p class="nf-faq-lede">We're buying coffee anyway. We'd rather make the purchase count.</p>
""",
            },
            {
                "id": "why-landscape-matters",
                "q": "Why does it matter where my coffee comes from?",
                "a": """
<p>Because two cups can look identical and come from completely different landscapes.</p>
<p>One might come from land already heavily simplified for agriculture. The other might come from farmers working around a forest that still holds orangutans, tigers, elephants and gibbons, and still has a great deal to lose.</p>
<p>Those places are not ecologically interchangeable. If both can give us good coffee at a price that works, we know which one we would rather support.</p>
<p class="nf-faq-lede">Where demand lands matters.</p>
""",
            },
            {
                "id": "farmers-and-conservation",
                "q": "Why are farmers so important to conservation?",
                "a": """
<p>Because farmers are the bedrock of conservation at the forest edge.</p>
<p>A boundary on a map only gets you so far. If the people living beside it cannot build a viable livelihood around the forest, the pressure on that boundary does not go away.</p>
<p>So we do not only send money to conservation organisations. We invest in the coffee economy too: processing, infrastructure, quality, market access and, above all, recurring demand.</p>
<p>A donation funds conservation. Demand changes what farmers keep producing. We want both working in the same place.</p>
""",
            },
            {
                "id": "certification",
                "q": "How is NoFilter different from Rainforest Alliance and Fairtrade?",
                "a": """
<p>Both do useful work. Neither is trying to answer the question we are.</p>
<p><b class="nf-sub">Rainforest Alliance</b> sets standards for how certified farms are managed, including limits on recent conversion of natural ecosystems. It does not mean the coffee was chosen because the surrounding landscape matters, or send any part of your purchase to conserving it.</p>
<p><b class="nf-sub">Fairtrade</b> works on trading terms. Its Minimum Price is a safety net; it does not guarantee every farmer's costs are covered or that every farmer earns a living income, which is why Fairtrade publishes separate Living Income Reference Prices.</p>
<p><b class="nf-sub">NoFilter</b> asks where the demand should land, and whether the coffee economy can strengthen conservation there.</p>
<p>We are not against certification. We just do not think a logo should end the conversation.</p>
<p class="nf-faq-src"><a href="%s" rel="noopener nofollow" target="_blank">Source · Rainforest Alliance standard ↗</a> &nbsp;·&nbsp; <a href="%s" rel="noopener nofollow" target="_blank">Fairtrade Minimum Price ↗</a></p>
""" % (SRC_RA, SRC_FT),
            },
        ],
    },
    {
        "n": "02", "id": "coffee-conservation", "cls": "The model", "plate": "Batang Gadis drying house · Mandailing",
        "title": "Coffee &amp; Conservation",
        "strap": "What happens on the ground, and where the money goes.",
        "img": "https://nofilter-shared.netlify.app/batang-gadis-signoff.webp",
        "alt": ("Growers, PRCF Indonesia and SRI members with the NoFilter founder at the "
                "Batang Gadis drying house, the forest edge behind them"),
        "origins_row": True,
        "items": [
            {
                "id": "conservation-coffee",
                "q": "What does conservation coffee actually mean?",
                "a": """
<p>That the forest is not a cause attached to ordinary coffee afterwards.</p>
<p>The starting point is a real conservation landscape where farmers, local organisations and NGOs are already at work, or where we can help build the coffee programme around that work.</p>
<p>Then a share of every sale goes back into conservation in the same landscape. The place, the farmers, the coffee economy and the conservation work are connected from the beginning.</p>
<p>We currently buy from four forest landscapes in Sumatra and Myanmar.</p>
""",
            },
            {
                "id": "what-nofilter-does",
                "img": "https://nofilter-shared.netlify.app/batang-gadis-signoff.webp",
                "alt": 'Growers, PRCF Indonesia and SRI members with the NoFilter founder at the Batang Gadis drying house',
                "cap": 'Batang Gadis drying house · Mandailing, North Sumatra',
                "q": "What does NoFilter actually do in these projects?",
                "a": """
<p>It varies by origin, and we would rather say so than claim one tidy role everywhere.</p>
<p>In some places we support a programme already underway as a committed buyer. In others we have helped build or materially expand the coffee side: financing processing equipment and infrastructure, improving quality, strengthening post-harvest systems and creating the route to market.</p>
<p class="nf-faq-lede">The conservation partners bring the conservation expertise. Farmers make the landscape work. We help build the coffee economy around it.</p>
""",
            },
            {
                "id": "conservation-contribution",
                "q": "Where does the conservation money go?",
                "a": """
<p>To the partners working in the landscape your coffee came from: PRCF Indonesia, SRI, OIC, Fauna &amp; Flora and local producer organisations, depending on the origin.</p>
<p>A share of every sale is ring-fenced for it. For trade customers the rate rises with the price paid per kilogram, and the <a href="/trade-pricing">quote builder</a> shows both the percentage and the money it generates before anything is submitted. An optional top-up goes to the partners rather than to our margin.</p>
<p>You should always be able to ask where the conservation part of your money went, and get a straight answer.</p>
""",
            },
            {
                "id": "forest-verification",
                "img": "https://nofilter-shared.netlify.app/verify-drone-poster.webp",
                "alt": 'Drone survey over mapped coffee plots and the forest beyond',
                "cap": 'Drone verification pass · plot boundary and forest edge',
                "q": "How do you verify the forests and coffee origins?",
                "a": """
<p>Coffee plots, their buffer and the forest beyond are mapped as GPS boundaries with partners on the ground, then checked against independent satellite monitoring and field evidence.</p>
<p>Drone and ground-verification layers are being added, and the site says which layers are live and which are not. We would rather show an evidence system honestly as it develops than present a claim you simply have to trust.</p>
<p class="nf-faq-cta"><a href="/origins">See how we verify it →</a></p>
""",
            },
        ],
    },
    {
        "n": "03", "id": "buying", "cls": "The setup", "plate": "CaféMatic 8 · NoFilter livery",
        "title": "Buying NoFilter",
        "strap": "Coffee, machines and what it actually costs.",
        "img": "https://nofilter-shared.netlify.app/cafematic-8-w1400.webp",
        "alt": "A CaféMatic 8 bean-to-cup machine in NoFilter livery",
        "items": [
            {
                "id": "trade-pricing",
                "q": "How do I get a price?",
                "a": """
<p>Build it yourself. Choose your coffees, expected volume, machines and servicing, and watch the trade rate, equipment cost and conservation contribution update as you go.</p>
<p>Because it contains live wholesale pricing, access is by a code sent to a work email address. No sales call required just to find out what your setup costs, and no waiting for somebody to turn a rate card into a PDF.</p>
<p class="nf-faq-cta"><a href="/trade-pricing">Build your quote →</a></p>
""",
            },
            {
                "id": "quote-binding",
                "q": "Is the quote binding?",
                "a": """
<p>No.</p>
<p>Change the coffees, the machines, the volume. Nothing is committed because somebody used the builder.</p>
<p>When you are happy you submit your selections, and we check the details before anything becomes final. Prices on a saved quote are held until the expiry date shown on it.</p>
""",
            },
            {
                "id": "machines",
                "q": "Can we use our existing machines?",
                "a": """
<p>Yes. Keep your machines and just buy the coffee.</p>
<p>Or take equipment from us, bought outright or on monthly rental, with milk coolers and the service programme included in the rental. Both are modelled in the builder so you can see the difference before deciding, and any included equipment is priced there rather than appearing later as a surprise.</p>
<p>Coffee and equipment are separate choices.</p>
""",
            },
            {
                "id": "sizing",
                "img": "https://nofilter-shared.netlify.app/cafematic-8-w1400.webp",
                "alt": 'A CaféMatic 8 bean-to-cup machine in NoFilter livery',
                "cap": 'CaféMatic 8 · NoFilter livery',
                "q": "How do you work out which machine and how much coffee we need?",
                "a": """
<p>Volume first: tell the builder roughly how many cups a year you expect and it converts them at 18 g a cup. If you already know your kilos, enter those instead.</p>
<p>Then the machine, sized on cups a day, the busiest period and what people actually drink, rather than on the name over the door. There is no separate office, café, hotel or zoo tariff.</p>
<p>The builder gives a sensible starting point and we sense-check it before anything is ordered. Tastings, on the equipment you are considering, can be arranged first.</p>
""",
            },
        ],
    },
    {
        "n": "04", "id": "once-with-us", "cls": "The day-to-day", "plate": "The pour · Singapore",
        "title": "Once you're with us",
        "strap": "Roasting, service, reporting and where we operate.",
        "img": "https://nofilter-shared.netlify.app/quote-pour-2.jpg",
        "alt": "Coffee being poured at a NoFilter counter",
        "items": [
            {
                "id": "servicing",
                "q": "How does servicing work, and what if something breaks?",
                "a": """
<p class="nf-faq-lede">Service on schedule, not on complaint.</p>
<p>Maintenance is planned in advance. Three weeks before a service is due the system proposes a date to your site contact and the technician at the same time, so it does not become somebody's manual reminder.</p>
<p>If something does break, tell us and we coordinate the response rather than leaving you to work out which distributor or technician to chase. Parts, labour and response arrangements vary by equipment package and are confirmed in the proposal.</p>
""",
            },
            {
                "id": "roasting",
                "q": "Is the coffee roasted fresh?",
                "a": """
<p>Yes. We roast against demand rather than producing large batches and leaving them in stock, so the coffee gets from roaster to counter without months in a warehouse in between.</p>
<p>In Singapore we also collect spent grounds with deliveries and divert them into local composting and community-garden channels. That arrangement is Singapore-specific for now, and we will say so rather than imply it exists elsewhere.</p>
""",
            },
            {
                "id": "impact-tracking",
                "q": "Can we track the conservation contribution?",
                "a": """
<p>Yes. Trade partnerships can include a tracker showing coffee supplied and conservation contribution generated over time.</p>
<p>The number follows what you actually buy. Drink less coffee and it grows more slowly; there is no impact counter ticking away independently of your orders.</p>
<p>For sustainability teams we can provide supporting supply-chain data covering origins, volumes, contributions and traceability, which is more useful than another logo.</p>
""",
            },
            {
                "id": "markets",
                "q": "Where does NoFilter currently operate?",
                "a": """
<p>Singapore and the United Arab Emirates, through NoFilter Pte. Ltd. and NoFilter LLC. Those are the markets where the operating setup and trade pricing sit behind the offer.</p>
<p>We take enquiries from elsewhere, including the UK. If we can supply a market properly we will explain how, and if we are not ready there yet we will say so rather than pretend Singapore or UAE terms travel automatically.</p>
""",
            },
        ],
    },
]

INTRO = ("NoFilter works with farmers and conservation partners around threatened "
         "forests to make agroforestry coffee worth growing, and puts a share of "
         "every sale back into protecting the same landscape.")

TECHLINE = "SINGAPORE · UAE · SUMATRA · MYANMAR"

# the file strip, between hero and content. Counts are derived from the data
# below rather than typed, so they cannot drift when a question is added.
STRIP_DATE = "05 Sep 2026"

# a faint coordinate under each category: the real one for that origin, taken
# from the site's own ORIGINS table
PLOT = {"why-nofilter":       "1°38′18″N · 99°15′56″E",
        "coffee-conservation":"0°38′N · 99°30′E",
        "buying":             "1°17′N · 103°51′E",
        "once-with-us":       "1°17′N · 103°51′E"}

H1_A = "Questions."
H1_B = "Straight answers."
H1 = H1_A + " " + H1_B          # the schema and <title> want it as one string

KICKER = "FAQ · NoFilter"

# One photograph, and a real one, from the site's own CDN rather than stock:
# the aerial the origins page already uses to make the point that "the line
# between farmed and untouched isn't a claim, it's a coordinate". The
# coordinate printed under it is Batang Toru's, the only one of the four the
# site marks ON RECORD rather than REGION · INDICATIVE.
HERO_IMG = "https://nofilter-shared.netlify.app/aerial-batang-toru-ricefield-mosaic.jpg"
HERO_ALT = ("Aerial view of the Batang Toru buffer in Tapanuli, North Sumatra: "
            "coffee and rice mosaic meeting standing forest along the boundary")
HERO_CAP_1 = "Batang Toru buffer · Tapanuli, North Sumatra"
HERO_CAP_2 = "1°38′18″N · 99°15′56″E · on record"

# Per market, and inside the lengths a result actually shows: a title over
# about 62 characters is truncated, and a description over about 165 is. The
# first cut ran to 83 and 219, and the two markets shared both, which is the one
# duplicate pair in the bundle. The house convention is followed: the UAE page
# says so in its own title rather than repeating the Singapore one.
TITLE = "FAQs — conservation coffee, certification, pricing | NoFilter"
DESC = ("How NoFilter buys coffee through NGO-led conservation projects, how that "
        "differs from Rainforest Alliance and Fairtrade, and how trade pricing works.")
TITLE_AE = "FAQs — conservation coffee in the UAE | NoFilter"
DESC_AE = ("How NoFilter buys coffee through NGO-led conservation projects, how that "
           "differs from certification schemes, and how UAE trade supply is priced.")
# 6 Sep · the UK pair, for /uk/faqs. Same convention: the page says which market
# it is in its own title, so no two pages in the bundle share a title or a
# description. Mirrored from the UAE wording — copy is Alex's to change.
TITLE_UK = "FAQs — conservation coffee in the UK | NoFilter"
DESC_UK = ("How NoFilter buys coffee through NGO-led conservation projects, how that "
           "differs from certification schemes, and how UK trade supply is priced.")
