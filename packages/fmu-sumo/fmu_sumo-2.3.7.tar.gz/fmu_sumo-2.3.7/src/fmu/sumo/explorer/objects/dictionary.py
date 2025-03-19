"""Module containing class for dictionary object"""

import json
from typing import Dict

from sumo.wrapper import SumoClient

from fmu.sumo.explorer.objects._child import Child


class Dictionary(Child):
    """Class representing a dictionary object in Sumo"""

    _parsed: dict

    def __init__(self, sumo: SumoClient, metadata: Dict, blob=None) -> None:
        """
        Args:
            sumo (SumoClient): connection to Sumo
            metadata (dict): dictionary metadata
        """
        self._parsed = None

        super().__init__(sumo, metadata, blob)

    def parse(self) -> Dict:
        if self._parsed is None:
            self._parsed = json.loads(self.blob.read().decode("utf-8"))

        return self._parsed

    async def parse_async(self) -> Dict:
        if self._parsed is None:
            self._parsed = json.loads(self.blob_async.read().decode("utf-8"))

        return self._parsed
