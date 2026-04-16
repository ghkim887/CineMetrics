import random
import os
from datetime import datetime, timedelta

random.seed(42)


def escape_sql(s):
    """Escape single quotes for SQL strings."""
    if s is None:
        return "NULL"
    return str(s).replace("'", "''")


# =============================================================================
# NAME POOLS (replaces faker dependency)
# =============================================================================
FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael",
    "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan",
    "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Daniel",
    "Lisa", "Matthew", "Nancy", "Anthony", "Betty", "Mark", "Margaret",
    "Donald", "Sandra", "Steven", "Ashley", "Andrew", "Dorothy", "Paul",
    "Kimberly", "Joshua", "Emily", "Kenneth", "Donna", "Kevin", "Michelle",
    "Brian", "Carol", "George", "Amanda", "Timothy", "Melissa", "Ronald",
    "Deborah",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts",
]

EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "protonmail.com",
    "icloud.com", "mail.com", "aol.com", "fastmail.com", "zoho.com",
]


# =============================================================================
# GENRE DATA (15 genres)
# =============================================================================
GENRES = [
    "Action", "Comedy", "Drama", "Horror", "Sci-Fi",
    "Romance", "Thriller", "Documentary", "Animation", "Fantasy",
    "Mystery", "Adventure", "Crime", "Musical", "Western",
]

# =============================================================================
# MOVIE DATA (40 hardcoded real movies)
# =============================================================================
MOVIES = [
    {
        "title": "Inception",
        "release_year": 2010,
        "runtime_minutes": 148,
        "synopsis": "A skilled thief who steals secrets from deep within the subconscious is offered a chance to have his criminal record erased if he can successfully perform inception.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Sci-Fi", "Action", "Thriller", "Mystery"],
    },
    {
        "title": "Parasite",
        "release_year": 2019,
        "runtime_minutes": 132,
        "synopsis": "A poor family schemes to infiltrate a wealthy household by posing as unrelated skilled workers. Class tension escalates with devastating consequences.",
        "country_of_origin": "South Korea",
        "language": "Korean",
        "genres": ["Thriller", "Drama", "Comedy", "Mystery"],
    },
    {
        "title": "The Dark Knight",
        "release_year": 2008,
        "runtime_minutes": 152,
        "synopsis": "Batman faces the Joker, a criminal mastermind who plunges Gotham City into anarchy and forces the Dark Knight closer to crossing the line between hero and vigilante.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Action", "Crime", "Drama", "Thriller"],
    },
    {
        "title": "Spirited Away",
        "release_year": 2001,
        "runtime_minutes": 125,
        "synopsis": "A young girl becomes trapped in a mysterious spirit world and must work in a bathhouse to free herself and her parents.",
        "country_of_origin": "Japan",
        "language": "Japanese",
        "genres": ["Animation", "Fantasy", "Adventure", "Drama"],
    },
    {
        "title": "The Godfather",
        "release_year": 1972,
        "runtime_minutes": 175,
        "synopsis": "The aging patriarch of an organized crime dynasty transfers control to his reluctant youngest son, who transforms into a ruthless mafia boss.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Crime", "Drama", "Thriller"],
    },
    {
        "title": "Pulp Fiction",
        "release_year": 1994,
        "runtime_minutes": 154,
        "synopsis": "Interlocking tales of crime and redemption in Los Angeles unfold through the lives of two hitmen, a boxer, a gangster, and his wife.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Crime", "Drama", "Thriller", "Mystery"],
    },
    {
        "title": "The Shawshank Redemption",
        "release_year": 1994,
        "runtime_minutes": 142,
        "synopsis": "A banker sentenced to life in prison forms an unlikely friendship and orchestrates a decades-long plan to escape.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Drama", "Crime", "Mystery"],
    },
    {
        "title": "Interstellar",
        "release_year": 2014,
        "runtime_minutes": 169,
        "synopsis": "A team of astronauts travels through a wormhole near Saturn in search of a new home for humanity as Earth faces ecological collapse.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Sci-Fi", "Adventure", "Drama", "Mystery"],
    },
    {
        "title": "The Matrix",
        "release_year": 1999,
        "runtime_minutes": 136,
        "synopsis": "A computer hacker discovers that reality is a simulated world controlled by machines and joins a rebellion to free humanity.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Sci-Fi", "Action", "Thriller"],
    },
    {
        "title": "Schindler's List",
        "release_year": 1993,
        "runtime_minutes": 195,
        "synopsis": "A German businessman saves over a thousand Jewish refugees during the Holocaust by employing them in his factories.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Drama", "Mystery", "Documentary"],
    },
    {
        "title": "Forrest Gump",
        "release_year": 1994,
        "runtime_minutes": 142,
        "synopsis": "A simple man with a low IQ unwittingly influences several historic events in 20th century America while searching for his childhood sweetheart.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Drama", "Romance", "Comedy", "Adventure"],
    },
    {
        "title": "Fight Club",
        "release_year": 1999,
        "runtime_minutes": 139,
        "synopsis": "An insomniac office worker and a soap salesman form an underground fight club that evolves into something much more dangerous.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Drama", "Thriller", "Mystery"],
    },
    {
        "title": "The Lord of the Rings: The Fellowship of the Ring",
        "release_year": 2001,
        "runtime_minutes": 178,
        "synopsis": "A hobbit and a fellowship of heroes embark on a quest to destroy a powerful ring and save Middle-earth from the Dark Lord Sauron.",
        "country_of_origin": "New Zealand",
        "language": "English",
        "genres": ["Fantasy", "Adventure", "Action", "Drama"],
    },
    {
        "title": "Goodfellas",
        "release_year": 1990,
        "runtime_minutes": 146,
        "synopsis": "The rise and fall of a mob associate and his friends in the Italian-American crime syndicate spanning three decades.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Crime", "Drama", "Thriller"],
    },
    {
        "title": "The Silence of the Lambs",
        "release_year": 1991,
        "runtime_minutes": 118,
        "synopsis": "A young FBI trainee seeks the help of an imprisoned cannibalistic serial killer to catch another serial killer on the loose.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Thriller", "Crime", "Horror", "Drama"],
    },
    {
        "title": "Gladiator",
        "release_year": 2000,
        "runtime_minutes": 155,
        "synopsis": "A betrayed Roman general is reduced to slavery and rises through the ranks of gladiatorial combat to avenge the murder of his family.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Action", "Adventure", "Drama", "Thriller"],
    },
    {
        "title": "Amelie",
        "release_year": 2001,
        "runtime_minutes": 122,
        "synopsis": "A shy Parisian waitress decides to change the lives of those around her for the better while struggling with her own isolation.",
        "country_of_origin": "France",
        "language": "French",
        "genres": ["Romance", "Comedy", "Fantasy"],
    },
    {
        "title": "City of God",
        "release_year": 2002,
        "runtime_minutes": 130,
        "synopsis": "Two boys growing up in a violent neighborhood of Rio de Janeiro take different paths: one becomes a photographer, the other a drug dealer.",
        "country_of_origin": "Brazil",
        "language": "Portuguese",
        "genres": ["Crime", "Drama", "Thriller"],
    },
    {
        "title": "The Grand Budapest Hotel",
        "release_year": 2014,
        "runtime_minutes": 99,
        "synopsis": "A legendary concierge at a famous European hotel and his trusted lobby boy are framed for murder and must prove their innocence.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Comedy", "Adventure", "Crime"],
    },
    {
        "title": "Mad Max: Fury Road",
        "release_year": 2015,
        "runtime_minutes": 120,
        "synopsis": "In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler with the help of a drifter and a group of female prisoners.",
        "country_of_origin": "Australia",
        "language": "English",
        "genres": ["Action", "Adventure", "Sci-Fi"],
    },
    {
        "title": "Whiplash",
        "release_year": 2014,
        "runtime_minutes": 106,
        "synopsis": "A young jazz drummer enrolls at a cutthroat conservatory where an abusive instructor pushes him beyond his limits.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Drama", "Musical", "Thriller"],
    },
    {
        "title": "Get Out",
        "release_year": 2017,
        "runtime_minutes": 104,
        "synopsis": "A young Black man visits his white girlfriend's family estate and uncovers a disturbing secret about the community.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Horror", "Thriller", "Mystery"],
    },
    {
        "title": "Coco",
        "release_year": 2017,
        "runtime_minutes": 105,
        "synopsis": "A boy who dreams of being a musician journeys to the Land of the Dead to find his great-great-grandfather and uncover his family history.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Animation", "Fantasy", "Musical"],
    },
    {
        "title": "Pan's Labyrinth",
        "release_year": 2006,
        "runtime_minutes": 118,
        "synopsis": "In post-Civil War Spain, a young girl escapes into a dark fairy tale world while her stepfather hunts anti-fascist rebels.",
        "country_of_origin": "Mexico",
        "language": "Spanish",
        "genres": ["Fantasy", "Drama", "Horror"],
    },
    {
        "title": "No Country for Old Men",
        "release_year": 2007,
        "runtime_minutes": 122,
        "synopsis": "A hunter stumbles upon a drug deal gone wrong and takes the money, setting off a violent chain of events involving a relentless killer.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Thriller", "Crime", "Western"],
    },
    {
        "title": "The Social Network",
        "release_year": 2010,
        "runtime_minutes": 120,
        "synopsis": "The founding of Facebook leads to personal and legal complications for its creator and his former friends.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Drama", "Documentary", "Mystery"],
    },
    {
        "title": "Blade Runner 2049",
        "release_year": 2017,
        "runtime_minutes": 164,
        "synopsis": "A young blade runner uncovers a long-buried secret that leads him to track down a former blade runner who has been missing for decades.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Sci-Fi", "Thriller", "Mystery"],
    },
    {
        "title": "Everything Everywhere All at Once",
        "release_year": 2022,
        "runtime_minutes": 139,
        "synopsis": "A middle-aged Chinese immigrant is swept up in an insane adventure where she must connect with parallel universe versions of herself to save the multiverse.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Sci-Fi", "Action", "Comedy"],
    },
    {
        "title": "La La Land",
        "release_year": 2016,
        "runtime_minutes": 128,
        "synopsis": "A jazz pianist and an aspiring actress fall in love while pursuing their dreams in Los Angeles.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Romance", "Musical", "Drama"],
    },
    {
        "title": "The Departed",
        "release_year": 2006,
        "runtime_minutes": 151,
        "synopsis": "An undercover cop and a mole in the police attempt to identify each other while infiltrating an Irish gang in Boston.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Crime", "Thriller", "Drama"],
    },
    {
        "title": "Alien",
        "release_year": 1979,
        "runtime_minutes": 117,
        "synopsis": "The crew of a commercial spacecraft encounters a deadly extraterrestrial creature after investigating a distress signal on an uncharted planet.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Sci-Fi", "Horror", "Thriller"],
    },
    {
        "title": "Django Unchained",
        "release_year": 2012,
        "runtime_minutes": 165,
        "synopsis": "A freed slave teams up with a German bounty hunter to rescue his wife from a brutal plantation owner in the antebellum South.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Western", "Drama", "Action"],
    },
    {
        "title": "The Truman Show",
        "release_year": 1998,
        "runtime_minutes": 103,
        "synopsis": "A man discovers his entire life is a constructed reality television show broadcast to millions of viewers worldwide.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Drama", "Comedy", "Sci-Fi", "Mystery"],
    },
    {
        "title": "Oldboy",
        "release_year": 2003,
        "runtime_minutes": 120,
        "synopsis": "A man imprisoned for 15 years without explanation is suddenly released and given five days to find his captor.",
        "country_of_origin": "South Korea",
        "language": "Korean",
        "genres": ["Thriller", "Mystery", "Action"],
    },
    {
        "title": "WALL-E",
        "release_year": 2008,
        "runtime_minutes": 98,
        "synopsis": "A lonely waste-collecting robot on a deserted Earth meets a sleek reconnaissance robot and follows her across the galaxy.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Animation", "Sci-Fi", "Adventure"],
    },
    {
        "title": "The Prestige",
        "release_year": 2006,
        "runtime_minutes": 130,
        "synopsis": "Two rival magicians in Victorian-era London engage in a bitter competition, each trying to outdo the other with increasingly dangerous tricks.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Mystery", "Thriller", "Drama"],
    },
    {
        "title": "Life Is Beautiful",
        "release_year": 1997,
        "runtime_minutes": 116,
        "synopsis": "An Italian Jewish man uses humor and imagination to shield his young son from the horrors of a Nazi concentration camp.",
        "country_of_origin": "Italy",
        "language": "Italian",
        "genres": ["Drama", "Comedy", "Romance"],
    },
    {
        "title": "Moonlight",
        "release_year": 2016,
        "runtime_minutes": 111,
        "synopsis": "A young Black man growing up in Miami grapples with his identity and sexuality across three defining chapters of his life.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Drama", "Romance", "Documentary"],
    },
    {
        "title": "Jurassic Park",
        "release_year": 1993,
        "runtime_minutes": 127,
        "synopsis": "A theme park showcasing genetically engineered dinosaurs turns deadly when the creatures break free during a security failure.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Sci-Fi", "Adventure", "Action"],
    },
    {
        "title": "The Shining",
        "release_year": 1980,
        "runtime_minutes": 146,
        "synopsis": "A family heads to an isolated hotel for the winter where a sinister presence drives the father into violent madness.",
        "country_of_origin": "USA",
        "language": "English",
        "genres": ["Horror", "Thriller", "Mystery"],
    },
]

# =============================================================================
# USER ROLES
# =============================================================================
ROLES = ["casual", "enthusiast", "admin", "analyst"]
USERS_PER_ROLE = 10

# =============================================================================
# HELPER DATA
# =============================================================================
WATCHLIST_NAMES = [
    "Weekend Picks", "Award Winners", "Must Watch", "Classics Collection",
    "Sci-Fi Marathon", "Date Night", "Rainy Day Movies", "Top Rated",
    "Foreign Films", "Hidden Gems", "Action Favorites", "Feel-Good Movies",
    "Mind Benders", "Family Movie Night", "Cult Classics", "Director Spotlight",
    "Oscar Nominees", "Summer Blockbusters", "Horror Night", "Comedy Gold",
    "Drama Essentials", "Animated Gems", "Thriller Picks", "Romance Collection",
    "Documentary Queue", "Binge List", "Staff Picks", "New Releases",
    "All-Time Favorites", "Watch Later", "Trending Now", "Critics Choice",
    "Underrated Picks", "Genre Mix", "International Cinema", "Quick Watches",
    "Epic Sagas", "Film School Essentials", "Nostalgia Trip", "Dark and Gritty",
    "Guilty Pleasures", "Cerebral Cinema", "Visual Masterpieces",
    "Soundtrack Stars", "Laugh Out Loud", "Tearjerkers", "Adrenaline Rush",
    "Before You Die List", "Conversation Starters", "Comfort Movies",
]

REVIEW_TITLES = [
    "An absolute masterpiece", "Completely overrated", "A must-see film",
    "Exceeded all expectations", "Good but not great", "A visual spectacle",
    "Deeply moving story", "Surprisingly entertaining", "Disappointing sequel",
    "A timeless classic", "Fantastic performances", "Boring and predictable",
    "One of the best this year", "Could have been better", "A wild ride",
    "Beautifully shot film", "Lacks depth and substance", "Highly recommended",
    "Not my cup of tea", "A gripping thriller", "Heartwarming and funny",
    "A slow burn that pays off", "Emotionally devastating", "Pure entertainment",
    "Thought-provoking cinema", "Overhyped and underwhelming", "A stunning debut",
    "Clever and original", "A perfect ending", "Too long and drawn out",
    "Edge of my seat", "A feel-good masterpiece", "Dark and atmospheric",
    "Surprisingly deep", "Simply unforgettable", "A rare gem",
    "Exceptional directing", "Falls flat halfway through", "Best film of the decade",
    "Worth every minute", "A cinematic experience", "Solid all around",
    "Intense from start to finish", "A bit overlong but still good",
    "Incredibly well-crafted", "A masterclass in storytelling",
    "Mediocre at best", "A triumphant return to form", "Hauntingly beautiful",
    "Riveting and powerful", "A mixed bag overall", "Elegant and understated",
    "One of the greats", "Perfectly cast", "A bold artistic choice",
    "Simply put: brilliant", "A refreshing take on the genre",
    "Ambitious but flawed", "Left me speechless", "A crowd-pleaser for sure",
]

REVIEW_BODY_TEMPLATES = [
    "I watched this film {time_ago} and I have to say, it {reaction}. The {element} was {quality} and the overall experience was {experience}. {recommendation}",
    "As a fan of {genre_ref} films, I found this to be {quality}. The director did a {job_quality} job with the pacing and the performances were {perf_quality}. {recommendation}",
    "This movie {reaction} in ways I didn't expect. {element_cap} alone makes it worth watching, but when combined with the {other_element}, it becomes something truly {adj}. {recommendation}",
    "I went in with {expectations} expectations and came out {feeling}. The story was {story_quality} and the cinematography was {cine_quality}. {recommendation}",
    "What can I say about this film? It {reaction} and left me {feeling}. The {element} was particularly {quality}, though I felt the {other_element} could have been {improvement}. {recommendation}",
    "{element_cap} carried this film from start to finish. While the {other_element} had its moments, it was the {element} that truly made this a {adj} viewing experience. {recommendation}",
    "I have seen this film {view_count} times now and it {repeat_reaction} with each viewing. The attention to detail in the {element} is {quality} and I always notice something new. {recommendation}",
    "From the opening scene, this film {reaction}. The {element} set the tone perfectly and the {other_element} kept me engaged throughout. A {adj} piece of cinema. {recommendation}",
]

FILL_DATA = {
    "time_ago": ["last weekend", "recently", "a while back", "for the first time last night", "on a flight recently", "with my family"],
    "reaction": ["blew me away", "left me thinking for days", "delivered exactly what I expected", "surprised me", "fell a bit flat", "exceeded my expectations", "was a rollercoaster"],
    "element": ["acting", "screenplay", "cinematography", "score", "direction", "production design", "editing", "sound design"],
    "element_cap": ["The acting", "The screenplay", "The cinematography", "The musical score", "The direction", "The production design", "The editing"],
    "other_element": ["plot", "pacing", "character development", "dialogue", "third act", "supporting cast", "visual effects", "ending"],
    "quality": ["outstanding", "remarkable", "solid", "impressive", "decent", "top-notch", "exceptional", "nuanced", "masterful"],
    "experience": ["unforgettable", "enjoyable", "worthwhile", "mixed", "satisfying", "powerful", "entertaining"],
    "recommendation": [
        "I highly recommend it to anyone.",
        "Definitely worth a watch.",
        "I would watch it again in a heartbeat.",
        "Not for everyone but give it a chance.",
        "Could have been stronger but still worth your time.",
        "A must-see for any film lover.",
        "I plan to revisit it soon.",
        "One of the best I have seen this year.",
        "I would recommend it with some reservations.",
        "Go in without expectations and enjoy the ride.",
    ],
    "genre_ref": ["action", "drama", "sci-fi", "thriller", "comedy", "horror", "fantasy", "crime", "animated", "romance"],
    "job_quality": ["fantastic", "commendable", "masterful", "decent", "great", "phenomenal", "solid", "respectable"],
    "perf_quality": ["top-tier", "believable", "award-worthy", "genuine", "captivating", "powerful", "convincing"],
    "expectations": ["high", "low", "mixed", "no", "moderate", "very high", "cautious"],
    "feeling": ["pleasantly surprised", "deeply moved", "thoroughly entertained", "a bit disappointed", "speechless", "wanting more", "satisfied"],
    "story_quality": ["compelling", "predictable but enjoyable", "layered and complex", "straightforward", "engaging", "inventive", "beautifully told"],
    "cine_quality": ["breathtaking", "stunning", "serviceable", "gorgeous", "evocative", "crisp and clean", "visually arresting"],
    "improvement": ["stronger", "more developed", "tighter", "more impactful", "better paced", "more cohesive"],
    "adj": ["remarkable", "exceptional", "memorable", "stunning", "unique", "phenomenal", "captivating", "extraordinary"],
    "view_count": ["three", "four", "two", "five", "multiple"],
    "repeat_reaction": ["gets better", "reveals new layers", "holds up remarkably well", "never gets old", "remains powerful"],
}

RECOMMENDATION_REASONS = [
    "Based on your interest in {genre} films",
    "Because you enjoyed {movie}",
    "Recommended for fans of {genre} movies",
    "Trending in the {genre} category",
    "Highly rated by viewers with similar taste",
    "Popular among {genre} enthusiasts",
    "Critics' pick in the {genre} genre",
    "Top rated this month in {genre}",
    "Similar to movies in your watchlist",
    "Curated for your viewing history",
]

FLAG_REASONS = [
    "Spoiler without warning",
    "Offensive language",
    "Spam or promotional content",
    "Harassment or personal attack",
    "Misleading information",
    "Inappropriate content",
    "Not a genuine review",
    "Contains hate speech",
    "Duplicate review",
    "Off-topic content",
]

ADMIN_ACTION_TYPES = [
    "edit_movie", "moderate_review", "ban_user", "unban_user",
    "delete_review", "approve_review", "flag_review", "edit_genre",
    "add_movie", "remove_movie", "update_user_role", "system_maintenance",
    "generate_report", "clear_flags", "send_notification",
]

ADMIN_DETAILS_TEMPLATES = {
    "edit_movie": "Updated movie details for movie_id={mid}",
    "moderate_review": "Moderated review_id={rid} - status changed to {status}",
    "ban_user": "Banned user_id={uid} for policy violation",
    "unban_user": "Reinstated user_id={uid} after review",
    "delete_review": "Deleted review_id={rid} for policy violation",
    "approve_review": "Approved review_id={rid} after moderation",
    "flag_review": "Flagged review_id={rid} for further review",
    "edit_genre": "Updated genre information for genre_id={gid}",
    "add_movie": "Added new movie to catalog: movie_id={mid}",
    "remove_movie": "Removed movie_id={mid} from active catalog",
    "update_user_role": "Changed role for user_id={uid} to {role}",
    "system_maintenance": "Performed routine system maintenance",
    "generate_report": "Generated {report_type} report",
    "clear_flags": "Cleared resolved flags for review_id={rid}",
    "send_notification": "Sent notification to user_id={uid}",
}


def generate_review_body():
    """Generate a realistic review body from templates."""
    template = random.choice(REVIEW_BODY_TEMPLATES)
    filled = template
    for key, options in FILL_DATA.items():
        placeholder = "{" + key + "}"
        if placeholder in filled:
            filled = filled.replace(placeholder, random.choice(options), 1)
    return filled


def random_date_in_range(start_date, end_date):
    """Generate a random datetime between start_date and end_date."""
    delta = end_date - start_date
    if delta.days <= 0:
        return start_date
    random_days = random.randint(0, delta.days)
    random_seconds = random.randint(0, 86399)
    return start_date + timedelta(days=random_days, seconds=random_seconds)


def generate_username(first, last, used):
    """Generate a unique username from first and last name."""
    base = f"{first.lower()}_{last.lower()}"
    if base not in used:
        used.add(base)
        return base
    for suffix in range(1, 100):
        candidate = f"{base}{suffix}"
        if candidate not in used:
            used.add(candidate)
            return candidate
    return base  # fallback


def generate_email(first, last, used):
    """Generate a unique email from first and last name."""
    domain = random.choice(EMAIL_DOMAINS)
    separators = [".", "_", ""]
    sep = random.choice(separators)
    base = f"{first.lower()}{sep}{last.lower()}@{domain}"
    if base not in used:
        used.add(base)
        return base
    for suffix in range(1, 100):
        candidate = f"{first.lower()}{sep}{last.lower()}{suffix}@{domain}"
        if candidate not in used:
            used.add(candidate)
            return candidate
    return base  # fallback


# =============================================================================
# GENERATE DATA
# =============================================================================

now = datetime(2026, 4, 15, 12, 0, 0)
two_years_ago = now - timedelta(days=730)

# ---- Users ----
users = []
used_usernames = set()
used_emails = set()

# Shuffle name combinations to get diverse pairings
name_pairs = []
shuffled_first = list(FIRST_NAMES)
shuffled_last = list(LAST_NAMES)
random.shuffle(shuffled_first)
random.shuffle(shuffled_last)
for i in range(40):
    name_pairs.append((shuffled_first[i % len(shuffled_first)], shuffled_last[i % len(shuffled_last)]))

pair_idx = 0
for role in ROLES:
    for i in range(USERS_PER_ROLE):
        first, last = name_pairs[pair_idx]
        pair_idx += 1

        username = generate_username(first, last, used_usernames)
        email = generate_email(first, last, used_emails)
        join_date = random_date_in_range(two_years_ago, now)

        # Most users active, a few inactive or banned
        rand_val = random.random()
        if rand_val < 0.85:
            status = "active"
        elif rand_val < 0.95:
            status = "inactive"
        else:
            status = "banned"

        users.append({
            "user_id": len(users) + 1,
            "username": username,
            "email": email,
            "password_hash": "$2b$12$LJ3m4ys3Lk0TBMqVtZZKeuNOd6v2nPzuBsQ3Jq.MHgTvWMFpCKWi6",
            "role": role,
            "join_date": join_date.strftime("%Y-%m-%d"),
            "status": status,
        })

# ---- Movie-Genre mappings ----
genre_id_map = {name: idx + 1 for idx, name in enumerate(GENRES)}

movie_genres = []
for movie_idx, movie in enumerate(MOVIES):
    movie_id = movie_idx + 1
    for genre_name in movie["genres"]:
        genre_id = genre_id_map[genre_name]
        movie_genres.append({
            "movie_id": movie_id,
            "genre_id": genre_id,
        })

# ---- WatchHistory ----
watch_history = []
wh_pairs = set()
wh_id = 1
while len(watch_history) < 75:
    user_id = random.randint(1, len(users))
    movie_id = random.randint(1, len(MOVIES))
    pair = (user_id, movie_id)
    if pair not in wh_pairs:
        wh_pairs.add(pair)
        watch_date = random_date_in_range(two_years_ago, now)
        watch_history.append({
            "history_id": wh_id,
            "user_id": user_id,
            "movie_id": movie_id,
            "watched_date": watch_date.strftime("%Y-%m-%d"),
        })
        wh_id += 1

# ---- Watchlists (for casual and enthusiast users) ----
casual_enthusiast_ids = [u["user_id"] for u in users if u["role"] in ("casual", "enthusiast")]
watchlists = []
wl_id = 1
watchlist_name_pool = list(WATCHLIST_NAMES)
random.shuffle(watchlist_name_pool)
name_idx = 0

# Target: 50 watchlists. Distribute 1-3 per user to hit exactly 50.
# With 20 casual/enthusiast users, we need an average of 2.5 lists/user.
user_list_counts = []
for uid in casual_enthusiast_ids:
    user_list_counts.append(random.choice([2, 2, 3]))
# Adjust to exactly 50
while sum(user_list_counts) < 50:
    idx = random.randrange(len(user_list_counts))
    if user_list_counts[idx] < 3:
        user_list_counts[idx] += 1
while sum(user_list_counts) > 50:
    idx = random.randrange(len(user_list_counts))
    if user_list_counts[idx] > 1:
        user_list_counts[idx] -= 1

for uid, num_lists in zip(casual_enthusiast_ids, user_list_counts):
    for _ in range(num_lists):
        if wl_id > 50:
            break
        wl_name = watchlist_name_pool[name_idx % len(watchlist_name_pool)]
        name_idx += 1
        created = random_date_in_range(two_years_ago, now)
        watchlists.append({
            "watchlist_id": wl_id,
            "user_id": uid,
            "name": wl_name,
            "created_at": created.strftime("%Y-%m-%d %H:%M:%S"),
        })
        wl_id += 1
    if wl_id > 50:
        break

# ---- WatchlistItems ----
watchlist_items = []
wi_id = 1
for wl in watchlists:
    num_items = random.randint(3, 5)
    chosen_movies = random.sample(range(1, len(MOVIES) + 1), num_items)
    for mid in chosen_movies:
        added_at = random_date_in_range(
            datetime.strptime(wl["created_at"], "%Y-%m-%d %H:%M:%S"), now
        )
        watchlist_items.append({
            "watchlist_item_id": wi_id,
            "watchlist_id": wl["watchlist_id"],
            "movie_id": mid,
            "added_at": added_at.strftime("%Y-%m-%d %H:%M:%S"),
        })
        wi_id += 1

# ---- Ratings ----
ratings = []
rating_pairs = set()
r_id = 1
while len(ratings) < 75:
    user_id = random.randint(1, len(users))
    movie_id = random.randint(1, len(MOVIES))
    pair = (user_id, movie_id)
    if pair not in rating_pairs:
        rating_pairs.add(pair)
        rating_value = round(random.uniform(1.0, 10.0), 1)
        rating_date = random_date_in_range(two_years_ago, now)
        ratings.append({
            "rating_id": r_id,
            "user_id": user_id,
            "movie_id": movie_id,
            "rating_value": rating_value,
            "rating_date": rating_date.strftime("%Y-%m-%d %H:%M:%S"),
        })
        r_id += 1

# ---- Reviews ----
reviews = []
review_pairs = set()
rev_id = 1
moderation_statuses = ["approved", "approved", "approved", "approved", "pending", "rejected"]
while len(reviews) < 60:
    user_id = random.randint(1, len(users))
    movie_id = random.randint(1, len(MOVIES))
    pair = (user_id, movie_id)
    if pair not in review_pairs:
        review_pairs.add(pair)
        review_title = random.choice(REVIEW_TITLES)
        review_body = generate_review_body()
        status = random.choice(moderation_statuses)
        review_date = random_date_in_range(two_years_ago, now)
        reviews.append({
            "review_id": rev_id,
            "user_id": user_id,
            "movie_id": movie_id,
            "review_title": review_title,
            "review_body": review_body,
            "moderation_status": status,
            "review_date": review_date.strftime("%Y-%m-%d %H:%M:%S"),
        })
        rev_id += 1

# ---- Recommendations (for casual and enthusiast users) ----
recommendations = []
rec_id = 1
while len(recommendations) < 60:
    user_id = random.choice(casual_enthusiast_ids)
    movie_id = random.randint(1, len(MOVIES))
    movie_data = MOVIES[movie_id - 1]
    genre = random.choice(movie_data["genres"])
    reason_template = random.choice(RECOMMENDATION_REASONS)
    reason = reason_template.replace("{genre}", genre).replace("{movie}", movie_data["title"])
    generated_at = random_date_in_range(two_years_ago, now)
    recommendations.append({
        "recommendation_id": rec_id,
        "user_id": user_id,
        "movie_id": movie_id,
        "reason": reason,
        "generated_at": generated_at.strftime("%Y-%m-%d %H:%M:%S"),
    })
    rec_id += 1

# ---- RecommendationClicks ----
rec_clicks = []
rc_id = 1
for rec in recommendations:
    num_clicks = random.choice([1, 2, 2, 2, 3])
    for _ in range(num_clicks):
        clicked_at = random_date_in_range(
            datetime.strptime(rec["generated_at"], "%Y-%m-%d %H:%M:%S"), now
        )
        rec_clicks.append({
            "click_id": rc_id,
            "recommendation_id": rec["recommendation_id"],
            "user_id": rec["user_id"],
            "clicked_at": clicked_at.strftime("%Y-%m-%d %H:%M:%S"),
        })
        rc_id += 1

# ---- ReviewFlags ----
review_flags = []
rf_id = 1
flaggable_reviews = [r for r in reviews if r["moderation_status"] in ("approved", "pending")]
flagged_review_ids = random.sample(
    [r["review_id"] for r in flaggable_reviews],
    min(30, len(flaggable_reviews)),
)
for rev_id_flag in flagged_review_ids:
    flagger_id = random.randint(1, len(users))
    flag_reason = random.choice(FLAG_REASONS)
    flag_date = random_date_in_range(two_years_ago, now)
    flag_status = random.choice(["pending", "pending", "reviewed", "dismissed"])
    review_flags.append({
        "flag_id": rf_id,
        "review_id": rev_id_flag,
        "flagged_by_user_id": flagger_id,
        "flag_reason": flag_reason,
        "flag_status": flag_status,
        "flag_date": flag_date.strftime("%Y-%m-%d %H:%M:%S"),
    })
    rf_id += 1

# ---- AdminLog ----
admin_ids = [u["user_id"] for u in users if u["role"] == "admin"]
admin_logs = []
al_id = 1
for _ in range(50):
    admin_user_id = random.choice(admin_ids)
    action_type = random.choice(ADMIN_ACTION_TYPES)
    template = ADMIN_DETAILS_TEMPLATES[action_type]
    notes = template.format(
        mid=random.randint(1, len(MOVIES)),
        rid=random.randint(1, max(len(reviews), 1)),
        uid=random.randint(1, len(users)),
        gid=random.randint(1, len(GENRES)),
        status=random.choice(["approved", "rejected"]),
        role=random.choice(ROLES),
        report_type=random.choice(["monthly analytics", "user activity", "content moderation", "system health"]),
    )
    action_timestamp = random_date_in_range(two_years_ago, now)
    admin_logs.append({
        "log_id": al_id,
        "admin_user_id": admin_user_id,
        "action_type": action_type,
        "notes": notes,
        "action_timestamp": action_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
    })
    al_id += 1


# =============================================================================
# WRITE SQL FILE
# =============================================================================

def write_sql():
    lines = []

    lines.append("USE CineMetrics;\n")

    # ---- Genre inserts ----
    lines.append("-- =============================================================")
    lines.append("-- Genre (15 rows)")
    lines.append("-- =============================================================\n")
    for idx, genre in enumerate(GENRES):
        gid = idx + 1
        lines.append(
            f"INSERT INTO Genre (genre_id, genre_name) VALUES ({gid}, '{escape_sql(genre)}');"
        )
    lines.append("")

    # ---- Movie inserts ----
    lines.append("-- =============================================================")
    lines.append(f"-- Movie ({len(MOVIES)} rows)")
    lines.append("-- =============================================================\n")
    for idx, movie in enumerate(MOVIES):
        mid = idx + 1
        lines.append(
            f"INSERT INTO Movie (movie_id, title, release_year, runtime_minutes, synopsis, country_of_origin, language) "
            f"VALUES ({mid}, '{escape_sql(movie['title'])}', {movie['release_year']}, {movie['runtime_minutes']}, "
            f"'{escape_sql(movie['synopsis'])}', '{escape_sql(movie['country_of_origin'])}', '{escape_sql(movie['language'])}');"
        )
    lines.append("")

    # ---- MovieGenre inserts ----
    lines.append("-- =============================================================")
    lines.append(f"-- MovieGenre ({len(movie_genres)} rows)")
    lines.append("-- =============================================================\n")
    for mg in movie_genres:
        lines.append(
            f"INSERT INTO MovieGenre (movie_id, genre_id) "
            f"VALUES ({mg['movie_id']}, {mg['genre_id']});"
        )
    lines.append("")

    # ---- User inserts ----
    lines.append("-- =============================================================")
    lines.append(f"-- User ({len(users)} rows)")
    lines.append("-- =============================================================\n")
    for u in users:
        lines.append(
            f"INSERT INTO `User` (user_id, username, email, password_hash, role, join_date, status) "
            f"VALUES ({u['user_id']}, '{escape_sql(u['username'])}', '{escape_sql(u['email'])}', "
            f"'{escape_sql(u['password_hash'])}', '{escape_sql(u['role'])}', "
            f"'{u['join_date']}', '{escape_sql(u['status'])}');"
        )
    lines.append("")

    # ---- WatchHistory inserts ----
    lines.append("-- =============================================================")
    lines.append(f"-- WatchHistory ({len(watch_history)} rows)")
    lines.append("-- =============================================================\n")
    for wh in watch_history:
        lines.append(
            f"INSERT INTO WatchHistory (history_id, user_id, movie_id, watched_date) "
            f"VALUES ({wh['history_id']}, {wh['user_id']}, {wh['movie_id']}, '{wh['watched_date']}');"
        )
    lines.append("")

    # ---- Watchlist inserts ----
    lines.append("-- =============================================================")
    lines.append(f"-- Watchlist ({len(watchlists)} rows)")
    lines.append("-- =============================================================\n")
    for wl in watchlists:
        lines.append(
            f"INSERT INTO Watchlist (watchlist_id, user_id, name, created_at) "
            f"VALUES ({wl['watchlist_id']}, {wl['user_id']}, '{escape_sql(wl['name'])}', '{wl['created_at']}');"
        )
    lines.append("")

    # ---- WatchlistItem inserts ----
    lines.append("-- =============================================================")
    lines.append(f"-- WatchlistItem ({len(watchlist_items)} rows)")
    lines.append("-- =============================================================\n")
    for wi in watchlist_items:
        lines.append(
            f"INSERT INTO WatchlistItem (watchlist_item_id, watchlist_id, movie_id, added_at) "
            f"VALUES ({wi['watchlist_item_id']}, {wi['watchlist_id']}, {wi['movie_id']}, '{wi['added_at']}');"
        )
    lines.append("")

    # ---- Rating inserts ----
    lines.append("-- =============================================================")
    lines.append(f"-- Rating ({len(ratings)} rows)")
    lines.append("-- =============================================================\n")
    for r in ratings:
        lines.append(
            f"INSERT INTO Rating (rating_id, user_id, movie_id, rating_value, rating_date) "
            f"VALUES ({r['rating_id']}, {r['user_id']}, {r['movie_id']}, {r['rating_value']}, '{r['rating_date']}');"
        )
    lines.append("")

    # ---- Review inserts ----
    lines.append("-- =============================================================")
    lines.append(f"-- Review ({len(reviews)} rows)")
    lines.append("-- =============================================================\n")
    for rv in reviews:
        lines.append(
            f"INSERT INTO Review (review_id, user_id, movie_id, review_title, review_body, moderation_status, review_date) "
            f"VALUES ({rv['review_id']}, {rv['user_id']}, {rv['movie_id']}, "
            f"'{escape_sql(rv['review_title'])}', '{escape_sql(rv['review_body'])}', "
            f"'{escape_sql(rv['moderation_status'])}', '{rv['review_date']}');"
        )
    lines.append("")

    # ---- Recommendation inserts ----
    lines.append("-- =============================================================")
    lines.append(f"-- Recommendation ({len(recommendations)} rows)")
    lines.append("-- =============================================================\n")
    for rec in recommendations:
        lines.append(
            f"INSERT INTO Recommendation (recommendation_id, user_id, movie_id, reason, generated_at) "
            f"VALUES ({rec['recommendation_id']}, {rec['user_id']}, {rec['movie_id']}, "
            f"'{escape_sql(rec['reason'])}', '{rec['generated_at']}');"
        )
    lines.append("")

    # ---- RecommendationClick inserts ----
    lines.append("-- =============================================================")
    lines.append(f"-- RecommendationClick ({len(rec_clicks)} rows)")
    lines.append("-- =============================================================\n")
    for rc in rec_clicks:
        lines.append(
            f"INSERT INTO RecommendationClick (click_id, recommendation_id, user_id, clicked_at) "
            f"VALUES ({rc['click_id']}, {rc['recommendation_id']}, {rc['user_id']}, '{rc['clicked_at']}');"
        )
    lines.append("")

    # ---- ReviewFlag inserts ----
    lines.append("-- =============================================================")
    lines.append(f"-- ReviewFlag ({len(review_flags)} rows)")
    lines.append("-- =============================================================\n")
    for rf in review_flags:
        lines.append(
            f"INSERT INTO ReviewFlag (flag_id, review_id, flagged_by_user_id, flag_reason, flag_status, flag_date) "
            f"VALUES ({rf['flag_id']}, {rf['review_id']}, {rf['flagged_by_user_id']}, "
            f"'{escape_sql(rf['flag_reason'])}', '{escape_sql(rf['flag_status'])}', '{rf['flag_date']}');"
        )
    lines.append("")

    # ---- AdminLog inserts ----
    lines.append("-- =============================================================")
    lines.append(f"-- AdminLog ({len(admin_logs)} rows)")
    lines.append("-- =============================================================\n")
    for al in admin_logs:
        lines.append(
            f"INSERT INTO AdminLog (log_id, admin_user_id, action_type, notes, action_timestamp) "
            f"VALUES ({al['log_id']}, {al['admin_user_id']}, '{escape_sql(al['action_type'])}', "
            f"'{escape_sql(al['notes'])}', '{al['action_timestamp']}');"
        )
    lines.append("")

    # ---- Update average_rating ----
    lines.append("-- =============================================================")
    lines.append("-- Update Movie average_rating from Rating table")
    lines.append("-- =============================================================\n")
    lines.append("""UPDATE Movie m
SET average_rating = (
    SELECT ROUND(AVG(r.rating_value), 2)
    FROM Rating r
    WHERE r.movie_id = m.movie_id
)
WHERE m.movie_id IN (SELECT DISTINCT movie_id FROM Rating);""")
    lines.append("")

    # Write to file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "database-files", "01_cinemetrics_seed.sql")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # Print summary
    print("Mock data generation complete!")
    print(f"Output written to: {output_path}")
    print(f"\nRow counts:")
    print(f"  Genre:               {len(GENRES)}")
    print(f"  Movie:               {len(MOVIES)}")
    print(f"  MovieGenre:          {len(movie_genres)}")
    print(f"  User:                {len(users)}")
    print(f"  WatchHistory:        {len(watch_history)}")
    print(f"  Watchlist:           {len(watchlists)}")
    print(f"  WatchlistItem:       {len(watchlist_items)}")
    print(f"  Rating:              {len(ratings)}")
    print(f"  Review:              {len(reviews)}")
    print(f"  Recommendation:      {len(recommendations)}")
    print(f"  RecommendationClick: {len(rec_clicks)}")
    print(f"  ReviewFlag:          {len(review_flags)}")
    print(f"  AdminLog:            {len(admin_logs)}")


if __name__ == "__main__":
    write_sql()
