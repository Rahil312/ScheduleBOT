![ScheduleBot logo](https://raw.githubusercontent.com/lyonva/ScheduleBot/main/docs/img/banner.png)

[![Python v3.9](https://img.shields.io/badge/python-v3.9-blue)](https://docs.python.org/3.9/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/CSC510-Leslie-Tim-Deepak/SEProj-ScheduleBot/compare/fall_2024...Rahil312:ScheduleBOT:Group63_Project3_New_Features ) 
[![Contributors Activity](https://img.shields.io/github/commit-activity/m/CSC510-Leslie-Tim-Deepak/SEProj-ScheduleBot)](https://github.com/CSC510-Leslie-Tim-Deepak/SEProj-ScheduleBot/compare/fall_2024...Rahil312:ScheduleBOT:Group63_Project3_New_Features )
[![Last Commit](https://img.shields.io/github/last-commit/Rahil312/ScheduleBOT/Group63_Project3_New_Features)](https://github.com/CSC510-Leslie-Tim-Deepak/SEProj-ScheduleBot/compare/fall_2024...Rahil312:ScheduleBOT:Group63_Project3_New_Features)
[![Lines of code](https://tokei.rs/b1/github/Rahil312/ScheduleBOT)](https://github.com/Rahil312/ScheduleBOT/tree/Group63_Project3_New_Feature)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10211125.svg)](https://doi.org/10.5281/zenodo.10211125)
[![Repo-size](https://img.shields.io/github/repo-size/Rahil312/ScheduleBOT)](https://github.com/Rahil312/ScheduleBOT/tree/Group63_Project3_New_Features)
[![file_count](https://img.shields.io/github/directory-file-count/Rahil312/ScheduleBOT)](https://github.com/Rahil312/ScheduleBOT/tree/Group63_Project3_New_Features)
![GitHub issues](https://img.shields.io/github/issues/CSC510-Leslie-Tim-Deepak/SEProj-ScheduleBot)
[![GitHub issues-closed](https://img.shields.io/github/issues-closed/CSC510-Leslie-Tim-Deepak/SEProj-ScheduleBot.svg)](https://github.com/CSC510-Leslie-Tim-Deepak/SEProj-ScheduleBot/issues?q=is%3Aissue+is%3Aclosed)
[![GitHub top language](https://img.shields.io/github/languages/top/CSC510-Leslie-Tim-Deepak/SEProj-ScheduleBot)](https://docs.python.org/3.9/)
[![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/Rahil312/ScheduleBOT)](https://github.com/Rahil312/ScheduleBOT/tree/Group63_Project3_New_Features)
[![Coverage Status](https://coveralls.io/repos/github/CSC510-Leslie-Tim-Deepak/SEProj-ScheduleBot/badge.svg?branch=Test_workflow)](https://coveralls.io/github/CSC510-Leslie-Tim-Deepak/SEProj-ScheduleBot?branch=Test_workflow)
![GitHub release (with filter)](https://img.shields.io/github/v/release/CSC510-Leslie-Tim-Deepak/SEProj-ScheduleBot)
[![GitHub all releases](https://img.shields.io/github/downloads/CSC510-Leslie-Tim-Deepak/SEProj-ScheduleBot/total)](https://github.com/CSC510-Leslie-Tim-Deepak/SEProj-ScheduleBot/releases)
![Contributors](https://img.shields.io/github/contributors/CSC510-Leslie-Tim-Deepak/SEProj-ScheduleBot)
[![Platform](https://img.shields.io/badge/platform-discord-blue)](https://discord.com/)
<!--- [![codecov](https://codecov.io/gh/SEProjGrp5/ScheduleBot/branch/main/graph/badge.svg?token=Z53J2ZN227)](https://codecov.io/gh/SEProjGrp5/ScheduleBot) --->


<!--- [![Pylint](https://github.com/A1231/SEProjGrp6-ScheduleBot/actions/workflows/pylint.yml/badge.svg)](https://github.com/A1231/SEProjGrp6-ScheduleBot/actions/workflows/pylint.yml) --->
<!--- ![example workflow](https://github.com/A1231/SEProjGrp6-ScheduleBot/actions/workflows/python-app.yml/badge.svg) --->

# ScheduleBot

> Don't let the fear of the time it will take to accomplish something stand in the way of your doing it. The time will pass anyway; we might just as well put that passing time to the best possible use. - Earl Nightingale

<p align="center">
  <a href="#rocket-getting-started">Getting Started</a>
  ::
  <a href="#thought_balloon-for-developers">For Developers</a>
  ::
  <a href="#sparkles-whats-new-in-v5">What's new in V5 (Our addition to the project!)</a>
</p>

ScheduleBot is a Python application that helps you calendarize events and work through a Discord bot. Want to try it out? Simply follow the steps outlined in the [For Developers](#For-Developers) section. ScheduleBot can be configured to run on your Discord server by adding just one line of code!


With ScheduleBot you can quickly schedule events, state your prefered times for certain types of activities (exercise, homework, meetings, etc.) and quickly find out which times you have available to do more stuff.

## Why should you work on this?

[![Pitch Video](https://img.youtube.com/vi/ekeR4NJLzoY/0.jpg)](https://www.youtube.com/watch?v=ekeR4NJLzoY)


:rocket: Getting started
---
To get a list of commands, DM the bot the command:

```
!help
```

The bot will reply back you with the list of available commands.

<img width="481" alt="Screen Shot 2021-11-03 at 10 15 04 PM" src="docs\img\start1.jpeg">


### **Scheduling an event**

ScheduleBot's unit of work is the **event**. When you use ScheduleBot to organize your activities, it keeps track of your registered events. Each event consists of a period of time, comprised between a starting and ending date/time, event type, event priority and optional notes.  

To schedule a new event, just DM the bot:

```
!schedule
```

The bot will ask you the details of your new event.

<img width="481" alt="Screen Shot 2021-11-03 at 10 15 04 PM" src="docs\img\start2.jpeg">



### **I forgot my agenda for the day**

You can take a look at your events scheduled for a specfic date with the command:

```
!day today(or tomorrow\yesterday)
```

```
!day 3 (3 days from now)
```

```
!day -3 (3 days ago)
```

```
!day 4/20/22 (On Apr 20, 2022)
```

The bot will show you what you have scheduled for the date. This includes events that start before, or end after this date.

![Day](docs/img/!day.gif)



### Import & Export your calendar

You can import or export their calendar events as a CSV file through the bot. You can also import ICS files downloaded from Google Calendar.

```
!exportfile
```
![Export file](docs/img/!export.gif)

```
!importfile
```
Then drag the file to the Schedulebot.

![Import file](docs/img/!import.gif)

### Looking for an event summary or want to know when you are free? 

ScheduleBot will help you find your free times. Just write:

```
!freetime
```
To look for event summary:
```
!summary
```
<img width="481" alt="Summary" src="docs\img\Summary.png">



:thought_balloon: For Developers
---

### Get your Discord bot 

 Follow this [tutorial](https://www.freecodecamp.org/news/create-a-discord-bot-with-python/) to create your discord bot account.

### Token
  To "login" to your bot through our program, place a file named `config.py` in your src directory with the content:
  
  ```
  TOKEN = ************(your discord bot token)
  ```
  
### Intall required packages
  ```
  pip install -r requirements.txt
  ```
  
### Connect to Google Cloud
  1. Create a Project 
  2. Setup Billing 
  3. Enable geocoding API and distancematrix API
  4. Generate API key-
      Refer to [this](https://developers.google.com/maps/documentation/geocoding/get-api-key) link for more information about the same.
  5. Store the API key in the following format-
      File name: key.json \
      File Content: 
      ```
      {"key": "your api key here"}
      ```
  6. Key needs to be stored in the json folder.

### Run the schedulebot.py
  ```
  python3 schedulebot.py
  ```
  Then your scheduleBot should start working.
  
## Releases
-   [v1.1](https://github.com/lyonva/ScheduleBot/releases/tag/v1.1): First functional release
-   [v2.0](https://github.com/qchen59/ScheduleBot/releases/tag/v2.0.0): First version 2 release with import/export events function, find available time feature, also supports 24 hour time format and event priority.
-   [v2.1](https://github.com/qchen59/ScheduleBot/releases/tag/v2.1.0): Finalized version 2, check what's new in V2
-   [v3.0](https://github.com/SEProjGrp5/ScheduleBot/releases) Finalized version 3, check out what's new in V3
-   [v4.0](https://github.com/A1231/SEProjGrp6-ScheduleBot/releases) Finalized version 4, check out what's new in V4!
-   [v5.0](https://github.com/A1231/SEProjGrp6-ScheduleBot/releases) Finalized version 5, check out what's new in V4!


:dizzy: Features in V2:
---

Please note that this is not an exhaustive list, however it does include all major improvements. For a complete list of all changes and bug fixes, please see our closed github issues or commit history.

#### Import & Export your calendar

The user can now import or export their calendar events as a CSV file through the bot. The user can also import ICS files downloaded from Google Calendar.

#### Find time based on schedule + preferred time

ScheduleBot can help you find available times for a type of event based on your schedule and preferred time for the event type.

#### Event types with priority

Users can now assign a priority value for each event. This will help them keep track of important events. It also provides a foundation for future improvements, such as suggesting event removals based on the priority of events.

#### Support 24-hour time format input

We support 24-hour time format input now, in addition to the 12-hour format.

#### User's files encryption/decryption

User's data is now encrypted when it is stored in the host server, so the host will not be able to see other users\' schedules as easily. This improves user's privacy when using Schedulebot.

#### Check schedule for arbitrary days 

Users are able to check the schedule for any specific day in addition to today. Previously, only the events occurring today could be retrieved by the user.

#### Code coverage improvement

In this version, we improved the project's code coverage from 39% to 54%.

Code coverage remains low in this project because many sections of code require a Discord channel, and responses from a non-bot user through Discord. However, we were able to create a mock discord channel and user for several tests by using the "dpytest" library.

#### Fixed bugs related to the welcome message sent at startup

At startup, the bot now sends an on_ready welcome message to all servers the bot is currently listening to, instead of just one specific server. The bot also no longer attempts to respond to reactions to the welcome message made by itself or other bots.

#### Fixed bugs related to finding freetime

!freetime function was not working under certain circumstances, such as when there was only one event in the schedule. This has been fixed in the latest version.

## Getting involved

Thank you for caring for this project and getting involved. To start, please check out [contributing](https://github.com/qchen59/ScheduleBot/blob/main/CONTRIBUTING.md) and [code of conduct](https://github.com/qchen59/ScheduleBot/blob/main/CODE_OF_CONDUCT.md). For more technical detail of implementation of code, you can check out the documentation. When you want to get your hands on the project, take a peek into the [github project](https://github.com/qchen59/ScheduleBot/projects/1), assign yourself a task, move it to To-Do, and convert it into an issue and assign it to yourself.

Check out the [internal documentation](https://htmlpreview.github.io/?https://github.com/qchen59/ScheduleBot/blob/main/docs/src/index.html) if you want to contribute or find out about the inner workings of ScheduleBot.

:muscle: Features in V3:
---
Following are the new features that we have implemented for version 3 : 

#### 1. Connection to Google: 
We have added the functionality to connect the account to google calendar
As and when we create events on discord those events get scheduled in your google calender.


https://user-images.githubusercontent.com/89954066/144730436-29f74af7-36f2-45d0-a8c1-e19b5271b584.mp4


#### 2. Adding location of an event
We are now storing the location data of the events


https://user-images.githubusercontent.com/89954066/144730441-a65cbfae-80e5-402a-b362-901dd4f9884d.mp4


#### 3. Adding travel time as a separate event before the actual event
The bot adds a separate event to block of travel time to an event


https://user-images.githubusercontent.com/89954066/144730454-1b4c36e7-8230-4f9d-a3df-f4f2d499cc07.mp4


#### 4. Delete Event from schedule
User can delete events from their schedule


https://user-images.githubusercontent.com/89954066/144730459-1a12d11f-d9ad-44dc-a823-5e8acdae20c7.mp4


#### 5. Added a new functionality to check daily summary
Ability to view the daily summary of events


https://user-images.githubusercontent.com/89954066/144730460-5bc5dca7-7758-4106-8ec1-5ccd287ef5c2.mp4


#### 6. Code Coverage improvement
For this version, we have improved the project's code coverage from 54% to 65%.

#### 7. Viewing Google Calender events
User can check their next 10 events in the google calendar


https://user-images.githubusercontent.com/89954066/144730470-7700507e-b2e9-4175-88c0-749c15097702.mp4



:sparkles: What's new in V4:
---
Following are the new features that we have implemented for version 4 : 

#### 1. Adding events to Google Calendar directly from discord:
So far, !GoogleEvents command imports the events from Google Calendar to your discord. We have been able to add new events directly from the discord terminal to the user's google calendar. The bot returns the google calendar link once the event is successfully created. The user can then view their events on their google calendars.

<img width="481" alt="Screen Shot 2021-11-03 at 10 15 04 PM" src="docs\img\EventCreated.png">


<img width="481" alt="Screen Shot 2021-11-03 at 10 15 04 PM" src="docs\img\Googlecalendar.png">





#### 2. Sending Reminders for events created:
Want to be reminded before each event? Don't worry! Schedule Bot's here for the rescue. We have added an option for google to send reminders to the user through popup message five minutes before the event start time and an email an hour before the event start time.


<img width="481" alt="Screen Shot 2021-11-03 at 10 15 04 PM" src="docs\img\Reminder.png">


<img width="481" alt="Screen Shot 2021-11-03 at 10 15 04 PM" src="docs\img\GCalReminder.png">





#### 3. Displaying the weather for the day along with the day's events:
Get each day's weather and temperature information along with the list of events you planned for the day.
The Bot displays weather conditions in the event location (for each event) on a particular day when user types in the command to view summary of the events scheduled for that day.
Type in the following command for the weather to be displayed:

```
!day today
```
<img width="481" alt="Screen Shot 2021-11-03 at 10 15 04 PM" src="docs\img\Weather.png">

#### 4. Fixed the bug caused by the delete event command:
On executing the !deleteEvent command, the bot kept sending multiple "event does not exist" messages, even though the event does exist. That bug has been fixed in this version!

Following was the issue:


<img width="481" alt="Screen Shot 2021-11-03 at 10 15 04 PM" src="docs\img\Delete1.png">


Once the issue got resolved:


<img width="481" alt="Screen Shot 2021-11-03 at 10 15 04 PM" src="docs\img\Delete2.png">



:sparkles: What's new in V5:
---
Following are the new features that we have implemented for version 4 : 

#### 1. Adding a Google Maps link for travel:
Schedule Bot's '!schedule' feature, already popular for event creation with details like date, time, source, destination, and mode of transport, has been enhanced. We've now added an extra feature: for each event you create, the bot will generate a Google Maps link based on the provided source and destination, and the chosen mode of transport. This complements our existing reminder service, where Google sends a pop-up notification five minutes before the event starts and an email one hour in advance, making sure you stay on top of your schedule.


```
!schedule
```


<img width="481" alt="Screen Shot 2021-11-03 at 10 15 04 PM" src="docs\img\Maps1.jpeg">


<img width="481" alt="Screen Shot 2021-11-03 at 10 15 04 PM" src="docs\img\Maps2.jpeg">


<img width="481" alt="Screen Shot 2021-11-03 at 10 15 04 PM" src="docs\img\Maps3.jpeg">


<img width="481" alt="Screen Shot 2021-11-03 at 10 15 04 PM" src="docs\img\Maps4.jpeg">


<img width="481" alt="Screen Shot 2021-11-03 at 10 15 04 PM" src="docs\img\Maps-5.png">





#### 2. Showing Weather for future days:
Weather forecast for a specific day can be categorized into three cases:
Case 1: The event both begins and concludes on the current day.
Case 2: The event starts on the current day but extends to a future date.
Case 3: The event has already commenced and will also conclude on the current day (in this scenario, a weather report cannot be generated).



```
!day today
```


<img width="481" alt="Screen Shot 2021-11-03 at 10 15 04 PM" src="docs\img\3Weather-1.jpeg">



```
!day tomorrow
```


<img width="481" alt="Screen Shot 2021-11-03 at 10 15 04 PM" src="docs\img\3Weather-2.jpeg">





#### 3. Mood-Based Event Recommendations:
Users have the option to enter their current mood, and in response, the bot provides event suggestions tailored to that mood, such as recommending relaxation activities for those feeling stressed. This allows users to schedule their events based on these personalized recommendations.


```
!recommend happy
```


<img width="481" alt="Screen Shot " src="docs\img\MoodRecomm.jpeg">



#### 4. Event History Feature: 
The bot keeps a detailed record of your attended events. Simply by querying, you can easily review your activity history, such as gym sessions and study times, with precise start and end timestamps.


```
!history
```


<img width="481" alt="Screen Shot " src="docs\img\history.jpeg">



## Here are some ideas for the future collaborators
These are example features that could be added to ScheduleBot in the future.


### Edit event
You can edit the event you created:

```
!eventedit
```

### Deleting the event from Google Calendar, once it gets deleted from discord
Currently, the events can be deleted on discord. What can be added is, getting them to be deleted from Google Calendar too.


### Rubric
Refer to Rubric.md file [here](https://github.com/kgudipe/SEProj-ScheduleBot/blob/main/Rubrics.md)



:ghost:	What's new in V6
--
#### 1. Generative AI chatbot
We’ve introduced a new feature: a Generative AI chatbot! Now, by typing `!ask` followed by your question, you can get answers directly from the bot. For example, let’s try asking, "Where is North Carolina State University?"
```
!ask [your question here]
```
https://github.com/user-attachments/assets/a2a056f1-7831-4dd1-877c-b7c14b42ced9

#### 2. Admin Control
Have events on your Google Calendar? No problem! Once you connect your Google account, Schedule Bot can fetch and display your calendar events. Just use the command `!syncEvents` followed by your password. You’ll receive a confirmation prompt—-type `CONFIRM` in all caps, and the bot will sync your schedule. You can clear all locally stored events by using the command
```!clearData``` followed by your password.

```
!syncEvents [your password here]
```
```
CONFIRM
```
```
!clearData [your password here]
```
https://github.com/user-attachments/assets/593f15eb-caa4-4b4b-bda7-79011f179b10

#### 3. Delete an event with synchronization
The third feature allows you to delete an event you no longer need, with updates syncing directly to your Google Calendar. Previously, deleting an event within Discord only removed it locally, leaving it on your Google Calendar. Now, any event you remove from Schedule Bot is seamlessly deleted from your Google Calendar too, keeping both in sync.
```
!deleteEvent
```
```
[index of the event being deleted]
```
https://github.com/user-attachments/assets/91be8c5a-719e-4dbe-952c-6b6506b17bec

#### 4. Code improvement
We’ve added error handling to Schedule Bot. Now, if the bot encounters an issue, it won’t stop running. Instead, it will display an error message and continue processing your next command. We also introduced a logging function to Schedule Bot, which now records the result of every command. This feature allows you to review past interactions and helps us improve troubleshooting by providing a clear record of each command’s outcome. Finally, this project emphasizes modular, refactored code by organizing each function into clear, manageable modules. Core logic like event handling, data storage, and Google Calendar integration is separated within a functionality folder, with shared utilities for data encryption, file handling, and other common tasks in a shared_functions module. The main bot logic in schedulebot.py accesses these modules, making the bot easier to update, troubleshoot, and scale.

https://github.com/user-attachments/assets/28e0dca5-1abb-455d-9bff-03e6e36263aa

## Future Scope

**Ride Integration for Meetings** : For in-person meetings, ScheduleBot can redirect users to the Uber app or webpage, displaying fare estimates based on the user's current location and the meeting destination.

**Class Schedule Integration** : Seamlessly connect the MyPack Portal with ScheduleBot to automatically import a student’s class schedule and sync it with Google Calendar.

**Rest Time Recommendations** : If a user’s daily schedule exceeds a certain time limit, ScheduleBot can suggest appropriate rest periods and even set an alarm to ensure downtime.

**Appointment Booking via Calendar** : Generate a shareable Google Calendar link, enabling others to book appointments automatically based on the user's availability.

## Collaborators
Karan Shaunak Patel

Rahil Hardik shukla

Rohan Mehul Champaneri


