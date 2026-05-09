# 📖 dwriter: 21 Creative Workflows

**dwriter** is a tool for reflection. While it shines in a developer's toolkit, its minimalist design makes it remarkably versatile for any hobby or profession where tracking progress matters.

With the addition of the **2nd-Brain**, dwriter moves beyond a passive archive to an active partner that synthesizes your history into actionable insights. Features like **Fact Memory**, **Graph Traversal**, **Standup Automation**, and **Obsidian Export** make it a complete productivity layer — not just a log file.

> **How to use the 2nd-Brain examples in this guide:** Run `dwriter` to open the TUI, navigate to the **🧠 2nd-Brain** tab, then press **💬 Follow-up** to open the freeform chat modal. All example questions labelled *"2nd-Brain:"* below are meant to be typed there.

---

## 🍲 1. The Fermenter's Log (Brewing & Sourdough)
Baking and brewing are sciences of patience. Tracking temperatures and timings is the only way to replicate a masterpiece.

*   **Fast CLI:** Log a reading in seconds while your hands are busy.
    ```bash
    dwriter add "Brew Day: OG 1.054. Mashed at 152°F &brew:pale-ale"
    ```
*   **2nd-Brain:** Ask for correlations: *"Based on my last 5 batches, how does mash temperature affect my final gravity?"*

**The Benefit: Scientific Synthesis.** By correlating months of logs, the 2nd-Brain identifies hidden variables — like how seasonal ambient temperature shifts affect fermentation speed — turning "getting lucky" into repeatable mastery.

## 🛠️ 2. The Maker's Build Log (Woodworking & Garden)
Physical projects often span weeks. Keep a running narrative of your progress.

*   **Fast CLI:** Quickly log a milestone before putting your tools away.
    ```bash
    dwriter add "Applied first coat of tung oil to the desk &woodworking"
    ```
*   **2nd-Brain:** Get a project health check: *"Show me the velocity of the desk project. Where am I spending the most time?"*

**The Benefit: Lifecycle Optimization.** Seeing a log of small milestones provides psychological momentum, but the 2nd-Brain takes it further by identifying "friction phases" (like sanding or drying) where you typically lose steam, helping you plan your next build more realistically.

## 🏆 3. The "Brag Document" for Performance Reviews
When performance reviews arrive, you'll have a complete, AI-ready record of your impact — and can send a formatted report to your manager in seconds.

*   **Fast CLI:** Log a win the moment it happens.
    ```bash
    dwriter add "Led the zero-downtime DB migration &career #milestone"
    ```
*   **Standup Automation:** Generate a polished summary and push it directly to your Obsidian vault:
    ```bash
    dwriter standup --obsidian
    ```
    Or open **💬 Follow-up** and ask: *"Generate a bulleted list of my high-impact contributions to the backend architecture this quarter."*

**The Benefit: Automated Impact Synthesis.** Humans suffer from "recency bias." The 2nd-Brain eliminates the dread of self-review by instantly surfacing a year's worth of data-backed achievements. The `--obsidian` flag delivers a formatted Markdown report straight to your vault — ready to paste into any review doc or share with your manager.

## 🎓 4. The Student's Deadline Manager
Never drop an assignment again. dwriter turns a chaotic semester into a prioritized queue you can triage in seconds.

*   **Fast CLI:** Add a deadline with urgency, snooze anything that can wait, and set reminders for study blocks.
    ```bash
    # Add with a hard due date and priority
    dwriter todo add "Submit History term paper" --due "Friday 11pm" --priority urgent

    # Snooze a lower-priority task by two days to protect mental bandwidth
    dwriter snooze 12 --for 2d

    # Set a reminder for your next study block
    dwriter remind "Start essay outline" --at "9am tomorrow"
    ```
*   **2nd-Brain:** Optimize your schedule: *"When is my peak focus window for deep work based on my last two weeks of timers?"*

**The Benefit: Cognitive Load Management.** By offloading deadlines into a trusted system and using `snooze` to aggressively triage, you reduce anxiety and protect your best thinking for your hardest subjects. The 2nd-Brain identifies your "Golden Hours" so you align deep work with your highest energy levels.

## 🔬 5. The Research Scientist's Lab Notebook
Science is a log of experiments. dwriter gives you a fast-capture notebook that the 2nd-Brain can traverse with graph queries — surfacing patterns across months of trials.

*   **Fast CLI:** Log each trial with structured tags and sub-projects.
    ```bash
    dwriter add "Trial 3: catalyst temp 220°C → yield 78% #result &chem:rxn-b"
    dwriter todo add "Test lower range: 180–200°C" --priority high &chem:rxn-b
    ```
*   **2nd-Brain (Graph Traversal):** Drill into patterns across experiments: *"Run a graph query to find all trials where yield exceeded 70% and compare their shared conditions."*

**The Benefit: Graph-Powered Discovery.** The 2nd-Brain's `run_cypher` tool traverses the LadybugDB graph index to find non-obvious correlations between trials — connections that would require manually scanning dozens of entries. What took an afternoon of spreadsheet work takes one question.

## ✈️ 6. The Traveler's Memory Journal
When traveling, capturing small moments beats writing long essays you'll never read.

*   **Fast CLI:** Log a restaurant or a hidden gem using sub-projects.
    ```bash
    dwriter add "Visited Little Island at Pier 55 &trip:nyc-2026"
    ```
*   **2nd-Brain:** Re-live the trip: *"What were the highlights of my NYC trip? Remind me of that coffee shop near the park."*

**The Benefit: Semantic Memory Retrieval.** Traditional journals are hard to search. The 2nd-Brain uses Local RAG to help you "re-live" the vibe of a trip through natural conversation, making your memories as accessible as a search engine.

## 🏮 7. The Language Learner's Immersion Log
Consistency is the only secret to learning a language — and the 2nd-Brain's **Fact Memory** learns your goals so you never have to re-state them.

*   **Fast CLI:** Start a focused study session and log reflections afterward.
    ```bash
    dwriter timer "30 &bangla #listening"
    dwriter add "Finished unit 7. Struggling with verb conjugations. #vocab &bangla"
    ```
*   **2nd-Brain (Fact Memory):** Tell the AI your goal once — it persists forever:
    *"Remember that I want to reach conversational Bangla by August."*
    The **Closed Learning Loop** automatically extracts this as a durable **Fact** node in the graph, referenced in every future session without being re-prompted.

**The Benefit: Personalized, Stateful Coaching.** Unlike a chat app that forgets you between sessions, dwriter's Fact Memory makes the 2nd-Brain permanently aware of your target level, preferred learning style, and weak spots — giving you advice that compounds over months, not just the current session.

## 🏋️ 8. The Fitness PR & Routine Tracker
Typing in a bulky app at the gym is annoying. If you work from home, the terminal is your fastest workout log.

*   **Fast CLI:** Log your lifts between sets.
    ```bash
    dwriter add "Deadlift PR: 3x5 @ 315lbs #lifting &fitness"
    ```
*   **2nd-Brain:** Detect overtraining: *"Looking at my fitness logs and my daily energy levels, am I showing signs of burnout?"*

**The Benefit: Predictive Recovery.** Beyond simple PR tracking, the 2nd-Brain correlates your physical output with your logged energy levels and sleep, helping you decide when to push for a new record and when to take a deload week.

## 📚 9. The Media, Book, & Article Log
Create a "Second Brain" for everything you consume.

*   **Fast CLI:** Log a one-sentence takeaway from a book chapter.
    ```bash
    dwriter add "Read Pragmatic Programmer Ch 2: Tracer bullets &books"
    ```
*   **2nd-Brain:** Connect the dots: *"I'm starting a new project on microservices. What relevant takeaways do I have from my recent reading?"*
    The `search_graph` tool performs a full-text search across all your entries and todos via the graph index — surfacing the relevant passage even if you tagged it months ago.

**The Benefit: Interdisciplinary Insight.** Logging transforms passive reading into active learning. The 2nd-Brain acts as "connective tissue," surfacing relevant ideas from books you read months ago that apply to the problem you're solving today.

## 🧘 10. The Daily Gratitude & Reflection Journal
A quiet space for evening reflection.

*   **Fast CLI:** End your day by capturing what mattered.
    ```bash
    dwriter add "Grateful for the sunny weather today #gratitude"
    ```
*   **2nd-Brain:** Reflect on well-being: *"What have been the recurring themes of my gratitude logs this month? What makes me most consistently happy?"*

**The Benefit: Emotional Intelligence.** Regularly logging gratitude "rewires" the brain. The 2nd-Brain helps you identify the specific "happiness anchors" in your life — certain people, activities, or environments — allowing you to double down on what actually improves your mood.

## ☕ 11. The "Anti-Burnout" Protocol
Enforce mandatory breaks during long coding sessions.

*   **Fast CLI:** Launch a 15-minute break timer.
    ```bash
    dwriter timer "15 #screen-break"
    ```
*   **2nd-Brain:** Audit your focus hygiene: *"How many breaks did I take during my 4-hour grind yesterday? Did it affect my energy levels in the evening?"*

**The Benefit: Behavioral Intervention.** High-focus workers often ignore cues of exhaustion. The 2nd-Brain uses your timer and energy data to prove that "forced deceleration" actually increases your total daily output by preventing the afternoon slump.

## 💡 12. The Idea Inbox
Don't let a random stroke of genius derail your current work.

*   **Fast CLI:** Capture the idea in 3 seconds.
    ```bash
    dwriter add "Idea: build a moisture sensor for the garden &someday"
    ```
*   **2nd-Brain:** Cluster your creativity: *"Look at my 'someday' project list. Are there any common themes or ideas that I could combine?"*

**The Benefit: Conceptual Clustering.** By "parking" ideas, you preserve flow state. The 2nd-Brain later helps you synthesize these "sparks" into larger projects, identifying when multiple small ideas are actually part of a single bigger vision.

## 💧 13. Micro-Habit Stacking
Turn dwriter into a minimalist habit tracker — with a built-in audit trail for every completion.

*   **Fast CLI:** Add a habit as a task. When done, complete it with a single command that auto-logs a timestamped journal entry.
    ```bash
    # Add the habit as a task
    dwriter todo add "Drink 2L of water" --priority normal

    # Mark complete — auto-creates a journal entry with a completion timestamp
    dwriter done 7
    ```
*   **2nd-Brain:** Analyze habit consistency: *"Which habits am I most likely to skip on days when I have high work velocity?"*

**The Benefit: Identity Analytics.** Every `dwriter done` is both a checkbox and a data point. The audit trail lets the 2nd-Brain surface friction points — like how a busy sprint kills your hydration habit — so you can adjust your environment rather than just your willpower.

## 🤝 14. The Manager's 1-on-1 Tracker
Keep track of small wins and feedback for your team members — and never forget to follow up.

*   **Fast CLI:** Log a win the moment it happens, then set a reminder to close the loop.
    ```bash
    dwriter add "Sarah crushed the Q2 presentation today &team:sarah"
    dwriter remind "Send Sarah written feedback" --at "Friday 3pm"
    ```
*   **2nd-Brain:** Prepare for 1-on-1s: *"Give me a summary of Sarah's wins and challenges over the last month for our meeting today."*

**The Benefit: Contextual Leadership.** Having a searchable history makes feedback meaningful. The `remind` command keeps you accountable between logs, and the 2nd-Brain ensures you never walk into a 1-on-1 with "blank page syndrome" — providing specific, data-backed examples of growth and impact.

## 💰 15. The Freelancer's Billing Engine
Log your billable tasks as they happen, then generate a client-ready report in one command.

*   **Fast CLI:** Log work as it happens, then export a formatted weekly summary.
    ```bash
    # Log billable work under a client sub-project
    dwriter add "Built OAuth integration for login flow #backend &client:acme"

    # Generate a 7-day summary and push to your Obsidian vault
    dwriter review --days 7 --obsidian
    ```
*   **2nd-Brain:** Analyze profitability: *"Compare the time spent on client Acme vs client Bravo. Which has the highest effort-to-revenue ratio?"*

**The Benefit: Financial Intelligence.** Real-time tracking ensures you're paid for every minute of work. The `--obsidian` flag delivers a clean Markdown report to your vault — ready to paste into your billing system. The 2nd-Brain adds business strategy by identifying which clients are genuinely profitable.

## 💼 16. The Job Hunter's Application Tracker
Manage multiple interview threads and application dates without a spreadsheet.

*   **Fast CLI:** Log a submitted application.
    ```bash
    dwriter add "Applied for Senior Backend role at Stripe &jobs"
    ```
*   **2nd-Brain:** Manage the pipeline: *"What are my active interview threads? When was the last time I followed up with the recruiter at Google?"*

**The Benefit: Anxiety Reduction.** Job hunting is a high-volume numbers game. The 2nd-Brain acts as a "personal recruiter," keeping you organized and reducing the cognitive load of managing multiple high-stakes conversations simultaneously.

## 🐞 17. The "Pre-Jira" Bug Scratchpad
Capture weird glitches before they become formal tickets — with automatic Git context attached.

*   **Fast CLI:** Drop a bug into your scratchpad without leaving your terminal. When inside a Git repo, dwriter automatically appends your current branch and repo name as tags.
    ```bash
    # Run from your repo — &branch:fix/auth and &repo:my-app are auto-appended
    dwriter add "500 error intermittently on /checkout #bug"
    ```
*   **2nd-Brain:** Correlate issues: *"I've seen three checkout errors this week. Are they related to the database migration I logged last Tuesday?"*

**The Benefit: Root-Cause Synthesis.** Don't break your flow to open Jira. Workspace Awareness means every bug is automatically linked to the branch it was found on — making cross-branch and cross-repo correlation a question you can ask in plain English.

## 🕒 18. The "Timesheet Savior" (Backdating)
Fix your history if you forgot to log a session — then generate a standup from the reconstructed record.

*   **Fast CLI:** Log work for a past date using natural language, then turn it into a standup.
    ```bash
    dwriter add "Worked on auth hotfix" --date "last Sunday"

    # Generate a structured daily standup from the reconstructed logs
    dwriter standup
    ```
*   **2nd-Brain:** Reconstruct your week: *"I forgot to log most of Tuesday. Based on my other logs from that day, what did I likely work on?"*

**The Benefit: Historical Integrity.** Life is messy. The ability to backdate entries ensures your activity log remains accurate. `dwriter standup` then converts your reconstructed history into a formatted report — exactly what you'd send to your team, with zero manual formatting.

## 📝 19. Minimalist Meeting Notes
Capture decisions and action items the second a meeting ends — then pipe them into your reporting pipeline.

*   **Fast CLI:** Log a key decision, then pull today's entries as JSON for automation.
    ```bash
    dwriter add "Decision: pushing launch to Q3 &meetings"

    # Export today's full log as machine-readable JSON for scripts or Notion sync
    dwriter today --json | python3 scripts/sync_to_notion.py
    ```
*   **2nd-Brain:** Track the decision chain: *"Why did we decide to push to Q3? What were the main blockers mentioned in the May 12th meeting?"*

**The Benefit: Institutional Memory.** Verbal agreements often vanish. The 2nd-Brain turns your quick notes into a searchable "Decision Registry." The `--json` flag makes dwriter a first-class data source for any downstream automation — Notion, Slack bots, Waybar widgets, or custom dashboards.

## 💳 20. Expense & Subscription Auditing
Track business software expenses for tax season — and wire dwriter into your own budgeting scripts.

*   **Fast CLI:** Log a renewal with a tag; pull structured stats anytime.
    ```bash
    dwriter add "Renewed GitHub Copilot $100 #software &expenses"

    # Pull machine-readable stats for a budget script
    dwriter stats --json | jq '.tag_totals["software"]'
    ```
*   **2nd-Brain:** Forecast burn rate: *"What is my projected software spend for the year based on my current logs? Are there any subscriptions I haven't used in 3 months?"*

**The Benefit: Financial Awareness.** Small subscriptions are "death by a thousand cuts." The `--json` flag makes it trivial to wire dwriter into a spreadsheet or Waybar panel. The 2nd-Brain identifies underutilized tools and forecasts your annual burn rate — making tax season and budget audits effortless.

## 🧠 21. The Strategic Retrospective (2nd-Brain)
Identify long-term patterns and friction points across your entire history — using graph traversal and durable Fact Memory.

*   **💬 Follow-up (Graph Traversal):** Open the Follow-up chat and ask the 2nd-Brain to surface patterns invisible in a chronological log:
    *"Run a graph traversal to find which projects co-occur most often with my low-energy logs. What's the pattern?"*
*   **💬 Follow-up (Fact Memory):** Review what dwriter has permanently learned about you:
    *"What facts have you extracted from my logs so far? Show me my durable goals and preferences."*
*   **Preset Briefings:** Use **Weekly Retro** or **Pulse** trigger for a structured "7-Day Pulse" — your behavioral archetype (e.g., "The Deep Diver" or "The Firefighter") computed from timer, energy, and activity data.

**The Benefit: Pattern Discovery at Scale.** We often miss the "forest for the trees" when logging day-to-day. The 2nd-Brain's `run_cypher` tool traverses the LadybugDB graph index to surface recurring struggles, peak performance windows, and behavioral shifts that aren't visible in a linear view. Combined with Fact Memory — a persistent knowledge base built from your own language — you get a retrospective partner that knows you better with every entry.

---

[⬅️ Back to README](../README.md)
