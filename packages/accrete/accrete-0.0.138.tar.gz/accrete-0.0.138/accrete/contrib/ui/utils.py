import ast
import json
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from .context import ModalContext


def modal_response(
    request: HttpRequest,
    template: str,
    context: ModalContext | dict,
    update: bool = False
) -> HttpResponse:

    if isinstance(context, ModalContext):
        context = context.dict()
    res = render(request, template, context)
    if update:
        res.headers['HX-Retarget'] = f'#{context["modal_id"]}'
        res.headers['HX-Reswap'] = 'outerHTML'
        return res
    res.headers['HX-Retarget'] = 'body'
    res.headers['HX-Reswap'] = 'beforeend'
    return res


def add_trigger(
    response: [HttpResponse],
    trigger: dict | str,
    header: str = 'HX-Trigger'
) -> HttpResponse:
    if isinstance(trigger, str):
        trigger = {trigger: ''}
    res_trigger = response.headers.get(header)
    if not res_trigger:
        response.headers[header] = json.dumps(trigger)
        return response
    try:
        res_trigger = ast.literal_eval(response.headers.get(header, '{}'))
    except SyntaxError:
        res_trigger = {response.headers[header]: ''}
    res_trigger.update(trigger)
    response.headers[header] = json.dumps(header)
    return response
