from rest_framework import viewsets

from .models import WrappedSubject
from .serializer import WrappedSubjectSerializer
from huscy.subjects.permissions import SubjectPermission


class WrappedSubjectViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options', 'trace']
    lookup_field = 'pseudonym'
    queryset = WrappedSubject.objects.all()
    serializer_class = WrappedSubjectSerializer
    permission_classes = SubjectPermission,

    def dispatch(self, request, *args, **kwargs):
        if 'pseudonym' in kwargs and 'format' in kwargs:
            kwargs = {'pseudonym': f"{kwargs['pseudonym']}.{kwargs['format']}"}
        return super().dispatch(request, *args, **kwargs)
