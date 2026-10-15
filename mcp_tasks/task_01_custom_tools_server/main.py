from datetime import date
import random
from fastmcp import FastMCP

mcp = FastMCP(name="Custom Tools Server")

@mcp.tool
def calculate_age(date_of_birth: str) -> int:
    """Calculate the current age from a given DOB(format: YYYY-MM-DD).
    Use this whenever someone asks you to find someone's age from their DOB"""
    year, month, day = map(int, date_of_birth.split(("-")))
    born = date(year, month, day)
    today = date.today()

    age = today.year-born.year
    if (today.month, today.day) < (born.month, born.day):
        age = age-1

    return age

@mcp.tool
def random_number(min_value: int, max_value: int) -> int:
    """Generate a random integer between the min_value and max_value. 
    Use this whenever someone asks you to generate a random number"""
    return random.randint(min_value, max_value)


if __name__ == "__main__":
    mcp.run()
