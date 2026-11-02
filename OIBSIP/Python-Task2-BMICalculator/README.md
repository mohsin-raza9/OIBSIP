# OIBSIP Python Programming Task 2: BMI Calculator (Advanced)

Desktop BMI calculator using Python, Tkinter, SQLite and Matplotlib.

## Features
- GUI inputs for named user, weight (kg), and height (m)
- BMI formula: `weight / (height ** 2)` and two-decimal result
- Categories: Underweight (<18.5), Normal (18.5 to <25), Overweight (25 to <30), Obese (>=30)
- Colour-coded result, input validation and helpful error messages
- Multiple named users with user-specific history
- SQLite persistence in `bmi_records.db`
- Matplotlib line chart of saved BMI records over time
- Database read/write error handling

## Requirements
Python 3.10+ recommended. Tkinter is included with most Windows Python installations.

Install Matplotlib:
```bash
python -m pip install matplotlib
```

## Run
```bash
python bmi_calculator.py
```

Enter a name, weight in kg, and height in metres, then choose **Calculate & Save**. Save multiple records for the same user to build a trend. Select another username to view that user's history.

## Storage and privacy
The app creates `bmi_records.db` in this folder. It stores username, weight, height, BMI, category, and local timestamp. Records are separated by username in queries, but this is not a login/authentication system. The database is not encrypted, so do not keep sensitive information in a shared/public folder. Do not commit the database file to GitHub.

## BMI note
BMI is a screening measure, not a diagnosis. Interpretation can vary by age, pregnancy status, muscle mass and other factors. This educational project does not replace professional medical advice.
