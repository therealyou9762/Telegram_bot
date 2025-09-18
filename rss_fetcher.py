import feedparser
from database import add_news, add_news_stat, get_keywords

NEWS_SOURCES = [
    # Великобритания
    "https://www.bbc.com/news/world/rss.xml",
    "https://www.theguardian.com/world/rss",
    "https://www.independent.co.uk/news/world/rss",
    "https://feeds.skynews.com/feeds/rss/world.xml",

    # Германия
    "https://www.spiegel.de/international/index.rss",
    "https://rss.sueddeutsche.de/rss/Politik",
    "https://www.dw.com/en/top-stories/s-9097/rss.xml",
    "https://www.tagesschau.de/xml/rss2/",

    # Франция
    "https://www.france24.com/en/rss",
    "https://www.lemonde.fr/international/rss_full.xml",
    "https://www.rfi.fr/en/rss",

    # Италия
    "https://www.ansa.it/sito/notizie/mondo/mondo_rss.xml",
    "https://www.ilpost.it/feed/",

    # Испания
    "https://english.elpais.com/rss/section/international/",
    "https://e00-elmundo.uecdn.es/elmundo/rss/internacional.xml",

    # Польша
    "https://www.tvn24.pl/najnowsze.xml",
    "https://wiadomosci.onet.pl/rss.xml",
    "https://wyborcza.pl/pub/rss/wyborcza.xml",
    "https://notesfrompoland.com/feed/",

    # Нидерланды
    "https://nltimes.nl/rss",
    "https://www.dutchnews.nl/feed/",

    # Бельгия
    "https://www.brusselstimes.com/feed/",
    "https://www.lesoir.be/rss/lesoir.xml",

    # Португалия
    "https://expresso.pt/rss/ultimas",
    "https://www.publico.pt/rss",

    # Чехия
    "https://www.seznamzpravy.cz/rss",
    "https://denikn.cz/feed/",

    # Словакия
    "https://dennikn.sk/feed/",
    "https://www.sme.sk/rss/sekcie/2/index.xml",

    # Финляндия
    "https://www.hs.fi/rss/english.xml",
    "https://yle.fi/uutiset/osasto/news/rss.xml",

    # Швеция
    "https://www.svt.se/rss.xml",
    "https://www.dn.se/rss/",

    # Дания
    "https://www.tv2.dk/rss",
    "https://politiken.dk/rss",

    # Норвегия
    "https://www.nrk.no/toppsaker.rss",
    "https://www.aftenposten.no/rss",

    # Ирландия
    "https://www.irishtimes.com/international/rss",

    # Австрия
    "https://www.derstandard.at/rss",
    "https://www.diepresse.com/rss",

    # Швейцария
    "https://www.nzz.ch/rss",
    "https://www.letemps.ch/rss",

    # Болгария
    "https://www.dnevnik.bg/rss/",
    "https://www.segabg.com/rss.xml",

    # Румыния
    "https://www.gandul.ro/rss",
    "https://www.digi24.ro/rss",

    # Греция
    "https://www.kathimerini.gr/feed/",
    "https://www.protothema.gr/rss/news-international.xml",

    # Литва, Латвия, Эстония (Балтия)
    "https://www.delfi.lt/rss/",
    "https://www.delfi.lv/rss/",
    "https://www.delfi.ee/rss/",
    "https://www.lrytas.lt/rss",
    "https://www.la.lv/feed",
    "https://www.postimees.ee/rss",

    # Хорватия
    "https://www.jutarnji.hr/rss",
    "https://www.index.hr/rss",

    # Сербия
    "https://nova.rs/feed/",
    "https://www.blic.rs/rss",
    "https://informer.rs/rss",

    # Босния и Герцеговина
    "https://www.klix.ba/rss",
    "https://www.oslobodjenje.ba/feed",

    # Черногория
    "https://www.vijesti.me/rss",

    # Словения
    "https://www.delo.si/rss/",

    # Албания
    "https://gazeta-shqip.com/feed/",

    # Северная Македония
    "https://novamakedonija.com.mk/feed/",

    # Кипр
    "https://www.philenews.com/rss/",
    "https://www.politis.com.cy/feed/",

    # Мальта
    "https://timesofmalta.com/rss",

    # Люксембург
    "https://www.wort.lu/en/rss",

    # Украина (главные англоязычные и русскоязычные ленты)
    "https://www.ukrinform.ua/rss/rss.php",
    "https://www.pravda.com.ua/eng/rss/",
    "https://www.liga.net/rss", 
    "https://censor.net/rss",
    "https://www.eurointegration.com.ua/rss.xml",
    "https://novayagazeta.eu/rss",
    "https://www.euronews.com/rss?level=theme&name=ukraine-crisis",

    # Международные (часто публикуют про Украину)
    "https://www.politico.eu/feed/",
    "https://www.eurotopics.net/en/rss.xml",
    "https://feeds.nova.bg/news/world/rss.xml",
]

def fetch_and_filter_news(user_id):
    keywords = [kw['word'] for kw in get_keywords()]
    stats = []
    for src in NEWS_SOURCES:
        feed = feedparser.parse(src)
        for kw in keywords:
            matched = [entry for entry in feed.entries if kw.lower() in (entry.title + entry.summary).lower()]
            for entry in matched:
                add_news(
                    entry.title,
                    entry.link,
                    entry.summary if hasattr(entry, 'summary') else '',
                    entry.get('category', 'Без категории'),
                    entry.published if hasattr(entry, 'published') else ''
                )
            stats.append({
                "keyword": kw,
                "source": src,
                "found_count": len(matched),
                "date": entry.published[:10] if hasattr(entry, 'published') else '',
            })
    # Сохраняем статистику
    for stat in stats:
        add_news_stat(user_id, stat['keyword'], stat['source'], stat['found_count'], stat['date'])
