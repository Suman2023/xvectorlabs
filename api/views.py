from django.db import connection,transaction

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.models import UploadedFile
from api.serializers import UploadedFileSerializer

import pandas as pd
from io import BytesIO

import json
import time
import re

# Create your views here.

def sanitize_table_name(tablename):
    sanitized = re.sub(r'[^a-zA-z0-9_]','_',tablename)
    sanitized = re.sub(r'^\d+','',sanitized)
    return sanitized.lower()

def handle_table_creation(dataframe,tablename):
    with connection.cursor() as cursor:
        tablename = sanitize_table_name(tablename)
        updated_tablename = None

        columns = dataframe.columns
        columns_and_types = []
        rowsdata = []

        for col,pd_type in dataframe.dtypes.items():
            if pd.api.types.is_integer_dtype(pd_type) or pd.api.types.is_float_dtype(pd_type):
                columns_and_types.append((col, "NUMERIC"))
            elif pd.api.types.is_datetime64_any_dtype(pd_type):
                columns_and_types.append((col, "TIMESTAMP"))
            else:
                columns_and_types.append((col, "VARCHAR(255)"))

        
        for index, row in dataframe.iterrows():
            rowsdata.append(tuple(row.values))

        create_table_query = f'''
            CREATE TABLE {tablename} (
            {', '.join([f"{column} {dtype}" for column,dtype in columns_and_types])}
        );
        '''
        try:
            cursor.execute(create_table_query)
        except Exception as e:
            if 'already exists' in str(e):
                updated_tablename = f"{tablename}_{int(time.time())}"
                create_table_query = create_table_query.replace(tablename, updated_tablename)
                cursor.execute(create_table_query)
            else:
                raise Exception("Something went wrong in creating database table")


        insert_row_query = f'''
            INSERT INTO {tablename} (
                {', '.join(columns)}) VALUES({', '.join(["%s" for col in columns])}
        );
        '''

        
        cursor.executemany(insert_row_query,rowsdata)
        transaction.commit()
        return updated_tablename if updated_tablename != None else tablename


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

        tablename = handle_table_creation(df,filename)

        num_rows, num_cols = df.shape
        new_file = UploadedFile.objects.create(
            filename=filename,
            uploadfile=uploaded_file,
            rowscount=num_rows,
            colscount=num_cols,
            tablename=tablename,
        )
        new_file.save()
        serializer = UploadedFileSerializer(new_file)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


def is_column_numeric(tablename,columnname):
    # For Sqlite
    # with connection.cursor() as cursor:
    #     cursor.execute(f"PRAGMA table_info({tablename})")
    #     columns_and_dtype = cursor.fetchall()
    #     for column in columns_and_dtype:
    #         if column[1] == columnname:
    #             return column[2] == 'NUMERIC'
    #     return False

    # For Postgres
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name='{tablename}' AND column_name='{columnname}'")
        data = cursor.fetchone()[1]
        return data == 'numeric'


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
        column = json_data.get("column")
        aggregator = json_data.get("aggregator")
        tablename = query_object.tablename
        response = None

        if not is_column_numeric(tablename,column):
            raise TypeError("Selected Column is not of type Numeric")
        if aggregator == "min":
            aggregator = f"MIN({column}) AS min"
        elif aggregator == "max":
            aggregator = f"MAX({column}) AS max"
        elif aggregator == "sum":
            aggregator = f"SUM({column}) AS sum"
        else:
            return Response(
                {"message": "Only min, max and sum can be passed as aggregator"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT {aggregator} FROM {tablename}")
            response = cursor.fetchone()[0]
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
    tablename = query_object.tablename
    try:
        x = []
        y = []
        with connection.cursor() as cursor:
            get_x_and_y_query = f''' SELECT {column1} AS x, {column2} as Y FROM {tablename}
            LIMIT 50
            '''
            cursor.execute(get_x_and_y_query)
            x_and_y = cursor.fetchall()
            for x_data, y_data in x_and_y:
                x.append(x_data)
                y.append(y_data)

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