from flask_restx import abort
from functools import wraps
import logging
from flask import request, jsonify

logger = logging.getLogger(__name__)  # Global logger instance

def errors(endpoint):
    @wraps(endpoint)
    def dec(*args, **kwargs):
        output = endpoint(*args, **kwargs)

        if isinstance(output, dict):
            log = f"Request: {request.method} {request.url}"
            log_extra = ""

            if "errors" in output:
                log += f" Response: errors: {output['errors']}"
                logger.info(log)
                response = jsonify(
                    message="Errors encountered. Check the 'custom' field.",
                    custom=output,
                )
                response.status_code = 422
                return response

            if "relation" in output:
                log_extra += f" Response: {output['relation']}"
            elif "normalized_description" in output and "input_description" in output:
                if output["normalized_description"] == output["input_description"]:
                    log_extra += " Response: equal"
                else:
                    log_extra += f" Response: {{\"normalized_description\": \"{output['normalized_description']}\"}}"
            elif "mapped_description" in output:
                log_extra += f" Response: {{\"mapped_description\": \"{output['mapped_description']}\"}}"
            if log_extra:
                logger.info(log + log_extra)

        return output

    return dec
