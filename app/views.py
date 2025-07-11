from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Game

@login_required
def home(request):
    return render(request,'home.html')

@login_required
def about(request):
    return render(request,'about.html')

@login_required
def contact(request):
    return render(request,'contact.html')



def livepool_list(request, country):
    country = country.capitalize()
    return render(request, 'app/livepool_list.html', {'country': country})

@login_required
def GameView(request, room_id):
    user = request.user

    # Now use `room_code` instead of `id`
    game, created = Game.objects.get_or_create(room_code=room_id)

    if game.op1 is None:
        game.op1 = user
        game.save()
    elif game.op2 is None and game.op1 != user:
        game.op2 = user
        game.save()
    elif user != game.op1 and user != game.op2:
        return render(request, "app/game_full.html")

    context = {
        'room_code': room_id,
        'username': user.username,
        'op1': game.op1.username if game.op1 else "Waiting...",
        'op2': game.op2.username if game.op2 else "Waiting...",
    }

    return render(request, "app/game_room.html", context)
  

# @login_required
# def pool_view(request, pool_name):
#     return render(request, "app/poollist.html", {"pool_name": pool_name})

# @login_required
# def tictactoe_view(request, room_id):
#     return render(request, "app/tictactoegame.html", {"room_id": room_id})
