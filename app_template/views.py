"""
Template views file.
Copy this folder and rename it to create a new module.
"""

from django.http import JsonResponse


def example_endpoint(request):
    return JsonResponse({"message": "template works"})
