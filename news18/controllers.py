from flask import Blueprint, jsonify
from flask import request
from news18.base import news18
from news18 import logger
news18blueprint = Blueprint('news18', __name__)


@news18blueprint.route('/get_news')
def news18_api():
    """
        This is the summary defined in yaml file
        First line is the summary
        All following lines until the hyphens is added to descriptions
        the format of the first lines until 3 hyphens will be not yaml compliant
        but everything below the 3 hyphens should be.
        ---
        tags:
         - news18
        description: gets one page of news18 channel news
        parameters:
         - name: page
           in: query
           type: string
           required: true
        responses:
         200:
          description: A list of news containing the title,snippet,date, url and contents of the news18 connector
         404:
          description: Error page not found

    """
    page = request.args.get('page')
    logger.info('successful request to the page {0} of news18 connector'.format(page))
    return jsonify(news18(page=str(page)))