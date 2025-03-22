# Inspectk

**Release Date:** 2025-03-21
**Author:** Lion Kimbro
**Install:** `pip install inspectk`

## 🧠 What is Inspectk?

Inspectk opens a live Tkinter window to explore Python variables on the current call stack.

Just drop this into your code at any point:

```python
import inspectk
breakpoint()
inspectk.go()
```

You’ll get an interactive window showing local and global variables, help for the variables, and the interiors of the objects — super handy for debugging.

## 📸 Screenshot

<p align="center">
  <img src="src/screenshot.png" alt="Inspectk screenshot" width="600"/>
</p>

## 📦 Installation

```bash
pip install inspectk
```

## 💡 Use Case

Useful when you want to:
- Pause and peek inside objects at a breakpoint
- Read help on your objects
- Access a tkinter based GUI for debugging, outside of IDLE

---

Made with 🐍 + ❤️ by 🦁