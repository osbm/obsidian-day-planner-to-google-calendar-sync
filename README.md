
This github action helps you sync your actions created by your obsidian Day Planner plugin to Google Calendar.

To add this github action to your repository add this file to `.github/workflows/sync.yml` with following content:

'''
on:
  push:
    paths:
    - life/daily/*
    - .github/workflows/sync.yml

  workflow_dispatch:

jobs:
  mainjob:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout the repository
      uses: actions/checkout@v4

    - name: Run calendar sync action
      uses: osbm/obsidian-day-planner-to-google-calendar-sync@main
      with:
        daily-notes-path: life/daily
        credentials-json:  ${{ secrets.CREDENTIALSJSON }}
        token-json:  ${{ secrets.TOKENJSON }}
        time-zone: Europe/Istanbul
        time-window: 30
        custom-description: Created by Obsidian Day Planner
        calendar-id: primary

'''