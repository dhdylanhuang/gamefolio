from django import template

from gamefolio_app.models import ListEntry

register = template.Library()

@register.simple_tag
def get_image(game, image_type):
    return game.get_image(image_type)

@register.inclusion_tag("gamefolio_app/list_image.html")
def render_list_images(list):
    entries = ListEntry.objects.filter(list = list)[:4];
    if(len(entries) < 4 and len(entries) > 0):
        entries =[entries[0]];
    return {"entries": entries, "list": list}

@register.inclusion_tag("gamefolio_app/game_card.html")
def render_game_card(game, *args, **kwargs):
    try:
        verbose = kwargs["verbose"]
    except:
        verbose = True
    return {"game": game, "verbose":verbose}