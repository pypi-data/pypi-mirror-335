import csv
import time


class BatchReader:
    def __init__(
        self,
        max_read: int = 0,
        start_limit: int = 0,
        start_offset: int = 0,
        to_csv=None,
    ):
        self._max_read = max_read
        self._start_limit = start_limit
        self._base_limit: int = (
            start_limit if start_limit > 0 else (100 if to_csv is None else 10000)
        )
        self._limit = self._base_limit
        self._start_offset = start_offset
        self._offset: int = start_offset
        self._total_lines_read: int = 0
        self._to_csv = to_csv
        self._reading_durations = []
        self._writing_durations = []
        self._results = {}
        self._header = []
        self._last_lines_read: int = 0
        self._column_order = []

    def read_next(self, read_fnc, **fnc_kwargs):
        if not self._continue():
            return {}

        start = time.time()
        fnc_kwargs["limit"] = self._limit
        fnc_kwargs["offset"] = self._offset
        self._results = read_fnc(**fnc_kwargs)
        self._reading_durations.append(time.time() - start)

        self._build_header()
        # self._header = list(self._results.keys())
        self._last_lines_read = len(self._results[self._header[0]])
        self._total_lines_read += self._last_lines_read

        return self._results

    def write_to_csv(self):
        start = time.time()
        mode = "w" if (self._offset == self._start_offset) else "a"
        with open(self._to_csv, mode, newline=None) as csv_file:
            writer = csv.writer(
                csv_file,
                delimiter=",",
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL,
            )
            if mode == "w":
                writer.writerow(self._header)
            for idx in range(self._last_lines_read):
                row = [self._results[h][idx] for h in self._header]
                writer.writerow(row)
        self._writing_durations.append(time.time() - start)

    def stop(self):
        if self._results and len(self._results[self._header[0]]) < self._base_limit:
            return True
        else:
            self._offset += self._limit
            return False

    def _continue(self):
        if self._max_read > 0:
            if self._total_lines_read >= self._max_read:
                return False
            elif self._total_lines_read + self._limit >= self._max_read:
                self._limit = self._max_read - self._total_lines_read

        return True

    def last_reading_duration(self):
        if self._reading_durations:
            return self._reading_durations[-1]
        else:
            return 0

    def last_writing_duration(self):
        if self._writing_durations:
            return self._writing_durations[-1]
        else:
            return 0

    def total_reading_duration(self):
        return sum(self._reading_durations)

    def total_writing_duration(self):
        return sum(self._writing_durations)

    @property
    def results(self):
        return self._results

    @property
    def lines_read(self):
        return self._total_lines_read

    def _build_header(self):
        if self._header:
            return

        columns = list(self._results.keys())

        for col in columns:
            if isinstance(col, tuple):
                continue
            self._header.append(col)

        for col in columns:
            if isinstance(col, tuple):
                if "sensor" in col:
                    self._header.append(col)

        for col in columns:
            if isinstance(col, tuple):
                if "actuator" in col:
                    self._header.append(col)

        for col in columns:
            if isinstance(col, tuple):
                if "reward" in col:
                    self._header.append(col)
