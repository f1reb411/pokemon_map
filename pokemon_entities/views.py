import folium
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound
from django.shortcuts import render

from .models import Pokemon, PokemonEntity

MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        # Warning! `tooltip` attribute is disabled intentionally
        # to fix strange folium cyrillic encoding bug
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    pokemon_entities = PokemonEntity.objects.all()
    pokemons = Pokemon.objects.all()

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in pokemon_entities:
        try:
            image_url = request.build_absolute_uri(pokemon_entity.pokemon.image.url)
        except:
            image_url = DEFAULT_IMAGE_URL
        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.lon,
            image_url
        )

    pokemons_on_page = []
    for pokemon in pokemons:
        try:
            image_url = request.build_absolute_uri(pokemon.image.url)
        except:
            image_url = DEFAULT_IMAGE_URL
        pokemons_on_page.append({
            'pokemon_id': pokemon.id,
            'img_url': image_url,
            'title_ru': pokemon.title_ru,
        })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    try:
        requested_pokemon = Pokemon.objects.get(id=pokemon_id)
    except Pokemon.ObjectDoesNotExist:
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')
    
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)

    requested_pokemon_entities = requested_pokemon.entities.all()
    image_url = request.build_absolute_uri(requested_pokemon.image.url)

    previous_evolution = None
    next_evolution = None

    if requested_pokemon.previous_evolution:
        try:
            previous_evolution_image_url = request.build_absolute_uri(requested_pokemon.previous_evolution.image.url)
        except AttributeError:
            previous_evolution_image_url = None
        previous_evolution = {
            'pokemon_id': int(pokemon_id) - 1,
            'title_ru': requested_pokemon.previous_evolution.title_ru,
            'img_url': previous_evolution_image_url
        }

    next_pokemon = requested_pokemon.next_evolution.first()

    if next_pokemon:
        try:
            title = Pokemon.objects.get(title_ru=next_pokemon)
            next_evolution_image_url = request.build_absolute_uri(title.image.url)
        except AttributeError:
            next_evolution_image_url = None
        next_evolution = {
            'pokemon_id': int(pokemon_id) + 1,
            'title_ru': title,
            'img_url': next_evolution_image_url
        }

    pokemons = {
        'pokemon_id': pokemon_id,
        'title_ru': requested_pokemon.title_ru,
        'title_en': requested_pokemon.title_en,
        'title_jp': requested_pokemon.title_jp,
        'img_url': image_url,
        'description': requested_pokemon.description,
        'previous_evolution': previous_evolution,
        'next_evolution': next_evolution
    }

    for pokemon_entity in requested_pokemon_entities:
        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.lon,
            image_url
        )
    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(), 'pokemon': pokemons
    })
