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

def get_event_json_from_parsed_line(date, parsed_line):
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
        "description": "Created by planner",
        "start": {
            "dateTime": start_string,
            "timeZone": "Europe/Istanbul"
        },
        "end": {
            "dateTime": end_string,
            "timeZone": "Europe/Istanbul"
        }

def get_all_day_planner_events(daily_notes_path, start_date, end_date):
    files = os.listdir(daily_notes_path)
    # filter files that are in the range of start_date and end_date
    files = [file for file in files if start_date <= datetime.datetime.strptime(file, "%Y-%m-%d") <= end_date]
    parsed_events = []
    for file in files:
        parsed_lines = parse_daily_note_file(daily_notes_path + file)
        for parsed_line in parsed_lines:
            parsed_events.append(get_event_json_from_parsed_line(file, parsed_line))

    return parsed_events

def delete_all_events_created_by_planner(service, start_date, end_date):
    events_result = (
        service.events()
        .list(
            calendarId="primary",
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
            service.events().delete(calendarId="primary", eventId=event["id"]).execute()




def main(service):
    all_day_planner_events = get_all_day_planner_events( # window of time is one month
        daily_notes_path="daily/", start_date=datetime.datetime.now(), end_date=datetime.datetime.now() + datetime.timedelta(days=30)
    )

    delete_all_events_created_by_planner(service, start_date=datetime.datetime.now(), end_date=datetime.datetime.now() + datetime.timedelta(days=30))

    for event in all_day_planner_events:
        event = service.events().insert(calendarId="primary", body=event).execute()
        print(f"event created {event.get('htmlLink')}")


def metaauthfunc():
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

        main(service)
        # event = {
        #     "summary": "testsummary",
        #     "description" : "descript",
        #     "colorId": 5,
        #     "start": {
        #         "dateTime": "2024-09-24T09:00:00+03:00",
        #         "timeZone": "Europe/Istanbul"
        #     },
        #     "end": {
        #         "dateTime": "2024-09-24T19:00:00+03:00",
        #         "timeZone": "Europe/Istanbul"
        #     }
        # }

        # event = service.events().insert(calendarId="primary", body=event).execute()

        # print(f"event created {event.get('htmlLink')}")

        # Call the Calendar API
        # now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        # print("Getting the upcoming 10 events")
        # events_result = (
        #     service.events()
        #     .list(
        #         calendarId="primary",
        #         timeMin=now,
        #         maxResults=10,
        #         singleEvents=True,
        #         orderBy="startTime",
        #     )
        #     .execute()
        # )
        # events = events_result.get("items", [])

        # if not events:
        #   print("No upcoming events found.")
        #   return

        # Prints the start and name of the next 10 events
        # for event in events:
        #   start = event["start"].get("dateTime", event["start"].get("date"))
        #   print(start, event["summary"])

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
  parse_daily_note_file("/home/osbm/Documents/rerouting/life/daily/2024-10-01.md")
