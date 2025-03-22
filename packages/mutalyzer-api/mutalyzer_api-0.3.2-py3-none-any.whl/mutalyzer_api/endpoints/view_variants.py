from flask_restx import Namespace, Resource, inputs, reqparse

from mutalyzer.viewer import view_variants

from .common import errors

ns = Namespace("/")


_args = reqparse.RequestParser()

_args.add_argument(
    "sequence",
    type=str,
    help="Reference sequence.",
    required=False,
)

_args.add_argument(
    "only_variants",
    type=inputs.boolean,
    help="The description consists only of variants.",
    default=False,
    required=False,
)


@ns.route("/view_variants/<string:description>")
class ViewVariants(Resource):
    @ns.expect(_args)
    @errors
    def get(self, description):
        """Visualize a variant description."""
        return view_variants(description, **_args.parse_args())
