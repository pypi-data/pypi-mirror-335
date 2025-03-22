from flask_restx import Namespace, Resource, reqparse

from mutalyzer.description_extractor import description_extractor

from .common import errors

ns = Namespace("/")

_args = reqparse.RequestParser()
_args.add_argument(
    "reference",
    type=str,
    help="Reference sequence.",
    default="AAAATTTCCCCCGGGG",
    required=True,
)
_args.add_argument(
    "observed",
    type=str,
    help="Observed sequence.",
    default="AAAATTTCCCCCGGGG",
    required=True,
)


@ns.route("/description_extract/")
class DescriptionExtract(Resource):
    @ns.expect(_args)
    @errors
    def get(self):
        """Generates the HGVS variant description from a reference sequence
        and an observed sequence."""
        return description_extractor(**_args.parse_args())
