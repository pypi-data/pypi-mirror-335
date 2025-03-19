import io
import json
import logging
import warnings

class Logger:
    def __init__(self, secateur_id, log):
        self.secateur_id = secateur_id
        self.logger = logging.getLogger(secateur_id)
        self.logger.setLevel(logging.INFO)
        self.log_stream = io.StringIO()
        self.report = {
            "id": secateur_id,
            "collections": {},
            "pruned": []
        }
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        if log and not self.logger.hasHandlers():
            sh = logging.StreamHandler(self.log_stream)
            sh.setLevel(logging.INFO)
            sh.setFormatter(formatter)

            fh = logging.FileHandler(f"secateur-{secateur_id}.log", mode="a")
            fh.setLevel(logging.INFO)
            fh.setFormatter(formatter)

            self.logger.addHandler(sh)
            self.logger.addHandler(fh)

    def save_report(self, path: str = None) -> None:
        path = f"report-{self.secateur_id}.json" if not(path) else path
        with open(path, 'w') as json_file:
            json.dump(self.report, json_file, indent=4)
