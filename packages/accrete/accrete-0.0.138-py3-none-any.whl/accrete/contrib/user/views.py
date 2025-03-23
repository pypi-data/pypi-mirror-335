from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import views, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render, resolve_url
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from accrete.utils import save_form
from accrete.contrib import ui
from .forms import UserForm, ChangePasswordForm, ChangeEmailForm


class LoginView(views.LoginView):

    form_class = AuthenticationForm
    template_name = 'user/login.html'
    redirect_authenticated_user = True

    def form_invalid(self, form):
        user = form.get_user()
        if user is not None and not user.is_active:
            ctx = {'to_confirm': True}
            if self.extra_context:
                self.extra_context.update(ctx)
            else:
                self.extra_context = ctx
        return super().form_invalid(form)


class LogoutView(views.LogoutView):

    def get_success_url(self):
        return resolve_url(settings.LOGIN_URL)


@login_required()
def user_detail(request):
    form = UserForm(
        initial={'language_code': request.user.language_code},
        instance=request.user
    )
    ctx = ui.Context(
        title=_('User Preferences'),
        extra=dict(
            user=request.user,
            form=form
        )
    ).dict()
    if request.method == 'POST':
        form = save_form(UserForm(request.POST, instance=request.user))
        ctx.update(form=form)
        if form.is_saved:
            res = render(request, 'user/user_form.html', ctx)
            res.headers['HX-Refresh'] = 'true'
            return res
    return render(request, 'user/user_form.html', ctx)


@login_required()
def user_change_password(request):
    if request.user.is_managed:
        return HttpResponseForbidden()
    form = ChangePasswordForm(instance=request.user)
    ctx = ui.ModalContext(
        title=_('Change Password'),
        modal_id='change-password',
        blocking=True,
        extra=dict(
            form=form,
            user=request.user
        )
    ).dict()
    if request.method == 'POST':
        form = save_form(ChangePasswordForm(request.POST, instance=request.user))
        if form.is_saved:
            update_session_auth_hash(request, form.instance)
            return redirect(
                resolve_url('user:detail')
                + f'?{request.GET.urlencode()}'
            )
        ctx.update(form=form)
        return ui.modal_response(request, 'user/change_password.html', ctx)
    return render(request, 'user/change_password.html', ctx)


@login_required()
def user_change_email(request):
    if request.user.is_managed:
        return HttpResponseForbidden()
    form = ChangeEmailForm(instance=request.user)
    ctx = ui.ModalContext(
        title=_('Change E-Mail'),
        modal_id='change-email',
        blocking=True,
        extra=dict(
            form=form,
            user=request.user
        )
    ).dict()
    if request.method == 'POST':
        form = save_form(ChangeEmailForm(request.POST, instance=request.user))
        if form.is_saved:
            return redirect('user:detail')
        ctx.update(form=form)
        return ui.modal_response(request, 'user/change_email.html', ctx)
    return render(request, 'user/change_email.html', ctx)
