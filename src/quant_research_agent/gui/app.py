import tkinter as tk
from tkinter import scrolledtext, ttk

from quant_research_agent.storage.database import ResearchDatabase


class ResearchViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quant Research Agent Viewer")
        self.geometry("1600x920")
        self.db = ResearchDatabase()
        self.current_run_id = None
        self.current_article_id = None
        self.alpha_payloads: dict[str, dict] = {}
        self._build_ui()
        self._load_runs()

    def _build_ui(self) -> None:
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self.runs_tab = ttk.Frame(self.notebook)
        self.articles_tab = ttk.Frame(self.notebook)
        self.alpha_tab = ttk.Frame(self.notebook)
        self.report_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.runs_tab, text="Daily Runs")
        self.notebook.add(self.articles_tab, text="Articles")
        self.notebook.add(self.alpha_tab, text="Alpha Results")
        self.notebook.add(self.report_tab, text="Run Detail")

        self._build_runs_tab()
        self._build_articles_tab()
        self._build_alpha_tab()
        self._build_report_tab()

    def _build_runs_tab(self) -> None:
        columns = ("run_date", "status", "collected", "selected", "alphas", "validated")
        self.runs_tree = ttk.Treeview(self.runs_tab, columns=columns, show="headings")
        for name, width in (
            ("run_date", 120),
            ("status", 100),
            ("collected", 90),
            ("selected", 90),
            ("alphas", 90),
            ("validated", 90),
        ):
            self.runs_tree.heading(name, text=name)
            self.runs_tree.column(name, width=width, anchor="w")
        self.runs_tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.runs_tree.bind("<<TreeviewSelect>>", self._on_run_selected)

    def _build_articles_tab(self) -> None:
        columns = ("title", "source", "action", "theme", "status")
        self.articles_tree = ttk.Treeview(self.articles_tab, columns=columns, show="headings")
        for name, width in (
            ("title", 520),
            ("source", 180),
            ("action", 140),
            ("theme", 160),
            ("status", 140),
        ):
            self.articles_tree.heading(name, text=name)
            self.articles_tree.column(name, width=width, anchor="w")
        self.articles_tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.articles_tree.bind("<<TreeviewSelect>>", self._on_article_selected)

    def _build_alpha_tab(self) -> None:
        self.alpha_tab.grid_columnconfigure(0, weight=1)
        self.alpha_tab.grid_rowconfigure(1, weight=1)

        columns = ("expression", "fitness", "sharpe", "returns", "turnover", "alpha_id")
        self.alpha_tree = ttk.Treeview(self.alpha_tab, columns=columns, show="headings", height=12)
        for name, width in (
            ("expression", 620),
            ("fitness", 80),
            ("sharpe", 80),
            ("returns", 80),
            ("turnover", 90),
            ("alpha_id", 160),
        ):
            self.alpha_tree.heading(name, text=name)
            self.alpha_tree.column(name, width=width, anchor="w")
        self.alpha_tree.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        self.alpha_tree.bind("<<TreeviewSelect>>", self._on_alpha_selected)

        self.alpha_detail_text = scrolledtext.ScrolledText(self.alpha_tab, wrap="word")
        self.alpha_detail_text.grid(row=1, column=0, padx=8, pady=(0, 8), sticky="nsew")

    def _build_report_tab(self) -> None:
        self.report_text = scrolledtext.ScrolledText(self.report_tab, wrap="word")
        self.report_text.pack(fill="both", expand=True, padx=8, pady=8)

    def _load_runs(self) -> None:
        for item in self.runs_tree.get_children():
            self.runs_tree.delete(item)
        for run in self.db.list_daily_runs():
            self.runs_tree.insert(
                "",
                "end",
                iid=str(run["id"]),
                values=(
                    run["run_date"],
                    run["status"],
                    run["collected_count"],
                    run["selected_count"],
                    run["generated_alpha_count"],
                    run["validated_count"],
                ),
            )

    def _on_run_selected(self, _event=None) -> None:
        selected = self.runs_tree.selection()
        if not selected:
            return
        self.current_run_id = int(selected[0])
        self._load_articles(self.current_run_id)
        self.report_text.delete("1.0", "end")
        self.report_text.insert("1.0", self.db.get_report_for_run(self.current_run_id))
        self.notebook.select(self.articles_tab)

    def _load_articles(self, run_id: int) -> None:
        for item in self.articles_tree.get_children():
            self.articles_tree.delete(item)
        for article in self.db.list_articles_for_run(run_id):
            self.articles_tree.insert(
                "",
                "end",
                iid=str(article["id"]),
                values=(
                    article["title"],
                    article["source_name"],
                    article["action"],
                    article["theme"] or "",
                    article["research_status"],
                ),
            )

    def _on_article_selected(self, _event=None) -> None:
        selected = self.articles_tree.selection()
        if not selected:
            return
        self.current_article_id = int(selected[0])
        self._load_alphas(self.current_article_id)
        self.notebook.select(self.alpha_tab)

    def _load_alphas(self, article_id: int) -> None:
        for item in self.alpha_tree.get_children():
            self.alpha_tree.delete(item)
        self.alpha_payloads = {}
        self.alpha_detail_text.delete("1.0", "end")
        for index, row in enumerate(self.db.list_alpha_results_for_article(article_id), start=1):
            row_id = f"alpha-{index}"
            self.alpha_payloads[row_id] = {key: row[key] for key in row.keys()}
            self.alpha_tree.insert(
                "",
                "end",
                iid=row_id,
                values=(
                    row["expression"],
                    row["fitness"],
                    row["sharpe"],
                    row["returns"],
                    row["turnover"],
                    row["alpha_id"],
                ),
            )

    def _on_alpha_selected(self, _event=None) -> None:
        selected = self.alpha_tree.selection()
        if not selected:
            return
        row_id = selected[0]
        payload = self.alpha_payloads.get(row_id, {})
        settings_json = payload.get("settings_json")
        settings_text = settings_json if settings_json else "{}"
        detail = (
            f"Expression:\n{payload.get('expression', '')}\n\n"
            f"Explanation:\n{payload.get('alpha_explanation', '')}\n\n"
            f"Source annotation:\n{payload.get('source_annotation', '')}\n\n"
            f"Translation notes:\n{payload.get('translation_notes', '')}\n\n"
            f"Metrics:\nSharpe={payload.get('sharpe')} Fitness={payload.get('fitness')} "
            f"Returns={payload.get('returns')} Turnover={payload.get('turnover')} Alpha ID={payload.get('alpha_id')}\n\n"
            f"Validation settings:\n{settings_text}\n\n"
            f"Error:\n{payload.get('error')}"
        )
        self.alpha_detail_text.delete("1.0", "end")
        self.alpha_detail_text.insert("1.0", detail)


def launch_gui() -> None:
    app = ResearchViewer()
    app.mainloop()
