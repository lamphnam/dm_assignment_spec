#!/usr/bin/env python3
"""READ-ONLY snapshot of competition rules metadata via the official kaggle / kagglesdk packages.

Usage (run with the python that has `kaggle` installed, e.g. %USERPROFILE%\\.kaggle-mcp-venv):
    python competition_info.py [--competition SLUG] [--pages OUT_DIR]

Prints deadline, merger/new-entrant deadlines, daily submission limit, max team size, team count,
whether the authenticated account has entered, and today's remaining submissions for THAT account.
--pages also saves every competition page (Overview, Data, Evaluation, Rules...) as Markdown.

Authentication: KAGGLE_API_TOKEN env var or ~/.kaggle/kaggle.json. The token is never printed.
This script performs no write operation (no submit, no team change).
"""
from __future__ import annotations

import argparse
import os
import sys


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--competition", default="assignment-data-mining-261")
    ap.add_argument("--pages", help="directory to save page snapshots (created if missing)")
    a = ap.parse_args()
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        from kagglesdk.competitions.types.competition_api_service import (
            ApiGetCompetitionRequest, ApiGetSubmissionLimitsRequest, ApiListCompetitionPagesRequest)
    except ImportError as e:
        print(f"Missing dependency ({e}). Use the venv described in docs/integrations/kaggle-mcp-setup.md")
        return 2
    api = KaggleApi()
    api.authenticate()
    with api.build_kaggle_client() as k:
        svc = k.competitions.competition_api_client
        g = ApiGetCompetitionRequest(); g.competition_name = a.competition
        c = svc.get_competition(g)
        for f in ("title", "deadline", "merger_deadline", "new_entrant_deadline", "enabled_date",
                  "max_daily_submissions", "max_team_size", "team_count", "user_has_entered"):
            print(f"{f}: {getattr(c, f, 'n/a')}")
        try:
            r = ApiGetSubmissionLimitsRequest(); r.competition_name = a.competition
            lim = svc.get_submission_limits(r)
            print(f"submission_limits (this account, now): {lim.to_json() if hasattr(lim, 'to_json') else lim}")
        except Exception as e:  # endpoint may be unavailable for some accounts
            print(f"submission_limits: unavailable ({type(e).__name__})")
        if a.pages:
            os.makedirs(a.pages, exist_ok=True)
            p = ApiListCompetitionPagesRequest(); p.competition_name = a.competition
            for page in svc.list_competition_pages(p).pages:
                path = os.path.join(a.pages, f"{page.name}.md")
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(page.content or "")
                print(f"saved page: {path}")
    print("note: merger_deadline=None means the API reports no separate merger deadline; "
          "the competition deadline then bounds merges (Kaggle rules §5c(iii)). Confirm on the website.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
