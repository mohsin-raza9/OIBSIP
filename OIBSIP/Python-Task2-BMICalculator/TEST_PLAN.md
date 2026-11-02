# Manual Test Plan

Run `python bmi_calculator.py` first.

| Test | Input/action | Expected |
|---|---|---|
| Normal | Alice, 70 kg, 1.75 m | BMI 22.86, Normal, green |
| Underweight | 45 kg, 1.70 m | BMI 15.57, Underweight |
| Overweight | 80 kg, 1.70 m | BMI 27.68, Overweight |
| Obese | 100 kg, 1.70 m | BMI 34.60, Obese |
| Non-numeric | Weight `abc` | Error; no record saved |
| Empty | Leave height empty | Error; no record saved |
| Zero/negative | Weight `0`, or height `-1.7` | Error |
| Wrong height unit | Height `175` | Error explaining height should be metres |
| Multi-user | Save Alice and Bob records | Each name sees only its own history |
| Persistence | Save, close, reopen | Record remains |
| Graph | Save 2+ records for a user | Line chart shows saved points over time |
| DB error | Test only in a copy with database write access blocked | Friendly error, no unhandled traceback |
