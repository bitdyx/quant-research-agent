import argparse
from pprint import pprint

from quant_research_agent.gui.app import launch_gui
from quant_research_agent.pipeline import QuantResearchAgent
from quant_research_agent.web.app import launch_web


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="quant-research-agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    collect_parser = subparsers.add_parser("collect", help="Collect and deduplicate articles without validation.")
    collect_parser.add_argument("--max-per-source", type=int, default=6)

    run_daily_parser = subparsers.add_parser("run-daily", help="Run the full daily research workflow.")
    run_daily_parser.add_argument("--date", dest="run_date")

    report_parser = subparsers.add_parser("report", help="Print the stored report for a given date.")
    report_parser.add_argument("--date", dest="run_date", required=True)

    subparsers.add_parser("open-gui", help="Open the local GUI viewer backed by SQLite.")
    subparsers.add_parser("open-web", help="Open the local web dashboard.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    agent = QuantResearchAgent()

    if args.command == "collect":
        payload = agent.collect_articles(max_per_source=args.max_per_source)
        summary = {
            "collected": len(payload),
            "actions": [item["action"] for item in payload],
        }
        pprint(summary)
        return

    if args.command == "run-daily":
        result = agent.run_daily(run_date=args.run_date)
        pprint(
            {
                "run_id": result["run_id"],
                "export_path": result["export_path"],
                "run_date": result["report"].run_date,
                "status": result["report"].status,
                "collected_count": result["report"].collected_count,
                "selected_count": result["report"].selected_count,
                "generated_alpha_count": result["report"].generated_alpha_count,
                "validated_count": result["report"].validated_count,
            }
        )
        return

    if args.command == "report":
        print(agent.report_for_date(args.run_date))
        return

    if args.command == "open-gui":
        launch_gui()
        return

    if args.command == "open-web":
        launch_web()
        return
