# 📖 dwriter: 16 Creative Use Cases & Workflows

**dwriter** is designed as a fast, low-friction terminal journaling tool. However, its combination of rapid CLI logging, built-in timers, interactive TUI, and smart organization (`-t` tags and `-p` projects) makes it an incredibly versatile life-tracking engine. 

Whether you are a **freelance designer** logging billable hours, a **student** running focus study sessions, a **maker** tracking the growth of your garden, or a **reflector** doing evening journaling, here are 16 creative ways to push `dwriter` beyond standard developer task management.

---

## 📋 Table of Contents
1. [The "Anti-Burnout" Protocol (Wellness & Breaks)](#1-the-anti-burnout-protocol-wellness--breaks)
2. [The "Brag Document" & Performance Review Prep](#2-the-brag-document--performance-review-prep)
3. [The Student's Focus & Assignment Tracker](#3-the-students-focus--assignment-tracker)
4. [Micro-Habit Stacking & Gamification](#4-micro-habit-stacking--gamification)
5. [The Freelancer & Creative's Billing Engine](#5-the-freelancer--creatives-billing-engine)
6. [The Maker's Build Log (Woodworking, Gardening, Electronics)](#6-the-makers-build-log-woodworking-gardening-electronics)
7. [The "Second Brain" Idea Inbox](#7-the-second-brain-idea-inbox)
8. [The Job Hunter's Interview & Application Tracker](#8-the-job-hunters-interview--application-tracker)
9. [The Language Learner's Immersion Log](#9-the-language-learners-immersion-log)
10. [The Fitness PR & Routine Tracker](#10-the-fitness-pr--routine-tracker)
11. [The Daily Gratitude & Evening Reflection Journal](#11-the-daily-gratitude--evening-reflection-journal)
12. [The "Pre-Jira" Bug Scratchpad](#12-the-pre-jira-bug-scratchpad)
13. [The Retroactive "Timesheet Savior" (Time-Traveling)](#13-the-retroactive-timesheet-savior-time-traveling)
14. [Minimalist Meeting Notes & Action Items](#14-minimalist-meeting-notes--action-items)
15. [Expense & Subscription Auditing](#15-expense--subscription-auditing)
16. [The Media, Book, & Article Log](#16-the-media-book--article-log)

---

## 1. The "Anti-Burnout" Protocol (Wellness & Breaks)
It’s easy to hyperfocus and forget to step away from the keyboard. You can use the `dwriter timer` not just for deep work, but to enforce mandatory breaks and track your wellness over time.

* **The Workflow:**
    When you feel eye strain, start a mandatory break timer and log it to a wellness project.
    ```bash
    dwriter timer 15 -t screen-break -t walking -p health
    ```
* **The Payoff:**
    At the end of the week, run `dwriter search "break" -p health` or look at your `dwriter stats` dashboard. If you don't see enough yellow `#screen-break` tags, you know you need to adjust your habits for the upcoming week.

## 2. The "Brag Document" & Performance Review Prep
When annual or mid-year performance reviews roll around, it is notoriously difficult to remember the impact you made 6 months ago. `dwriter` can serve as your ongoing "Brag Document" so you are perfectly prepared to advocate for your promotion.

* **The Workflow:**
    Whenever you complete a major milestone, fix a critical bug, or receive praise from a coworker, intentionally log it as a "win."
    ```bash
    dwriter add "Led the successful migration to Postgres with zero downtime!" -t milestone -t leadership -p brag_doc
    dwriter add "Shoutout from Sarah in slack for helping her debug the auth service" -t praise -p brag_doc
    ```
* **The Payoff:**
    When it's time to write your self-reflection or update your resume, you don't have to stare at a blank page. Run `dwriter search -p brag_doc` or `dwriter review --days 180 -f markdown` to instantly compile a chronological, detailed list of your biggest accomplishments.

## 3. The Student's Focus & Assignment Tracker
For students, managing assignments and actually sitting down to study are two different battles. `dwriter` helps you track upcoming due dates and run timed study sessions for different subjects.

* **The Workflow:**
    Add your syllabus assignments to the todo board, then use the timer to force yourself to focus on specific subjects.
    ```bash
    dwriter todo "Write first draft of History term paper" --priority high -t essay -p history_101
    dwriter timer 45 -t reading -p organic_chemistry
    ```
* **The Payoff:**
    You can easily see exactly how much time you are dedicating to different subjects by searching your project tags (`-p organic_chemistry`).

## 4. Micro-Habit Stacking & Gamification
With the interactive Todo board (`dwriter todo`) and the GitHub-style contribution calendar (`dwriter stats`), you can turn `dwriter` into a minimalist, keyboard-driven habit tracker. 

* **The Workflow:**
    Add your daily habits as recurring tasks with specific priorities.
    ```bash
    dwriter todo "Drink 2L of water" -t hydration -p habits --priority high
    dwriter todo "15 mins Duolingo" -t spanish -p learning
    ```
    Later, pop open the interactive TUI (`dwriter todo`), hit `Space` to check them off, and they automatically log to today's journal.
* **The Payoff:**
    Because checking off a todo logs an entry, it counts toward your `dwriter` streak. Open `dwriter stats` to watch your logging streak grow, gamifying your daily routine without needing a separate app.

## 5. The Freelancer & Creative's Billing Engine
Writers, designers, and consultants often juggle multiple clients and need to effortlessly log billable hours. `dwriter` handles context switching elegantly so you know exactly what you worked on this week.

* **The Workflow:**
    Log your tasks or run focus timers explicitly tied to a client's project name.
    ```bash
    dwriter timer 45 -t wireframing -t figma -p client_acmecorp
    dwriter add "Drafted Q3 marketing copy" -t copywriting -p side_hustle
    ```
* **The Payoff:**
    When Friday rolls around and it's time to invoice, you don't need to guess what you did. Simply run `dwriter search -p client_acmecorp` or use `dwriter review --days 7 --format markdown` to instantly generate a bulleted timesheet for your client.

## 6. The Maker's Build Log (Woodworking, Gardening, Electronics)
`dwriter` is perfect for hobbyists and makers tracking the daily growth of a garden, building furniture, or soldering electronics. It lets you log milestones in seconds without leaving your keyboard.

* **The Workflow:**
    Use quick terminal commands to log physical milestones or measurements so you don't forget them.
    ```bash
    dwriter add "Applied 2nd coat of polyurethane to the tabletop" -t finishing -p desk_build
    dwriter add "Planted heirloom tomato seeds, watered with 10ml fertilizer" -t planting -p garden_2024
    ```
* **The Payoff:**
    Three weeks later, when you can't remember what grit sandpaper you used or exactly when the seeds were planted, open the interactive search (`dwriter search`) and start typing "polyurethane" or "tomato" to pull up the exact timestamp.

## 7. The "Second Brain" Idea Inbox
Don't let a random stroke of genius derail your current coding session. Capture it instantly without leaving the terminal, then get right back to work.

* **The Workflow:**
    When an idea strikes, throw it into a `#someday` tag. 
    ```bash
    dwriter add "Idea: build a moisture sensor for the monstera plant" -t hardware -p someday
    ```
* **The Payoff:**
    Next time you are bored on a Sunday afternoon, run `dwriter search -p someday`. Your terminal instantly becomes a curated list of past ideas and side-projects ready to be built.

## 8. The Job Hunter's Interview & Application Tracker
Searching for a job involves managing a lot of parallel threads: applications sent, take-home assignments, and interview prep. `dwriter` can act as your personal CRM for the job hunt.

* **The Workflow:**
    Log your applications as entries and use the todo system to manage upcoming interviews or coding challenges.
    ```bash
    dwriter add "Submitted application for Senior Backend Dev role" -t application -p stripe_interview
    dwriter todo "Complete the API design take-home assignment" --priority urgent -p stripe_interview
    dwriter timer 60 -t leetcode -p interview_prep
    ```
* **The Payoff:**
    Ten minutes before your final round interview, run `dwriter search -p stripe_interview`. You'll instantly see the exact dates you applied, the notes you took after the first round, and the tasks you completed.

## 9. The Language Learner's Immersion Log
Consistency is the hardest part of learning a new language. You can use `dwriter` to track your study hours, log new grammar rules you learned, and keep your daily streak alive.

* **The Workflow:**
    Use the timer for active study sessions and the standard add command for logging milestones.
    ```bash
    dwriter timer 30 -t listening_practice -p japanese_N4
    dwriter add "Finally understand the difference between 'wa' and 'ga' particles!" -t grammar -p japanese_N4
    ```
* **The Payoff:**
    Run `dwriter stats` to watch your language-learning streak grow on the contribution calendar. You can also run `dwriter review --days 30 -f markdown` to see exactly how much you progressed.

## 10. The Fitness PR & Routine Tracker
Typing out a workout log in a bulky fitness app between sets can be annoying. If your laptop is nearby, `dwriter` is a lightning-fast way to log your reps or track nutrition.

* **The Workflow:**
    Quickly log your lifts or meal prep using specific tags.
    ```bash
    dwriter add "Deadlift: 3x5 @ 315lbs. Felt heavy today, slept poorly." -t lifting -p fitness
    dwriter add "Meal prep Sunday: cooked chicken and rice for the next 4 days" -t nutrition -p fitness
    ```
* **The Payoff:**
    Six weeks later, when you can't remember what your last deadlift working weight was, just launch `dwriter search "deadlift"` to fuzzy-search your entire history.

## 11. The Daily Gratitude & Evening Reflection Journal
For daily journalers and reflectors, recalling exactly what you did yesterday can be difficult. `dwriter` makes evening journaling and mood tracking a breeze.

* **The Workflow:**
    At the end of the day, use the standup tool to review your tasks, then take 30 seconds to log your mental state or gratitude.
    ```bash
    dwriter standup
    dwriter add "Grateful for the sunny weather and a really good cup of pour-over coffee" -t gratitude -p personal
    ```
* **The Payoff:**
    When you're having a rough week, use `dwriter search -t gratitude` or generate a markdown summary with `dwriter review`. You'll get a beautifully formatted, chronological list of all the positive moments you've captured.

## 12. The "Pre-Jira" Bug Scratchpad
Sometimes you spot a weird UI glitch or an unhandled edge case, but you aren't ready to open a formal Jira ticket yet because you haven't verified it. `dwriter` is the perfect messy middle-ground.

* **The Workflow:**
    Log unverified bugs or technical debt as todos in a specific scratchpad project.
    ```bash
    dwriter todo "Investigate random 500 error on the checkout page" -t bug_hunt -p scratchpad
    dwriter todo "Refactor the user context provider (it's getting messy)" -t tech_debt -p scratchpad
    ```
* **The Payoff:**
    When it's time for sprint planning, pop open the TUI (`dwriter todo`) and filter by `scratchpad`. You can either graduate these tasks to real Jira tickets, or just hit `Space` to knock them out.

## 13. The Retroactive "Timesheet Savior" (Time-Traveling)
We all forget to log our work sometimes. If you spent your entire Sunday fixing a critical production outage but forgot to log it, `dwriter`'s natural language `--date` flag lets you fix your history effortlessly.

* **The Workflow:**
    Use natural language dates to backdate entries and keep your records accurate.
    ```bash
    dwriter add "Pushed hotfix for the database deadlock" --date "last Sunday" -t incident -p on_call
    dwriter add "Onboarding call with the new contractor" --date yesterday -t meeting -p management
    ```
* **The Payoff:**
    Even if you slip up and forget to log things in real-time, you can use the `--date` flag to reconstruct your week on Friday morning. When you run `dwriter review --days 7`, everything will be in the perfectly correct chronological order.

## 14. Minimalist Meeting Notes & Action Items
Jumping from Zoom to Zoom leaves little time to organize notes. `dwriter` allows you to instantly log decisions and action items the second a meeting ends.

* **The Workflow:**
    Use tags to separate general notes from actionable tasks.
    ```bash
    dwriter add "Decision: We are pushing the v2 launch to Q3" -t decision -p weekly_sync
    dwriter todo "Email the finalized API spec to the frontend team" --priority high -t action_item -p weekly_sync
    ```
* **The Payoff:**
    Before your next `weekly_sync`, run `dwriter search -p weekly_sync`. You will instantly see what was decided last week and what action items you still have pending on your todo board.

## 15. Expense & Subscription Auditing
It's surprisingly hard to keep track of one-off business expenses, software subscriptions, or freelance write-offs. Since you already live in the terminal, you can log expenses the moment you pay for them.

* **The Workflow:**
    Whenever you buy a tool, course, or asset, log it with the cost.
    ```bash
    dwriter add "Renewed GitHub Copilot for $100" -t software -p expenses_2024
    dwriter add "Bought 'Designing Data-Intensive Applications' for $35" -t education -p expenses_2024
    ```
* **The Payoff:**
    Come tax season, you don't need to dig through your credit card statements. Just run `dwriter review -p expenses_2024 -f plain` and you have a clean, easily parsable list of all your deductible purchases for the year.

## 16. The Media, Book, & Article Log
We consume so much information daily that it's easy to forget the brilliant article we read last Tuesday. `dwriter` can act as a lightweight bookmarking and review system.

* **The Workflow:**
    Log what you read or watched, along with a 1-sentence takeaway.
    ```bash
    dwriter add "Read 'The Pragmatic Programmer' Ch 2. Takeaway: always use tracer bullets for new architecture." -t book_notes -p reading
    dwriter todo "Read the new Vercel blog post on React Server Components" -t article -p to_read
    ```
* **The Payoff:**
    It builds a searchable database of knowledge. If a coworker asks you about React Server Components six months from now, `dwriter search "server components"` will instantly pull up the article you saved and the notes you took on it.
