from app import app, S3_KEY, S3_BUCKET, S3_SECRET_ACCESS_KEY
import unittest
import pytest
import boto3


class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

    # Checks if the landing page is up and running (if so, the app is able to run)
    # Potential error: FileNotFoundError: [WinError 2] The system cannot find the file specified
    # Possible reason for failing: When running locally, comment out the section that begins with
    # app.config["WKHTMLTOPDF_CMD"] = subprocess.Popen(, as this is for production.
    def test_landing(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # Tests whether an user can access the login page without being logged in
    def test_login_loads(self):
        tester = app.test_client(self)
        response = tester.get('/login', content_type='html/text')
        self.assertTrue(b'Testing Login' in response.data)

    # Tests whether an user can access the signup page without being logged in
    def test_signup_loads(self):
        tester = app.test_client(self)
        response = tester.get('/signup', content_type='html/text')
        self.assertTrue(b'Testing Signup' in response.data)

    # Tests whether an user can access the portfolio page without being logged in (they should be redirected
    # to login)
    def test_portfolio_redirect(self):
        tester = app.test_client(self)
        response = tester.get('/art_portfolio', content_type='html/text', follow_redirects=True)
        self.assertTrue(b'Testing Login' in response.data)

    # Tests whether an user can access the profile page without being logged in (they should be redirected
    # to login)
    def test_profile_redirect(self):
        tester = app.test_client(self)
        response = tester.get('/profile', content_type='html/text', follow_redirects=True)
        self.assertTrue(b'Testing Login' in response.data)

    # Test whether the user successfully logs in given the correct email/pswd
    def test_login_success(self):
        tester = app.test_client(self)
        response = tester.post('/login', data=dict(email="kai@test.com", password="kaitest999"), follow_redirects=True)
        self.assertIn(b'Testing Login Success', response.data)

    # Test whether the page displays a flash message that the user credentials are wrong when entering the wrong
    # email/pswd
    def test_login_failure(self):
        tester = app.test_client(self)
        response = tester.post('/login', data=dict(email="wrong@wrong.com", password="wro0o0ng"), follow_redirects=True)
        self.assertIn(b'Invalid', response.data)

    # Test whether logging out redirects to the landing page
    def test_logout(self):
        tester = app.test_client(self)
        tester.post('/login', data=dict(email="kai@test.com", password="kaitest999"), follow_redirects=True)
        response = tester.get('/logout', follow_redirects=True)
        self.assertIn(b'ePortfolio -COMP30022', response.data)


if __name__ == '__main__':
    unittest.main()
