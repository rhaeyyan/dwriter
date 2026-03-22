# 📖 dwriter: 20 Creative Use Cases & Workflows

**dwriter** is designed as a fast, low-friction terminal journaling tool centered around a **Unified TUI**. While it offers a powerful CLI for lightning-fast capture, the interactive dashboard is your primary command center for productivity.

Whether you are a **freelance designer**, a **student**, a **maker**, or a **software engineer**, here are 20 creative ways to push `dwriter` beyond standard developer task management.

---

## 📋 Table of Contents
1. [The Fermenter's Tinkering Log (Brewing, Cheese, Sourdough)](#1-the-fermenters-tinkering-log-brewing-cheese-sourdough)
2. [The Maker's Build Log (Woodworking, Gardening, Electronics)](#2-the-makers-build-log-woodworking-gardening-electronics)
3. [The News Junkie's Personal Archive (Current Events Timeline)](#3-the-news-junkies-personal-archive-current-events-timeline)
4. [The Travel Itinerary & Memory Journal](#4-the-travel-itinerary--memory-journal)
5. [The Language Learner's Immersion Log](#5-the-language-learners-immersion-log)
6. [The Fitness PR & Routine Tracker](#6-the-fitness-pr--routine-tracker)
7. [The Media, Book, & Article Log](#7-the-media-book--article-log)
8. [The Daily Gratitude & Evening Reflection Journal](#8-the-daily-gratitude--evening-reflection-journal)
9. [The "Anti-Burnout" Protocol (Wellness & Breaks)](#9-the-anti-burnout-protocol-wellness--breaks)
10. [The "Second Brain" Idea Inbox](#10-the-second-brain-idea-inbox)
11. [Micro-Habit Stacking & Gamification](#11-micro-habit-stacking--gamification)
12. [The Manager's 1-on-1 & Feedback Tracker](#12-the-managers-1-on-1--feedback-tracker)
13. [The "Brag Document" & Performance Review Prep](#13-the-brag-document--performance-review-prep)
14. [The Student's Focus & Assignment Tracker](#14-the-students-focus--assignment-tracker)
15. [The Freelancer & Creative's Billing Engine](#15-the-freelancer--creatives-billing-engine)
16. [The Job Hunter's Interview & Application Tracker](#16-the-job-hunters-interview--application-tracker)
17. [The "Pre-Jira" Bug Scratchpad](#17-the-pre-jira-bug-scratchpad)
18. [The Retroactive "Timesheet Savior" (Time-Traveling & Editing)](#18-the-retroactive-timesheet-savior-time-traveling--editing)
19. [Minimalist Meeting Notes & Action Items](#19-minimalist-meeting-notes--action-items)
20. [Expense & Subscription Auditing](#20-expense--subscription-auditing)
21. [💡 How to Get the Most Out of dwriter](#-how-to-get-the-most-out-of-dwriter)

---

## 1. The Fermenter's Tinkering Log (Brewing, Cheese, Sourdough)
Baking sourdough, brewing beer, making cheese, or fermenting kimchi requires iterative experimentation and tracking variables over long periods. If you tweak a recipe or take a measurement (like specific gravity or pH), you need a reliable way to remember *exactly* what you did days, weeks, or even months later.

* **Headless CLI:** Keep your laptop on the kitchen counter and use the lightning-fast CLI to log your ingredient tweaks, temperatures, or specific gravity readings using subprojects like `brew:dish` or `cheese:type`.
  ```bash
  dwriter add "Brew day: Mashed at 152F for 60 mins. Original Gravity: 1.054." -t measurement -p brew:pale_ale
  dwriter add "Added mesophilic culture and rennet. Milk temp holding at 86F." -t culturing -p cheese:cheddar
  dwriter todo "Rack kombucha to secondary fermentation and add blackberries" --priority high -p ferment:kombucha
  ```
* **Interactive TUI:** Three months later, when you finally crack open that aged wheel of cheddar or pour a pint of your homebrew and it tastes incredible, open `dwriter search` and filter by `cheese:cheddar` or `brew:pale_ale`. You'll have a complete, chronological history of every temperature change, failure, and tasting note, ensuring you can perfectly replicate your best batches.

## 2. The Maker's Build Log (Woodworking, Gardening, Electronics)
Perfect for physical hobbies where your hands are dirty and you only have 5 seconds before walking away from the computer.

* **Headless CLI:** Lightning-fast logging.
  ```bash
  dwriter add "Planted heirloom tomatoes, watered with 10ml fertilizer" -t planting -p garden_2024
  ```
* **Interactive TUI:** Three weeks later, when you can't remember when the seeds were planted, open `dwriter search` and type "tomato". The fuzzy-finder handles typos, instantly highlighting the exact timestamp you planted them.

## 3. The News Junkie's Personal Archive (Current Events Timeline)
Consuming the daily news can feel like drinking from a firehose. If you want to remember specific events, market shifts, or tech announcements—and your own thoughts on them—`dwriter` lets you build a personal, searchable historical timeline. By using the `&project:subproject` syntax, you can keep global events neatly categorized.

* **Headless CLI:** When you read a major headline, instantly log the event, a URL, and your quick take using subcategories like `news:tech` or `news:finance`.
  ```bash
  dwriter add "Fed cuts interest rates by 0.5%. Market rallied immediately." -t economy -p news:finance
  dwriter add "OpenAI releases new reasoning model. https://techcrunch..." -t ai -t release -p news:tech
  dwriter add "Local city council passed the new zoning laws for downtown." -t local -p news:politics
  ```
* **Interactive TUI:** Three months later, when you are trying to remember exactly when a specific tech release happened or how the market reacted to a policy change, open `dwriter search` and type `news:tech`. 
  
  **Bonus Payoff:** If you write a weekly newsletter or just want to review the week's global events, use the CLI review command: `dwriter review --days 7 -p news -f markdown`. `dwriter` will instantly compile a chronological, bulleted summary of every major headline you tracked this week across all your news subprojects.

## 4. The Travel Itinerary & Memory Journal
When you are traveling, you don't want to spend 20 minutes writing in a diary or fighting with a slow mobile app. You just want to capture a quick memory, log an expense, or track a reservation number and get back to your vacation.

* **Headless CLI:** Use the CLI for rapid-fire logging of your trip as it happens, categorizing by your destination.
  ```bash
  dwriter add "Checked into the Airbnb. Door code is 4928." -t logistics -p trip:tokyo_2024
  dwriter add "Ate at the tiny ramen shop in Shinjuku. Incredible broth." -t food -p trip:tokyo_2024
  dwriter add "Bought train tickets to Kyoto: $85" -t expense -p trip:tokyo_2024
  ```
* **Interactive TUI (The Payoff):** When you get back home and want to share recommendations with a friend, use `dwriter review -p trip:tokyo_2024 -f markdown`. `dwriter` will instantly spit out a beautifully formatted, chronological travelogue of everywhere you went, what you ate, and how much you spent.

## 5. The Language Learner's Immersion Log
Keep track of your study hours, grammar rules, and maintain your daily consistency.

* **Headless CLI:** Start a study timer directly from your shell.
  ```bash
  dwriter timer 30 -t listening_practice -p japanese_N4
  ```
* **Interactive TUI:** Launch the Dashboard (`dwriter stats`). The Weekly Chart and Contribution Calendar provide immediate visual feedback on your consistency, helping you visually identify if you've been skipping study days.

## 6. The Fitness PR & Routine Tracker
Typing out a workout log in a bulky fitness app between sets can be annoying. If your laptop is nearby, the terminal is faster.

* **Headless CLI:** Quickly log your lifts or meal prep.
  ```bash
  dwriter add "Deadlift: 3x5 @ 315lbs. Felt heavy today." -t lifting -p fitness
  ```
* **Interactive TUI:** Made a typo on the weight? Launch the Edit TUI (`dwriter edit`). Navigate to the mistake with `j`/`k`, press `e` to fix the text, or `t` to adjust the tags without wrestling with complex commands.

## 7. The Media, Book, & Article Log
Act as a lightweight bookmarking and review system for articles and books.

* **Headless CLI:** Log what you read with a 1-sentence takeaway.
  ```bash
  dwriter add "Read Pragmatic Programmer Ch 2. Takeaway: use tracer bullets." -t book_notes
  ```
* **Interactive TUI:** If a coworker asks you about an architectural concept six months from now, launch `dwriter search`. The real-time filtering updates the results with every keystroke, helping you find your notes instantly even if you only remember a fraction of the title.

## 8. The Daily Gratitude & Evening Reflection Journal
`dwriter` is the perfect quiet environment for evening journaling and mood tracking.

* **Headless CLI:** Review today's work, then log your mental state.
  ```bash
  dwriter today
  dwriter add "Grateful for the sunny weather today." -t gratitude -p personal
  ```
* **Interactive TUI:** When you're having a rough week, open `dwriter search` and type `gratitude`. Use `j` and `k` to read through a clean, distraction-free list of all the positive moments you've captured.

## 9. The "Anti-Burnout" Protocol (Wellness & Breaks)
It’s easy to hyperfocus and forget to step away from the keyboard. Use `dwriter` to enforce mandatory breaks and visualize your wellness over time.

* **Headless CLI:** Quickly start a 15-minute break timer and automatically tag it when done.
  ```bash
  dwriter timer 15 -t screen-break -t walking -p health
  ```
* **Interactive TUI:** Launch `dwriter timer` to view the large visual countdown. You can hit `Space` to pause/resume or `+`/`-` to adjust time. At the end of the week, open `dwriter stats` to see if `#screen-break` made it into your "Top Tags" chart.

## 10. The "Second Brain" Idea Inbox
Don't let a random stroke of genius derail your current work session. 

* **Headless CLI:** Capture it in exactly 3 seconds.
  ```bash
  dwriter add "Idea: build a moisture sensor for the monstera plant" -t hardware -p someday
  ```
* **Interactive TUI:** Next time you are bored on a Sunday afternoon, open `dwriter search` and type `someday`. Your terminal instantly becomes a curated, easily scrollable list of past ideas ready to be built.

## 11. Micro-Habit Stacking & Gamification
Turn `dwriter` into a minimalist, keyboard-driven habit tracker.

* **Headless CLI:** Add recurring habits as tasks.
  ```bash
  dwriter todo "Drink 2L of water" -t hydration -p habits
  ```
* **Interactive TUI:** Every morning, pop open `dwriter todo`. Simply hit `Space` on your habits to check them off. Because checking off a todo logs an entry, it counts toward your logging streak. Open `dwriter stats` to watch your GitHub-style contribution calendar grow!

## 12. The Manager's 1-on-1 & Feedback Tracker
If you manage a team, it is incredibly difficult to remember every small win, roadblock, or piece of feedback that occurs between weekly 1-on-1 meetings. `dwriter` can act as your secure, terminal-based leadership diary. By using subprojects for each direct report, you keep everything organized.

* **Headless CLI:** Throughout the week, whenever an employee does something great or mentions a blocker, log it instantly with their specific subproject tag.
  ```bash
  dwriter todo "Discuss the new Q3 architecture proposal" --priority high -p 1on1:sarah
  dwriter add "Crushed the client presentation today! Remember to praise." -t feedback -p 1on1:david
  dwriter add "Mentioned feeling blocked by the devops team." -t roadblock -p 1on1:sarah
  ```
* **Interactive TUI:** Five minutes before your meeting with Sarah, launch `dwriter search` and type `1on1:sarah`. Use `Ctrl+N` to toggle to **Todos** to see what you need to ask her, and toggle back to **Entries** to see the feedback you collected for her throughout the week.

## 13. The "Brag Document" & Performance Review Prep
When performance reviews roll around, it is notoriously difficult to remember the impact you made 6 months ago. 

* **Headless CLI:** Whenever you complete a major milestone or receive praise, log it instantly without breaking context.
  ```bash
  dwriter add "Led the successful DB migration with zero downtime!" -t milestone -p brag_doc
  ```
* **Interactive TUI:** When it's time to write your self-reflection, launch `dwriter search`. Press `/` and type `brag_doc`. Use `j` and `k` to scroll through a beautifully color-coded, chronological list of your biggest accomplishments.

## 14. The Student's Focus & Assignment Tracker
Manage assignments and actually sit down to study with focused pomodoro sessions.

* **Headless CLI:** Add your syllabus assignments from the terminal.
  ```bash
  dwriter todo "Write first draft of History term paper" --priority high -p history_101
  ```
* **Interactive TUI:** Open `dwriter todo`, select the assignment with `j`/`k`, and hit `+` to increase its priority to Red (Urgent). When you finish studying, hit `Space` to mark it complete and automatically log it to your daily journal.

## 15. The Freelancer & Creative's Billing Engine
Writers, designers, and consultants often juggle multiple clients and need to effortlessly log billable hours.

* **Headless CLI:** Generate a clean, markdown-formatted invoice payload for a specific client at the end of the week.
  ```bash
  dwriter review --days 7 -p client_acmecorp --format markdown
  ```
* **Interactive TUI:** Need to see what tasks are pending vs. completed for a client? Open `dwriter search`, filter by `client_acmecorp`, and press `Ctrl+N` to instantly toggle between your completed Entries and your pending Todos.

## 16. The Job Hunter's Interview & Application Tracker
Searching for a job involves managing parallel threads: applications sent, assignments, and prep.

* **Headless CLI:** Log submitted applications.
  ```bash
  dwriter add "Submitted application for Senior Backend Dev role" -p stripe_interview
  ```
* **Interactive TUI:** Ten minutes before your final round interview, open `dwriter search` and filter by the company name. You'll instantly see your past notes, submitted dates, and completed tasks right in your terminal, perfectly refreshing your memory.

## 17. The "Pre-Jira" Bug Scratchpad
Sometimes you spot a weird UI glitch, but you aren't ready to open a formal Jira ticket yet. 

* **Headless CLI:** Throw it into your scratchpad without losing your train of thought.
  ```bash
  dwriter todo "Investigate random 500 error on checkout" -t bug_hunt -p scratchpad
  ```
* **Interactive TUI:** Keep `dwriter todo` open on a second monitor during sprint planning. If a scratchpad bug turns out to be real, graduate it to Jira, then hit `Space` to mark it done. If it's a duplicate, press `d` to delete it forever.

## 18. The Retroactive "Timesheet Savior" (Time-Traveling & Editing)
We all forget to log our work sometimes. `dwriter` lets you fix history.

* **Headless CLI:** Use natural language dates to backdate entries if you completely forgot to log a weekend shift.
  ```bash
  dwriter add "Pushed hotfix for the database deadlock" --date "last Sunday" -p on_call
  ```
* **Interactive TUI:** If you logged something today but forgot to add the correct client project, open `dwriter edit`. Select the entry, press `p`, and type the correct project name.

## 19. Minimalist Meeting Notes & Action Items
Jumping from Zoom to Zoom leaves little time to organize notes. 

* **Headless CLI:** Log decisions and action items the second a meeting ends.
  ```bash
  dwriter add "Decision: We are pushing the v2 launch to Q3" -t decision -p weekly_sync
  dwriter todo "Email the finalized API spec to frontend" --priority high -p weekly_sync
  ```
* **Interactive TUI:** Before your next sync, open `dwriter search` and type `weekly_sync`. Toggle between your Entries (last week's decisions) and Todos (your pending action items) using `Ctrl+N`.

## 20. Expense & Subscription Auditing
Keep track of one-off business expenses, software subscriptions, or freelance write-offs.

* **Headless CLI:** Whenever you buy a tool, log it with the cost.
  ```bash
  dwriter add "Renewed GitHub Copilot for $100" -t software -p expenses_2024
  ```
* **Interactive TUI:** Come tax season, launch `dwriter search` and filter by `expenses_2024`. Hit `Enter` on any entry to instantly copy its full content to your clipboard so you can paste it into your tax spreadsheet.

---

## 💡 How to Get the Most Out of dwriter

To truly make `dwriter` a seamless part of your daily routine, it helps to adopt a few simple habits and workflows. Here are some pro tips to maximize your experience:

### 1. The TUI is your "Command Center"
The most effective way to use `dwriter` is to keep the **interactive TUI** open in a dedicated terminal tab or window throughout the day. It acts as your dashboard for focus, task management, and reflection. Use the **headless CLI** (`dwriter add`) only for "surgical" data entry when you are in the middle of a coding session and don't want to switch tabs.

### 2. Establish a Tagging Convention Early
Because `dwriter` relies heavily on `#tags` and `&projects` to generate summaries, consistency is key. Pick a handful of standard tags and stick to them. 
* **Good convention:** Use `&projects` for the *context* or *client* (e.g., `&acmecorp`, `&personal`) and `#tags` for the *action* (e.g., `#bugfix`, `#meeting`, `#reading`). 

### 3. Create Subcategories with Colons (`&project:subproject`)
If you have a large project with multiple moving parts, you don't need to invent entirely new project names. You can create clean subcategories by using a colon in your project tag!
* **For Freelancers:** `&client_acme:website` vs. `&client_acme:marketing`
* **For Students:** `&cs_101:homework` vs. `&cs_101:labs`
* **For Makers:** `&desk_build:woodworking` vs. `&desk_build:finishing`
This syntax keeps your root projects organized while giving you granular control over what you are tracking. 

### 4. Let the Timer Do the Logging
If you are sitting down for a focused session, don't just use `dwriter add` afterward. Launch the **Timer** in the TUI (`dwriter timer 25 -p my_project`). Not only do you get a visual countdown to keep you accountable, but the TUI will automatically prompt you to log what you accomplished the second the timer finishes. It combines focus tracking and journaling into one step.

### 5. Leverage Natural Language Time-Traveling
Don't stress if you forget to log a massive debugging session on a Friday afternoon. `dwriter` understands natural language. On Monday morning, just run `dwriter add "Fixed the memory leak" --date "last Friday"`. This keeps your timeline pristine for your weekly reviews and contribution calendar.

### 6. Alias it for Ultimate Speed
If you are typing out `dwriter` 20 times a day, save your keystrokes! Add a simple alias to your `.bashrc` or `.zshrc` file:
```bash
alias dw="dwriter"
alias dwt="dwriter todo"
alias dws="dwriter search"
```
Now, logging an idea takes literally three keystrokes: `dw add "New idea!"`. 
