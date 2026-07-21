# CANRI Android Launcher

החבילה מכילה Launcher לאנדרואיד שנכתב ב-Python וב-Kivy.

## מה הוא עושה

1. קורא GitHub Releases.
2. מציג גרסאות שיש להן ZIP ששמו מכיל `android`.
3. מוריד ומתקין את הגרסה שנבחרה.
4. מפעיל את CANRI בתוך מסך האפליקציה.

## חשוב

ה-Launcher לא יכול להריץ את גרסת Windows של CANRI. גרסת CANRI לאנדרואיד חייבת להשתמש ב-Kivy, לא ב-Tkinter, ולהכיל `canri_entry.py` עם פונקציה `build_screen(on_back)` שמחזירה Widget.

## בניית APK בלי להתקין Python

1. צור מאגר GitHub חדש.
2. העלה אליו את כל הקבצים.
3. פתח Actions.
4. פתח `Build Android APK`.
5. לחץ `Run workflow`.
6. הורד את ה-APK מתוך Artifacts.

GitHub בונה את האפליקציה בענן, לכן אין צורך להתקין Python או Buildozer בטלפון.

## מאגר פרטי

אפשר להזין Token במסך ההגדרות. אל תכניס Token לתוך הקוד ואל תשלח אותו לאנשים. להפצה עדיף מאגר Releases ציבורי שמכיל רק קובצי Android מוכנים.
