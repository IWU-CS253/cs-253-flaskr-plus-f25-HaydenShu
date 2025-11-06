import os
import app as flaskr
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.testing = True
        self.app = flaskr.app.test_client()
        with flaskr.app.app_context():
            flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No entries here so far' in rv.data

    def test_messages(self):
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='A category'
        ), follow_redirects=True)
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data
        assert b'A category' in rv.data

    def test_add_multiple_entries(self):
        self.app.post('/add', data=dict(
            title='First Entry',
            text='First Text',
            category='Category1'
        ), follow_redirects=True)

        rv = self.app.post('/add', data=dict(
            title='Second Entry',
            text='Second Text',
            category='Category2'
        ), follow_redirects=True)

        assert b'First Entry' in rv.data
        assert b'Second Entry' in rv.data

    def test_delete_entry(self):
        self.app.post('/add', data=dict(
            title='To Be Deleted',
            text='Delete Me',
            category='Test'
        ), follow_redirects=True)

        rv = self.app.get('/')
        assert b'To Be Deleted' in rv.data

        rv = self.app.post('/delete', data=dict(
            id='1'
        ), follow_redirects=True)

        assert b'To Be Deleted' not in rv.data

    def test_update_entry_page(self):

        self.app.post('/add', data=dict(
            title='Original Title',
            text='Original Text',
            category='Original Category'
        ), follow_redirects=True)

        rv = self.app.post('/update', data=dict(id='1'))

        assert b'Original Title' in rv.data
        assert b'Original Text' in rv.data
        assert b'Original Category' in rv.data

    def test_submit_update(self):

        self.app.post('/add', data=dict(
            title='Original Title',
            text='Original Text',
            category='Original Category'
        ), follow_redirects=True)

        rv = self.app.post('/submit_update', data=dict(
            id='1',
            title='Updated Title',
            text='Updated Text',
            category='Updated Category'
        ), follow_redirects=True)

        assert b'New entry was successfully updated' in rv.data
        assert b'Updated Title' in rv.data
        assert b'Updated Text' in rv.data
        assert b'Original Title' not in rv.data

    def test_all_categories_displayed(self):
        self.app.post('/add', data=dict(
            title='Entry 1',
            text='Text 1',
            category='Category A'
        ), follow_redirects=True)

        self.app.post('/add', data=dict(
            title='Entry 2',
            text='Text 2',
            category='Category B'
        ), follow_redirects=True)

        rv = self.app.get('/')

        assert b'Category A' in rv.data
        assert b'Category B' in rv.data

    def test_filter_by_category(self):
        self.app.post('/add', data=dict(
            title='Entry 1',
            text='Text 1',
            category='Category A'
        ), follow_redirects=True)

        self.app.post('/add', data=dict(
            title='Entry 2',
            text='Text 2',
            category='Category B'
        ), follow_redirects=True)

        rv = self.app.get('/?sort_selected=Category A')

        assert b'Entry 1' in rv.data
        assert b'Entry 2' not in rv.data

    def test_entries_ordered_by_id_desc(self):
        self.app.post('/add', data=dict(
            title='First Entry',
            text='Text 1',
            category='Test'
        ), follow_redirects=True)

        rv = self.app.post('/add', data=dict(
            title='Second Entry',
            text='Text 2',
            category='Test'
        ), follow_redirects=True)

        assert rv.data.index(b'Second Entry') < rv.data.index(b'First Entry')

if __name__ == '__main__':
    unittest.main()