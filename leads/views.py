from django.db.models.query_utils import select_related_descend
from django.forms import Form
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, request
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from .models import Lead, Category
from agents.mixins import OrganizerLoginRequired
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import LeadForm, LeadModelForm, AssignAgentForm, LeadUpdateCategoryForm, CategoryModelForm
from django.core.mail import send_mail
from .forms import CustomUserCreationForm


class LandingViewPage(TemplateView):
    template_name = "landing_page.html"


def landing_page(request):
    return render(request, "landing_page.html")


class SignupView(CreateView):
    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return reverse("login")


# login required mixins restrict access for unauthorized user
class LeadListView(LoginRequiredMixin, ListView):
    template_name = "leads/lead_list.html"
    context_object_name = "leads"

    def get_queryset(self):
        # fetching logged in user
        user = self.request.user

        # initial queryset for the entire organisation
        if user.is_organizer:
            # check the userprofile for the logged in user that is organiser
            queryset = Lead.objects.filter(organization=user.userprofile, agent__isnull=False)
        else:
            # check the organisation for the logged in user that is an agent
            queryset = Lead.objects.filter(organization=user.agent.organization, agent__isnull=False)
            # filter leads for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
        return queryset

    # extra context by overriding get_context_data method
    def get_context_data(self, **kwargs):
        # grab the already existing context if there is any
        context = super(LeadListView, self).get_context_data(**kwargs)
        # fetching all users from that organization
        user = self.request.user
        if user.is_organizer:
            # filtering leads which have no agent
            queryset = Lead.objects.filter(organization=user.userprofile,
                                           agent__isnull=True)
            context.update({
                "unassigned_leads": queryset
            })
        return context
            

def lead_list(request):
    leads = Lead.objects.all()
    context = {
        "leads": leads
    }
    return render(request, "leads/lead_list.html", context)


class LeadDetailView(LoginRequiredMixin, DetailView):
    template_name = "leads/lead_detail.html"
    context_object_name = "lead"  # context object will be 'object_list' default if we are not specifying it

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Lead.objects.filter(organization=user.userprofile)
        else:
            queryset = Lead.objects.filter(organization=user.agent.organization)
            queryset = Lead.objects.filter(agent__user=user)
        return queryset
       

def lead_detail(request, pk):
    lead = Lead.objects.get(id=pk)
    context = {
        "lead": lead
    }
    return render(request, "leads/lead_detail.html", context)


# OrganizerLoginRequireMixin is custom class by using LoginRequireMixin class,
# it only provide access when the user will be organizer
class LeadCreateView(OrganizerLoginRequired, CreateView):
    template_name = "leads/lead_create.html"
    form_class = LeadModelForm
    # send_mail(
    # subject="New Lead Create",
    # message="Go to site to view",
    # from_email="samik3306@gmail.com",
    # recipient_list=["affan4211@gmail.com"]
    # )

    def form_valid(self, form):
        # assign the organization for newly created lead
        lead = form.save(commit=False)
        lead.organizations = self.request.user.userprofile
        lead.save()
        return super(LeadCreateView, self).form_valid(form)

    def get_success_url(self):  # return when form is submitted successfully
        return reverse("leads:lead-list")   


def lead_create(request):
    form = LeadModelForm()
    if request.method == "POST":
        form = LeadModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/leads")
    context = {
        "form": form
    }
    return render(request, "leads/lead_create.html", context)


# OrganizerLoginRequireMixin is custom class by using LoginRequireMixin class,
# it only provide access when the user will be organizer
class LeadUpdateView(OrganizerLoginRequired, UpdateView):
    template_name = "leads/lead_update.html"
    form_class = LeadModelForm

    def get_queryset(self):
        user = self.request.user
        # grab the model instance for current logged in user
        return Lead.objects.filter(organization=user.userprofile)

    def get_success_url(self):
        # reverse to desired user instance by using its id in kwargs
        return reverse("leads:lead-detail", kwargs={'pk': self.get_object().id})


def lead_update(request, pk):
    #  grab the id of a lead model object
    lead = Lead.objects.get(id=pk)
    # grab the single instance by using its id and store it on the form variable
    form = LeadModelForm(instance=lead)
    if request.method == "POST":
        form = LeadModelForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            return redirect("/leads")
    context = {
        "lead": lead,
        "form": form
    }
    return render(request, "leads/lead_update.html", context)


# OrganizerLoginRequireMixin is custom class by using LoginRequireMixin class,
# it only provide access when the user will be organizer
class LeadDeleteView(OrganizerLoginRequired, DeleteView):
    template_name = "leads/lead_delete.html"

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organization
        return Lead.objects.filter(organization=user.userprofile)

    def get_success_url(self):  # reverse lead list after deleting form run efficiently
        return reverse("leads:lead-list")


def lead_delete(request, pk):
    lead = Lead.objects.get(id=pk)
    lead.delete()
    return redirect("/leads")


# OrganizerLoginRequireMixin is custom class by using LoginRequireMixin class,
# it only provide access when the user will be organizer
class AssignAgentView(OrganizerLoginRequired, FormView):
    template_name = "leads/assign_agent.html"
    form_class = AssignAgentForm

    # passing extra arguments into the forms by using this method
    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            "request": self.request
        })
        return kwargs
        
    def get_success_url(self):
        return reverse("leads:lead-list")

    def form_valid(self, form):
        # grab the selected agent from the form field
        agent = form.cleaned_data["agent"]
        # grab the selected lead's primary key
        lead = Lead.objects.get(id=self.kwargs["pk"])
        # assign the agent for the lead
        lead.agent = agent
        lead.save()
        return super(AssignAgentView, self).form_valid(form)


class CategoryListView(LoginRequiredMixin, ListView):
    template_name = "leads/category_list.html"
    context_object_name = "category_list"

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user
        # queryset for the entire organization
        if user.is_organizer:
            queryset = Lead.objects.filter(organization=user.userprofile)
        else:
            queryset = Lead.objects.filter(organization=user.agent.organization)
        context.update({
            # count the leads that is not assign any category
            "unassigned_lead_count": queryset.filter(category__isnull=True).count()
        })
        return context
    
    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Category.objects.filter(organizations=user.userprofile)
        else:
            queryset = Category.objects.filter(organizations=user.agent.organization)
        return queryset


class CategoryDetailView(LoginRequiredMixin, DetailView):
    template_name = "leads/category_detail.html"
    context_object_name = "category"

    def get_queryset(self):
        user = self.request.user
        # grab the category instance
        if user.is_organizer:
            queryset = Category.objects.filter(organizations=user.userprofile)
        else:
            queryset = Category.objects.filter(organizations=user.agent.organization)
        return queryset


class LeadCategoryUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "leads/lead_update_category.html"
    form_class = LeadUpdateCategoryForm

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            # initial queryset for the entire organization
            queryset = Lead.objects.filter(organization=user.userprofile)
        else:
            queryset = Lead.objects.filter(organization=user.agent.organization)
            # filter queryset the user that is logged in
            queryset = Lead.objects.filter(agent__user=user)
        return queryset

    def get_success_url(self):
        return reverse("leads:lead-detail", kwargs={"pk": self.get_object().id})


# OrganizerLoginRequireMixin is custom class by using LoginRequireMixin class,
# it only provide access when the user will be organizer
class CategoryCreateView(OrganizerLoginRequired, CreateView):
    template_name = "leads/create_category.html"
    form_class = CategoryModelForm

    def get_success_url(self):
        return reverse("leads:category-list")   

    def form_valid(self, form):
        category = form.save(commit=False)
        category.organizations = self.request.user.userprofile
        category.save()
        return super(CategoryCreateView, self).form_valid(form)


# OrganizerLoginRequireMixin is custom class by using LoginRequireMixin class,
# it only provide access when the user will be organizer
class CategoryUpdateView(OrganizerLoginRequired, UpdateView):
    template_name = "leads/category_update.html"
    form_class = CategoryModelForm

    def get_queryset(self):
        user = self.request.user
        return Category.objects.filter(organizations=user.userprofile)

    def get_success_url(self):
        return reverse("leads:category-list")


class CategoryDeleteView(OrganizerLoginRequired, DeleteView):
    template_name = "leads/category_delete.html"

    def get_queryset(self):
        organizations = self.request.user.userprofile
        return Category.objects.filter(organizations=organizations)
    
    def get_success_url(self):
        return reverse("leads:category-list")


def lead_update(request, pk):
    lead = Lead.objects.get(id=pk)
    form = LeadForm()
    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            age = form.cleaned_data['age']
            lead.first_name = first_name
            lead.last_name = last_name
            lead.age = age
            lead.save()
            return redirect("/leads")
    context = {
        "lead": lead,
        "form": form
    }
    return render(request, "leads/lead_update.html", context)