import inquirer
import requests
from datetime import datetime, timedelta
from PIL import Image
import subprocess


def get_github_information() -> tuple[str, list[str]]:
    github_username = input("Enter your GitHub username: ")
    data = requests.get(f"https://api.github.com/users/{github_username}").json()

    if data.get("status") == "404":
        raise Exception("Unable to find GitHub username")
    
    year_account_created, current_year = int(data["created_at"][:4]), int(datetime.now().year)
    return github_username, [str(year) for year in range(current_year-1, year_account_created-1, -1)]


def get_user_input(years: list[str]) -> dict[str]:
    questions = [
        inquirer.List(
            'year',
            message="What YEAR would you like to commit to?",
            choices=years,
        ),
        inquirer.Text('img_name', message="Enter the name of your image ('sketch.jpg')"),
    ]
    answers = inquirer.prompt(questions)
    return answers


def get_start_date(year: str) -> datetime:
    date = datetime(int(year), 1, 1)

    while date.weekday() != 6:
        date += timedelta(days=1)

    if date.day == 1:
        date += timedelta(days=7)
        
    return date


def get_image_pixels(img_name: str) -> list[int]:
    img = Image.open(f"img/{img_name}").convert("L")
    width, height = img.size

    if width != 50 and height != 7:
        raise Exception("Invalid file size! Please select a JPG image that is 50x7 pixels.")

    pixels = []
    for i in range(width):
        for j in range(height):
            brightness = int((255 - img.getpixel((i, j))) / 51)
            pixels.append(brightness)

    return pixels


def create_commit(date: datetime):
    with open("commits.txt", "a") as f:
        f.write("!")

    subprocess.run(["git", "add", "commits.txt"])
    subprocess.run(["git", "commit", "-m", "drawing"])
    subprocess.run(["git", "commit", "--amend", "-m", "drawing", f'--date="{date.strftime("%a %b %d %I:%M %Y +0700")}"'])


def create_commits(pixels: tuple[int, int, int], start_date: datetime):
    subprocess.run(["git", "init"])
    date = start_date

    for brightness in pixels:
        for _ in range(brightness):
            create_commit(date)
        date += timedelta(days=1)
    
    subprocess.run(["git", "push", "origin", "main"])


if __name__ == '__main__':
    print("Welcome to the commit canvas!")
    print("NOTE: You can only commit to previous years!\n")

    github_username, years = get_github_information()
    user_input = get_user_input(years)

    start_date = get_start_date(user_input["year"])
    pixels = get_image_pixels(user_input.get("img_name"))
    create_commits(pixels, start_date)

    print(f"\N{SPARKLES} Your canvas is completed! Check it out here: https://github.com/{github_username}?tab=overview&from={user_input['year']}-12-01&to={user_input['year']}-12-31")

    