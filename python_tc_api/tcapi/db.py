import sqlite3
from typing import Optional

import click
from flask import current_app, g
from flask.cli import with_appcontext


CREATE_DB_SQL=''' DROP TABLE IF EXISTS accepts;

CREATE TABLE accepts (
  urn TEXT PRIMARY KEY NOT NULL,
  until TEXT NOT NULL,
  main_accept BOOLEAN NOT NULL DEFAULT FALSE
);

'''


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(CREATE_DB_SQL)


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def find_accept(user_urn: str) -> Optional[dict]:
    db = get_db()
    res = db.execute('SELECT urn,until,main_accept FROM accepts WHERE urn = ?', (user_urn,)).fetchone()

    if res is None:
        return None

    return {
        'user': res['urn'],
        'until': res['until'],
        'main_accept': bool(res['main_accept']),
    }


def register_accept(user_urn: str, until: str, main_accept: bool) -> None:
    db = get_db()
    db.execute(
        'INSERT OR REPLACE INTO accepts (urn, until, main_accept) VALUES (?, ?, ?)',
        (user_urn, until, main_accept)
    )
    db.commit()


def delete_accept(user_urn: str) -> None:
    db = get_db()
    db.execute(
        'DELETE FROM accepts WHERE urn = ?',
        (user_urn,)
    )
    db.commit()
