# -*- coding: utf-8 -*-
"""Taxo 10.7-r1 — safe tachograph recognition fixes.

This layer intentionally patches the current tachograph module without rewriting
historical release layers. It keeps manual operator work immutable during
re-recognition and fixes circular/time-line edge cases around 00:00.
"""
from datetime import datetime
from pathlib import Path
import shutil


def circular_runs(mask, min_len=8):
    """Return circular True-runs as (start, end) with end allowed to exceed n."""
    values = [bool(x) for x in mask]
    n = len(values)
    if not n or not any(values):
        return []
    if all(values):
        return [(0, n)] if n >= min_len else []

    pivot = next(i for i, value in enumerate(values) if not value)
    runs = []
    start = None
    for step in range(1, n + 1):
        idx = (pivot + step) % n
        pos = pivot + step
        value = values[idx]
        if value and start is None:
            start = pos
        elif not value and start is not None:
            length = pos - start
            if length >= min_len:
                start_mod = start % n
                runs.append((start_mod, start_mod + length))
            start = None
    return runs


def timeline_segments(start_min, end_min):
    """Split one clock interval into drawable segments within a 0..1440 day."""
    start = int(start_min) % 1440
    end = int(end_min) % 1440
    if end == start:
        return []
    if end > start:
        return [(start, end)]
    return [(start, 1440), (0, end)]


def replace_auto_intervals(con, disc_id, items):
    """Replace only automatic candidates, preserving all operator/manual rows."""
    con.execute(
        "DELETE FROM intervals WHERE disc_id=? AND COALESCE(source,'auto')='auto'",
        (disc_id,),
    )
    for start_min, end_min, activity, confidence in items:
        con.execute(
            """INSERT INTO intervals(
                   disc_id,start_min,end_min,activity,confidence,source
               ) VALUES(?,?,?,?,?,?)""",
            (disc_id, start_min, end_min, activity, confidence, "auto"),
        )


def _slice_mean(values, start, end):
    n = len(values)
    if end <= n:
        sample = values[start:end]
    else:
        sample = list(values[start:n]) + list(values[0:end - n])
    if len(sample) == 0:
        return 0.0
    return float(sum(float(x) for x in sample) / len(sample))


def install(core, App):
    import tachograph as tacho

    def polar_signal_safe(path, cx, cy, radius, rotation_deg=0):
        if tacho.cv2 is None or tacho.np is None:
            return []
        img = tacho.cv2.imread(str(path), tacho.cv2.IMREAD_GRAYSCALE)
        if img is None:
            return []
        n = 1440
        angles = tacho.np.linspace(0, 2 * tacho.np.pi, n, endpoint=False)
        rs = tacho.np.linspace(radius * 0.42, radius * 0.63, 24)
        xx = []
        yy = []
        for rr in rs:
            a = angles + tacho.math.radians(rotation_deg)
            xx.append(cx + rr * tacho.np.cos(a))
            yy.append(cy + rr * tacho.np.sin(a))
        mapx = tacho.np.array(xx, dtype=tacho.np.float32)
        mapy = tacho.np.array(yy, dtype=tacho.np.float32)
        vals = tacho.cv2.remap(
            img, mapx, mapy, tacho.cv2.INTER_LINEAR,
            borderMode=tacho.cv2.BORDER_CONSTANT, borderValue=255,
        )
        darkness = (vals < 135).mean(axis=0)
        smooth = tacho.cv2.GaussianBlur(darkness.reshape(1, -1), (1, 0), 0).ravel()
        mask = smooth > max(0.13, float(tacho.np.percentile(smooth, 72)) * 0.78)

        out = []
        for start, end in circular_runs(mask, min_len=8):
            length = end - start
            if length > 500:
                continue
            sm = (start / n * 1440 + rotation_deg / 360 * 1440) % 1440
            em = (end / n * 1440 + rotation_deg / 360 * 1440) % 1440
            confidence = round(_slice_mean(smooth, start, end), 2)
            out.append((int(sm) % 1440, int(em) % 1440, "Керування", confidence))
        return out

    def recognize_rows(self, rows):
        total = 0
        con = tacho.tdb()
        try:
            for row in rows:
                rotation = float(row["rotation_deg"] or 0)
                items = polar_signal_safe(
                    tacho.scan_path(row["source_path"]),
                    row["cx"], row["cy"], row["radius"], rotation,
                )
                replace_auto_intervals(con, row["id"], items)
                manual_count = con.execute(
                    "SELECT COUNT(*) FROM intervals WHERE disc_id=? AND source='manual'",
                    (row["id"],),
                ).fetchone()[0]
                con.execute(
                    "UPDATE discs SET status=? WHERE id=?",
                    (
                        "Розпізнано — %d авто-кандидатів; ручних збережено: %d"
                        % (len(items), manual_count),
                        row["id"],
                    ),
                )
                total += len(items)
            con.commit()
        finally:
            con.close()
        return total

    def import_one_safe(self, path):
        source = Path(path)
        dest = tacho.SCAN_DIR / (
            datetime.now().strftime("%Y%m%d_%H%M%S_%f") + "_" + source.name
        )
        shutil.copy2(source, dest)
        circles = tacho.detect_discs(dest)
        detected = bool(circles)
        if not circles:
            circles = [(0, 0, 0)]

        ids = []
        con = tacho.tdb()
        try:
            for index, (cx, cy, radius) in enumerate(circles, 1):
                cur = con.execute(
                    """INSERT INTO discs(
                           source_path,scan_name,disc_no,cx,cy,radius,created_at
                       ) VALUES(?,?,?,?,?,?,?)""",
                    (
                        tacho.stored_scan_path(dest), source.name, index,
                        cx, cy, radius, datetime.now().isoformat(timespec="seconds"),
                    ),
                )
                ids.append(cur.lastrowid)
            con.commit()
        finally:
            con.close()

        if not detected:
            tacho.messagebox.showwarning(
                "Шайба",
                "Не вдалося автоматично знайти коло у %s. "
                "Запис збережено без автозапуску розпізнавання." % source.name,
                parent=self.parent,
            )
        return ids

    def import_scan_safe(self):
        paths = tacho.filedialog.askopenfilenames(
            parent=self.parent,
            title="Виберіть скани шайб",
            filetypes=[
                ("Зображення", "*.jpg *.jpeg *.png *.bmp"),
                ("Усі файли", "*.*"),
            ],
        )
        if not paths:
            return
        new_ids = []
        for path in paths:
            new_ids.extend(import_one_safe(self, Path(path)))
        self.load()

        if not new_ids:
            return
        placeholders = ",".join("?" for _ in new_ids)
        con = tacho.tdb()
        try:
            rows = con.execute(
                "SELECT * FROM discs WHERE id IN (%s) AND radius IS NOT NULL AND radius>0 "
                "ORDER BY id" % placeholders,
                tuple(new_ids),
            ).fetchall()
        finally:
            con.close()
        if rows:
            total = recognize_rows(self, rows)
            self.load()
            tacho.messagebox.showinfo(
                "Розпізнавання",
                "Імпортовано нових записів: %d. Автоматично оброблено тільки нові "
                "шайби: %d. Створено авто-кандидатів: %d."
                % (len(new_ids), len(rows), total),
                parent=self.parent,
            )

    def recognize_all_safe(self, silent=False):
        con = tacho.tdb()
        try:
            rows = con.execute(
                "SELECT * FROM discs WHERE radius IS NOT NULL AND radius>0 ORDER BY id"
            ).fetchall()
        finally:
            con.close()
        if not rows:
            tacho.messagebox.showwarning(
                "Розпізнавання", "Немає шайб із знайденим колом.", parent=self.parent
            )
            return
        total = recognize_rows(self, rows)
        self.load()
        if not silent:
            tacho.messagebox.showinfo(
                "Розпізнавання",
                "Оброблено шайб: %d. Створено авто-кандидатів: %d.\n\n"
                "Ручні інтервали не змінено. Автокандидати потрібно перевірити по зображенню."
                % (len(rows), total),
                parent=self.parent,
            )

    def recognize_selected_safe(self):
        row = self._selected()
        if not row:
            return
        if not row["radius"]:
            tacho.messagebox.showwarning(
                "Розпізнавання",
                "Для цієї шайби не знайдено коло.",
                parent=self.parent,
            )
            return
        try:
            rotation = float(self.v_rot.get().replace(",", "."))
        except Exception:
            rotation = 0

        # Use the current UI rotation for this explicit recognition and persist it.
        mutable = dict(row)
        mutable["rotation_deg"] = rotation
        total = recognize_rows(self, [mutable])
        con = tacho.tdb()
        try:
            con.execute(
                "UPDATE discs SET rotation_deg=? WHERE id=?", (rotation, row["id"])
            )
            con.commit()
        finally:
            con.close()
        self.select()
        tacho.messagebox.showinfo(
            "Розпізнавання",
            "Створено авто-кандидатів: %d. Ручні інтервали збережено. "
            "Автокандидати потрібно перевірити по зображенню." % total,
            parent=self.parent,
        )

    def select_safe(self):
        row = self._selected()
        if not row:
            return
        self.current_id = row["id"]
        self.v_date.set(self.fdate(row["disc_date"] or ""))
        self.v_rot.set(str(row["rotation_deg"] or 0))
        self.refresh_catalogs()
        did = row["driver_id"]
        vid = row["vehicle_id"]
        self.v_driver.set(next((k for k, v in self.driver_map.items() if str(v) == str(did)), ""))
        self.v_vehicle.set(next((k for k, v in self.vehicle_map.items() if str(v) == str(vid)), ""))
        self.show_image(row)
        self.load_intervals()
        self.candidate_var.set("Кандидатів: %d" % len(self.itree.get_children()))
        if hasattr(self, "stats_var"):
            self.update_stats()

    def draw_timeline_safe(self, rows=None):
        if not hasattr(self, "timeline_canvas"):
            return
        canvas = self.timeline_canvas
        canvas.delete("all")
        width = max(720, canvas.winfo_width())
        if width < 100:
            width = 900
        left = 42
        right = 16
        top = 24
        usable = max(100, width - left - right)
        axis_y = top + 32
        canvas.create_text(left, 10, anchor="w", text="00:00")
        for hour in range(25):
            x = left + usable * hour / 24
            canvas.create_line(x, axis_y - 8, x, axis_y + 8, fill="#888888")
            if hour < 24:
                canvas.create_text(
                    x, axis_y + 18, anchor="n", text="%02d" % hour, fill="#555555"
                )
        canvas.create_line(left, axis_y, left + usable, axis_y, fill="#555555", width=2)

        if rows is None and getattr(self, "current_id", None):
            con = tacho.tdb()
            try:
                rows = con.execute(
                    "SELECT * FROM intervals WHERE disc_id=? ORDER BY start_min",
                    (self.current_id,),
                ).fetchall()
            finally:
                con.close()
        rows = rows or []

        if not self.current_id:
            canvas.create_text(width / 2, 66, text="Оберіть шайбу", fill="#888888")
            self.timeline_hint.set("Оберіть шайбу")
            return

        lane_top = axis_y - 3
        lane_h = 18
        for row in rows:
            segments = timeline_segments(row["start_min"], row["end_min"])
            fill, outline = self._activity_style(row["activity"])
            for start, end in segments:
                x1 = left + usable * start / 1440
                x2 = left + usable * end / 1440
                if x2 - x1 < 2:
                    x2 = x1 + 2
                canvas.create_rectangle(
                    x1, lane_top, x2, lane_top + lane_h, fill=fill, outline=outline
                )
                if x2 - x1 >= 42:
                    canvas.create_text(
                        (x1 + x2) / 2,
                        lane_top + lane_h / 2,
                        text=row["activity"],
                        fill=outline,
                        font=("TkDefaultFont", 8),
                    )

        legend_y = 94
        x = left
        seen = []
        for row in rows:
            activity = row["activity"]
            if activity in seen:
                continue
            seen.append(activity)
            fill, outline = self._activity_style(activity)
            canvas.create_rectangle(x, legend_y, x + 14, legend_y + 12, fill=fill, outline=outline)
            canvas.create_text(
                x + 18, legend_y + 6, anchor="w", text=activity,
                fill=outline, font=("TkDefaultFont", 8),
            )
            x += 110 + len(activity) * 3
            if x > width - 120:
                break
        self.timeline_hint.set(
            "Періодів: %d. Подвійний клік по шкалі — відкрити редактор інтервалу."
            % len(rows)
        )

    tacho._polar_signal = polar_signal_safe
    tacho.TachographModule._import_one = import_one_safe
    tacho.TachographModule.import_scan = import_scan_safe
    tacho.TachographModule.recognize_all = recognize_all_safe
    tacho.TachographModule.recognize_selected = recognize_selected_safe
    tacho.TachographModule.select = select_safe
    tacho.TachographModule.draw_timeline = draw_timeline_safe

    core.APP_VERSION = "10.7-r1"
    return App
