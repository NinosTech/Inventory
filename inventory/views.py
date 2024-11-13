from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, View, CreateView, UpdateView, DeleteView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import UserRegisterForm, InventoryItemForm, ProjectForm
from .models import InventoryItem, Category, Project, MaterialHistory, Location

class Index(TemplateView):
    template_name = 'inventory/index.html'

class Dashboard(LoginRequiredMixin, View):
    def get(self, request):
        main_project = Project.objects.filter(name="Main Project").first()
        projects = Project.objects.exclude(id=main_project.id).order_by('name') if main_project else Project.objects.all().order_by('name')
        search_query = request.GET.get('search', '')

        items = InventoryItem.objects.filter(project=main_project)
        if search_query:
            items = items.filter(name__icontains=search_query)

        items = items.order_by('category__name', 'name')

        grouped_inventory = {}
        items_per_page = 9
        for item in items:
            category = item.category.name if item.category else 'Uncategorized'  # Handle missing categories
            if category not in grouped_inventory:
                grouped_inventory[category] = []
            grouped_inventory[category].append(item)

        category_pages = {}
        active_category = request.GET.get('active_category', list(grouped_inventory.keys())[0])  # Default to first category
        for category, item_list in grouped_inventory.items():
            paginator = Paginator(item_list, items_per_page)
            page_number = request.GET.get(f'page_{category}', 1)
            category_pages[category] = paginator.get_page(page_number)

        return render(request, 'inventory/dashboard.html', {
            'main_project': main_project,
            'projects': projects,
            'grouped_inventory': category_pages,
            'active_category': active_category,
        })

class SearchResultsView(LoginRequiredMixin, View):
    template_name = 'inventory/search_results.html'

    def get(self, request):
        search_query = request.GET.get('search', '')
        items = InventoryItem.objects.filter(name__icontains=search_query).order_by('project__name', 'category__name', 'name') if search_query else []
        grouped_inventory = {}

        for item in items:
            project = item.project.name
            category = item.category.name
            if project not in grouped_inventory:
                grouped_inventory[project] = {}
            if category not in grouped_inventory[project]:
                grouped_inventory[project][category] = []
            grouped_inventory[project][category].append(item)

        return render(request, self.template_name, {
            'grouped_inventory': grouped_inventory,
            'search_query': search_query,
        })

class UpdateQuantityView(LoginRequiredMixin, View):
    template_name = 'inventory/update_quantity.html'

    def get(self, request, project_id, pk=None):
        project = get_object_or_404(Project, id=project_id)
        item = get_object_or_404(InventoryItem, id=pk, project=project) if pk else None
        history = item.history.order_by('date') if item else None
        return render(request, self.template_name, {'item': item, 'history': history, 'project': project})

    def post(self, request, project_id, pk=None):
        project = get_object_or_404(Project, id=project_id)
        item = get_object_or_404(InventoryItem, id=pk, project=project) if pk else None

        try:
            quantity_change = int(request.POST.get('quantity_change', 0))
            operation = request.POST.get('operation', 'add')
            if operation == 'add':
                item.quantity += quantity_change
                messages.success(request, f'Added {quantity_change} units to {item.name}.')
            elif operation == 'remove':
                if item.quantity >= quantity_change:
                    item.quantity -= quantity_change
                    messages.success(request, f'Removed {quantity_change} units from {item.name}.')
                else:
                    messages.error(request, f'Cannot remove {quantity_change} units. Only {item.quantity} available.')
            item.save()
            MaterialHistory.objects.create(
                item=item,
                quantity_change=quantity_change,
                operation=operation,
                user=request.user
            )
        except (InventoryItem.DoesNotExist, ValueError):
            messages.error(request, 'Invalid item selected or invalid quantity.')
        return redirect(reverse('project_inventory', args=[project.id]))

class SignUpView(View):
    def get(self, request):
        form = UserRegisterForm()
        return render(request, 'inventory/signup.html', {'form': form})

    def post(self, request):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )
            login(request, user)
            return redirect('index')
        return render(request, 'inventory/signup.html', {'form': form})

class AddItem(LoginRequiredMixin, CreateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        main_project, created = Project.objects.get_or_create(
            name="Main Project",
            defaults={'description': 'This is the main project.', 'user': self.request.user}
        )
        form.instance.project = main_project
        return super().form_valid(form)

class EditItem(LoginRequiredMixin, UpdateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.object.project
        return kwargs

    def get_success_url(self):
        project_id = self.object.project.id
        if self.object.project.name == "Main Project":
            return reverse('dashboard')
        return reverse('project_inventory', args=[project_id])

class DeleteItem(LoginRequiredMixin, DeleteView):
    model = InventoryItem
    template_name = 'inventory/confirm_delete.html'

    def get_success_url(self):
        project = self.object.project
        if project.name == "Main Project":
            return reverse_lazy('dashboard')
        return reverse_lazy('project_inventory', args=[project.id])

class AddItemToProject(LoginRequiredMixin, CreateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, id=self.kwargs['project_id'])
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = get_object_or_404(Project, id=self.kwargs['project_id'])
        return kwargs

    def form_valid(self, form):
        form.instance.project = get_object_or_404(Project, id=self.kwargs['project_id'])
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        project = get_object_or_404(Project, id=self.kwargs['project_id'])
        if project.name == "Main Project":
            return reverse('dashboard')
        return reverse('project_inventory', args=[project.id])

class DeleteProject(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'inventory/confirm_delete.html'
    success_url = reverse_lazy('dashboard')

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'inventory/project_create.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Project created successfully.')
        return super().form_valid(form)

class ProjectInventoryView(LoginRequiredMixin, View):
    template_name = 'inventory/project_inventory.html'

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        search_query = request.GET.get('search', '')

        items = InventoryItem.objects.filter(project=project)
        if search_query:
            items = items.filter(name__icontains=search_query)
        items = items.order_by('category__name', 'name')

        paginated_inventory = {}
        items_per_page = 9

        for item in items:
            category = item.category.name if item.category else 'Uncategorized'
            if category not in paginated_inventory:
                paginated_inventory[category] = []
            paginated_inventory[category].append(item)

        category_pages = {}
        active_category = request.GET.get('active_category', list(paginated_inventory.keys())[0])  # Default to first category
        for category, item_list in paginated_inventory.items():
            paginator = Paginator(item_list, items_per_page)
            page_number = request.GET.get(f'page_{category}', 1)
            category_pages[category] = paginator.get_page(page_number)

        return render(request, self.template_name, {
            'project': project,
            'grouped_inventory': category_pages,
            'active_category': active_category,
        })