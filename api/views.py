from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.models import UploadedFile
from api.serializers import UploadedFileSerializer

import pandas as pd
from io import BytesIO

import json

# Create your views here.


@api_view(["GET", "POST"])
def get_or_upload_datasets(request):
    if request.method == "GET":
        uploaded_files = UploadedFile.objects.all()
        serializer = UploadedFileSerializer(uploaded_files, many=True)
        return Response(serializer.data)
    else:
        filename = request.POST.get("filename")
        uploaded_file = request.FILES.get("datasetfile").read()

        if not filename or not uploaded_file:
            return Response(
                {"message": "Both Files and Filename are required!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        file_like_object = BytesIO(uploaded_file)
        df = pd.read_csv(file_like_object)
        num_rows, num_cols = df.shape
        new_file = UploadedFile.objects.create(
            filename=filename,
            uploadfile=uploaded_file,
            rowscount=num_rows,
            colscount=num_cols,
        )
        new_file.save()
        return Response({"message": "Success"}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def compute(request, id):
    json_data = json.loads(request.body)
    query_object = UploadedFile.objects.filter(id=id).first()
    if not query_object:
        return Response(
            {"message": "No dataset found for the provided id"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    dataset = BytesIO(query_object.uploadfile)
    df = pd.read_csv(dataset)
    column = json_data.get("column")
    aggregator = json_data.get("aggregator")
    response = None
    if aggregator == "min":
        response = df[column].min()
    elif aggregator == "max":
        response = df[column].max()
    elif aggregator == "sum":
        response = df[column].sum()
    else:
        return Response(
            {"message": "Only min, max and sum can be passed as aggregator"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response({"result": response}, status=status.HTTP_200_OK)


@api_view(["GET"])
def plot(request, id):
    json_data = json.loads(request.body)
    query_object = UploadedFile.objects.filter(id=id).first()
    if not query_object:
        return Response(
            {"message": "No dataset found for the provided id"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    column1 = json_data.get("column1")
    column2 = json_data.get("column2")
    dataset = BytesIO(query_object.uploadfile)
    df = pd.read_csv(dataset)

    x = df[column1][:30]
    y = df[column2][:30]

    return Response({"x": x, "y": y}, status=status.HTTP_200_OK)
