from datetime import date
import random
from fastmcp import FastMCP

mcp = FastMCP(name="Custom Tools Server")

@mcp.tool
def calculate_age(date_of_birth: str) -> int:
    """Calculate the current age from a date of birth.
    (format: YYYY-MM-DD)"""
    year, month, day = map(int, date_of_birth.split("-"))
    born = date(year, month, day)
    today = date.today()

    age = today.year - born.year
    if (today.month, today.day) < (born.month, born.day):
        age = age-1

    return age

@mcp.tool
def random_number(min_value: int, max_value: int) -> int:
    """From the given min_value and max_value, generate an
    integer that falls in between"""
    return random.randint(min_value, max_value)

if __name__ == "__main__":
    mcp.run()

