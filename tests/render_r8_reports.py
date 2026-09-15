"""Create deterministic r8 report samples for visual QA (not user data)."""
import sys
import tempfile
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

_temporary_home=tempfile.TemporaryDirectory()
_original_path_home=Path.home
Path.home=classmethod(lambda cls:Path(_temporary_home.name))
try:
    import main
finally:
    Path.home=_original_path_home


def render(output_dir):
    output_dir=Path(output_dir); output_dir.mkdir(parents=True,exist_ok=True)
    main.DB_PATH=output_dir/"qa_r8.sqlite3"
    if main.DB_PATH.exists():
        main.DB_PATH.unlink()
    main.init_db(); con=main.db(); now="2031-09-01T08:00:00"
    con.execute("UPDATE company SET name=? WHERE id=1",("Тестове автобусне підприємство",))
    mechanic=con.execute(
        """INSERT INTO employees(personnel_no,last_name,first_name,middle_name,position,employment_date,active,created_at)
           VALUES(?,?,?,?,?,?,1,?)""",
        ("0017","Коваль","Марія","Іванівна","Механік","2031-09-01",now),
    ).lastrowid
    doctor=con.execute(
        """INSERT INTO employees(personnel_no,last_name,first_name,middle_name,position,employment_date,active,created_at)
           VALUES(?,?,?,?,?,?,1,?)""",
        ("0024","Мельник","Олена","Петрівна","Лікар","2031-09-01",now),
    ).lastrowid
    con.executemany("INSERT INTO employee_roles(employee_id,role) VALUES(?,?)",[(mechanic,"Механік"),(doctor,"Лікар")])
    for day_no in range(1,16):
        work_date=f"2031-09-{day_no:02d}"
        if day_no in (6,7,13,14):
            continue
        actual=None if day_no in (10,15) else (7.5 if day_no==9 else 8.0)
        con.execute(
            """INSERT INTO employee_time_entries(employee_id,work_date,day_type,planned_hours,actual_hours,notes,created_at,updated_at)
               VALUES(?,?,?,?,?,?,?,?)""",
            (mechanic,work_date,"Робота",8.0,actual,"ремонт автобуса" if day_no==9 else "",now,now),
        )
        con.execute(
            """INSERT INTO employee_time_entries(employee_id,work_date,day_type,planned_hours,actual_hours,notes,created_at,updated_at)
               VALUES(?,?,?,?,?,?,?,?)""",
            (doctor,work_date,"Робота",8.0,8.0,"",now,now),
        )
    con.commit(); con.close()
    main.export_employee_timesheet_xlsx(mechanic,2031,9,output_dir/"employee_timesheet_r8.xlsx")
    main.export_employee_timesheet_pdf(mechanic,2031,9,output_dir/"employee_timesheet_r8.pdf")
    main.export_personnel_monthly_balance_xlsx(2031,9,output_dir/"personnel_balance_r8.xlsx")
    main.export_personnel_monthly_balance_pdf(2031,9,output_dir/"personnel_balance_r8.pdf")


if __name__=="__main__":
    render(sys.argv[1] if len(sys.argv)>1 else ROOT/"tmp"/"r8_report_qa")
