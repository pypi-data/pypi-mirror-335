import random
import datetime

#List of fortunes
FORTUNES = [
    "Do not be afraid of competition.",
    "An exciting opportunity lies ahead of you.",
    "You love peace.",
    "Get your mind set…confidence will lead you on.",
    "You will always be surrounded by true friends.",
    "Sell your ideas—they have exceptional merit.",
    "You should be able to undertake and complete anything.",
    "You are kind and friendly.",
    "You are wise beyond your years.",
    "Your ability to juggle many tasks will take you far.",
    "A routine task will turn into an enchanting adventure.",
    "Beware of all enterprises that require new clothes.",
    "Be true to your work, your word, and your friend.",
    "Goodness is the only investment that never fails.",
    "A journey of a thousand miles begins with a single step.",
    "Forget injuries; never forget kindnesses.",
    "Respect yourself and others will respect you.",
    "A man cannot be comfortable without his own approval.",
    "Always do right. This will gratify some people and astonish the rest.",
    "It is easier to stay out than to get out.",
    "Sing every day and chase the mean blues away.",
    "You will receive money from an unexpected source.",
    "Attitude is a little thing that makes a big difference.",
    "Plan for many pleasures ahead.",
    "Experience is the best teacher.",
    "You will be happy with your spouse.",
    "Expect the unexpected.",
    "Stay healthy. Walk a mile.",
    "The family that plays together stays together.",
    "Eat chocolate to have a sweeter life.",
    "Once you make a decision the universe conspires to make it happen.",
    "Make yourself necessary to someone.",
    "The only way to have a friend is to be one.",
    "Nothing great was ever achieved without enthusiasm.",
    "Dance as if no one is watching.",
    "Live this day as if it were your last.",
    "Your life will be happy and peaceful.",
    "Reach for joy and all else will follow.",
    "Move in the direction of your dreams.",
    "Bloom where you are planted.",
    "Appreciate. Appreciate. Appreciate.",
    "Happy news is on its way.",
    "Paradise is always where love dwells.",
    "The one you love is closer than you think.",
    "Love is like wildflowers…it is often found in the most unlikely places.",
    "In dreams and in love there are no impossibilities.",
    "Love isn't something you find. Love is something that finds you.",
    "True love is not something that comes every day; follow your heart, it knows the right answer."
]

#Categories of themed fortunes
THEMED_FORTUNES = {
    "love": [
        "Paradise is always where love dwells.",
        "The one you love is closer than you think.",
        "Love is like wildflowers…it is often found in the most unlikely places.",
        "In dreams and in love there are no impossibilities.",
        "Love isn't something you find. Love is something that finds you.",
        "True love is not something that comes every day; follow your heart, it knows the right answer."
        "You will be happy with your spouse."], 
    "career": [
        "Do not be afraid of competition.",
        "An exciting opportunity lies ahead of you.",
        "Get your mind set…confidence will lead you on.",
        "Sell your ideas—they have exceptional merit.",
        "You should be able to undertake and complete anything.",
        "Your ability to juggle many tasks will take you far.",
        "A routine task will turn into an enchanting adventure.",
        "Beware of all enterprises that require new clothes.",
        "Be true to your work, your word, and your friend.",
        "Goodness is the only investment that never fails."], 
    "happiness": [
        "Your life will be happy and peaceful.",
        "Reach for joy and all else will follow.",
        "Happy news is on its way.",
        "Dance as if no one is watching.",
        "Live this day as if it were your last.",
        "Bloom where you are planted.",
        "Appreciate. Appreciate. Appreciate."]
}

#Days of the week
week_days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']

def get_random_fortune():
    """
    Returns a random fortune from the list
    """
    return random.choice(FORTUNES)

def get_lucky_numbers(length: int):
    """
    Returns a set of len lucky numbers
    """
    len_num = int(length)
    if 1 <= len_num <= 10:
        return random.sample(range(1, 99), len_num)
    else:
        return 0
    
def get_daily_fortune(day:str):
    """
    Returns the same fortune for everyone given a certain day of the week.
    """
    if not isinstance(day, str):
        return ""
    
    if day.lower() in week_days:  
        day_num = week_days.index(day.lower()) + 1  
        today = datetime.date.today().timetuple().tm_yday
        index = int((today%len(FORTUNES)) / day_num)
        return FORTUNES[index]
    else:
        return ""
    
def get_custom_fortune(name:str):
    """
    Returns a personalized fortune.
    """
    if not name.strip():
        return random.choice(FORTUNES)
    return f"{name}, {random.choice(FORTUNES)}"

def get_themed_fortune(theme:str):
    """
    Returns a fortune based on a specific theme
    """
    themes = theme.strip().lower
    if not themes:
        return "Invalid theme. Please choose 'love', 'career', or 'happiness'."
    return random.choice(THEMED_FORTUNES.get(theme.strip().lower(), ["There are no fortunes for your provided theme, please choose 'love', 'career', or 'happiness'"]))

