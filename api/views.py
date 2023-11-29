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
        serializer = UploadedFileSerializer(new_file)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def compute(request, id):
    json_data = json.loads(request.body)
    query_object = UploadedFile.objects.filter(id=id).first()
    if not query_object:
        return Response(
            {"message": "No dataset found for the provided id"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        dataset = BytesIO(query_object.uploadfile)
        df = pd.read_csv(dataset)
        column = json_data.get("column")
        aggregator = json_data.get("aggregator")
        response = None

        if not pd.api.types.is_numeric_dtype(df[column]):
            raise TypeError("Selected Column is not of type Numeric")

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
    except KeyError:
        return Response(
            {"message": "Invalid Column Name"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except pd.errors.EmptyDataError:
        return Response(
            {"message": "File Corrupted"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except TypeError as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception:
        return Response(
            {"message": "Something went Wrong. Please try again!"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response({"result": response}, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
def plot(request, id):
    json_data = json.loads(request.body)
    query_object = UploadedFile.objects.filter(id=id).first()
    if not query_object:
        return Response(
            {"message": "No dataset found for the provided id"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    column1 = json_data.get("columnx")
    column2 = json_data.get("columny")
    try:
        dataset = BytesIO(query_object.uploadfile)
        df = pd.read_csv(dataset)

        x = df[column1][:50]
        y = df[column2][:50]

    except KeyError:
        return Response(
            {"message": "Invalid Column Name"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except pd.errors.EmptyDataError:
        return Response(
            {"message": "File Corrupted"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except TypeError as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception:
        return Response(
            {"message": "Something went Wrong. Please try again!"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response({"x": x, "y": y}, status=status.HTTP_200_OK)
