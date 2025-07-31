from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    # Appelle le gestionnaire d'exception DRF par défaut
    response = exception_handler(exc, context)

    if response is not None:
        # Tu peux personnaliser ici
        response.data['status_code'] = response.status_code
        response.data['detail'] = response.data.get('detail', 'Une erreur est survenue.')

    else:
        # Si DRF n’a pas géré, renvoyer une réponse standardisée
        return Response({
            'detail': 'Erreur interne du serveur',
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
