from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_NAME = BASE_DIR / "guidehub.db"

USERS = [
    {"username": "Giku", "email": "giku@example.com", "password": "1234", "role": "admin"},
    {"username": "Alex", "email": "alex@example.com", "password": "1234", "role": "user"},
    {"username": "Bianca", "email": "bianca@example.com", "password": "1234", "role": "user"},
    {"username": "Pufu", "email": "pufu@example.com", "password": "1234", "role": "user"},
]

CATEGORIES = [
    "Guide",
    "Review",
    "Build",
    "Tips & Tricks",
    "Codes",
    "Discount Coupons",
]

GAMES = [
    {
        "slug": "elden-ring",
        "title": "Elden Ring",
        "description": "Open-world fantasy RPG with deep build freedom, punishing bosses and huge exploration rewards.",
        "image_url": "assets/images/elden-ring.jpg",
        "genre": "Soulslike RPG",
        "difficulty": "Medium / Hard",
        "studio": "FromSoftware",
        "release_year": 2022,
        "platforms": ["PC", "PS5", "Xbox Series X|S"],
        "official_url": "https://en.bandainamcoent.eu/elden-ring/elden-ring",
        "wiki_url": "https://eldenring.wiki.fextralife.com/",
        "community_url": "https://www.reddit.com/r/Eldenring/",
        "priorities": [
            "Upgrade one reliable weapon early instead of splitting materials across many options.",
            "Explore Limgrave and the Weeping Peninsula before forcing difficult legacy bosses.",
            "Invest in vigor and stamina early for a much smoother first 10 hours.",
        ],
    },
    {
        "slug": "cyberpunk-2077",
        "title": "Cyberpunk 2077",
        "description": "Dense sci-fi action RPG focused on build identity, atmospheric districts and quest-driven progression.",
        "image_url": "assets/images/cyberpunk2077.jpg",
        "genre": "Open World Action RPG",
        "difficulty": "Medium",
        "studio": "CD Projekt Red",
        "release_year": 2020,
        "platforms": ["PC", "PS5", "Xbox Series X|S"],
        "official_url": "https://www.cyberpunk.net/",
        "wiki_url": "https://cyberpunk.fandom.com/wiki/Cyberpunk_Wiki",
        "community_url": "https://www.reddit.com/r/cyberpunkgame/",
        "priorities": [
            "Choose early whether you want to lean into hacking, blades or guns.",
            "Street Cred and cyberware upgrades matter as much as pure weapon rarity.",
            "Treat side gigs as the best way to unlock money, XP and world context.",
        ],
    },
    {
        "slug": "baldurs-gate-3",
        "title": "Baldur's Gate 3",
        "description": "Party-based CRPG built around dialogue choices, exploration and tactical turn-based combat.",
        "image_url": "assets/images/bg3.jpg",
        "genre": "CRPG",
        "difficulty": "Medium",
        "studio": "Larian Studios",
        "release_year": 2023,
        "platforms": ["PC", "PS5", "Mac"],
        "official_url": "https://baldursgate3.game/",
        "wiki_url": "https://bg3.wiki/",
        "community_url": "https://www.reddit.com/r/BaldursGate3/",
        "priorities": [
            "A balanced party with crowd control often outperforms raw damage stacking.",
            "Use elevation, surfaces and consumables because encounters are built around them.",
            "Explore every zone carefully because side content is tied directly to long-term power.",
        ],
    },
    {
        "slug": "black-myth-wukong",
        "title": "Black Myth: Wukong",
        "description": "Boss-focused action RPG with strong animation commitment, stance usage and ability timing.",
        "image_url": "assets/images/wukong.jpg",
        "genre": "Action RPG",
        "difficulty": "Hard",
        "studio": "Game Science",
        "release_year": 2024,
        "platforms": ["PC", "PS5"],
        "official_url": "https://www.heishenhua.com/",
        "wiki_url": "https://blackmythwukong.wiki.fextralife.com/",
        "community_url": "https://www.reddit.com/r/BlackMythWukong/",
        "priorities": [
            "Read boss timings before trying to extend long combos.",
            "Stamina discipline is often more important than raw aggression.",
            "Use transformation skills as momentum tools, not panic buttons.",
        ],
    },
    {
        "slug": "helldivers-2",
        "title": "Helldivers 2",
        "description": "Co-op shooter built around squad communication, stratagem timing and fast objective execution.",
        "image_url": "assets/images/helldivers2.jpg",
        "genre": "Co-op Shooter",
        "difficulty": "Medium",
        "studio": "Arrowhead Game Studios",
        "release_year": 2024,
        "platforms": ["PC", "PS5"],
        "official_url": "https://www.playstation.com/en-ro/games/helldivers-2/",
        "wiki_url": "https://helldivers.wiki.gg/wiki/Helldivers_2",
        "community_url": "https://www.reddit.com/r/Helldivers/",
        "priorities": [
            "Bring anti-armor options because difficulties scale hard around elite targets.",
            "Complementary stratagems beat duplicate loadouts in most squads.",
            "Good communication saves more missions than raw aim.",
        ],
    },
    {
        "slug": "the-witcher-3",
        "title": "The Witcher 3: Wild Hunt",
        "description": "Story-rich fantasy RPG with large zones, strong side quests and rewarding preparation systems.",
        "image_url": "assets/images/the-witcher-3.jpg",
        "genre": "RPG",
        "difficulty": "Medium",
        "studio": "CD Projekt Red",
        "release_year": 2015,
        "platforms": ["PC", "PS5", "Xbox Series X|S", "Switch"],
        "official_url": "https://www.thewitcher.com/en/witcher3",
        "wiki_url": "https://witcher.fandom.com/wiki/The_Witcher_3:_Wild_Hunt",
        "community_url": "https://www.reddit.com/r/Witcher3/",
        "priorities": [
            "Craft oils and bombs because preparation matters more than blind rushing.",
            "Do contracts and side quests near your level for steady progression.",
            "Upgrade signs and saddlebags early for smoother exploration.",
        ],
    },
    {
        "slug": "hades",
        "title": "Hades",
        "description": "Fast roguelike action game built around repeat runs, boon synergy and reliable meta progression.",
        "image_url": "assets/images/hades.jpg",
        "genre": "Action",
        "difficulty": "Medium",
        "studio": "Supergiant Games",
        "release_year": 2020,
        "platforms": ["PC", "Switch", "PS5"],
        "official_url": "https://www.supergiantgames.com/games/hades/",
        "wiki_url": "https://hades.fandom.com/wiki/Hades_Wiki",
        "community_url": "https://www.reddit.com/r/HadesTheGame/",
        "priorities": [
            "Build around one damage engine instead of taking random boons.",
            "Mirror upgrades are as important as mechanical execution.",
            "Practice one weapon aspect deeply before switching constantly.",
        ],
    },
    {
        "slug": "red-dead-redemption-2",
        "title": "Red Dead Redemption 2",
        "description": "Narrative open-world western with immersive systems, hunting and slow-burn exploration.",
        "image_url": "assets/images/red-dead-redemption-2.jpg",
        "genre": "Action Adventure",
        "difficulty": "Easy / Medium",
        "studio": "Rockstar Games",
        "release_year": 2018,
        "platforms": ["PC", "PS4", "Xbox One"],
        "official_url": "https://www.rockstargames.com/reddeadredemption2",
        "wiki_url": "https://reddead.fandom.com/wiki/Red_Dead_Redemption_2",
        "community_url": "https://www.reddit.com/r/reddeadredemption/",
        "priorities": [
            "Camp upgrades and satchel progression improve free roam quality dramatically.",
            "Treat side activities as part of the game, not just optional filler.",
            "Dead Eye upgrades help more than weapon shopping in early chapters.",
        ],
    },
    {
        "slug": "god-of-war-ragnarok",
        "title": "God of War Ragnarok",
        "description": "Story-driven action adventure focused on reactive combat, builds and cinematic boss encounters.",
        "image_url": "assets/images/god-of-war-ragnarok.jpg",
        "genre": "Action Adventure",
        "difficulty": "Medium",
        "studio": "Santa Monica Studio",
        "release_year": 2022,
        "platforms": ["PS5", "PS4", "PC"],
        "official_url": "https://www.playstation.com/en-us/games/god-of-war-ragnarok/",
        "wiki_url": "https://godofwar.fandom.com/wiki/God_of_War_Ragnar%C3%B6k",
        "community_url": "https://www.reddit.com/r/GodofWar/",
        "priorities": [
            "Use runic attacks for control windows instead of only burst damage.",
            "Upgrade armor sets with a build goal in mind.",
            "Companion arrows can set up safer damage than overcommitting to melee.",
        ],
    },
    {
        "slug": "hollow-knight",
        "title": "Hollow Knight",
        "description": "Atmospheric metroidvania focused on exploration, precision movement and patient boss learning.",
        "image_url": "assets/images/hollow-knight.jpg",
        "genre": "Platformer",
        "difficulty": "Medium / Hard",
        "studio": "Team Cherry",
        "release_year": 2017,
        "platforms": ["PC", "Switch", "PS4"],
        "official_url": "https://www.hollowknight.com/",
        "wiki_url": "https://hollowknight.fandom.com/wiki/Hollow_Knight_Wiki",
        "community_url": "https://www.reddit.com/r/HollowKnight/",
        "priorities": [
            "Buy map tools early to reduce unnecessary backtracking.",
            "Charm loadouts matter more than a brute-force approach.",
            "Movement upgrades are the real progression gates-hunt them first.",
        ],
    },
    {
        "slug": "minecraft",
        "title": "Minecraft",
        "description": "Sandbox survival game built around creativity, resource loops and open-ended progression.",
        "image_url": "assets/images/minecraft.jpg",
        "genre": "Sandbox",
        "difficulty": "Easy",
        "studio": "Mojang Studios",
        "release_year": 2011,
        "platforms": ["PC", "PS5", "Xbox Series X|S", "Switch"],
        "official_url": "https://www.minecraft.net/",
        "wiki_url": "https://minecraft.wiki/",
        "community_url": "https://www.reddit.com/r/Minecraft/",
        "priorities": [
            "Establish food and shelter before pushing exploration too far.",
            "Early iron tools and shield timing make survival dramatically easier.",
            "Automate repetitive resources as soon as you understand the loop.",
        ],
    },
    {
        "slug": "valorant",
        "title": "VALORANT",
        "description": "Tactical hero shooter focused on crosshair discipline, utility usage and team communication.",
        "image_url": "assets/images/valorant.jpg",
        "genre": "Shooter",
        "difficulty": "Hard",
        "studio": "Riot Games",
        "release_year": 2020,
        "platforms": ["PC"],
        "official_url": "https://playvalorant.com/",
        "wiki_url": "https://valorant.fandom.com/wiki/VALORANT_Wiki",
        "community_url": "https://www.reddit.com/r/VALORANT/",
        "priorities": [
            "Crosshair placement creates more consistency than aim training alone.",
            "Learn core utility lineups only after mastering default timings.",
            "Communication quality decides more rounds than flashy mechanics.",
        ],
    },
    {
        "slug": "league-of-legends",
        "title": "League of Legends",
        "description": "Competitive MOBA built around macro decisions, champion mastery and objective control.",
        "image_url": "assets/images/league-of-legends.jpg",
        "genre": "Strategy",
        "difficulty": "Hard",
        "studio": "Riot Games",
        "release_year": 2009,
        "platforms": ["PC"],
        "official_url": "https://www.leagueoflegends.com/",
        "wiki_url": "https://wiki.leagueoflegends.com/en-us/",
        "community_url": "https://www.reddit.com/r/leagueoflegends/",
        "priorities": [
            "Limit champion pool size if you want reliable improvement.",
            "Wave control and objective timing decide games more than lane kills.",
            "Track summoner spells and jungle pathing to reduce randomness.",
        ],
    },
    {
        "slug": "counter-strike-2",
        "title": "Counter-Strike 2",
        "description": "Competitive tactical shooter from Valve with utility depth, economy management and map control.",
        "image_url": "assets/images/counter-strike-2.jpg",
        "genre": "Shooter",
        "difficulty": "Hard",
        "studio": "Valve",
        "release_year": 2023,
        "platforms": ["PC"],
        "official_url": "https://www.counter-strike.net/cs2",
        "wiki_url": "https://liquipedia.net/counterstrike/Counter-Strike_2",
        "community_url": "https://www.reddit.com/r/GlobalOffensive/",
        "priorities": [
            "Good economy calls save more rounds than unnecessary force buys.",
            "Utility timing creates cleaner site hits than raw entry confidence.",
            "Learn one CT setup and one T default per map before expanding.",
        ],
    },
    {
        "slug": "dota-2",
        "title": "Dota 2",
        "description": "Complex strategic MOBA with item spikes, timing windows and huge macro depth.",
        "image_url": "assets/images/dota-2.jpg",
        "genre": "Strategy",
        "difficulty": "Hard",
        "studio": "Valve",
        "release_year": 2013,
        "platforms": ["PC"],
        "official_url": "https://www.dota2.com/",
        "wiki_url": "https://liquipedia.net/dota2/Main_Page",
        "community_url": "https://www.reddit.com/r/DotA2/",
        "priorities": [
            "Understand lane equilibrium and support rotations before advanced item theory.",
            "Teamfight timing and objective conversion matter more than highlight kills.",
            "Hero mastery is worth more than blind meta chasing in most brackets.",
        ],
    },
    {
        "slug": "gta-v",
        "title": "Grand Theft Auto V",
        "description": "Open-world action game with sandbox missions, driving freedom and dense urban exploration.",
        "image_url": "assets/images/gta-v.jpg",
        "genre": "Action Adventure",
        "difficulty": "Easy / Medium",
        "studio": "Rockstar Games",
        "release_year": 2015,
        "platforms": ["PC", "PS5", "Xbox Series X|S"],
        "official_url": "https://www.rockstargames.com/gta-v",
        "wiki_url": "https://gta.fandom.com/wiki/Grand_Theft_Auto_V",
        "community_url": "https://www.reddit.com/r/GTAV/",
        "priorities": [
            "Use character abilities in missions because they are built around them.",
            "Money comes easier if you sequence side activities smartly.",
            "Treat map familiarity as a gameplay advantage, not just visual flavor.",
        ],
    },
    {
        "slug": "sekiro-shadows-die-twice",
        "title": "Sekiro: Shadows Die Twice",
        "description": "Precision action adventure focused on deflect timing, posture pressure and aggression.",
        "image_url": "assets/images/sekiro.jpg",
        "genre": "Action",
        "difficulty": "Hard",
        "studio": "FromSoftware",
        "release_year": 2019,
        "platforms": ["PC", "PS4", "Xbox One"],
        "official_url": "https://www.sekirothegame.com/",
        "wiki_url": "https://sekiroshadowsdietwice.wiki.fextralife.com/",
        "community_url": "https://www.reddit.com/r/Sekiro/",
        "priorities": [
            "Deflect consistency matters more than dodge habits from other games.",
            "Use prosthetic tools for matchup advantages, not as a main crutch.",
            "Pressure posture instead of relying only on health chip damage.",
        ],
    },
    {
        "slug": "stardew-valley",
        "title": "Stardew Valley",
        "description": "Relaxed farming RPG centered on town routines, seasonal planning and long-term upgrades.",
        "image_url": "assets/images/stardew-valley.jpg",
        "genre": "Simulation",
        "difficulty": "Easy",
        "studio": "ConcernedApe",
        "release_year": 2016,
        "platforms": ["PC", "Switch", "PS4"],
        "official_url": "https://www.stardewvalley.net/",
        "wiki_url": "https://stardewvalleywiki.com/Stardew_Valley_Wiki",
        "community_url": "https://www.reddit.com/r/StardewValley/",
        "priorities": [
            "Plan crop cycles around season transitions to avoid wasted seeds.",
            "Upgrade tools and backpack space before splurging on cosmetics.",
            "Relationship events often unlock useful recipes and game pacing.",
        ],
    },
    {
        "slug": "terraria",
        "title": "Terraria",
        "description": "2D sandbox adventure with crafting loops, boss progression and build experimentation.",
        "image_url": "assets/images/terraria.jpg",
        "genre": "Sandbox",
        "difficulty": "Medium",
        "studio": "Re-Logic",
        "release_year": 2011,
        "platforms": ["PC", "Switch", "PS5", "Xbox Series X|S"],
        "official_url": "https://terraria.org/",
        "wiki_url": "https://terraria.wiki.gg/wiki/Terraria_Wiki",
        "community_url": "https://www.reddit.com/r/Terraria/",
        "priorities": [
            "Housing and NPC unlocks accelerate progression in every stage.",
            "Mobility accessories solve more problems than raw defense early on.",
            "Boss sequencing is smoother if you gather class-specific gear first.",
        ],
    },
    {
        "slug": "apex-legends",
        "title": "Apex Legends",
        "description": "Squad-based battle royale hero shooter with fast rotations and legend-driven teamplay.",
        "image_url": "assets/images/apex-legends.jpg",
        "genre": "Shooter",
        "difficulty": "Medium",
        "studio": "Respawn Entertainment",
        "release_year": 2019,
        "platforms": ["PC", "PS5", "Xbox Series X|S"],
        "official_url": "https://www.ea.com/games/apex-legends",
        "wiki_url": "https://apexlegends.wiki.gg/wiki/Apex_Legends_Wiki",
        "community_url": "https://www.reddit.com/r/apexlegends/",
        "priorities": [
            "Clean rotations and positioning beat greedy late looting.",
            "Play around legend synergy, not isolated individual picks.",
            "Winning fights quickly matters because third parties are inevitable.",
        ],
    },
    {
        "slug": "control",
        "title": "Control",
        "description": "Atmospheric action adventure with telekinetic combat and layered environmental storytelling.",
        "image_url": "https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/870780/capsule_616x353.jpg",
        "genre": "Action Adventure",
        "difficulty": "Medium",
        "studio": "Remedy Entertainment",
        "release_year": 2019,
        "platforms": ["PC", "PS5", "Xbox Series X|S"],
        "official_url": "https://controlgame.com/",
        "wiki_url": "https://control.fandom.com/wiki/Control_Wiki",
        "community_url": "https://www.reddit.com/r/controlgame/",
        "priorities": [
            "Launch and mobility upgrades pay off faster than pure weapon investment.",
            "Read documents and side rooms because they explain both lore and progression.",
            "Aggressive movement is safer than static cover in many arenas.",
        ],
    },
    {
        "slug": "dead-cells",
        "title": "Dead Cells",
        "description": "Fast action platformer with route planning, unlocks and strong emphasis on run consistency.",
        "image_url": "https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/588650/capsule_616x353.jpg",
        "genre": "Platformer",
        "difficulty": "Medium / Hard",
        "studio": "Motion Twin",
        "release_year": 2018,
        "platforms": ["PC", "Switch", "PS5"],
        "official_url": "https://dead-cells.com/",
        "wiki_url": "https://deadcells.wiki.gg/wiki/Dead_Cells_Wiki",
        "community_url": "https://www.reddit.com/r/deadcells/",
        "priorities": [
            "Build around one damage color instead of splitting upgrades randomly.",
            "Route knowledge matters almost as much as combat execution.",
            "Use mutation swaps between biomes to adapt to bosses.",
        ],
    },
    {
        "slug": "monster-hunter-world",
        "title": "Monster Hunter: World",
        "description": "Large-scale hunting action game based on weapon mastery, preparation and resource management.",
        "image_url": "https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/582010/capsule_616x353.jpg",
        "genre": "Action",
        "difficulty": "Medium",
        "studio": "Capcom",
        "release_year": 2018,
        "platforms": ["PC", "PS4", "Xbox One"],
        "official_url": "https://www.monsterhunter.com/world/",
        "wiki_url": "https://monsterhunter.fandom.com/wiki/Monster_Hunter:_World",
        "community_url": "https://www.reddit.com/r/MonsterHunter/",
        "priorities": [
            "Weapon mastery is more valuable than switching constantly.",
            "Items, traps and meal buffs are part of your actual combat power.",
            "Armor skills shape builds more than raw defense values.",
        ],
    },
    {
        "slug": "resident-evil-4",
        "title": "Resident Evil 4",
        "description": "Modern survival horror with resource pressure, strong pacing and satisfying combat routing.",
        "image_url": "https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/2050650/capsule_616x353.jpg",
        "genre": "Horror",
        "difficulty": "Medium",
        "studio": "Capcom",
        "release_year": 2023,
        "platforms": ["PC", "PS5", "Xbox Series X|S"],
        "official_url": "https://www.residentevil.com/re4/en-us/",
        "wiki_url": "https://residentevil.fandom.com/wiki/Resident_Evil_4_(2023_game)",
        "community_url": "https://www.reddit.com/r/residentevil/",
        "priorities": [
            "Inventory upgrades and ammo discipline smooth out every chapter.",
            "Crowd control positioning is more important than flashy headshots.",
            "Know when to sell, save or upgrade key weapons.",
        ],
    },
    {
        "slug": "doom-eternal",
        "title": "Doom Eternal",
        "description": "High-speed combat shooter built around movement, target priority and constant resource cycling.",
        "image_url": "https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/782330/capsule_616x353.jpg",
        "genre": "Shooter",
        "difficulty": "Medium / Hard",
        "studio": "id Software",
        "release_year": 2020,
        "platforms": ["PC", "PS5", "Xbox Series X|S"],
        "official_url": "https://slayersclub.bethesda.net/en-US/game/doom-eternal",
        "wiki_url": "https://doom.fandom.com/wiki/Doom_Eternal",
        "community_url": "https://www.reddit.com/r/Doom/",
        "priorities": [
            "Never stand still-mobility is survival.",
            "Weak point breaks and chainsaw routing keep arenas under control.",
            "Treat every weapon as part of one resource loop.",
        ],
    },
    {
        "slug": "warframe",
        "title": "Warframe",
        "description": "Online looter shooter built around mobility, build experimentation and constant progression systems.",
        "image_url": "https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/230410/capsule_616x353.jpg",
        "genre": "Shooter",
        "difficulty": "Medium",
        "studio": "Digital Extremes",
        "release_year": 2013,
        "platforms": ["PC", "PS5", "Xbox Series X|S", "Switch"],
        "official_url": "https://www.warframe.com/",
        "wiki_url": "https://warframe.fandom.com/wiki/WARFRAME_Wiki",
        "community_url": "https://www.reddit.com/r/Warframe/",
        "priorities": [
            "Learn a few strong mods before chasing every new frame.",
            "Resource and relic farming is easier with route planning.",
            "Mobility and survivability tools matter as much as raw DPS.",
        ],
    },
]

BUILD_FOCUS_GAMES = {
    "elden-ring", "cyberpunk-2077", "baldurs-gate-3", "black-myth-wukong",
    "helldivers-2", "valorant", "league-of-legends", "counter-strike-2",
    "monster-hunter-world", "warframe",
}
PENDING_GAMES = {
    "elden-ring", "cyberpunk-2077", "baldurs-gate-3", "helldivers-2",
    "valorant", "counter-strike-2", "resident-evil-4", "warframe",
}
CODE_GAMES = {
    "helldivers-2", "minecraft", "apex-legends", "valorant", "warframe", "league-of-legends",
}
COUPON_GAMES = {
    "cyberpunk-2077", "the-witcher-3", "god-of-war-ragnarok", "resident-evil-4", "doom-eternal",
}


def create_tables(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")

    cur.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'admin'))
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL,
            image_url TEXT NOT NULL,
            genre TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            studio TEXT NOT NULL,
            release_year INTEGER NOT NULL,
            platforms TEXT NOT NULL,
            official_url TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            summary TEXT,
            content TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('pending', 'approved', 'rejected')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE game_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
        )
        """
    )


def seed_users(cur):
    cur.executemany(
        "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
        [(u["username"], u["email"], generate_password_hash(u["password"]), u["role"]) for u in USERS],
    )


def seed_categories(cur):
    cur.executemany("INSERT INTO categories (name) VALUES (?)", [(c,) for c in CATEGORIES])


def seed_games(cur):
    cur.executemany(
        """
        INSERT INTO games (title, slug, description, image_url, genre, difficulty, studio, release_year, platforms, official_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                g["title"], g["slug"], g["description"], g["image_url"], g["genre"], g["difficulty"],
                g["studio"], g["release_year"], json.dumps(g["platforms"]), g["official_url"],
            )
            for g in GAMES
        ],
    )


def build_article_content(game, article_type):
    p1, p2, p3 = game["priorities"]
    if article_type == "Guide":
        title = f"{game['title']} Beginner Guide"
        summary = f"Fast entry guide for {game['title']}, focused on the first hours and clean progression."
        content = (
            f"{game['title']} rewards players who understand its core loop early. "
            f"Start by focusing on {p1.lower()} "
            f"Then move into {p2.lower()} "
            f"Finally, remember that {p3.lower()} "
            f"This guide is meant as a practical starting route rather than an exhaustive walkthrough."
        )
    elif article_type == "Review":
        title = f"{game['title']} Community Review"
        summary = f"A short review of {game['title']} covering pacing, combat feel and replay value."
        content = (
            f"{game['title']} stands out because it combines {game['genre'].lower()} ideas with a strong identity from {game['studio']}. "
            f"The experience is especially successful when the player embraces its intended rhythm instead of forcing shortcuts. "
            f"Across its strongest moments, the title delivers a polished loop, memorable encounters and clear reasons to keep playing."
        )
    elif article_type == "Build":
        title = f"{game['title']} Build Ideas"
        summary = f"Reliable build directions for {game['title']} depending on how you want to play."
        content = (
            f"The most stable builds in {game['title']} come from committing to one plan instead of hybrid confusion. "
            f"Players who want consistency should center their setup around one damage profile, one defensive solution and one utility layer. "
            f"This article highlights practical priorities so the build stays effective through mid-game and late-game content."
        )
    elif article_type == "Tips & Tricks":
        title = f"{game['title']} Tips & Tricks"
        summary = f"Useful short tips that save time and help avoid common mistakes in {game['title']}."
        content = (
            f"If you want a smoother experience in {game['title']}, avoid overcomplicating early decisions. "
            f"Use systems the game clearly rewards, revisit difficult content later and build habits around consistency rather than brute force. "
            f"These tips are aimed at players who want cleaner progression and fewer wasted resources."
        )
    elif article_type == "Codes":
        title = f"{game['title']} Active Codes & Rewards"
        summary = f"Tracking currently useful reward codes and bonus content for {game['title']}."
        content = (
            f"This entry collects code-related rewards connected to {game['title']}. "
            f"Always verify expiration windows and platform restrictions before redeeming. "
            f"When codes are unavailable, keep the official channels and community pages in view because limited-time rewards rotate quickly."
        )
    else:
        title = f"{game['title']} Discount Watch"
        summary = f"Storewatch notes and discount timing ideas for {game['title']}."
        content = (
            f"This entry tracks discount opportunities for {game['title']}. "
            f"For better value, compare official publisher sales with storefront bundles and seasonal events. "
            f"Wishlist alerts and platform-specific campaigns often create the best buy window."
        )
    return title, summary, content


def seed_sources_and_articles(cur):
    category_ids = {name: cid for cid, name in cur.execute("SELECT id, name FROM categories")}
    user_ids = {name: uid for uid, name in cur.execute("SELECT id, username FROM users")}
    game_rows = {slug: gid for gid, slug in cur.execute("SELECT id, slug FROM games")}

    for game in GAMES:
        gid = game_rows[game["slug"]]

        cur.executemany(
            "INSERT INTO game_sources (game_id, title, url) VALUES (?, ?, ?)",
            [
                (gid, f"{game['title']} Official Site", game["official_url"]),
                (gid, f"{game['title']} Wiki", game["wiki_url"]),
                (gid, f"{game['title']} Community", game["community_url"]),
            ],
        )

        approved_types = ["Guide", "Review", "Tips & Tricks"]
        if game["slug"] in BUILD_FOCUS_GAMES:
            approved_types.append("Build")
        if game["slug"] in CODE_GAMES:
            approved_types.append("Codes")
        if game["slug"] in COUPON_GAMES:
            approved_types.append("Discount Coupons")

        for idx, article_type in enumerate(approved_types):
            author = "Giku" if idx % 2 == 0 else "Alex"
            title, summary, content = build_article_content(game, article_type)
            cur.execute(
                """
                INSERT INTO articles (game_id, category_id, user_id, title, summary, content, status)
                VALUES (?, ?, ?, ?, ?, ?, 'approved')
                """,
                (gid, category_ids[article_type], user_ids[author], title, summary, content),
            )
            article_id = cur.lastrowid
            cur.execute(
                "INSERT INTO sources (article_id, title, url) VALUES (?, ?, ?)",
                (article_id, f"{game['title']} main source", game["official_url"]),
            )

        if game["slug"] in PENDING_GAMES:
            title = f"{game['title']} Pending Community Draft"
            summary = f"Pending user draft for {game['title']} waiting for moderator review."
            content = (
                f"This draft was submitted by a community member and is still pending review. "
                f"It focuses on practical advice for {game['title']} and will become public after moderation."
            )
            cur.execute(
                """
                INSERT INTO articles (game_id, category_id, user_id, title, summary, content, status)
                VALUES (?, ?, ?, ?, ?, ?, 'pending')
                """,
                (gid, category_ids["Guide"], user_ids["Bianca"], title, summary, content),
            )
            article_id = cur.lastrowid
            cur.execute(
                "INSERT INTO sources (article_id, title, url) VALUES (?, ?, ?)",
                (article_id, f"{game['title']} pending source", game["wiki_url"]),
            )

    elden_gid = game_rows.get("elden-ring")
    if elden_gid:
        cur.execute(
            """
            INSERT INTO articles (game_id, category_id, user_id, title, summary, content, status)
            VALUES (?, ?, ?, ?, ?, ?, 'approved')
            """,
            (
                elden_gid,
                category_ids["Build"],
                user_ids["Alex"],
                "Elden Ring Endgame Build Routing",
                "Extra approved entry for endgame routing and stat breakpoints.",
                "This endgame routing note adds one extra approved blueprint focused on stat breakpoints, talisman swaps and late-game boss consistency.",
            ),
        )
        article_id = cur.lastrowid
        cur.execute(
            "INSERT INTO sources (article_id, title, url) VALUES (?, ?, ?)",
            (article_id, "Elden Ring extra source", "https://eldenring.wiki.fextralife.com/"),
        )


def rebuild_database() -> None:
    if DB_NAME.exists():
        DB_NAME.unlink()

    conn = sqlite3.connect(DB_NAME)
    create_tables(conn)
    cur = conn.cursor()
    seed_users(cur)
    seed_categories(cur)
    seed_games(cur)
    seed_sources_and_articles(cur)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    rebuild_database()
    print(f"{DB_NAME.name} created successfully.")
