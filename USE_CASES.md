# 📖 dwriter: 16 Creative Use Cases & Workflows

**dwriter** is designed as a fast, low-friction terminal journaling tool. Its unique architecture means it thrives in two different environments:
1. **Headless CLI:** Lightning-fast, one-off commands that don't interrupt your flow.
2. **Interactive TUI:** Keyboard-driven, real-time dashboards for review, editing, and planning.

Whether you are a **freelance designer**, a **student**, a **maker**, or a **software engineer**, here are 16 creative ways to push `dwriter` beyond standard developer task management, utilizing both the CLI and TUI.

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
13. [The Retroactive "Timesheet Savior" (Time-Traveling & Editing)](#13-the-retroactive-timesheet-savior-time-traveling--editing)
14. [Minimalist Meeting Notes & Action Items](#14-minimalist-meeting-notes--action-items)
15. [Expense & Subscription Auditing](#15-expense--subscription-auditing)
16. [The Media, Book, & Article Log](#16-the-media-book--article-log)

---

## 1. The "Anti-Burnout" Protocol (Wellness & Breaks)
It’s easy to hyperfocus and forget to step away from the keyboard. Use `dwriter` to enforce mandatory breaks and visualize your wellness over time.

* **Headless CLI:** Quickly start a 15-minute break timer and automatically tag it when done.
  ```bash
  dwriter timer 15 -t screen-break -t walking -p health
  ```
* **Interactive TUI:** Launch `dwriter timer` to view the large visual countdown. You can hit `Space` to pause/resume or `+`/`-` to adjust time. At the end of the week, open `dwriter stats` to see if `#screen-break` made it into your "Top Tags" chart.

## 2. The "Brag Document" & Performance Review Prep
When performance reviews roll around, it is notoriously difficult to remember the impact you made 6 months ago. 

* **Headless CLI:** Whenever you complete a major milestone or receive praise, log it instantly without breaking context.
  ```bash
  dwriter add "Led the successful DB migration with zero downtime!" -t milestone -p brag_doc
  ```
* **Interactive TUI:** When it's time to write your self-reflection, launch `dwriter search`. Press `/` and type `brag_doc`. Use `j` and `k` to scroll through a beautifully color-coded, chronological list of your biggest accomplishments.

## 3. The Student's Focus & Assignment Tracker
Manage assignments and actually sit down to study with focused pomodoro sessions.

* **Headless CLI:** Add your syllabus assignments from the terminal.
  ```bash
  dwriter todo "Write first draft of History term paper" --priority high -p history_101
  ```
* **Interactive TUI:** Open `dwriter todo`, select the assignment with `j`/`k`, and hit `+` to increase its priority to Red (Urgent). When you finish studying, hit `Space` to mark it complete and automatically log it to your daily journal.

## 4. Micro-Habit Stacking & Gamification
Turn `dwriter` into a minimalist, keyboard-driven habit tracker.

* **Headless CLI:** Add recurring habits as tasks.
  ```bash
  dwriter todo "Drink 2L of water" -t hydration -p habits
  ```
* **Interactive TUI:** Every morning, pop open `dwriter todo`. Simply hit `Space` on your habits to check them off. Because checking off a todo logs an entry, it counts toward your logging streak. Open `dwriter stats` to watch your GitHub-style contribution calendar grow!

## 5. The Freelancer & Creative's Billing Engine
Writers, designers, and consultants often juggle multiple clients and need to effortlessly log billable hours.

* **Headless CLI:** Generate a clean, markdown-formatted invoice payload for a specific client at the end of the week.
  ```bash
  dwriter review --days 7 -p client_acmecorp --format markdown
  ```
* **Interactive TUI:** Need to see what tasks are pending vs. completed for a client? Open `dwriter search`, filter by `client_acmecorp`, and press `Ctrl+N` to instantly toggle between your completed Entries and your pending Todos.

## 6. The Maker's Build Log (Woodworking, Gardening, Electronics)
Perfect for physical hobbies where your hands are dirty and you only have 5 seconds before walking away from the computer.

* **Headless CLI:** Lightning-fast logging.
  ```bash
  dwriter add "Planted heirloom tomatoes, watered with 10ml fertilizer" -t planting -p garden_2024
  ```
* **Interactive TUI:** Three weeks later, when you can't remember when the seeds were planted, open `dwriter search` and type "tomato". The fuzzy-finder handles typos, instantly highlighting the exact timestamp you planted them.

## 7. The "Second Brain" Idea Inbox
Don't let a random stroke of genius derail your current work session. 

* **Headless CLI:** Capture it in exactly 3 seconds.
  ```bash
  dwriter add "Idea: build a moisture sensor for the monstera plant" -t hardware -p someday
  ```
* **Interactive TUI:** Next time you are bored on a Sunday afternoon, open `dwriter search` and type `someday`. Your terminal instantly becomes a curated, easily scrollable list of past ideas ready to be built.

## 8. The Job Hunter's Interview & Application Tracker
Searching for a job involves managing parallel threads: applications sent, assignments, and prep.

* **Headless CLI:** Log submitted applications.
  ```bash
  dwriter add "Submitted application for Senior Backend Dev role" -p stripe_interview
  ```
* **Interactive TUI:** Ten minutes before your final round interview, open `dwriter search` and filter by the company name. You'll instantly see your past notes, submitted dates, and completed tasks right in your terminal, perfectly refreshing your memory.

## 9. The Language Learner's Immersion Log
Keep track of your study hours, grammar rules, and maintain your daily consistency.

* **Headless CLI:** Start a study timer directly from your shell.
  ```bash
  dwriter timer 30 -t listening_practice -p japanese_N4
  ```
* **Interactive TUI:** Launch the Dashboard (`dwriter stats`). The Weekly Chart and Contribution Calendar provide immediate visual feedback on your consistency, helping you visually identify if you've been skipping study days.

## 10. The Fitness PR & Routine Tracker
Typing out a workout log in a bulky fitness app between sets can be annoying. If your laptop is nearby, the terminal is faster.

* **Headless CLI:** Quickly log your lifts or meal prep.
  ```bash
  dwriter add "Deadlift: 3x5 @ 315lbs. Felt heavy today." -t lifting -p fitness
  ```
* **Interactive TUI:** Made a typo on the weight? Launch the Edit TUI (`dwriter edit`). Navigate to the mistake with `j`/`k`, press `e` to fix the text, or `t` to adjust the tags without wrestling with complex commands.

## 11. The Daily Gratitude & Evening Reflection Journal
`dwriter` is the perfect quiet environment for evening journaling and mood tracking.

* **Headless CLI:** Review today's work, then log your mental state.
  ```bash
  dwriter today
  dwriter add "Grateful for the sunny weather today." -t gratitude -p personal
  ```
* **Interactive TUI:** When you're having a rough week, open `dwriter search` and type `gratitude`. Use `j` and `k` to read through a clean, distraction-free list of all the positive moments you've captured.

## 12. The "Pre-Jira" Bug Scratchpad
Sometimes you spot a weird UI glitch, but you aren't ready to open a formal Jira ticket yet. 

* **Headless CLI:** Throw it into your scratchpad without losing your train of thought.
  ```bash
  dwriter todo "Investigate random 500 error on checkout" -t bug_hunt -p scratchpad
  ```
* **Interactive TUI:** Keep `dwriter todo` open on a second monitor during sprint planning. If a scratchpad bug turns out to be real, graduate it to Jira, then hit `Space` to mark it done. If it's a duplicate, press `d` to delete it forever.

## 13. The Retroactive "Timesheet Savior" (Time-Traveling & Editing)
We all forget to log our work sometimes. `dwriter` lets you fix history.

* **Headless CLI:** Use natural language dates to backdate entries if you completely forgot to log a weekend shift.
  ```bash
  dwriter add "Pushed hotfix for the database deadlock" --date "last Sunday" -p on_call
  ```
* **Interactive TUI:** If you logged something today but forgot to add the correct client project, open `dwriter edit`. Select the entry, press `p`, and type the correct project name.

## 14. Minimalist Meeting Notes & Action Items
Jumping from Zoom to Zoom leaves little time to organize notes. 

* **Headless CLI:** Log decisions and action items the second a meeting ends.
  ```bash
  dwriter add "Decision: We are pushing the v2 launch to Q3" -t decision -p weekly_sync
  dwriter todo "Email the finalized API spec to frontend" --priority high -p weekly_sync
  ```
* **Interactive TUI:** Before your next sync, open `dwriter search` and type `weekly_sync`. Toggle between your Entries (last week's decisions) and Todos (your pending action items) using `Ctrl+N`.

## 15. Expense & Subscription Auditing
Keep track of one-off business expenses, software subscriptions, or freelance write-offs.

* **Headless CLI:** Whenever you buy a tool, log it with the cost.
  ```bash
  dwriter add "Renewed GitHub Copilot for $100" -t software -p expenses_2024
  ```
* **Interactive TUI:** Come tax season, launch `dwriter search` and filter by `expenses_2024`. Hit `Enter` on any entry to instantly copy its full content to your clipboard so you can paste it into your tax spreadsheet.

## 16. The Media, Book, & Article Log
Act as a lightweight bookmarking and review system for articles and books.

* **Headless CLI:** Log what you read with a 1-sentence takeaway.
  ```bash
  dwriter add "Read Pragmatic Programmer Ch 2. Takeaway: use tracer bullets." -t book_notes
  ```
* **Interactive TUI:** If a coworker asks you about an architectural concept six months from now, launch `dwriter search`. The real-time filtering updates the results with every keystroke, helping you find your notes instantly even if you only remember a fraction of the title.
