# 📖 dwriter: 21 Creative Workflows for Everyone

**dwriter** is a tool for reflection and tracking. While built for the terminal, its minimalist design makes it remarkably versatile for any hobby, profession, or lifestyle. Whether you are coding, brewing, learning, or managing, dwriter adapts to your needs.

With the addition of the **2nd-Brain**, dwriter moves beyond a passive archive to an active partner that synthesizes your history into actionable insights. Features like **Fact Memory**, **Graph Traversal**, **Standup Automation**, and **Obsidian Export** make it a complete productivity layer — not just a log file.

> **How to use the 2nd-Brain examples in this guide:** Run `dwriter` to open the TUI, navigate to the **🧠 2nd-Brain** tab, then press **💬 Follow-up** to open the freeform chat modal. All example questions labelled *"2nd-Brain:"* below are meant to be typed there.

---

## 💻 For Developers & Engineers
*You live in the terminal. Why leave it to track your work?*

### 1. The "Pre-Jira" Bug Scratchpad
Capture weird glitches before they become formal tickets — with automatic Git context attached.
*   **Fast CLI:** Drop a bug into your scratchpad without leaving your terminal. `&branch:fix/auth` and `&repo:my-app` are auto-appended.
    ```bash
    dwriter add "500 error intermittently on /checkout #bug"
    ```
*   **2nd-Brain:** Correlate issues: *"I've seen three checkout errors this week. Are they related to the database migration I logged last Tuesday?"*

### 2. The "Timesheet Savior" (Backdating)
Fix your history if you forgot to log a session — then generate a standup from the reconstructed record.
*   **Fast CLI:** Log work for a past date using natural language, then turn it into a standup.
    ```bash
    dwriter add "Worked on auth hotfix" --date "last Sunday"
    dwriter standup
    ```
*   **2nd-Brain:** Reconstruct your week: *"I forgot to log most of Tuesday. Based on my other logs, what did I likely work on?"*

### 3. The "Anti-Burnout" Protocol
Enforce mandatory breaks during long coding sessions.
*   **Fast CLI:** Launch a 15-minute break timer.
    ```bash
    dwriter timer "15 #screen-break"
    ```
*   **2nd-Brain:** Audit your focus hygiene: *"How many breaks did I take during my 4-hour grind yesterday? Did it affect my energy levels in the evening?"*

---

## 💼 For Freelancers & Consultants
*Time is money. Track it seamlessly and turn logs into invoices.*

### 4. The Freelancer's Billing Engine
Log your billable tasks as they happen, then generate a client-ready report in one command.
*   **Fast CLI:** Log billable work, then export a formatted weekly summary.
    ```bash
    dwriter add "Built OAuth integration for login flow #backend &client:acme"
    dwriter review --days 7 --obsidian
    ```
*   **2nd-Brain:** Analyze profitability: *"Compare time spent on client Acme vs client Bravo. Which has the highest effort-to-revenue ratio?"*

### 5. Expense & Subscription Auditing
Track business software expenses for tax season — and wire dwriter into your budgeting scripts.
*   **Fast CLI:** Log a renewal with a tag; pull structured stats anytime.
    ```bash
    dwriter add "Renewed GitHub Copilot $100 #software &expenses"
    dwriter stats --json | jq '.tag_totals["software"]'
    ```
*   **2nd-Brain:** Forecast burn rate: *"What is my projected software spend for the year? Are there subscriptions I haven't used in 3 months?"*

### 6. Minimalist Meeting Notes
Capture decisions the second a meeting ends — then pipe them into your reporting pipeline.
*   **Fast CLI:** Log a key decision, then pull today's entries as JSON for automation.
    ```bash
    dwriter add "Decision: pushing launch to Q3 &meetings"
    dwriter today --json | python3 scripts/sync_to_notion.py
    ```
*   **2nd-Brain:** Track the decision chain: *"Why did we decide to push to Q3? What were the main blockers mentioned in the May 12th meeting?"*

---

## 🚀 For Leaders & Managers
*Keep your team aligned, track wins, and ace your own performance reviews.*

### 7. The Manager's 1-on-1 Tracker
Keep track of small wins and feedback for your team members — and never forget to follow up.
*   **Fast CLI:** Log a win the moment it happens, then set a reminder.
    ```bash
    dwriter add "Sarah crushed the Q2 presentation today &team:sarah"
    dwriter remind "Send Sarah written feedback" --at "Friday 3pm"
    ```
*   **2nd-Brain:** Prepare for 1-on-1s: *"Give me a summary of Sarah's wins and challenges over the last month for our meeting today."*

### 8. The "Brag Document" for Performance Reviews
When performance reviews arrive, you'll have a complete, AI-ready record of your impact.
*   **Fast CLI:** Log a win the moment it happens.
    ```bash
    dwriter add "Led the zero-downtime DB migration &career #milestone"
    dwriter standup --obsidian
    ```
*   **2nd-Brain:** Impact synthesis: *"Generate a bulleted list of my high-impact contributions to the backend architecture this quarter."*

### 9. The Job Hunter's Application Tracker
Manage multiple interview threads and application dates without a spreadsheet.
*   **Fast CLI:** Log a submitted application.
    ```bash
    dwriter add "Applied for Senior Backend role at Stripe &jobs"
    ```
*   **2nd-Brain:** Manage the pipeline: *"What are my active interview threads? When was the last time I followed up with Google?"*

---

## 🎓 For Students & Academics
*Manage deadlines, synthesize reading, and connect research dots across semesters.*

### 10. The Student's Deadline Manager
Never drop an assignment again. Triaging your chaotic semester takes seconds.
*   **Fast CLI:** Add deadlines, snooze what can wait, and set reminders.
    ```bash
    dwriter todo add "Submit History term paper" --due "Friday 11pm" --priority urgent
    dwriter snooze 12 --for 2d
    ```
*   **2nd-Brain:** Optimize your schedule: *"When is my peak focus window for deep work based on my last two weeks of timers?"*

### 11. The Research Scientist's Lab Notebook
A fast-capture notebook that the 2nd-Brain can traverse with graph queries.
*   **Fast CLI:** Log each trial with structured tags.
    ```bash
    dwriter add "Trial 3: catalyst temp 220°C → yield 78% #result &chem:rxn-b"
    ```
*   **2nd-Brain (Graph Traversal):** Drill into patterns: *"Run a graph query to find all trials where yield exceeded 70% and compare their shared conditions."*

### 12. The Media, Book, & Article Log
Create a "Second Brain" for everything you consume.
*   **Fast CLI:** Log a one-sentence takeaway from a book chapter.
    ```bash
    dwriter add "Read Pragmatic Programmer Ch 2: Tracer bullets &books"
    ```
*   **2nd-Brain:** Connect the dots: *"I'm starting a new project on microservices. What relevant takeaways do I have from my recent reading?"*

---

## 🎨 For Creators & Hobbyists
*Your projects span weeks. Keep your momentum and capture fleeting ideas.*

### 13. The Idea Inbox
Don't let a random stroke of genius derail your current work.
*   **Fast CLI:** Capture the idea in 3 seconds.
    ```bash
    dwriter add "Idea: build a moisture sensor for the garden &someday"
    ```
*   **2nd-Brain:** Cluster your creativity: *"Look at my 'someday' list. Are there any common themes I could combine?"*

### 14. The Fermenter's Log (Brewing & Sourdough)
Tracking temperatures and timings is the only way to replicate a masterpiece.
*   **Fast CLI:** Log a reading in seconds while your hands are busy.
    ```bash
    dwriter add "Brew Day: OG 1.054. Mashed at 152°F &brew:pale-ale"
    ```
*   **2nd-Brain:** Scientific Synthesis: *"Based on my last 5 batches, how does mash temperature affect my final gravity?"*

### 15. The Maker's Build Log (Woodworking & Garden)
Keep a running narrative of physical projects that span weeks.
*   **Fast CLI:** Quickly log a milestone before putting your tools away.
    ```bash
    dwriter add "Applied first coat of tung oil to the desk &woodworking"
    ```
*   **2nd-Brain:** Project health check: *"Show me the velocity of the desk project. Where am I spending the most time?"*

---

## 🌿 For Everyday Life & Wellbeing
*Cultivate habits, improve health, and remember the best parts of your day.*

### 16. Micro-Habit Stacking
Turn dwriter into a minimalist habit tracker — with a built-in audit trail.
*   **Fast CLI:** Add a habit as a task. Mark it done to auto-log a timestamp.
    ```bash
    dwriter todo add "Drink 2L of water" --priority normal
    dwriter done 7
    ```
*   **2nd-Brain:** Identity Analytics: *"Which habits am I most likely to skip on days when I have high work velocity?"*

### 17. The Fitness PR & Routine Tracker
Typing in a bulky app at the gym is annoying. The terminal is your fastest workout log.
*   **Fast CLI:** Log your lifts between sets.
    ```bash
    dwriter add "Deadlift PR: 3x5 @ 315lbs #lifting &fitness"
    ```
*   **2nd-Brain:** Predictive Recovery: *"Looking at my fitness logs and daily energy levels, am I showing signs of burnout?"*

### 18. The Language Learner's Immersion Log
Consistency is key — and the 2nd-Brain's Fact Memory learns your goals.
*   **Fast CLI:** Start a focused study session and log reflections.
    ```bash
    dwriter timer "30 &bangla #listening"
    ```
*   **2nd-Brain (Fact Memory):** Tell the AI your goal once: *"Remember that I want to reach conversational Bangla by August."*

### 19. The Daily Gratitude & Reflection Journal
A quiet space for evening reflection.
*   **Fast CLI:** End your day by capturing what mattered.
    ```bash
    dwriter add "Grateful for the sunny weather today #gratitude"
    ```
*   **2nd-Brain:** Emotional Intelligence: *"What have been the recurring themes of my gratitude logs this month?"*

### 20. The Traveler's Memory Journal
Capture small moments without writing long essays you'll never read.
*   **Fast CLI:** Log a restaurant or a hidden gem.
    ```bash
    dwriter add "Visited Little Island at Pier 55 &trip:nyc-2026"
    ```
*   **2nd-Brain:** Re-live the trip: *"What were the highlights of my NYC trip? Remind me of that coffee shop near the park."*

### 21. The Strategic Retrospective (2nd-Brain)
Identify long-term patterns and friction points across your entire history.
*   **💬 Follow-up (Graph Traversal):** *"Run a graph traversal to find which projects co-occur most often with my low-energy logs."*
*   **💬 Follow-up (Fact Memory):** *"What facts have you extracted from my logs so far? Show me my durable goals and preferences."*
*   **Preset Briefings:** Use the **Weekly Retro** trigger for a structured behavioral archetype analysis.

---

[⬅️ Back to README](../README.md)
