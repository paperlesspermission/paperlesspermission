"""Test module for views.py

Copyright 2020 Mark Stenglein, The Paperless Permission Authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging
from time import sleep
from datetime import date, time

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

import paperlesspermission.views as views
import paperlesspermission.models as models

class ViewTest(TestCase):
    """Defines functions and data available to all view test cases."""
    def setUp(self):
        """Set up data available to all view test cases."""
        # pylint: disable=invalid-name,too-many-statements
        super(ViewTest, self).setUp()

        logging.disable(logging.CRITICAL)

        self.teacher_user = User.objects.create_user(
            'teacher',
            email='tuser@school.test',
            password='test'
        )

        self.admin_user = User.objects.create_user(
            'admin',
            email='auser@school.test',
            password='test'
        )
        self.admin_user.is_staff = True
        self.admin_user.save()

        self.super_user = User.objects.create_superuser(
            'super',
            email='suser@school.test',
            password='test'
        )

        student1 = models.Student(
            person_id='202300001',
            first_name='Test',
            last_name='Student',
            email='tstudent@school.test',
            cell_number='+17035555555',
            notify_cell=True,
            grade_level=models.Student.FRESHMAN
        )
        student1.save()

        student2 = models.Student(
            person_id='202200002',
            first_name='Alice',
            last_name='Hanson',
            email='ahanson@school.test',
            cell_number='+7035555555',
            notify_cell=True,
            grade_level=models.Student.FRESHMAN
        )
        student2.save()

        guardian1 = models.Guardian(
            person_id='2001',
            first_name='Guardian',
            last_name='Student',
            email='gstudent@email.test',
            cell_number='+17035555555',
            notify_cell=True,
        )
        guardian1.save()
        guardian1.students.add(student1)
        guardian1.save()

        guardian2 = models.Guardian(
            person_id='2002',
            first_name='Alice',
            last_name='Hanson',
            email='ahanson@email.test',
            cell_number='+17035555555',
            notify_cell=True
        )
        guardian2.save()
        guardian2.students.add(student2)
        guardian2.save()

        guardian3 = models.Guardian(
            person_id='2003',
            first_name='OtherGuardian',
            last_name='Student',
            email='ogstudent@email.test',
            cell_number='+17035555555',
            notify_cell=True,
        )
        guardian3.save()
        guardian3.students.add(student1)
        guardian3.save()

        teacher1 = models.Faculty(
            person_id='1000001',
            first_name='Teacher',
            last_name='User',
            email='tuser@school.test',
            cell_number='+17035555555',
            notify_cell=True,
            preferred_name='Mrs. Teacher'
        )
        teacher1.save()

        teacher2 = models.Faculty(
            person_id='1000002',
            first_name='Joey',
            last_name='West',
            email='jwest@school.test',
            cell_number='+17035555555',
            notify_cell=True,
            preferred_name='Mrs. West'
        )
        teacher2.save()

        course100 = models.Course(
            course_number='100',
            course_name='English 1'
        )
        course100.save()

        course105 = models.Course(
            course_number='105',
            course_name='Biology 2'
        )
        course105.save()

        section101 = models.Section(
            section_id='100101',
            course=course100,
            section_number='101',
            teacher=teacher1,
            school_year='2020',
            room='202',
            period='2nd'
        )
        section101.save()
        section101.students.add(student1)
        section101.save()

        section102 = models.Section(
            section_id='105102',
            course=course105,
            section_number='102',
            teacher=teacher2,
            school_year='2020',
            room='312',
            period='3rd'
        )
        section102.save()
        section102.students.add(student1)
        section102.students.add(student2)
        section102.save()

        trip = models.FieldTrip(
            id=1,
            name='Test Trip',
            group_name='Fishing Club',
            location='Bermuda Triangle',
            start_date='2020-03-01',
            dropoff_time='13:30',
            dropoff_location='Front Entrance',
            end_date='2020-04-01',
            pickup_time='13:30',
            pickup_location='Front Entrance',
            due_date='2020-02-15'
        )
        trip.save()
        trip.students.add(student1)
        trip.faculty.add(teacher1)
        trip.save()
        trip.generate_permission_slips()

        trip2 = models.FieldTrip(
            id=2,
            name='Trip 2',
            group_name='Hiking Club',
            location='Bald Mountain',
            start_date='2020-04-01',
            dropoff_time='12:34',
            dropoff_location='Rear Entrance',
            end_date='2020-04-06',
            pickup_time='16:10',
            pickup_location='Rear Entrance',
            due_date='2020-03-15'
        )
        trip2.save()
        trip2.sections.add(section102)
        trip2.faculty.add(teacher2)
        trip2.save()

        trip_archived = models.FieldTrip(
            id=3,
            name='Trip 3 Hidden',
            group_name='Hiking Club',
            location='Bald Mountain',
            start_date='2020-04-01',
            dropoff_time='12:34',
            dropoff_location='Rear Entrance',
            end_date='2020-04-06',
            pickup_time='16:10',
            pickup_location='Rear Entrance',
            due_date='2020-03-15'
        )
        trip_archived.save()
        trip_archived.sections.add(section102)
        trip_archived.faculty.add(teacher1)
        trip_archived.save()
        trip_archived.archive()

    def tearDown(self):
        """Reset logging."""
        # pylint: disable=invalid-name
        super(ViewTest, self).tearDown()

        logging.disable(logging.NOTSET)

    def check_view_redirect(self, url, expected_redirect, user=None):
        """Ensure an authenticated user is redirected to /trip

        Run this function in other test cases. This allows for testing
        multiple types of users."""
        if user is not None:
            self.client.force_login(user)
        response = self.client.get(url)

        # Check that status code is a redirect
        self.assertEqual(response.status_code, 302)

        # Check that response class is HttpResponseRedirect
        self.assertEqual(response.__class__.__name__, 'HttpResponseRedirect')

        # Check that the redirect URL is to '/trip'
        self.assertEqual(response.url, expected_redirect)


class IndexViewTests(ViewTest):
    """Test cases for the index view"""
    def test_index_view_exists(self):
        """Tests to ensure the index view exists"""
        self.assertTrue(hasattr(views, 'index'))

    def test_index_view_mapped_correctly(self):
        """Ensure that the index view is mapped to '/'"""
        self.assertEqual(reverse('index'), '/')

    def test_index_view_not_authenticated_redirect(self):
        """Ensure an unauthenticated user is redirected to /login"""
        self.check_view_redirect(reverse('index'), '/login')

    def test_index_view_authenticated_redirect_teacher(self):
        """Test index redirect for teacher user"""
        self.check_view_redirect(reverse('index'), '/trip', self.teacher_user)

    def test_index_view_authenticated_redirect_admin(self):
        """Test index redirect for admin user"""
        self.check_view_redirect(reverse('index'), '/trip', self.admin_user)

    def test_index_view_authenticated_redirect_superuser(self):
        """Test index redirect for super user"""
        self.check_view_redirect(reverse('index'), '/trip', self.super_user)

class DJOImportAllViewTests(ViewTest):
    """Test cases for djo import all view."""
    def test_djo_import_all_view_exists(self):
        """Ensure that the djo_import_all view exists."""
        self.assertTrue(hasattr(views, 'djo_import_all'))

    def test_djo_import_all_view_mapped_correctly(self):
        """Ensure that the URL mapping is correct."""
        self.assertEqual(reverse('import all'), '/import/')

    def test_djo_import_all_view_unauthenticated(self):
        """Ensure import view cannot be run while unauthenticated."""
        self.check_view_redirect(reverse('import all'), '/login?next=/import/')

    def test_djo_import_all_not_staff(self):
        """Ensure import view cannot be run while not logged in as admin."""
        self.client.force_login(self.teacher_user)
        response = self.client.get(reverse('import all'))

        # Check that status code is set to 403
        self.assertEqual(response.status_code, 403)

        # Check that response type is ResponseForbidden
        self.assertEqual(response.__class__.__name__, 'HttpResponseForbidden')

    def test_djo_import_all_staff_allowed(self):
        """Ensure djo_import_all runs when logged in as admin."""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('import all'))

        # Check that the call returns success (HTTP 204 No Content)
        self.assertEqual(response.status_code, 204)

    def test_djo_import_all_staff_allowed_super(self):
        """Ensure super users are able to run djo_import_all."""
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('import all'))

        # Check that the call returns success (HTTP 204 No Content)
        self.assertEqual(response.status_code, 204)

class SlipViewTests(ViewTest):
    """Test cases for the slip view."""
    def test_slip_view_exists(self):
        """Ensure that the slip view exists."""
        self.assertTrue(hasattr(views, 'slip'))

    def test_slip_view_mapped_correctly(self):
        """Ensure that the URL mapping is correct."""
        self.assertEqual(
            reverse('permission slip', kwargs={'slip_id': '1'}),
            '/slip/1/'
        )

    def test_slip_view_get_student_slip(self):
        """Ensure that a student link returns the student submission."""

        # We're going to get student1's trip1 permission slip.
        student1 = models.Student.objects.get(person_id='202300001')
        trip = models.FieldTrip.objects.get(id=1)
        permission_slip = models.PermissionSlip.objects.get(
            field_trip=trip,
            student=student1
        )
        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            student=student1
        )
        slip_url_id = slip_link.link_id

        response = self.client.get(
            reverse('permission slip', kwargs={'slip_id': slip_url_id})
        )

        self.assertContains(
            response,
            'Student Submission',
            status_code=200,
            html=True,
        )

    def test_slip_view_submit_student_slip(self):
        """Ensure that submitting a student slip returns a filled
        out student portion."""

        # We're going to get student1's trip1 permission slip.
        student1 = models.Student.objects.get(person_id='202300001')
        trip = models.FieldTrip.objects.get(id=1)
        permission_slip = models.PermissionSlip.objects.get(
            field_trip=trip,
            student=student1
        )
        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            student=student1
        )
        slip_url_id = slip_link.link_id
        slip_url = reverse('permission slip', kwargs={'slip_id': slip_url_id})

        csrf_token = self.client.get(slip_url).context.get('csrf_token')
        response = self.client.post(
            slip_url,
            {
                'name': 'Test Student Submission',
                'electronic_consent': True,
                'csrf_token': csrf_token
            },
        )

        # Assert that the returned page shows the page submitted.
        self.assertContains(
            response,
            'Submitted',
            status_code=200,
            html=False,
        )

        # Assert that the student slip has actually been submitted.
        permission_slip.refresh_from_db()
        self.assertEqual(permission_slip.student_signature, 'Test Student Submission')
        self.assertTrue(permission_slip.student_signature_date)

    def test_slip_view_reject_invalid_student_submission_ec(self):
        """Student submissions with no electronic_consent must be rejected."""

        # We're going to get student1's trip1 permission slip.
        student1 = models.Student.objects.get(person_id='202300001')
        trip = models.FieldTrip.objects.get(id=1)
        permission_slip = models.PermissionSlip.objects.get(
            field_trip=trip,
            student=student1
        )
        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            student=student1
        )
        slip_url_id = slip_link.link_id
        slip_url = reverse('permission slip', kwargs={'slip_id': slip_url_id})

        initial_student_sig = permission_slip.student_signature
        initial_student_sig_date = permission_slip.student_signature_date

        csrf_token = self.client.get(slip_url).context.get('csrf_token')
        response = self.client.post(
            slip_url,
            {
                'name': 'Test Student Submission', # NOTE: This is not blank
                'electronic_consent': False,       # NOTE: This is blank
                'csrf_token': csrf_token
            },
        )

        # Assert that the returned page is an error.
        self.assertEqual(response.status_code, 400)

        # Assert that the permission_slip has not been updated.
        permission_slip.refresh_from_db()
        final_student_sig = permission_slip.student_signature
        final_student_sig_date = permission_slip.student_signature_date

        self.assertEqual(initial_student_sig, final_student_sig)
        self.assertEqual(initial_student_sig_date, final_student_sig_date)

    def test_slip_view_reject_invalid_student_submission_sig(self):
        """Student submissions with no name/signature must be rejected."""

        # We're going to get student1's trip1 permission slip.
        student1 = models.Student.objects.get(person_id='202300001')
        trip = models.FieldTrip.objects.get(id=1)
        permission_slip = models.PermissionSlip.objects.get(
            field_trip=trip,
            student=student1
        )
        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            student=student1
        )
        slip_url_id = slip_link.link_id
        slip_url = reverse('permission slip', kwargs={'slip_id': slip_url_id})

        initial_student_sig = permission_slip.student_signature
        initial_student_sig_date = permission_slip.student_signature_date

        csrf_token = self.client.get(slip_url).context.get('csrf_token')
        response = self.client.post(
            slip_url,
            {
                'name': '',                 # NOTE: This is blank
                'electronic_consent': True, # NOTE: This is not blank
                'csrf_token': csrf_token
            },
        )

        # Assert that the returned page is an error.
        self.assertEqual(response.status_code, 400)

        # Assert that the permission_slip has not been updated.
        permission_slip.refresh_from_db()
        final_student_sig = permission_slip.student_signature
        final_student_sig_date = permission_slip.student_signature_date

        self.assertEqual(initial_student_sig, final_student_sig)
        self.assertEqual(initial_student_sig_date, final_student_sig_date)

    def test_slip_view_already_submitted_student_slip(self):
        """Ensure that an already submitted student slip is rendered with
        submitted shown in the green badge."""

        # We're going to get student1's trip1 permission slip.
        student1 = models.Student.objects.get(person_id='202300001')
        trip = models.FieldTrip.objects.get(id=1)
        permission_slip = models.PermissionSlip.objects.get(
            field_trip=trip,
            student=student1
        )
        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            student=student1
        )
        slip_url_id = slip_link.link_id
        slip_url = reverse('permission slip', kwargs={'slip_id': slip_url_id})

        csrf_token = self.client.get(slip_url).context.get('csrf_token')
        self.client.post(
            slip_url,
            {
                'name': 'Test Student Submission',
                'electronic_consent': True,
                'csrf_token': csrf_token
            },
        )
        response = self.client.get(slip_url)

        # Assert that the returned page shows the page submitted.
        self.assertContains(
            response,
            'Submitted',
            status_code=200,
            html=False,
        )

    def test_slip_view_get_parent_slip(self):
        """Ensure that a parent link returns the parent submission."""

        # We're going to get guardian1's trip1 permission slip.
        student1 = models.Student.objects.get(person_id='202300001')
        guardian1 = models.Guardian.objects.get(person_id='2001')
        trip = models.FieldTrip.objects.get(id=1)
        permission_slip = models.PermissionSlip.objects.get(
            field_trip=trip,
            student=student1
        )
        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            guardian=guardian1
        )
        slip_url_id = slip_link.link_id

        response = self.client.get(
            reverse('permission slip', kwargs={'slip_id': slip_url_id})
        )

        self.assertContains(
            response,
            'Parent Submission',
            status_code=200,
            html=True,
        )

    def test_slip_view_POST_parent_slip(self):
        """Ensure that submitting a student slip returns a filled out guardian portion."""

        # We're going to get guardian1's trip1 permission slip.
        student1 = models.Student.objects.get(person_id='202300001')
        guardian1 = models.Guardian.objects.get(person_id='2001')
        trip = models.FieldTrip.objects.get(id=1)
        permission_slip = models.PermissionSlip.objects.get(
            field_trip=trip,
            student=student1
        )
        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            guardian=guardian1
        )
        slip_url_id = slip_link.link_id
        slip_url = reverse('permission slip', kwargs={'slip_id': slip_url_id})

        csrf_token = self.client.get(slip_url).context.get('csrf_token')
        response = self.client.post(
            slip_url,
            {
                'name': 'Test Parent Submission',
                'electronic_consent': True,
                'csrf_token': csrf_token
            },
        )

        # Assert that the returned page shows the page submitted.
        self.assertContains(
            response,
            'Submitted',
            status_code=200,
            html=False,
        )

        # Assert that the returned page shows the guardian name.
        self.assertContains(
            response,
            'Guardian Student',
            status_code=200,
            html=False
        )

        # Assert that the student slip has actually been submitted.
        permission_slip.refresh_from_db()
        self.assertEqual(permission_slip.guardian_signature, 'Test Parent Submission')
        self.assertTrue(permission_slip.guardian_signature_date)

    def test_slip_view_POST_second_parent_slip(self):
        """A parent submission from a different parent should update the slip."""

        # First get guardian1's slip and fill it out.
        student1 = models.Student.objects.get(person_id='202300001')
        guardian1 = models.Guardian.objects.get(person_id='2001')
        trip = models.FieldTrip.objects.get(id=1)
        permission_slip = models.PermissionSlip.objects.get(
            field_trip=trip,
            student=student1
        )
        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            guardian=guardian1
        )
        slip_url = reverse('permission slip', kwargs={'slip_id': slip_link.link_id})

        csrf_token = self.client.get(slip_url).context.get('csrf_token')
        response = self.client.post(
            slip_url,
            {
                'name': 'Test Guardian 1 Submission',
                'electronic_consent': True,
                'csrf_token': csrf_token
            },
        )

        permission_slip.refresh_from_db()
        initial_sig_date = permission_slip.guardian_signature_date

        # At this point the slip should be filled out by guardian1. Lets change
        # that to guardian3 and assert that the database gets that update.

        # First, let's wait a couple of seconds to ensure the time/date is
        # different, as we'll be testing to make sure the database changes that
        # stored/logged value.
        sleep(2)

        guardian3 = models.Guardian.objects.get(person_id='2003')
        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            guardian=guardian3
        )
        slip_url = reverse('permission slip', kwargs={'slip_id': slip_link.link_id})

        csrf_token = self.client.get(slip_url).context.get('csrf_token')
        signature = 'Test Guardian 3 Submission'
        response = self.client.post(
            slip_url,
            {
                'name': signature,
                'electronic_consent': True,
                'csrf_token': csrf_token
            },
        )

        # Assert response is correct

        self.assertContains(
            response,
            'OtherGuardian Student',
            status_code=200,
            html=False,
        )

        # Assert database was updated
        permission_slip.refresh_from_db()
        final_sig_date = permission_slip.guardian_signature_date
        self.assertEqual(permission_slip.guardian_signature, signature)
        self.assertNotEqual(initial_sig_date, final_sig_date)

    def test_slip_view_reject_invalid_parent_submission_ec(self):
        """Parent submissions with no electronic_consent must be rejected."""

        # We're going to get guardian1's trip1 permission slip.
        student1 = models.Student.objects.get(person_id='202300001')
        guardian1 = models.Guardian.objects.get(person_id='2001')
        trip = models.FieldTrip.objects.get(id=1)
        permission_slip = models.PermissionSlip.objects.get(
            field_trip=trip,
            student=student1
        )
        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            guardian=guardian1
        )
        slip_url_id = slip_link.link_id
        slip_url = reverse('permission slip', kwargs={'slip_id': slip_url_id})

        initial_student_sig = permission_slip.student_signature
        initial_student_sig_date = permission_slip.student_signature_date

        csrf_token = self.client.get(slip_url).context.get('csrf_token')
        response = self.client.post(
            slip_url,
            {
                'name': 'Test Parent Submission', # NOTE: This is not blank
                'electronic_consent': False,      # NOTE: This is blank
                'csrf_token': csrf_token
            },
        )

        # Assert that the returned page is an error.
        self.assertEqual(response.status_code, 400)

        # Assert that the permission_slip has not been updated.
        permission_slip.refresh_from_db()
        final_student_sig = permission_slip.student_signature
        final_student_sig_date = permission_slip.student_signature_date

        self.assertEqual(initial_student_sig, final_student_sig)
        self.assertEqual(initial_student_sig_date, final_student_sig_date)

    def test_slip_view_reject_invalid_parent_submission_sig(self):
        """Parent submissions with no name/signature must be rejected."""

        # We're going to get guardian1's trip1 permission slip.
        student1 = models.Student.objects.get(person_id='202300001')
        guardian1 = models.Guardian.objects.get(person_id='2001')
        trip = models.FieldTrip.objects.get(id=1)
        permission_slip = models.PermissionSlip.objects.get(
            field_trip=trip,
            student=student1
        )
        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            guardian=guardian1
        )
        slip_url_id = slip_link.link_id
        slip_url = reverse('permission slip', kwargs={'slip_id': slip_url_id})

        initial_student_sig = permission_slip.student_signature
        initial_student_sig_date = permission_slip.student_signature_date

        csrf_token = self.client.get(slip_url).context.get('csrf_token')
        response = self.client.post(
            slip_url,
            {
                'name': '',                 # NOTE: This is blank
                'electronic_consent': True, # NOTE: This is not blank
                'csrf_token': csrf_token
            },
        )

        # Assert that the returned page is an error.
        self.assertEqual(response.status_code, 400)

        # Assert that the permission_slip has not been updated.
        permission_slip.refresh_from_db()
        final_student_sig = permission_slip.student_signature
        final_student_sig_date = permission_slip.student_signature_date

        self.assertEqual(initial_student_sig, final_student_sig)
        self.assertEqual(initial_student_sig_date, final_student_sig_date)

    def test_completed_slip_shows_completed(self):
        """Completed slips should show a green badge in the upper right."""

        # We're going to get guardian1 and student1s' trip1 permission slip.
        student1 = models.Student.objects.get(person_id='202300001')
        guardian1 = models.Guardian.objects.get(person_id='2001')
        trip = models.FieldTrip.objects.get(id=1)
        permission_slip = models.PermissionSlip.objects.get(
            field_trip=trip,
            student=student1
        )
        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            guardian=guardian1
        )
        slip_url = reverse('permission slip', kwargs={'slip_id': slip_link.link_id})

        csrf_token = self.client.get(slip_url).context.get('csrf_token')
        self.client.post(
            slip_url,
            {
                'name': 'Guardian 1 Name',
                'electronic_consent': True,
                'csrf_token': csrf_token
            },
        )

        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            student=student1
        )
        slip_url = reverse('permission slip', kwargs={'slip_id': slip_link.link_id})

        csrf_token = self.client.get(slip_url).context.get('csrf_token')
        response = self.client.post(
            slip_url,
            {
                'name': 'Student 1 Name',
                'electronic_consent': True,
                'csrf_token': csrf_token
            },
        )

        self.assertContains(
            response,
            '<h3 class="float-right"><span class="badge badge-success">Complete</span></h3>',
            status_code=200,
            html=False,
        )

class TripListViewTest(ViewTest):
    """Test the trip_list view."""
    def test_trip_list_view_exists(self):
        """Tests to ensure the trip list view exists."""
        self.assertTrue(hasattr(views, 'index'))

    def test_trip_list_view_mapped_correctly(self):
        """The trip_list view should be mapped to /trip/"""
        self.assertEqual(reverse('trip list'), '/trip/')

    def test_trip_list_hidden_view_mapped_correctly(self):
        """trip_list view should also have a pointer from /archive/"""
        self.assertEqual(reverse('trip archive'), '/archive/')

    def test_trip_list_login_redirect(self):
        """trip_list should redirect anonymous users to the login page"""
        next_url = '/login?next={0}'.format(reverse('trip list'))
        self.check_view_redirect(reverse('trip list'), next_url)

    def test_trip_list_hidden_login_redirect(self):
        """trip_list archive should redirect anonymous users to the login page"""
        next_url = '/login?next={0}'.format(reverse('trip archive'))
        self.check_view_redirect(reverse('trip archive'), next_url)

    def test_trip_list_get_admin(self):
        """trip list should include all trips when admin logged in"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('trip list'))
        self.assertContains(
            response,
            'Test Trip',
            status_code=200,
            html=False
        )
        self.assertContains(
            response,
            'Trip 2',
            status_code=200,
            html=False
        )
        self.assertNotContains(
            response,
            'Trip 3 Hidden',
            status_code=200,
            html=False
        )

    def test_trip_list_get_teacher(self):
        """trip list should include only trips teacher is on when teacher logged in"""
        self.client.force_login(self.teacher_user)
        response = self.client.get(reverse('trip list'))
        self.assertContains(
            response,
            'Test Trip',
            status_code=200,
            html=False
        )
        self.assertNotContains(
            response,
            'Trip 2',
            status_code=200,
            html=False
        )
        self.assertNotContains(
            response,
            'Trip 3 Hidden',
            status_code=200,
            html=False
        )

    def test_trip_list_archive_get_admin(self):
        """trip list archive should only return (all) hidden trips"""
        self.client.force_login(self.admin_user)
        response = self.client.get(
            reverse('trip archive')
        )
        self.assertNotContains(
            response,
            'Test Trip',
            status_code=200,
            html=False
        )
        self.assertNotContains(
            response,
            'Trip 2',
            status_code=200,
            html=False
        )
        self.assertContains(
            response,
            'Trip 3 Hidden',
            status_code=200,
            html=False
        )

    def test_trip_list_archive_get_teacher(self):
        """teachers are not permitted to view archive"""
        self.client.force_login(self.teacher_user)
        response = self.client.get(reverse('trip archive'))
        self.assertEqual(response.status_code, 403)

class TripDetailTest(ViewTest):
    """Tests the trip_detail view"""
    def test_trip_detail_exists(self):
        """The test_trip view should exist"""
        self.assertTrue(hasattr(views, 'trip_detail'))

    def test_trip_detail_mapping(self):
        """trip_detail should map to /trip/<int:trip_id>/"""
        self.assertEqual(reverse('trip detail', kwargs={'trip_id': 1}), '/trip/1/')

    def test_trip_redirect_anonymous(self):
        """should redirect anonymous users to /login?next=/trip/"""
        url = reverse('trip detail', kwargs={'trip_id': 1})
        self.check_view_redirect(url, '/login?next={0}'.format(url))

    def test_trip_detail_404_on_nonexistent_trip(self):
        """should return 404 when nonexistent trip requested"""
        self.client.force_login(self.admin_user)
        url = reverse('trip detail', kwargs={'trip_id': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.__class__.__name__, 'HttpResponseNotFound')

    def test_trip_detail_403_notadmin_notcoordinator(self):
        """should return 403 when not admin and not faculty coordinator for trip"""
        self.client.force_login(self.teacher_user)
        url = reverse('trip detail', kwargs={'trip_id': 2})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.__class__.__name__, 'HttpResponseForbidden')

    def test_trip_detail_archived_trips_admin_readonly(self):
        """should return archived trips as readonly even for admin users"""
        self.client.force_login(self.admin_user)
        url = reverse('trip detail', kwargs={'trip_id': 3})
        response = self.client.get(url)
        self.assertTrue(response.context['form'].read_only)

    def test_trip_detail_archived_trips_notadmin_readonly(self):
        """should return archived trips as readonly"""
        self.client.force_login(self.teacher_user)
        url = reverse('trip detail', kwargs={'trip_id': 3})
        response = self.client.get(url)
        self.assertTrue(response.context['form'].read_only)

    def test_trip_detail_approved_notadmin_readonly(self):
        """should return readonly when trip approved and user non admin"""
        trip1 = models.FieldTrip.objects.get(id=1)
        trip1.approve()
        url = reverse('trip detail', kwargs={'trip_id': 1})
        self.client.force_login(self.teacher_user)
        response = self.client.get(url)
        self.assertTrue(response.context['form'].read_only)

    def test_trip_detail_approved_admin_fillable(self):
        """should return fillable when trip approved and user admin"""
        trip1 = models.FieldTrip.objects.get(id=1)
        trip1.approve()
        url = reverse('trip detail', kwargs={'trip_id': 1})
        self.client.force_login(self.admin_user)
        response = self.client.get(url)
        self.assertFalse(response.context['form'].read_only)

    def test_trip_detail_released_notadmin_readonly(self):
        """should return readonly when trip released and user non admin"""
        trip1 = models.FieldTrip.objects.get(id=1)
        trip1.approve()
        trip1.release()
        url = reverse('trip detail', kwargs={'trip_id': 1})
        self.client.force_login(self.teacher_user)
        response = self.client.get(url)
        self.assertTrue(response.context['form'].read_only)

    def test_trip_detail_released_admin_fillable(self):
        """should return fillable when trip released and user admin"""
        trip1 = models.FieldTrip.objects.get(id=1)
        trip1.approve()
        trip1.release()
        url = reverse('trip detail', kwargs={'trip_id': 1})
        self.client.force_login(self.admin_user)
        response = self.client.get(url)
        self.assertFalse(response.context['form'].read_only)

    def test_trip_detail_new_trip_mapped(self):
        """new trip /trip/new should be mapped"""
        self.assertEqual(reverse('new field trip'), '/trip/new/')

    def test_trip_detail_new_trip_uses_trip_detail(self):
        """/trip/new should use the trip_detail method/template"""
        self.client.force_login(self.teacher_user)
        response = self.client.get(reverse('new field trip'))
        self.assertTemplateUsed(response, 'paperlesspermission/trip_detail.html')

    def test_trip_detail_GET_redirected_new_trip_anonymous(self):
        """should return a login redirect when anonymous user requests /trip/new"""
        expected_url = '/login?next={0}'.format(reverse('new field trip'))
        self.check_view_redirect(reverse('new field trip'), expected_url)

    def test_trip_detail_GET_200_new_trip_loggedin(self):
        """should return fillable when trip new and user logged in"""
        self.client.force_login(self.teacher_user)
        url = reverse('new field trip')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].read_only)

    def test_trip_detail_POST_400_on_invalid_data(self):
        """should return 400 on invalid data POST"""
        self.client.force_login(self.teacher_user)
        url = reverse('trip detail', kwargs={'trip_id': 1})
        csrf_token = self.client.get(url).context.get('csrf_token')
        response = self.client.post(url, {'csrf_token': csrf_token})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.__class__.__name__, 'HttpResponseBadRequest')

    def test_trip_detail_POST_403_on_readonly(self):
        """should return 403 on 'authorized' POST to readonly form"""
        self.client.force_login(self.teacher_user)
        trip1 = models.FieldTrip.objects.get(id=1)
        trip1.approve() # trip is now readonly for teacher_user
        url = reverse('trip detail', kwargs={'trip_id': 1})
        csrf_token = self.client.get(url).context.get('csrf_token')
        response = self.client.post(url, {'csrf_token': csrf_token})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.__class__.__name__, 'HttpResponseForbidden')

    def test_trip_detail_POST_302_on_valid(self):
        """should return redirect to /trip/ on authorized, valid data"""
        self.client.force_login(self.teacher_user)
        url = reverse('trip detail', kwargs={'trip_id': 1})
        csrf_token = self.client.get(url).context.get('csrf_token')
        post_body = {
            'csrf_token'       : csrf_token,
            'name'             : 'Updated Trip Name',
            'due_date'         : '05/05/2020',
            'group_name'       : 'Updated Group Name',
            'location'         : 'Updated Location',
            'start_date'       : '06/06/2020',
            'dropoff_time'     : '10:10',
            'dropoff_location' : 'Updated Dropoff',
            'end_date'         : '06/07/2020',
            'pickup_time'      : '11:11',
            'pickup_location'  : 'Updated Pickup',
            'faculty'          : models.Faculty.objects.get(person_id='1000001').id,
            'students'         : models.Student.objects.get(person_id='202300001').id,
        }
        response = self.client.post(url, post_body)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.__class__.__name__, 'HttpResponseRedirect')
        self.assertEqual(response.url, '/trip')

    def test_trip_detail_POST_302_on_new(self):
        """should return redirect to /trip on authorized, valid data to /trip/new"""
        self.client.force_login(self.teacher_user)
        url = reverse('trip detail', kwargs={'trip_id': 1})
        csrf_token = self.client.get(url).context.get('csrf_token')
        post_body = {
            'csrf_token'       : csrf_token,
            'name'             : 'Updated Trip Name',
            'due_date'         : '05/05/2020',
            'group_name'       : 'Updated Group Name',
            'location'         : 'Updated Location',
            'start_date'       : '06/06/2020',
            'dropoff_time'     : '10:10',
            'dropoff_location' : 'Updated Dropoff',
            'end_date'         : '06/07/2020',
            'pickup_time'      : '11:11',
            'pickup_location'  : 'Updated Pickup',
            'faculty'          : models.Faculty.objects.get(person_id='1000001').id,
            'students'         : models.Student.objects.get(person_id='202300001').id,
        }
        response = self.client.post(url, post_body)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.__class__.__name__, 'HttpResponseRedirect')
        self.assertEqual(response.url, '/trip')

    def test_trip_detail_POST_update_db_on_valid(self):
        """should update database on valid POST"""
        self.client.force_login(self.teacher_user)
        url = reverse('trip detail', kwargs={'trip_id': 1})
        csrf_token = self.client.get(url).context.get('csrf_token')
        post_body = {
            'csrf_token'       : csrf_token,
            'name'             : 'Updated Trip Name',
            'due_date'         : '05/05/2020',
            'group_name'       : 'Updated Group Name',
            'location'         : 'Updated Location',
            'start_date'       : '06/06/2020',
            'dropoff_time'     : '10:10',
            'dropoff_location' : 'Updated Dropoff',
            'end_date'         : '06/07/2020',
            'pickup_time'      : '11:11',
            'pickup_location'  : 'Updated Pickup',
            'faculty'          : models.Faculty.objects.get(person_id='1000002').id,
            'students'         : models.Student.objects.get(person_id='202200002').id,
        }
        self.client.post(url, post_body)

        trip1 = models.FieldTrip.objects.get(id=1)
        self.assertEqual(trip1.name, 'Updated Trip Name')
        self.assertEqual(trip1.due_date, date(2020, 5, 5))
        self.assertEqual(trip1.group_name, 'Updated Group Name')
        self.assertEqual(trip1.location, 'Updated Location')
        self.assertEqual(trip1.start_date, date(2020, 6, 6))
        self.assertEqual(trip1.dropoff_time, time(10, 10))
        self.assertEqual(trip1.dropoff_location, 'Updated Dropoff')
        self.assertEqual(trip1.end_date, date(2020, 6, 7))
        self.assertEqual(trip1.pickup_time, time(11, 11))
        self.assertEqual(trip1.pickup_location, 'Updated Pickup')
        try:
            trip1.students.get(person_id='202200002')
        except models.Student.DoesNotExist:
            self.fail('Students not updated')
        try:
            trip1.faculty.get(person_id='1000002')
        except models.Faculty.DoesNotExist:
            self.fail('Faculty not updated')

    def test_trip_detail_GET_afterupdate_show_values(self):
        """after db update, values should change"""
        self.client.force_login(self.teacher_user)
        url = reverse('trip detail', kwargs={'trip_id': 1})
        csrf_token = self.client.get(url).context.get('csrf_token')
        post_body = {
            'csrf_token'       : csrf_token,
            'name'             : 'Updated Trip Name',
            'due_date'         : '05/05/2020',
            'group_name'       : 'Updated Group Name',
            'location'         : 'Updated Location',
            'start_date'       : '06/06/2020',
            'dropoff_time'     : '10:10',
            'dropoff_location' : 'Updated Dropoff',
            'end_date'         : '06/07/2020',
            'pickup_time'      : '11:11',
            'pickup_location'  : 'Updated Pickup',
            'faculty'          : models.Faculty.objects.get(person_id='1000001').id,
            'students'         : models.Student.objects.get(person_id='202200002').id,
        }
        self.client.post(url, post_body)
        response = self.client.get(url)
        self.assertContains(response, 'Updated Trip Name')

class ApproveTripViewTest(ViewTest):
    """tests for the approve_trip view"""
    def test_exists(self):
        """The approve_trip view should exist"""
        self.assertTrue(hasattr(views, 'approve_trip'))

    def test_mapping(self):
        """approve_trip should map to /trip/<int:trip_id>/approve/"""
        self.assertEqual(reverse('approve trip', kwargs={'trip_id': 1}), '/trip/1/approve/')

    def test_redirect_anonymous(self):
        """should redirect anonymous users to /login?next=/trip/<int:trip_id>/approve/"""
        url = reverse('approve trip', kwargs={'trip_id': 1})
        self.check_view_redirect(url, '/login?next={0}'.format(url))

    def test_returns_404_on_invalid_trip(self):
        """should return a 404 if the given trip does not exist"""
        url = reverse('approve trip', kwargs={'trip_id': 99})
        self.client.force_login(self.admin_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_reject_nonadmin(self):
        """should reject nonadmin users"""
        url = reverse('approve trip', kwargs={'trip_id': 1})
        trip1 = models.FieldTrip(id=1)
        # Check initial status
        self.assertEqual(trip1.status, models.FieldTrip.NEW)
        self.client.force_login(self.teacher_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        trip1 = models.FieldTrip.objects.get(id=1)
        # Check final status
        self.assertEqual(trip1.status, models.FieldTrip.NEW)

    def test_approves_valid_trip(self):
        """should update the database and approve a given trip"""
        url = reverse('approve trip', kwargs={'trip_id': 1})
        trip1 = models.FieldTrip.objects.get(id=1)
        # Check initial status
        self.assertEqual(trip1.status, models.FieldTrip.NEW)
        # Call the update
        self.client.force_login(self.admin_user)
        self.client.get(url)
        # Check final status
        trip1.refresh_from_db()
        self.assertEqual(trip1.status, models.FieldTrip.APPROVED)

class ReleaseTripViewTest(ViewTest):
    """tests for the release_trip view"""
    def test_exists(self):
        """The release_trip view should exist"""
        self.assertTrue(hasattr(views, 'release_trip'))

    def test_mapping(self):
        """approve_trip should map to /trip/<int:trip_id>/approve/"""
        self.assertEqual(reverse('release trip emails', kwargs={'trip_id': 1}), '/trip/1/release/')

    def test_redirect_anonymous(self):
        """should redirect anonymous users to /login?next=/trip/<int:trip_id>/release/"""
        url = reverse('release trip emails', kwargs={'trip_id': 1})
        self.check_view_redirect(url, '/login?next={0}'.format(url))

    def test_reject_nonadmin(self):
        """should reject non-admin users"""
        url = reverse('release trip emails', kwargs={'trip_id': 1})
        trip1 = models.FieldTrip.objects.get(id=1)
        trip1.approve()
        # Check initial status
        self.assertEqual(trip1.status, models.FieldTrip.APPROVED)
        # Call web request
        self.client.force_login(self.teacher_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        # Check final status
        trip1.refresh_from_db()
        self.assertEqual(trip1.status, models.FieldTrip.APPROVED)

    def test_releases_valid_trip(self):
        """should update database and release a given trip"""
        url = reverse('release trip emails', kwargs={'trip_id': 1})
        trip1 = models.FieldTrip.objects.get(id=1)
        trip1.approve()
        # Check initial status
        self.assertEqual(trip1.status, models.FieldTrip.APPROVED)
        # Call web request
        self.client.force_login(self.admin_user)
        self.client.get(url)
        # Check final status
        trip1.refresh_from_db()
        self.assertEqual(trip1.status, models.FieldTrip.RELEASED)

class ArchiveTripViewTest(ViewTest):
    """tests for the archive_trip view"""
    def test_exists(self):
        """The archive_trip view should exist"""
        self.assertTrue(hasattr(views, 'archive_trip'))

    def test_mapping(self):
        """archive_trip should map to /trip/<int:trip_id>/archive/"""
        self.assertEqual(reverse('archive trip', kwargs={'trip_id': 1}), '/trip/1/archive/')

    def test_redirect_anonymous(self):
        """should redirect anonymous users to /login?next=/trip/<int:trip_id>/archive/"""
        url = reverse('archive trip', kwargs={'trip_id': 1})
        self.check_view_redirect(url, '/login?next={0}'.format(url))

    def test_reject_nonadmin(self):
        """should reject nonadmin users"""
        url = reverse('archive trip', kwargs={'trip_id': 1})
        trip1 = models.FieldTrip.objects.get(id=1)
        # Check initial status
        self.assertNotEqual(trip1.status, models.FieldTrip.ARCHIVED)
        # web request
        self.client.force_login(self.teacher_user)
        response = self.client.get(url)
        # check web request
        self.assertEqual(response.status_code, 403)
        # check final status
        trip1.refresh_from_db()
        self.assertNotEqual(trip1.status, models.FieldTrip.ARCHIVED)

    def test_404_on_invalid_trip(self):
        """should return 404 when given invalid trip"""
        url = reverse('archive trip', kwargs={'trip_id': 99})
        self.client.force_login(self.admin_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_archive_valid_trip(self):
        """should update database on valid request"""
        url = reverse('archive trip', kwargs={'trip_id': 1})
        trip1 = models.FieldTrip.objects.get(id=1)
        # initial check
        self.assertNotEqual(trip1.status, models.FieldTrip.ARCHIVED)
        # web request
        self.client.force_login(self.admin_user)
        self.client.get(url)
        # final check
        trip1.refresh_from_db()
        self.assertEqual(trip1.status, models.FieldTrip.ARCHIVED)

class TripStatusViewTest(ViewTest):
    """tests for the trip_status view"""
    def test_exists(self):
        """The trip_status view should exist"""
        self.assertTrue(hasattr(views, 'archive_trip'))

    def test_mapping(self):
        """trip_status should map to /trip/<int:trip_id>/status/"""
        self.assertEqual(reverse('trip status', kwargs={'trip_id': 1}), '/trip/1/status/')

    def test_redirect_anonymous(self):
        """should redirect anonymous users to /login?next=/trip/<int:trip_id>/status/"""
        url = reverse('trip status', kwargs={'trip_id': 1})
        self.check_view_redirect(url, '/login?next={0}'.format(url))

class NewTripViewTest(ViewTest):
    """tests for the new_trip view"""
    def test_exists(self):
        """The new_trip view should exist"""
        self.assertTrue(hasattr(views, 'new_trip'))

    def test_mapping(self):
        """new_trip should map to /trip/new/"""
        self.assertEqual(reverse('new field trip'), '/trip/new/')

    def test_redirect_anonymous(self):
        """should redirect anonymous users to /login?next=/trip/<int:trip_id>/status/"""
        url = reverse('new field trip')
        self.check_view_redirect(url, '/login?next={0}'.format(url))

class SlipResetViewTest(ViewTest):
    """tests for the slip_reset view"""
    def test_exists(self):
        """The slip_reset view should exist"""
        self.assertTrue(hasattr(views, 'slip_reset'))

    def test_mapping(self):
        """slip_reset should map to /slip/<int:slip_id>/reset/"""
        self.assertEqual(reverse('reset permission slip', kwargs={'slip_id': 1}), '/slip/1/reset/')

    def test_redirect_anonymous(self):
        """should redirect anonymous users to /login?next=/slip/<int:slip_id>/status/"""
        url = reverse('reset permission slip', kwargs={'slip_id': 1})
        self.check_view_redirect(url, '/login?next={0}'.format(url))

class SlipResendViewTest(ViewTest):
    """tests for the slip_resend view"""
    def test_exists(self):
        """The slip_resend view should exist"""
        self.assertTrue(hasattr(views, 'slip_resend'))

    def test_mapping(self):
        """slip_reset should map to /slip/<int:slip_id>/resend/"""
        self.assertEqual(reverse('resend permission slip', kwargs={'slip_id': 1}), '/slip/1/resend/')

    def test_redirect_anonymous(self):
        """should redirect anonymous users to /login?next=/slip/<int:slip_id>/resend/"""
        url = reverse('resend permission slip', kwargs={'slip_id': 1})
        self.check_view_redirect(url, '/login?next={0}'.format(url))

