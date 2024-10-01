import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def parse_daily_note_file(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()

    # i only want the lines after the '## Day Planner' line
    start_index = 0
    for i, line in enumerate(lines):
        if line == "## Day Planner\n" or line == "##  Day Planner\n":
            start_index = i + 1
            break

    if start_index == 0:
        return []
    # all the lines after the '## Day Planner' line
    lines = lines[start_index:]
    # from pprint import pprint
    # pprint(lines)

    # remove all lines that does not start with '- '
    lines = [line for line in lines if line.startswith("- ")]
    # pprint(lines)

    # remove the end of line character from each line
    lines = [line.strip() for line in lines]
    # pprint(lines)

    # remove empty lines
    lines = [line for line in lines if line]
    # pprint(lines)

    # remove the '- ' or '- [ ] ' or '- [x] ' from the beginning of each line
    lines = [line[2:] if line.startswith("- ") else line[6:] for line in lines]
    # pprint(lines)

    # now hard part is to parse the time and the event
    # example lines
    split_lines = [line.split(" ", 3) for line in lines]
    # pprint(split_lines)

    return split_lines

def get_event_json_from_parsed_line(date, parsed_line, time_zone="Europe/Istanbul", custom_description="Created by planner"):
    # ['9:00', '-', '9:30', 'japanese'],
    #  ['21:00', '-', '22:00', 'Diary'],
    #   ['22:00', '-', '23:00', 'Reading'],
    #  ['23:00', '-', '00:00', 'Sleep']]
    start_string = f"{date}T{parsed_line[0]}:00"
    end_string = f"{date}T{parsed_line[2]}:00"
    if parsed_line[2] == "00:00":
        end_string = f"{date}T23:59:59"
    return {
        "summary": parsed_line[3],
        "description": custom_description,
        "start": {
            "dateTime": start_string,
            "timeZone": time_zone
        },
        "end": {
            "dateTime": end_string,
            "timeZone": time_zone
        }
    }

def get_all_day_planner_events(daily_notes_path, start_date, end_date, time_zone="Europe/Istanbul", custom_description="Created by planner"):
    files = os.listdir(daily_notes_path)

    # filter files that are in the range of start_date and end_date
    files = [file for file in files if start_date <= datetime.datetime.strptime(file.replace(".md", ""), "%Y-%m-%d") <= end_date]
    print('files to be processed:', files)
    parsed_events = []
    for file in files:
        parsed_lines = parse_daily_note_file(os.path.join(daily_notes_path, file))
        for parsed_line in parsed_lines:
            event = get_event_json_from_parsed_line(file.replace(".md", ""), parsed_line, time_zone=time_zone, custom_description=custom_description)
            parsed_events.append(event)
    return parsed_events

def delete_all_events_created_by_planner(service, start_date, end_date, calendar_id="primary"):
    events_result = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=start_date.isoformat() + "Z",
            timeMax=end_date.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    for event in events:
        if event.get("description") == "Created by planner":
            service.events().delete(calendarId=calendar_id, eventId=event["id"]).execute()




def main(service, daily_notes_path="daily/", time_window=30, calendar_id="primary", time_zone="Europe/Istanbul", custom_description="Created by planner", **kwargs):

    start_date = datetime.datetime.now() - datetime.timedelta(days=1)
    end_date = datetime.datetime.now() + datetime.timedelta(days=time_window)
    all_day_planner_events = get_all_day_planner_events( # window of time is one month
        daily_notes_path=daily_notes_path,
        start_date=start_date,
        end_date=end_date,
        time_zone=time_zone,
        custom_description=custom_description
    )
    print('all_day_planner_events:', all_day_planner_events)
    delete_all_events_created_by_planner(
        service,
        start_date=start_date,
        end_date=end_date,
        calendar_id=calendar_id
    )

    for event in all_day_planner_events:
        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"event created {event.get('htmlLink')}")


def metaauthfunc(**kwargs):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        main(service, **kwargs)


    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create events in google calendar from daily notes")
    parser.add_argument('--credentials_content', default=None, help='Content of the credentials.json file')
    parser.add_argument("--token_content", default=None, help="Content of the token.json file")
    parser.add_argument("--daily_notes_path", default="daily/", help="Path to the daily notes folder")
    parser.add_argument("--time_window", default=30, type=int, help="Time window in days")
    parser.add_argument("--calendar_id", default="primary", help="Calendar id")
    parser.add_argument("--time_zone", default="Europe/Istanbul", help="Time zone")
    parser.add_argument("--custom_description", default="Created by Obsidian Day Planner", help="Custom description")
    args = parser.parse_args()

    if args.credentials_content and args.token_content:
        with open("credentials.json", "w") as file:
            file.write(args.credentials_content)
        with open("token.json", "w") as file:
            file.write(args.token_content)

    metaauthfunc(**vars(args))
