# 🔄 How to Sync Your Journal Across Devices (Easy Guide)

This guide will help you keep your **dwriter** journal consistent whether you're on your work laptop, home PC, or a second machine. 

---

## 🏗️ Step 1: The "Cloud" Home (One-Time Setup)

To sync your data, you need a central "home" for it. We use **GitHub** (or any Git provider) because it is free, secure, and private.

1.  **Create a Repository:** Go to [GitHub](https://github.com/new) and create a new **Private** repository named `my-journal-sync`. 
    *   *Important:* Keep it **Private** so only you can see your notes!
    *   Do **not** initialize it with a README or license.
2.  **Copy the Link:** You will get a link that looks like this: `https://github.com/your-username/my-journal-sync.git`. Copy it.

---

## 🔗 Step 2: Connect Your First Device

On your primary computer (where your journal is currently located):

1.  Open your terminal.
2.  Run this command (replace the link with yours):
    ```bash
    dwriter sync --remote "https://github.com/your-username/my-journal-sync.git"
    ```
3.  **Push your data:** Send your current notes to the cloud:
    ```bash
    dwriter sync --push
    ```

---

## 💻 Step 3: Connect Your Second Device

On your second computer (after installing **dwriter**):

1.  Open the terminal.
2.  Run the same connection command:
    ```bash
    dwriter sync --remote "https://github.com/your-username/my-journal-sync.git"
    ```
3.  **Pull your data:** Download your notes from the cloud:
    ```bash
    dwriter sync --pull
    ```

---

## 🚀 Step 4: Daily Use (Automatic Sync)

**dwriter** is designed to handle syncing for you automatically.

*   **When you start:** Every time you open the TUI (by typing `dwriter`), it automatically "Pulls" (downloads) any new changes from your other devices.
*   **When you work:** Every time you add a note or complete a task, **dwriter** waits 10 seconds and then "Pushes" (uploads) the change to the cloud in the background.
*   **Manual Sync:** If you ever want to force a sync right now, just type:
    ```bash
    dwriter sync
    ```

---

## ❓ Common Questions

### "What if I edit the same note on two computers at once?"
Don't worry! **dwriter** uses "Smart Merging" (technical term: CRDT). It compares the timestamps and keeps the most recent version of every note. You won't lose data.

### "How do I know if it's working?"
In the Visual Dashboard (`dwriter`), look at the **Status Bar** at the bottom. 
- `[✅ Synced]` means you're up to date.
- `[🧠 Syncing...]` means it's talking to the cloud right now.

### "Can I use this without a remote cloud?"
Yes! Syncing is completely optional. If you don't set a `--remote`, your data stays only on your local machine.

---

[⬅️ Back to README](../README.md)
