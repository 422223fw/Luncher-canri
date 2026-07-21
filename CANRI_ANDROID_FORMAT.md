# מבנה ZIP של CANRI לאנדרואיד

שם מומלץ ל-Release Asset:

`CANRI-1.0.0-android.zip`

מבנה:

```text
CANRI-1.0.0-android/
├── canri_entry.py
├── brains/
├── data/
└── assets/
```

הקובץ `canri_entry.py` חייב להכיל:

```python
def build_screen(on_back):
    return root_widget
```

הקבצים שיורדו נמצאים בטלפון ולכן משתמש מתקדם עדיין עשוי לקרוא אותם. אל תשמור סיסמאות, מפתחות או Tokens בתוך CANRI.
