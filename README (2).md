# To-Do List App

A clean desktop to-do list built with **Python and Tkinter**. Add, edit, complete and remove tasks. Everything is saved automatically, so your list is waiting for you next time.

## Features

- **Add tasks** with the button or by pressing **Enter**
- **Mark tasks done / undo** (button or double-click a task)
- **Edit** any task
- **Remove** a task (button or **Delete** key)
- **Clear completed** tasks in one click, with a confirmation
- **Auto-save** to `tasks.json` after every change and when you close the window
- **Task counter** showing total and completed tasks
- **Input checks** for empty tasks and missing selections
- Imports tasks from `tasks.txt` if you used the first version of the app

## Project Structure

```
├── to_do_list.py    # The application
├── tasks.json       # Created automatically when you add your first task
└── README.md
```

## Requirements

- Python 3.8 or newer
- Tkinter (included with the standard Python installer on Windows and macOS)

On some Linux systems, install Tkinter first:

```bash
sudo apt install python3-tk
```

No other libraries are needed.

## Getting Started

```bash
git clone https://github.com/niks175/To_Do_List.git
cd To_Do_List
python to_do_list.py
```

## How to Use

| Action | How |
|---|---|
| Add a task | Type it in the box, then click **Add Task** or press **Enter** |
| Complete a task | Select it and click **Done / Undo**, or double-click it |
| Edit a task | Select it and click **Edit** |
| Remove a task | Select it and click **Remove**, or press **Delete** |
| Clear finished tasks | Click **Clear Completed** |

Completed tasks show `[x]` and appear in grey. Changes are saved automatically.

## How It Works

- Each task is stored as `{"text": "...", "done": true/false}`.
- Tasks are saved as JSON in `tasks.json`, in the same folder as the script.
- If `tasks.json` is damaged, the app warns you and starts with an empty list instead of crashing.

## Ideas for Future Improvements

- Due dates and priorities
- Search and filter
- Dark mode

## Contributing

Suggestions and improvements are welcome. Open an issue or submit a pull request.
