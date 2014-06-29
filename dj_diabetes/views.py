# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import logging
import arrow

from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, DeleteView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

# dj_diabetes
from dj_diabetes.models import Appointments, Examinations
from dj_diabetes.models import Issues, Exercises, Glucoses, Weights, Meals
from dj_diabetes.forms import GlucosesForm, AppointmentsForm, IssuesForm
from dj_diabetes.forms import WeightsForm, MealsForm, ExercisesForm
from dj_diabetes.forms import ExamsForm, ExamDetailsFormSet

# Get an instance of a logger
logger = logging.getLogger(__name__)


#************************
# FBV : simple actions  *
#************************
def page_it(data, record_per_page, page=''):
    """
        return the data of the current page
    """
    paginator = Paginator(data, record_per_page)
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        data = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999),
        # deliver last page of results.
        data = paginator.page(paginator.num_pages)

    return data


def right_now(model):
    """
        return a dict of 2 property set with current date and time
    """
    now_date = arrow.utcnow().to(settings.TIME_ZONE).format('YYYY-MM-DD')
    now_hour = arrow.utcnow().to(settings.TIME_ZONE).format('HH:mm:ss')
    my_date = 'date_' + model
    my_hour = 'hour_' + model
    return {my_date: now_date, my_hour: now_hour}


def logout_view(request):
    """
        logout the user then redirect him to the home page
    """
    logout(request)
    return HttpResponseRedirect(reverse('home'))


def round_value(value):
    if value:
        return round(float(value), 1)
    else:
        return 0


@login_required
def chart_data_json(request):
    data = {}
    data['chart_data'] = ChartData.get_datas()
    return HttpResponse(json.dumps(data), content_type='application/json')


class ChartData(object):

    @classmethod
    def get_datas(cls):
        glucose_data = Glucoses.objects.all().order_by('-date_glucose')[:14]

        data = {'date_glucose': [], 'glucose': []}
        for g in glucose_data:
            data['date_glucose'].append(g.date_glucose.strftime('%m/%d'))
            data['glucose'].append(round_value(g.glucose))

        return data

#************************
# Classe Based View
#************************


class GlucosesCreateView(CreateView):
    """
        to Create Glucoses
    """
    form_class = GlucosesForm
    template_name = "dj_diabetes/glucoses_form.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GlucosesCreateView, self).dispatch(*args, **kwargs)

    def get_initial(self):
        """
            set the default date and hour of the date_xxx and hour_xxx
            property of the current model
        """
        return right_now("glucose")

    def form_valid(self, form):
        glucose = form.save(commit=False)
        if form.is_valid():
            glucose.user = self.request.user
            glucose.save()

        return HttpResponseRedirect(reverse('home'))

    def get_context_data(self, **kw):
        data = Glucoses.objects.all().order_by('-date_glucose')
        #paginator vars
        record_per_page = 5
        page = self.request.GET.get('page')
        # paginator call
        data = page_it(data, record_per_page, page)

        context = super(GlucosesCreateView, self).get_context_data(**kw)
        #context['use_insuline'] = [False if insulin in GlucosesForm]
        context['action'] = 'add_glucoses'
        context['data'] = data
        return context


class GlucosesUpdateView(UpdateView):
    """
        to Edit Glucoses
    """
    model = Glucoses
    form_class = GlucosesForm
    template_name = "dj_diabetes/glucoses_form.html"
    fields = ['moment', 'comment', 'glucose', 'insulin', 'date_glucose']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GlucosesUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        if form.is_valid():
            form.save()

        return HttpResponseRedirect(reverse('home'))

    def get_context_data(self, **kw):
        data = Glucoses.objects.all().order_by('-date_glucose')
        #paginator vars
        record_per_page = 5
        page = self.request.GET.get('page')
        # paginator call
        data = page_it(data, record_per_page, page)

        context = super(GlucosesUpdateView, self).get_context_data(**kw)
        context['data'] = data
        return context


class GlucosesDeleteView(DeleteView):
    """
        to Delete Glucoses
    """
    model = Glucoses
    success_url = reverse_lazy('home')
    template_name = 'dj_diabetes/confirm_delete.html'


class AppointmentsCreateView(CreateView):
    """
        to Create Appointments
    """
    form_class = AppointmentsForm
    template_name = "dj_diabetes/appointments_form.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AppointmentsCreateView, self).dispatch(*args, **kwargs)

    def get_initial(self):
        """
            set the default date and hour of the date_xxx and hour_xxx
            property of the current model
        """
        return right_now("appointment")

    def form_valid(self, form):
        appointments = form.save(commit=False)
        if form.is_valid():
            appointments.user = self.request.user
            appointments.save()

        return HttpResponseRedirect(reverse('appointments'))

    def get_context_data(self, **kw):
        data = Appointments.objects.all().order_by('-date_appointment')
        #paginator vars
        record_per_page = 15
        page = self.request.GET.get('page')
        # paginator call
        data = page_it(data, record_per_page, page)

        context = super(AppointmentsCreateView, self).get_context_data(**kw)
        context['action'] = 'add_appointments'
        context['data'] = data
        return context


class AppointmentsUpdateView(UpdateView):
    """
        to Edit Appointments
    """
    model = Appointments
    form_class = AppointmentsForm
    template_name = "dj_diabetes/appointments_form.html"
    fields = ['appointment_types', 'title', 'body', 'date_appointment',
              'recall_one_duration', 'recall_two_duration',
              'recall_one_unit', 'recall_two_unit']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AppointmentsUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        if form.is_valid():
            form.save()

        return HttpResponseRedirect(reverse('appointments'))

    def get_context_data(self, **kw):
        data = Appointments.objects.all().order_by('-date_appointment')
        #paginator vars
        record_per_page = 15
        page = self.request.GET.get('page')
        # paginator call
        data = page_it(data, record_per_page, page)

        context = super(AppointmentsUpdateView, self).get_context_data(**kw)
        context['data'] = data
        return context


class AppointmentsDeleteView(DeleteView):
    """
        to Delete Appointments
    """
    model = Appointments
    success_url = reverse_lazy('appointments')
    template_name = 'dj_diabetes/confirm_delete.html'


class IssuesCreateView(CreateView):
    """
        to Create Issues
    """
    form_class = IssuesForm
    template_name = "dj_diabetes/issues_form.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(IssuesCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        appointments = form.save(commit=False)
        if form.is_valid():
            appointments.user = self.request.user
            appointments.save()

        return HttpResponseRedirect(reverse('issues'))

    def get_context_data(self, **kw):
        data = Issues.objects.all().order_by('-created')
        #paginator vars
        record_per_page = 15
        page = self.request.GET.get('page')
        # paginator call
        data = page_it(data, record_per_page, page)

        context = super(IssuesCreateView, self).get_context_data(**kw)
        context['action'] = 'add_issue'
        context['data'] = data
        return context


class IssuesUpdateView(UpdateView):
    """
        to Edit Issues
    """
    model = Issues
    form_class = IssuesForm
    fields = ['question', 'question_to', 'answer', 'date_answer']
    template_name = "dj_diabetes/issues_form.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(IssuesUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        if form.is_valid():
            form.save()

        return HttpResponseRedirect(reverse('issues'))

    def get_context_data(self, **kw):
        data = Issues.objects.all().order_by('-created')
        #paginator vars
        record_per_page = 15
        page = self.request.GET.get('page')
        # paginator call
        data = page_it(data, record_per_page, page)

        context = super(IssuesUpdateView, self).get_context_data(**kw)
        context['data'] = data
        return context


class IssuesDeleteView(DeleteView):
    """
        to Delete Issues
    """
    model = Issues
    success_url = reverse_lazy('issues')
    template_name = 'dj_diabetes/confirm_delete.html'


class WeightsCreateView(CreateView):
    """
        to Create Weights
    """
    form_class = WeightsForm
    template_name = "dj_diabetes/weights_form.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(WeightsCreateView, self).dispatch(*args, **kwargs)

    def get_initial(self):
        return {'date_weight': arrow.utcnow().to(settings.TIME_ZONE).format('YYYY-MM-DD')}

    def form_valid(self, form):
        weights = form.save(commit=False)
        if form.is_valid():
            weights.user = self.request.user
            weights.save()

        return HttpResponseRedirect(reverse('weights'))

    def get_context_data(self, **kw):
        data = Weights.objects.all()
        #paginator vars
        record_per_page = 15
        page = self.request.GET.get('page')
        # paginator call
        data = page_it(data, record_per_page, page)

        context = super(WeightsCreateView, self).get_context_data(**kw)
        context['action'] = 'add_weight'
        context['data'] = data
        return context


class WeightsUpdateView(UpdateView):
    """
        to Edit Weights
    """
    model = Weights
    form_class = WeightsForm
    fields = ['weight', 'date_weight']
    template_name = "dj_diabetes/weights_form.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(WeightsUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        if form.is_valid():
            form.save()

        return HttpResponseRedirect(reverse('weights'))

    def get_context_data(self, **kw):
        data = Weights.objects.all()
        #paginator vars
        record_per_page = 15
        page = self.request.GET.get('page')
        # paginator call
        data = page_it(data, record_per_page, page)

        context = super(WeightsUpdateView, self).get_context_data(**kw)
        context['data'] = data
        return context


class WeightsDeleteView(DeleteView):
    """
        to Delete Weights
    """
    model = Weights
    success_url = reverse_lazy('weights')
    template_name = 'dj_diabetes/confirm_delete.html'


class MealsCreateView(CreateView):
    """
        to Create Meals
    """
    form_class = MealsForm
    template_name = "dj_diabetes/meals_form.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MealsCreateView, self).dispatch(*args, **kwargs)

    def get_initial(self):
        """
            set the default date and hour of the date_xxx and hour_xxx
            property of the current model
        """
        return right_now("meal")

    def form_valid(self, form):
        meals = form.save(commit=False)
        print "meals ? ", meals.breakfast_lunch_diner
        print type(meals.breakfast_lunch_diner)
        if form.is_valid():
            meals.user = self.request.user
            meals.save()

        return HttpResponseRedirect(reverse('meals'))

    def get_context_data(self, **kw):
        data = Meals.objects.all()
        #paginator vars
        record_per_page = 15
        page = self.request.GET.get('page')
        # paginator call
        data = page_it(data, record_per_page, page)

        context = super(MealsCreateView, self).get_context_data(**kw)
        context['action'] = 'add_meal'
        context['data'] = data
        return context


class MealsUpdateView(UpdateView):
    """
        to Edit Meals
    """
    model = Meals
    form_class = MealsForm
    fields = ['food', 'breakfast_lunch_diner', 'meal_date']
    template_name = "dj_diabetes/meals_form.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MealsUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        if form.is_valid():
            form.save()

        return HttpResponseRedirect(reverse('meals'))

    def get_context_data(self, **kw):
        data = Meals.objects.all()
        #paginator vars
        record_per_page = 15
        page = self.request.GET.get('page')
        # paginator call
        data = page_it(data, record_per_page, page)

        context = super(MealsUpdateView, self).get_context_data(**kw)
        context['data'] = data
        return context


class MealsDeleteView(DeleteView):
    """
        to Delete Meals
    """
    model = Meals
    success_url = reverse_lazy('meals')
    template_name = 'dj_diabetes/confirm_delete.html'


class ExercisesCreateView(CreateView):
    """
        to Create Exercises
    """
    form_class = ExercisesForm
    template_name = "dj_diabetes/exercises_form.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ExercisesCreateView, self).dispatch(*args, **kwargs)

    def get_initial(self):
        """
            set the default date and hour of the date_xxx and hour_xxx
            property of the current model
        """
        return right_now("exercise")

    def form_valid(self, form):
        exercise = form.save(commit=False)
        if form.is_valid():
            exercise.user = self.request.user
            exercise.save()

        return HttpResponseRedirect(reverse('exercises'))

    def get_context_data(self, **kw):
        data = Exercises.objects.all()
        #paginator vars
        record_per_page = 15
        page = self.request.GET.get('page')
        # paginator call
        data = page_it(data, record_per_page, page)

        context = super(ExercisesCreateView, self).get_context_data(**kw)
        context['action'] = 'add_exercise'
        context['data'] = data
        return context


class ExercisesUpdateView(UpdateView):
    """
        to Edit Exercises
    """
    model = Exercises
    form_class = ExercisesForm
    fields = fields = ['sports', 'comment', 'duration', 'date_exercise']
    template_name = "dj_diabetes/exercises_form.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ExercisesUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        if form.is_valid():
            form.save()

        return HttpResponseRedirect(reverse('exercises'))

    def get_context_data(self, **kw):
        data = Exercises.objects.all()
        #paginator vars
        record_per_page = 15
        page = self.request.GET.get('page')
        # paginator call
        data = page_it(data, record_per_page, page)

        context = super(ExercisesUpdateView, self).get_context_data(**kw)
        context['data'] = data
        return context


class ExercisesDeleteView(DeleteView):
    """
        to Delete Exercises
    """
    model = Exercises
    success_url = reverse_lazy('exercises')
    template_name = 'dj_diabetes/confirm_delete.html'


class ExamsCreateView(CreateView):
    """
        to Create Exams
    """
    form_class = ExamsForm
    template_name = "dj_diabetes/exams_form.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ExamsCreateView, self).dispatch(*args, **kwargs)

    def get_initial(self):
        """
            set the default date and hour of the date_xxx and hour_xxx
            property of the current model
        """
        return right_now("examination")

    def form_valid(self, form):
        exercise = form.save(commit=False)
        if form.is_valid():
            exercise.user = self.request.user
            exercise.save()

        return HttpResponseRedirect(reverse('exams'))

    def get_context_data(self, **kw):
        data = Examinations.objects.all().order_by('-created')
        #paginator vars
        record_per_page = 15
        page = self.request.GET.get('page')
        # paginator call
        data = page_it(data, record_per_page, page)

        context = super(ExamsCreateView, self).get_context_data(**kw)
        context['action'] = 'add_exam'
        context['data'] = data

        if self.request.POST:
            context['examsdetails_form'] = ExamDetailsFormSet(self.request.POST)
        else:
            context['examsdetails_form'] = ExamDetailsFormSet(instance=self.object)
        return context


class ExamsUpdateView(UpdateView):
    """
        to Edit Exams
    """
    model = Examinations
    form_class = ExamsForm
    fields = ['examination_types', 'comments', 'date_examination']
    template_name = "dj_diabetes/exams_form.html"

#    @method_decorator(login_required)
#    def dispatch(self, *args, **kwargs):
#        return super(ExamsUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        if self.request.POST:
            formset = ExamDetailsFormSet(self.request.POST, instance=self.object)
            if formset.is_valid():
                self.object = form.save()
                formset.instance = self.object
                formset.save()

        else:
            formset = ExamDetailsFormSet(instance=self.object)
        return HttpResponseRedirect(reverse('exams'))

    def get_context_data(self, **kw):
        data = Examinations.objects.all().order_by('-created')
        #paginator vars
        record_per_page = 15
        page = self.request.GET.get('page')
        # paginator call
        data = page_it(data, record_per_page, page)

        context = super(ExamsUpdateView, self).get_context_data(**kw)
        context['data'] = data

        if self.request.POST:
            context['examsdetails_form'] = ExamDetailsFormSet(self.request.POST)
        else:
            context['examsdetails_form'] = ExamDetailsFormSet(instance=self.object)
        return context


class ExamsDeleteView(DeleteView):
    """
        to Delete Examination Details
    """
    model = Examinations
    success_url = reverse_lazy('exams')
    template_name = 'dj_diabetes/confirm_delete.html'
