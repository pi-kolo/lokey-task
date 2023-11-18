from http import HTTPStatus

from connexion import NoContent

from lib.models import Article, db

from sqlalchemy import extract, and_

from datetime import datetime

def get(user, year=None):
    filter_expression = [Article.author_user_id == user['user_id']]

    if year:
        filter_expression.append(extract('year', Article.release_date) == year)

    articles = Article.query.filter(and_(*filter_expression)).all()

    return [
        {
           'article_id': article.article_id,
           'title': article.title,
           'content': article.content,
           'release_date': article.release_date
        }

       for article in articles
    ], HTTPStatus.OK


def post(user, body):
    try:
        release_date = datetime.strptime(body['release_date'], '%Y-%m-%dT%H:%M:%S.%fZ')
    except:
        release_date = None

    db.session.add(Article(
        author_user_id=user['user_id'],
        title=body['title'],
        content=body['content'],
        release_date=release_date
    ))
    db.session.commit()

    return NoContent, HTTPStatus.OK


def put(user, article_id, body):
    article = Article.query.filter(
        Article.article_id == article_id,
        Article.author_user_id == user['user_id'],
    ).first()

    if not article:
        return NoContent, HTTPStatus.NOT_FOUND

    article.title = body['title']
    article.content = body['content']

    try:
        article.release_date = datetime.strptime(body['release_date'], '%Y-%m-%dT%H:%M:%S.%fZ')
    except:
        article.release_date = None

    db.session.commit()

    return NoContent, HTTPStatus.OK


def delete(user, article_id):
    Article.query.filter(
        Article.article_id == article_id,
        Article.author_user_id == user['user_id'],
    ).delete()

    db.session.commit()

    return NoContent, HTTPStatus.OK


