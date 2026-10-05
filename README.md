# Secure Random Password Generator

A Python desktop password generator built for the **Oasis Infobyte Python Programming Internship - Task 3**.

## Objective

Build a strong random password generator based on user-defined criteria.

This project implements the **Advanced Tier**, which includes all Beginner Tier requirements plus a graphical interface, cryptographically secure generation, password strength feedback, clipboard integration, ambiguous-character exclusion, and session-only history.

## Features

### Beginner requirements

- Minimum password length of 8 characters
- User-controlled character types:
  - Uppercase letters
  - Lowercase letters
  - Numbers
  - Symbols
- Requires at least two character types
- Input validation
- Generates another password without restarting the application

### Advanced requirements

- Tkinter GUI
- Password length control from 8 to 64 characters
- Character-type checkboxes
- Python `secrets` module for cryptographically secure generation
- Password strength indicator: Weak / Medium / Strong
- Guarantees at least one character from every selected character type
- Copy to Clipboard functionality using Tkinter's clipboard interface
- Optional exclusion of ambiguous characters such as `0`, `O`, `l`, `1`, `I`, and `|`
- Last 5 generated passwords displayed during the current session
- Password history is not saved to disk

## Tech Stack

- Python 3
- Tkinter
- `secrets`
- `string`

No third-party Python packages are required.

## Project Structure

```text
Python-Task3-RandomPasswordGenerator/
├── password_generator.py
└── README.md
```

## Requirements

- Python 3.8 or newer
- Tkinter installed with your Python distribution

Check Python:

```bash
python --version
```

## How to Run

Clone the repository or download the project folder.

Open a terminal inside the project directory:

```bash
python password_generator.py
```

On some Windows installations, use:

```bash
py password_generator.py
```

## How to Use

1. Choose a password length between 8 and 64.
2. Select at least two character types.
3. Optionally enable ambiguous-character exclusion.
4. Click **Generate Password**.
5. The generated password is automatically copied to the clipboard.
6. Check the strength indicator.
7. Use **Generate Again** whenever another password is needed.
8. The last five generated passwords remain visible only during the current application session.

## Security Notes

The project uses Python's `secrets` module instead of `random` because passwords are security-sensitive values.

Generated passwords are not written to a file or database. The displayed history exists only while the application is running.

The strength indicator is a simple project-level heuristic based on password length and character diversity. It is not a formal password-strength audit.

## Testing Checklist

- [ ] Length below 8 is rejected
- [ ] Fewer than 2 character types is rejected
- [ ] Uppercase characters can be selected
- [ ] Lowercase characters can be selected
- [ ] Numbers can be selected
- [ ] Symbols can be selected
- [ ] Every selected type appears in the generated password
- [ ] Ambiguous characters can be excluded
- [ ] Generated password is copied to clipboard
- [ ] Strength indicator updates
- [ ] Generate Again works without restarting
- [ ] Only the latest 5 passwords appear in history
- [ ] Password history is not saved to a file

## Internship Submission

Track: **Python Programming**

Task: **Task 3 - Random Password Generator**

Tier: **Advanced**

GitHub folder naming:

```text
OIBSIP/Python-Task3-RandomPasswordGenerator/
```

The project should be demonstrated in a screen recording with the required title card:

**Full Name + Python Programming + Task 3 - Random Password Generator**

The LinkedIn post should tag Oasis Infobyte and include:

```text
#oasisinfobyte
#python
#pythonprogramming
#internship
```
