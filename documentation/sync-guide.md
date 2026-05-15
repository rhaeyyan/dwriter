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
*   **Graph Index — Always Current:** The graph index updates incrementally in the background after every entry you add, so your AI 2nd-Brain and Analytics always reflect your latest work instantly. After a successful "Pull" from another device, it re-syncs automatically to incorporate changes from other machines too.
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

### "I see: `Push failed: error: src refspec main does not match any`"
This was a bug in versions before **v4.10.5** where the local sync repository was initialised with a `master` branch instead of `main`, but the push step always looked for `main`.

**If you are on v4.10.5 or later**, the fix is automatic — just run `dwriter sync` again and it will self-heal.

**If you are on an older version**, run this one-time command to fix it manually:
```bash
git -C ~/.dwriter/sync branch -m master main
```
Then retry `dwriter sync --push`.

---

[⬅️ Back to README](../README.md)
