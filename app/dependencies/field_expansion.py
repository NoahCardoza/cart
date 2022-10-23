from typing import Optional

from app.exceptions import JSONException
from fastapi import Query


class FieldExpansionQueryParams():
    def __init__(self, expansions):
        """Expands the fields of a SQLAlchemy statement based on a query parameter.

        Args:
            expansions (Dict[str, Any]): a dictionary of fields to expand and their expansions
        """
        self.expansions = expansions

    def __call__(self, expand: Optional[str] = Query(
        default=None,
        description="The fields to expand. Separated by commas."
    )):
        """To be passed to an endpoint as a dependency

        Args:
            expand (str): a comma separated list of fields to expand

        Raises:
            JSONException: if an invalid field is passed

        Returns: A list of options to be passes to a SQLAlchemy statement
        """
        if expand is None:
            return None
        options = []
        expanders = expand.split(',')

        for field in expanders:
            if field not in self.expansions:
                raise JSONException(
                    code=422,
                    body={
                        "loc": [
                            "query",
                            "expand"
                        ],
                        "msg": f"invalid expansion field {field}",
                        "type": "value_error.expand.unknown",
                        "ctx": {
                            "values": list(self.expansions.keys()),
                        }
                    }

                )
            options.append(self.expansions[field])

        return options
