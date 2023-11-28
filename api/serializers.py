from rest_framework import serializers

from api.models import UploadedFile


class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = [
            "id",
            "filename",
            "rowscount",
            "colscount",
            "uploadtime",
        ]
