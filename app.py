import sys

import flask
from flask import redirect, url_for
from flask import render_template
from flask import request

from forms import Form, FormField, validate_text, validate_url
from category import Category
from miner import Miner


app = flask.Flask(__name__)
app.config['DEBUG'] = True

miners = {}


class CategoryForm(Form):
    def __init__(self, values={}):
        super(CategoryForm, self).__init__(values)
        self.name = FormField('text', 'name', 'Name', 'Name of the miner.', validate_text, True)
        self.parent_uri = FormField('text', 'parent_uri', 'Engine URL', 'Url of the engine.', validate_url, True)
        self.users = FormField('text', 'users', 'Accounts to Mine', 'Comma separated list of Twitter user names.', validate_text, True)
        self.access_secret = FormField('text', 'access_secret', 'Access Secret', 'Access Secret for Twitter API.', validate_text, True)
        self.access_token = FormField('text', 'access_token', 'Access Token', 'Access Token for Twitter API.', validate_text, True)
        self.consumer_key = FormField('text', 'consumer_key', 'Consumer Key', 'Consumer Key for Twitter API.', validate_text, True)
        self.consumer_secret = FormField('text', 'consumer_secret', 'Consumer Secret', 'Consumer Secret for Twitter API.', validate_text, True)

        self.add_field(self.name)
        self.add_field(self.parent_uri)
        self.add_field(self.users)
        self.add_field(self.access_secret)
        self.add_field(self.access_token)
        self.add_field(self.consumer_key)
        self.add_field(self.consumer_secret)


@app.route('/categories', methods=['GET', 'POST'])
def categories():
    if request.method == 'GET':
        # return an html list of all the categories
        return render_template('category/index.html', categories=Category.all(), success=True)
    elif request.method == 'POST':
        # create new category based on the posted id
        params = request.get_json()
        new_category_id = int(params['id'])
        new_category = Category(new_category_id)
        new_category.save()
        return 'OK', 200
    else:
        return 'error', 400


@app.route('/categories/<category_id>', methods=['GET', 'POST', 'DELETE'])
def categories_edit(category_id):
    try:
        category = Category.find_by_id(category_id)
        if category:
            if request.method == 'GET':
                category_dict = category.__dict__
                form = CategoryForm(category_dict)
                return render_template('category/edit.html', form=form, category_id=category_id, success=True)
            elif request.method == 'POST':
                form = CategoryForm(request.form)
                if form.validate():
                    values = form.named_values()
                    category.from_dict(values)
                    category.save()
                    miner = Miner(category)
                    miners[category_id] = miner
                    miner.start()
                    return redirect(url_for('categories'))
                else:
                    return render_template('category/edit.html', form=form, category_id=category_id, success=True)
            elif request.method == 'DELETE':
                miner = miners[category_id]
                miner.stop()
                del miners[category_id]
                Category.delete(category_id)
                return 'Category {} deleted.'.format(category_id), 200
            else:
                return 'Unsupported request method.', 400
        else:
            return 'Category {} not found.'.format(category_id), 400
    except ValueError:
        return '{} is not a valid category id.'.format(category_id), 400


def main():
    app.run()


if __name__ == "__main__":
    main()

