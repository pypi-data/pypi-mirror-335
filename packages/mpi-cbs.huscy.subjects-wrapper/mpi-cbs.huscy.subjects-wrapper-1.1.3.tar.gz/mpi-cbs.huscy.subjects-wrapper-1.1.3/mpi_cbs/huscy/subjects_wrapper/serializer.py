from rest_framework import serializers

from .models import WrappedSubject
from huscy.subjects.serializers import SubjectSerializer


class WrappedSubjectSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()

    class Meta:
        model = WrappedSubject
        fields = (
            'pseudonym',
            'subject',
        )

    def create(self, validated_data):
        subject_serializer = SubjectSerializer(data=validated_data.pop('subject'))
        subject_serializer.is_valid(raise_exception=True)
        subject = subject_serializer.save()

        return WrappedSubject.objects.create(subject=subject, **validated_data)

    def update(self, wrapped_subject, validated_data):
        subject_serializer = SubjectSerializer(wrapped_subject.subject,
                                               data=validated_data.pop('subject'))
        subject_serializer.is_valid(raise_exception=True)
        subject_serializer.save()

        return wrapped_subject
