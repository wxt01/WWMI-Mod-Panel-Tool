# -*- coding: utf-8 -*-
"""WWMI MOD 面板助手 - 图形界面（注入式）
首启选语言+MOD目录 -> 选Mod -> 选方案 -> 注入面板 -> 备份/回滚/调整/改字
"""
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine
import history
from i18n import get_dict

APP_DIR = history.APP_DIR


def log(msg):
    try:
        p = os.path.join(APP_DIR, "panel_tool.log")
        with open(p, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass


class PanelToolApp:
    def __init__(self, root):
        self.root = root
        self.settings = history.get_settings()
        if not isinstance(self.settings, dict):
            self.settings = {"lang": "zh"}
        self.lang = self.settings.get("lang", "zh")
        self.T = get_dict(self.lang)
        self.mod_dir = None
        self.injected_ini = None
        self._build_ui()
        self._refresh_records()

    # ---------- UI ----------
    def _build_ui(self):
        T = self.T
        self.root.title(T["app_title"])
        self.root.geometry("940x560")
        self.root.minsize(780, 440)

        top = ttk.Frame(self.root, padding=(10, 8, 10, 4))
        top.pack(fill="x")
        self.ent_dir = ttk.Entry(top, width=30, state="readonly")
        self.ent_dir.pack(side="left", fill="x", expand=True)
        self.btn_select = ttk.Button(top, text=T["select_mod"], command=self._pick_mod)
        self.btn_select.pack(side="left", padx=(6, 0))
        self.btn_add = ttk.Button(top, text=T["add_panel"], command=self._add_panel, state="disabled")
        self.btn_add.pack(side="left", padx=(6, 0))
        self.btn_edit = ttk.Button(top, text=T["edit_labels"], command=self._edit_labels, state="disabled")
        self.btn_edit.pack(side="left", padx=(6, 0))
        self.btn_settings = ttk.Button(top, text=T["settings"], command=self._open_settings)
        self.btn_settings.pack(side="left", padx=(6, 0))
        self.btn_ai = ttk.Button(top, text=T["ai_prompt"], command=self._show_ai_prompt)
        self.btn_ai.pack(side="left", padx=(6, 0))
        self.btn_about = ttk.Button(top, text=T["about"], command=self._show_help)
        self.btn_about.pack(side="left", padx=(6, 0))

        mid = ttk.LabelFrame(self.root, text=T["generated_files"], padding=(10, 6))
        mid.pack(fill="both", expand=True, padx=10, pady=(4, 6))
        cols = ("mod", "time", "method", "count", "key", "status")
        self.tree = ttk.Treeview(mid, columns=cols, show="headings", selectmode="browse")
        for c, w, txt in (("mod", 250, T["col_mod"]), ("time", 135, T["col_time"]),
                          ("method", 70, T["col_method"]), ("count", 55, T["col_count"]),
                          ("key", 190, T["col_key"]), ("status", 90, T["col_status"])):
            self.tree.heading(c, text=txt)
            self.tree.column(c, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda e: self._rollback_selected())
        self.tree.bind("<Button-3>", self._show_context_menu)

        bottom = ttk.Frame(self.root, padding=(10, 4, 10, 8))
        bottom.pack(fill="x")
        self.btn_scan = ttk.Button(bottom, text=T["scan_panels"], command=self._scan_panels)
        self.btn_scan.pack(side="left")
        self.btn_rb_all = ttk.Button(bottom, text=T["rollback_all"], command=self._rollback_all)
        self.btn_rb_all.pack(side="left", padx=(8, 0))
        self.btn_clear = ttk.Button(bottom, text=T["clear_records"], command=self._clear_records)
        self.btn_clear.pack(side="left", padx=(8, 0))
        self.lbl_status = ttk.Label(bottom, text="", foreground="#555")
        self.lbl_status.pack(side="right")

    # ---------- 工具 ----------
    def _t(self):
        return get_dict(self.lang)

    def _status(self, msg):
        self.lbl_status.config(text=msg)
        self.root.after(8000, lambda: self.lbl_status.config(text=""))

    def _pick_mod(self):
        start = self.settings.get("mod_start_dir") or os.path.expanduser("~")
        d = filedialog.askdirectory(title=self._t()["select_mod"], initialdir=start)
        if not d:
            return
        self.mod_dir = d
        self.ent_dir.config(state="normal")
        self.ent_dir.delete(0, "end")
        self.ent_dir.insert(0, d)
        self.ent_dir.config(state="readonly")
        ini = engine.find_injected_ini(d)
        self.injected_ini = ini
        self.btn_add.config(state="normal")
        self.btn_edit.config(state="normal" if ini else "disabled")
        if ini:
            self._status(self._t()["panel_exists"].format(path="") + "  " + os.path.basename(ini))

    def _add_panel(self):
        T = self._t()
        if not self.mod_dir:
            self._err(T["select_folder_first"], T["select_folder_first"])
            return
        if self.injected_ini:
            self._err(T["panel_exists"], T["panel_exists_detail"].format(path=self.injected_ini))
            return
        self._run_bg(self._do_add_panel)

    def _do_add_panel(self):
        T = self._t()
        try:
            buttons, used_keys = engine.parse_mod_keys(self.mod_dir)
        except Exception as e:
            self.root.after(0, lambda: self._err(T["fail_title"], T["fail_msg"].format(
                mod=os.path.basename(self.mod_dir), reason=str(e))))
            return
        if not buttons:
            self.root.after(0, lambda: self._err(T["no_keys_found"], T["no_keys_detail"]))
            return

        inis = sorted(set(b["src"] for b in buttons))
        if len(inis) == 1:
            ini_path = inis[0]
        else:
            rec, info = engine.recommend_ini(buttons)
            ini_path = self._ask_ini(inis, T, info=info, rec=rec)
        if ini_path is None:
            return

        method = self._ask_method(buttons, T)
        if method is None:
            return
        # 图片自定义（测试功能，设置内开关）
        layout_override = None
        if self.settings.get("custom_images"):
            mode = self._ask_inject_mode(T)
            if mode is None:
                return
            if mode == "custom":
                cust = self._ask_custom(buttons, T)
                if cust is None:
                    return
                self._write_custom_files(cust, os.path.dirname(ini_path))
                # 自定义注入：有图 -> 背景放大20% + fill（放大铺满/居中）；
                # 无图 -> 普通布局，仅按用户设置的每行按钮数（cols）
                has_img = bool(cust.get("bg")) or bool(cust.get("btns"))
                layout_override = {"cols": int(cust.get("cols") or 0) or None}
                if has_img:
                    layout_override["pw_scale"] = 1.2
                    layout_override["fill"] = bool(cust.get("fill", True))
        lay = engine.make_layout(len(buttons), layout_override)
        pref = self.settings.get("toggle_key") or "/"
        toggle_key = engine.pick_toggle_key(used_keys, pref)

        last_err = "unknown"
        key_summary = " / ".join(engine.key_display(b["key"]) for b in buttons if b.get("key"))
        if len(key_summary) > 200:
            key_summary = key_summary[:200] + "…"
        for m in (method, 2 if method == 1 else None):
            if m is None:
                break
            try:
                bak = engine.inject_panel(ini_path, buttons, m, os.path.basename(self.mod_dir),
                                          toggle_key, layout=lay, lang=self.lang)
                history.add_record(self.mod_dir, os.path.basename(self.mod_dir), ini_path,
                                   bak, m, len(buttons), toggle_key, key_summary)
                self.root.after(0, lambda: self._ok(
                    T["success_title"],
                    T["success_msg"].format(mod=os.path.basename(self.mod_dir),
                                            count=len(buttons), key=toggle_key)))
                self.root.after(0, self._refresh_records)
                self.root.after(0, lambda: self.btn_edit.config(state="normal"))
                return
            except Exception as e:
                last_err = str(e)
                if m == 1:
                    again = messagebox.askyesno(T["fail_title"], T["fail_retry_method2"])
                    if again:
                        continue
                self.root.after(0, lambda: self._err(T["fail_title"], T["fail_msg"].format(
                    mod=os.path.basename(self.mod_dir), reason=last_err)))
                return
        self.root.after(0, lambda: self._err(T["fail_title"], T["fail_msg"].format(
            mod=os.path.basename(self.mod_dir), reason=last_err)))

    def _ask_ini(self, inis, T, info=None, rec=None):
        win = tk.Toplevel(self.root)
        win.title(T["method_pick_title"])
        win.geometry("660x440")
        win.transient(self.root)
        win.grab_set()
        if info:
            ttk.Label(win, text=T["multi_ini_hint"], wraplength=620,
                      justify="left", foreground="#333").pack(padx=12, pady=8)
        else:
            ttk.Label(win, text=T["method_pick_desc"]).pack(padx=12, pady=8)
        lb = tk.Listbox(win, font=("Consolas", 9))
        for p in inis:
            if info:
                item = p
                for ini, c, ns, sc in info:
                    if ini == p:
                        mark = " >> " if (rec and ini == rec) else "    "
                        nsm = " ns=%s" % ns if ns else ""
                        item = "%s %2d keys%s  %s" % (mark, c, nsm, p)
                        break
                lb.insert("end", item)
            else:
                lb.insert("end", p)
        lb.pack(fill="both", expand=True, padx=12, pady=4)
        result = {"v": None}

        def choose():
            sel = lb.curselection()
            if sel:
                result["v"] = inis[sel[0]]
            win.destroy()

        def cancel():
            win.destroy()

        ttk.Button(win, text=T["ok"], command=choose).pack(side="right", padx=12, pady=8)
        ttk.Button(win, text=T["cancel"], command=cancel).pack(side="right", pady=8)
        self.root.wait_window(win)
        return result["v"]

    def _ask_inject_mode(self, T):
        """自定义/通用注入方式选择弹窗。返回 'custom' / 'normal' / None(取消)"""
        win = tk.Toplevel(self.root)
        win.title(T["custom_mode_title"])
        win.geometry("520x240")
        win.transient(self.root)
        win.grab_set()
        result = {"v": None}
        ttk.Label(win, text=T["custom_mode_desc"], wraplength=480, justify="left",
                  foreground="#333").pack(padx=16, pady=(16, 8))
        frm = ttk.Frame(win)
        frm.pack(pady=4)
        ttk.Button(frm, text=T["custom_mode_btn1"], width=46,
                   command=lambda: (result.__setitem__("v", "custom"), win.destroy())).pack(pady=4)
        ttk.Button(frm, text=T["custom_mode_btn2"], width=46,
                   command=lambda: (result.__setitem__("v", "normal"), win.destroy())).pack(pady=4)
        ttk.Button(win, text=T["cancel"], command=win.destroy).pack(pady=10)
        self.root.wait_window(win)
        return result["v"]

    def _ask_custom(self, buttons, T):
        """自定义面板图片弹窗：背景尺寸+选背景图 / 按钮两列逐按钮选图 / 透明度 / 取消继续。
        返回 {"bg": path|"", "btns": {1:path}, "opacity": str} 或 None(取消)"""
        win = tk.Toplevel(self.root)
        win.title(T["custom_title"])
        win.geometry("720x640")
        win.transient(self.root)
        win.grab_set()
        result = {"v": None}

        # 行列设置（可调每行按钮数，行数自动计算）
        _n = len(buttons)
        _def_cols = engine.make_layout(_n)["cols"]
        rowfrm = ttk.Frame(win)
        rowfrm.pack(fill="x", padx=14, pady=(10, 0))
        ttk.Label(rowfrm, text=T["custom_total"].format(n=_n)).pack(side="left")
        ttk.Label(rowfrm, text=T["custom_cols"]).pack(side="left", padx=(16, 4))
        cols_var = tk.IntVar(value=_def_cols)
        ttk.Spinbox(rowfrm, from_=1, to=9, textvariable=cols_var, width=3).pack(side="left")
        _rows_lbl = ttk.Label(rowfrm, text="", foreground="#333")
        _rows_lbl.pack(side="left", padx=(16, 0))
        ttk.Label(win, text=T["custom_cols_hint"], foreground="#888").pack(padx=14, anchor="w")

        # 尺寸标签（随列数联动）
        _size_lbl = ttk.Label(win, text="", foreground="#333")
        _size_lbl.pack(padx=14, pady=(4, 2), anchor="w")

        def _update_geom(*_a):
            try:
                _c = max(1, cols_var.get())
            except Exception:
                _c = _def_cols
            _rows_lbl.config(text=T["custom_rows"].format(r=(_n + _c - 1) // _c))
            try:
                _lay = engine.make_layout(_n, {"pw_scale": 1.2, "fill": True, "cols": _c})
                _size_lbl.config(text=T["custom_bg_size"].format(
                    pw=round(_lay["pw"] * 1920), ph=round(_lay["ph"] * 1920)))
            except Exception:
                pass

        cols_var.trace_add("write", _update_geom)
        _update_geom()

        # 第一栏：背景图
        bg_row2 = ttk.Frame(win)
        bg_row2.pack(fill="x", padx=14, pady=(8, 0))
        bg_row = bg_row2
        bg_var = {"path": ""}
        bg_lbl = ttk.Label(bg_row, text="", foreground="#555")
        fill_var = tk.BooleanVar(value=True)

        def pick_bg():
            p = filedialog.askopenfilename(
                title=T["custom_pick_bg"],
                filetypes=[("图片", "*.png;*.jpg;*.jpeg;*.bmp;*.webp"), ("PNG", "*.png"), ("全部", "*.*")])
            if p:
                bg_var["path"] = p
                bg_lbl.config(text=os.path.basename(p))

        ttk.Button(bg_row, text=T["custom_pick_bg"], command=pick_bg).pack(side="left", padx=(0, 10))
        bg_lbl.pack(side="left")
        ttk.Checkbutton(bg_row, text=T["custom_fill"], variable=fill_var).pack(side="left", padx=(16, 0))

        # 按钮两列
        ttk.Label(win, text=T["custom_btn_section"], foreground="#333").pack(padx=14, pady=(12, 2), anchor="w")
        frm = ttk.Frame(win)
        frm.pack(fill="both", expand=True, padx=14)
        btn_vars = {}
        for idx, b in enumerate(buttons):
            i = idx + 1
            row, col = divmod(idx, 2)
            label = engine.translate_label(b.get("label", ""), self.lang) if b.get("label") else str(i)
            ttk.Label(frm, text="%d. %s" % (i, label), width=16, anchor="w").grid(
                row=row, column=col * 3, sticky="w", padx=(0, 6), pady=3)
            v = {"path": ""}
            btn_vars[i] = v
            flbl = ttk.Label(frm, text="", width=15, anchor="w", foreground="#555")

            def make_pick(vi, vv, lbl):
                def pick():
                    p = filedialog.askopenfilename(
                        title=T["custom_pick_btn"],
                        filetypes=[("图片", "*.png;*.jpg;*.jpeg;*.bmp;*.webp"), ("PNG", "*.png"), ("全部", "*.*")])
                    if p:
                        vv["path"] = p
                        lbl.config(text=os.path.basename(p))
                return pick

            ttk.Button(frm, text=T["custom_pick_btn"], command=make_pick(i, v, flbl)).grid(
                row=row, column=col * 3 + 1, padx=(0, 8), pady=3)
            flbl.grid(row=row, column=col * 3 + 2, sticky="w", pady=3)

        # 透明度
        op_row = ttk.Frame(win)
        op_row.pack(fill="x", padx=14, pady=(8, 4))
        ttk.Label(op_row, text=T["custom_opacity"]).pack(side="left")
        op_var = tk.StringVar()
        ttk.Entry(op_row, textvariable=op_var, width=8).pack(side="left", padx=10)

        # 底部
        btns = ttk.Frame(win)
        btns.pack(fill="x", padx=14, pady=10)

        def go():
            try:
                _c = max(1, cols_var.get())
            except Exception:
                _c = _def_cols
            result["v"] = {"bg": bg_var["path"],
                           "btns": {i: v["path"] for i, v in btn_vars.items() if v["path"]},
                           "opacity": op_var.get().strip(),
                           "fill": bool(fill_var.get()),
                           "cols": _c}
            win.destroy()

        ttk.Button(btns, text=T["custom_continue"], command=go).pack(side="right", padx=(10, 0))
        ttk.Button(btns, text=T["cancel"], command=win.destroy).pack(side="right")
        self.root.wait_window(win)
        return result["v"]

    def _write_custom_files(self, cust, mod_dir):
        """把自定义图片复制到 mod_dir/zz_panel_custom/（bg.png / 1.png..N.png / opacity.txt）"""
        import shutil
        if not cust or not mod_dir:
            return
        cdir = os.path.join(mod_dir, "zz_panel_custom")
        try:
            os.makedirs(cdir, exist_ok=True)
            if cust.get("bg"):
                shutil.copy2(cust["bg"], os.path.join(cdir, "bg.png"))
            for i, pp in (cust.get("btns") or {}).items():
                shutil.copy2(pp, os.path.join(cdir, "%d.png" % i))
            op = cust.get("opacity")
            if op:
                fv = float(op)
                if 0 <= fv <= 100:
                    with open(os.path.join(cdir, "opacity.txt"), "w", encoding="utf-8") as f:
                        f.write(str(int(fv)))
        except Exception:
            pass

    def _ask_method(self, buttons, T):
        win = tk.Toplevel(self.root)
        win.title(T["method_pick_title"])
        win.geometry("640x440")
        win.transient(self.root)
        win.grab_set()
        ttk.Label(win, text=T["method_pick_desc"]).pack(padx=12, pady=8)
        frame = ttk.Frame(win)
        frame.pack(fill="both", expand=True, padx=12, pady=4)
        result = {"v": None}

        def choose(m):
            result["v"] = m
            win.destroy()

        prev1 = ", ".join(engine.translate_label(b["label"], self.lang) for b in buttons[:16])
        if len(buttons) > 16:
            prev1 += "  ...(共%d 个)" % len(buttons)
        prev2 = ", ".join(str(i) for i in range(1, min(len(buttons), 16) + 1))
        if len(buttons) > 16:
            prev2 += "  ...(共%d 个)" % len(buttons)

        for m, title, desc, prev in ((1, T["method1"], T["method1_desc"], prev1),
                                     (2, T["method2"], T["method2_desc"], prev2)):
            box = ttk.LabelFrame(frame, text=title, padding=10)
            box.pack(fill="x", pady=6)
            ttk.Label(box, text=desc, justify="left", wraplength=580).pack(anchor="w")
            ttk.Label(box, text=T["preview_label"] + prev, justify="left",
                      wraplength=580, foreground="#2a6a2a").pack(anchor="w", pady=(6, 2))
            ttk.Button(box, text=T["btn_use"], command=lambda m=m: choose(m)).pack(anchor="e", pady=(6, 0))
        self.root.wait_window(win)
        return result["v"]

    # ---------- 备份列表 ----------
    def _refresh_records(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        T = self._t()
        for r in history.get_records():
            method = ("M1" if r.get("method") == 1 else "M2") if r.get("method") else "-"
            self.tree.insert("", "end", values=(
                r.get("mod_name", "-"), r.get("time", "-"), method,
                r.get("button_count", "-"), r.get("toggle_key", "-") or "-",
                T["status_ok"]))

    def _selected_record(self):
        sel = self.tree.selection()
        if not sel:
            return None
        idx = self.tree.index(sel[0])
        recs = history.get_records()
        return recs[idx] if 0 <= idx < len(recs) else None

    def _rollback_selected(self, rec=None):
        T = self._t()
        rec = rec or self._selected_record()
        if not rec:
            return
        ini, bak = rec.get("ini_path") or "", rec.get("bak_path") or ""
        if not ini or not os.path.isfile(ini):
            self._err(T["record_gone"], T["record_gone_detail"])
            return
        if not messagebox.askyesno(T["rollback_confirm"], T["rollback_confirm"].format(
                mod=rec.get("mod_name", ""))):
            return
        try:
            engine.rollback(ini, bak)  # engine 自动找最早备份并清理全部
            history.remove_record(rec["mod_path"])
            self._refresh_records()
            self._status(T["rollback_done"].format(mod=rec.get("mod_name", "")))
        except Exception as e:
            self._err(T["fail_title"], str(e))

    def _rollback_all(self):
        T = self._t()
        recs = history.get_records()
        if not recs:
            return
        if not messagebox.askyesno(T["rollback_all_confirm"], T["rollback_all_confirm"]):
            return
        fail = []
        for r in recs:
            ini, bak = r.get("ini_path"), r.get("bak_path")
            if ini and os.path.isfile(ini):
                try:
                    engine.rollback(ini, bak)  # engine 自动找最早备份并清理全部
                except Exception:
                    fail.append(r.get("mod_name", "?"))
            else:
                fail.append(r.get("mod_name", "?"))
        history.clear_records()
        self._refresh_records()
        msg = T["rollback_all_done"]
        if fail:
            msg += "\n" + T["fail_msg"].format(mod=",".join(fail), reason="文件缺失")
        self._status(msg)
        messagebox.showinfo(T["success_title"], msg)

    def _clear_records(self):
        T = self._t()
        history.clear_records()
        self._refresh_records()
        self._status(T["clear_done"])

    def _scan_panels(self):
        T = self._t()
        root = (self.settings.get("mod_start_dir") or "").strip()
        if not root or not os.path.isdir(root):
            self._err(T["scan_need_dir"], T["scan_need_dir_detail"])
            return
        found = engine.scan_panels(root)
        if not found:
            self._status(T["scan_empty"])
            messagebox.showinfo(T["scan_title"], T["scan_empty"])
            return
        existing = set(r.get("mod_path") for r in history.get_records())
        n_new = 0
        for r in found:
            if r["mod_path"] in existing:
                continue
            history.add_record(r["mod_path"], r["mod_name"], r["ini_path"], r["bak_path"],
                               r["method"], r["button_count"], r["toggle_key"],
                               r["key_summary"])
            existing.add(r["mod_path"])
            n_new += 1
        self._refresh_records()
        msg = T["scan_done"].format(n=n_new)
        self._status(msg)
        messagebox.showinfo(T["scan_title"], msg)

    # ---------- 右键菜单 ----------
    def _show_context_menu(self, event):
        T = self._t()
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        self.tree.selection_set(iid)
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label=T["menu_rollback"], command=self._rollback_selected)
        menu.add_separator()
        for key, act in (("menu_bigger", "bigger"), ("menu_smaller", "smaller"),
                         ("menu_taller", "taller"), ("menu_wider", "wider"),
                         ("menu_reset", "reset")):
            menu.add_command(label=T[key], command=lambda a=act: self._adjust(a))
        menu.add_separator()
        menu.add_command(label=T["menu_open"], command=self._open_labels)
        menu.add_command(label=T["edit_labels"], command=self._edit_labels)
        menu.tk_popup(event.x_root, event.y_root)

    def _adjust(self, action):
        T = self._t()
        rec = self._selected_record()
        if not rec:
            return
        ini = rec.get("ini_path") or ""
        if not ini or not os.path.isfile(ini):
            self._err(T["record_gone"], T["record_gone_detail"])
            return
        try:
            engine.adjust(ini, action)
            self._refresh_records()
            name = {"bigger": T["adjust_bigger"], "smaller": T["adjust_smaller"],
                    "taller": T["adjust_taller"], "wider": T["adjust_wider"],
                    "reset": T["adjust_reset"]}[action]
            self._status(T["adjust_done"].format(action=name, mod=rec.get("mod_name", "")))
        except Exception as e:
            self._err(T["fail_title"], T["fail_msg"].format(
                mod=rec.get("mod_name", ""), reason=str(e)))

    def _open_labels(self):
        rec = self._selected_record()
        if not rec:
            return
        ini = rec.get("ini_path") or ""
        lp = os.path.join(os.path.dirname(ini), engine.LABELS_FILE) if ini else ""
        if not os.path.isfile(lp):
            self._err(self._t()["fail_title"], self._t()["no_file"].format(path=lp))
            return
        try:
            os.startfile(lp)
        except Exception:
            import subprocess
            subprocess.Popen(["notepad", lp])

    def _edit_labels(self):
        T = self._t()
        rec = self._selected_record()
        ini = rec.get("ini_path") if rec else self.injected_ini
        if not ini or not os.path.isfile(ini):
            self._err(T["need_select_for_adjust"], T["need_select_for_adjust"])
            return
        data = engine.load_labels(ini)
        if data is None:
            self._err(T["fail_title"], T["no_panel_record"])
            return
        win = tk.Toplevel(self.root)
        win.title(T["edit_title"])
        win.geometry("500x560")
        win.transient(self.root)
        win.grab_set()
        ttk.Label(win, text=T["edit_desc"]).pack(padx=10, pady=6)
        txt = tk.Text(win, wrap="word", font=("Microsoft YaHei", 11))
        txt.pack(fill="both", expand=True, padx=10, pady=4)
        txt.insert("1.0", "\n".join(data.get("labels", [])))

        def apply():
            lines = [l.strip() for l in txt.get("1.0", "end").splitlines()]
            lines = [l for l in lines if l]
            try:
                engine.apply_labels(ini, lines)
                win.destroy()
                self._status(T["edit_done"])
                messagebox.showinfo(T["success_title"], T["edit_done"])
            except Exception as e:
                messagebox.showerror(T["edit_title"],
                                     T["edit_fail"].format(reason=str(e)))

        ttk.Button(win, text=T["edit_apply"], command=apply).pack(pady=8)

    # ---------- 设置 ----------
    def _open_settings(self):
        T = self._t()
        win = tk.Toplevel(self.root)
        win.title(T["settings_title"])
        win.geometry("600x400")
        win.transient(self.root)
        win.grab_set()

        frm = ttk.Frame(win, padding=14)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text=T["lang_label"]).grid(row=0, column=0, sticky="w")
        lang_var = tk.StringVar(value=self.lang)
        ttk.Radiobutton(frm, text=T["lang_zh"], value="zh", variable=lang_var).grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(frm, text=T["lang_en"], value="en", variable=lang_var).grid(row=0, column=2, sticky="w")

        ttk.Label(frm, text=T["mod_start_label"]).grid(row=1, column=0, sticky="w", pady=(14, 0))
        dir_var = tk.StringVar(value=self.settings.get("mod_start_dir", ""))
        ttk.Entry(frm, textvariable=dir_var, width=40).grid(row=1, column=1, columnspan=2, sticky="we", pady=(14, 0))

        def pick_dir():
            d = filedialog.askdirectory(initialdir=dir_var.get() or os.path.expanduser("~"))
            if d:
                dir_var.set(d)
        ttk.Button(frm, text=T["mod_start_set"], command=pick_dir).grid(row=1, column=3, sticky="w", pady=(14, 0))

        ttk.Label(frm, text=T["toggle_key_label"]).grid(row=2, column=0, sticky="w", pady=(14, 0))
        key_var = tk.StringVar(value=self.settings.get("toggle_key", "/"))
        ttk.Entry(frm, textvariable=key_var, width=12).grid(row=2, column=1, sticky="w", pady=(14, 0))
        ttk.Label(frm, text=T["toggle_key_help"], foreground="#666").grid(
            row=2, column=2, columnspan=2, sticky="w", pady=(14, 0))

        ttk.Label(frm, text=T["custom_images_label"], foreground="#c00").grid(
            row=3, column=0, sticky="w", pady=(14, 0))
        custom_var = tk.BooleanVar(value=bool(self.settings.get("custom_images")))
        ttk.Checkbutton(frm, text=T["custom_images_help"], variable=custom_var).grid(
            row=3, column=1, columnspan=3, sticky="w", pady=(14, 0))

        def save():
            self.lang = lang_var.get()
            self.settings["lang"] = self.lang
            if dir_var.get().strip():
                self.settings["mod_start_dir"] = dir_var.get().strip()
            if key_var.get().strip():
                self.settings["toggle_key"] = key_var.get().strip()
            self.settings["custom_images"] = bool(custom_var.get())
            history.save_settings(self.settings)
            win.destroy()
            self.T = get_dict(self.lang)
            self._rebuild_ui_texts()

        ttk.Button(frm, text=T["save"], command=save).grid(row=4, column=1, pady=(18, 0))
        ttk.Button(frm, text=T["cancel"], command=win.destroy).grid(row=4, column=2, pady=(18, 0))

    def _rebuild_ui_texts(self):
        T = self._t()
        self.root.title(T["app_title"])
        self.btn_select.config(text=T["select_mod"])
        self.btn_add.config(text=T["add_panel"])
        self.btn_edit.config(text=T["edit_labels"])
        self.btn_settings.config(text=T["settings"])
        self.btn_ai.config(text=T["ai_prompt"])
        self.btn_about.config(text=T["about"])
        self.btn_scan.config(text=T["scan_panels"])
        self.btn_rb_all.config(text=T["rollback_all"])
        self.btn_clear.config(text=T["clear_records"])
        heads = {"mod": T["col_mod"], "time": T["col_time"], "method": T["col_method"],
                 "count": T["col_count"], "key": T["col_key"], "status": T["col_status"]}
        for c in ("mod", "time", "method", "count", "key", "status"):
            self.tree.heading(c, text=heads[c])
        self._refresh_records()

    # ---------- 帮助 / 错误弹窗 ----------
    def _show_ai_prompt(self):
        T = self._t()
        win = tk.Toplevel(self.root)
        win.title(T["ai_prompt_title"])
        win.geometry("760x600")
        win.transient(self.root)
        ttk.Label(win, text=T["ai_prompt_hint"], wraplength=720, justify="left",
                  foreground="#333").pack(padx=12, pady=(10, 4), fill="x")
        txt = tk.Text(win, wrap="word", font=("Microsoft YaHei", 9))
        txt.pack(fill="both", expand=True, padx=12, pady=4)
        txt.insert("1.0", T["ai_prompt_text"])
        txt.config(state="disabled")
        btn_frm = ttk.Frame(win)
        btn_frm.pack(pady=8)

        def copy():
            self.root.clipboard_clear()
            self.root.clipboard_append(T["ai_prompt_text"])
            self._status(T["ai_copied"])
            win.destroy()
            messagebox.showinfo(T["success_title"], T["ai_copied"])

        ttk.Button(btn_frm, text=T["ai_copy"], command=copy).pack(side="left", padx=6)
        ttk.Button(btn_frm, text=T["close"], command=win.destroy).pack(side="left", padx=6)

    def _show_help(self):
        T = self._t()
        win = tk.Toplevel(self.root)
        win.title(T["learn_usage_title"])
        win.geometry("660x540")
        win.transient(self.root)
        txt = tk.Text(win, wrap="word", font=("Microsoft YaHei", 10))
        txt.pack(fill="both", expand=True, padx=10, pady=8)
        txt.insert("1.0", T["learn_usage"])
        txt.config(state="disabled")
        ttk.Button(win, text=T["close"], command=win.destroy).pack(pady=8)

    def _err(self, title, msg):
        T = self._t()
        win = tk.Toplevel(self.root)
        win.title(title or T["error_title"])
        win.geometry("560x320")
        win.transient(self.root)
        win.grab_set()
        ttk.Label(win, text=msg, justify="left", wraplength=500).pack(padx=16, pady=14, fill="x")
        btn_frm = ttk.Frame(win)
        btn_frm.pack(pady=10)
        ttk.Button(btn_frm, text=T["learn_more"], command=self._show_help).pack(side="left", padx=6)
        ttk.Button(btn_frm, text=T["close"], command=win.destroy).pack(side="left", padx=6)

    def _ok(self, title, msg):
        messagebox.showinfo(title, msg)

    def _run_bg(self, fn):
        def wrap():
            try:
                fn()
            except Exception as e:
                log("bg error: %s" % e)
        threading.Thread(target=wrap, daemon=True).start()


# ---------- 首启流程 ----------
def first_run_flow(root):
    settings = history.get_settings()
    if not settings.get("first_done"):
        lang = {"v": "zh"}
        win = tk.Toplevel(root)
        win.title("选择语言 / Choose Language")
        win.geometry("380x200")
        win.transient(root)
        win.grab_set()
        ttk.Label(win, text="选择界面语言 / Choose Language").pack(pady=18)

        def choose(l):
            lang["v"] = l
            win.destroy()
        ttk.Button(win, text="中文", command=lambda: choose("zh")).pack(pady=4)
        ttk.Button(win, text="English", command=lambda: choose("en")).pack(pady=4)
        root.wait_window(win)
        settings["lang"] = lang["v"]

        d = filedialog.askdirectory(title="选择 Mod 文件夹 / Choose Mod Folder")
        if d:
            settings["mod_start_dir"] = d
        settings["first_done"] = True
        history.save_settings(settings)
    return settings


def main():
    root = tk.Tk()
    first_run_flow(root)
    PanelToolApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
