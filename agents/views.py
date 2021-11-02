from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse
from django.views import generic
import random
from leads.models import Agent
from .forms import AgentModelForm
from .mixins import OrganizerLoginRequired


class AgentListView(OrganizerLoginRequired, generic.ListView):
    template_name = "agents/agent_list.html"
    
    def get_queryset(self):
        organization = self.request.user.userprofile
        return Agent.objects.filter(organization=organization)


class AgentCreateView(OrganizerLoginRequired, generic.CreateView):
    template_name = "agents/agent_create.html"
    form_class = AgentModelForm

    def get_success_url(self):
        return reverse("agents:agent-list")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_agent = True
        user.is_organizer = False
        user.set_password(f"{random.randint(0, 1000000000)}")
        user.save()
        Agent.objects.create(
            user=user,
            organization=self.request.user.userprofile
        )
        return super(AgentCreateView, self).form_valid(form)


class AgentDetailView(OrganizerLoginRequired, generic.DetailView):
    template_name = "agents/agent_detail.html"
    context_object_name = "agent"
    def get_queryset(self):
        organization = self.request.user.userprofile
        return Agent.objects.filter(organization=organization)
    


class AgentUpdateView(OrganizerLoginRequired, generic.UpdateView):
    template_name = "agents/agent_update.html"
    queryset = Agent.objects.all()
    form_class = AgentModelForm
    def get_success_url(self):
        return reverse("agents:agent-list")


class AgentDeleteView(OrganizerLoginRequired, generic.DeleteView):
    template_name = "agents/agent_delete.html"
    def get_queryset(self):
        organization = self.request.user.userprofile
        return Agent.objects.filter(organization=organization)
    
    def get_success_url(self):
        return reverse("agents:agent-list")