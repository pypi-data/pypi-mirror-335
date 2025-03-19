"""Module for (pseudo) iteration class."""

from typing import Dict

from sumo.wrapper import SumoClient

from fmu.sumo.explorer.objects._document import Document
from fmu.sumo.explorer.objects._search_context import SearchContext


class Iteration(Document, SearchContext):
    """Class for representing an iteration in Sumo."""

    def __init__(self, sumo: SumoClient, metadata: Dict):
        Document.__init__(self, metadata)
        SearchContext.__init__(
            self,
            sumo,
            must=[{"term": {"fmu.iteration.uuid.keyword": self.uuid}}],
        )
        pass

    @property
    def field(self) -> str:
        """Case field"""
        return self.get_property("masterdata.smda.field[0].identifier")

    @property
    def asset(self) -> str:
        """Case asset"""
        return self.get_property("access.asset.name")

    @property
    def user(self) -> str:
        """Name of user who uploaded iteration."""
        return self.get_property("fmu.case.user.id")

    @property
    def caseuuid(self) -> str:
        """FMU case uuid"""
        return self.get_property("fmu.case.uuid")

    @property
    def casename(self) -> str:
        """FMU case name"""
        return self.get_property("fmu.case.name")

    @property
    def name(self) -> str:
        """FMU iteration name"""
        return self.get_property("fmu.iteration.name")
