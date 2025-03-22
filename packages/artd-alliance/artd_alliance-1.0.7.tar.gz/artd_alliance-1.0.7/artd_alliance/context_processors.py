# myapp/context_processors.py
import threading

# Crea un objeto de almacenamiento de hilo
_thread_local = threading.local()


def get_current_user():
    return getattr(_thread_local, "user", None)


def set_current_user(user):
    _thread_local.user = user


def user_context_processor(request):
    # Almacena el usuario en el almacenamiento de hilo
    set_current_user(request.user)
    return {}
