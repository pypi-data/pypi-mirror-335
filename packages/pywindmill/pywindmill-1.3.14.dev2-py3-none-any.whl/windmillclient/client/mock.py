# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright(C) 2023 baidu, Inc. All Rights Reserved

# @Time : 2024/2/27 16:16
# @Author : yangtingyu01
# @Email: yangtingyu01@baidu.com
# @File : mock.py
# @Software: PyCharm
"""
from flask import Flask, jsonify, request
from baidubce.bce_response import BceResponse
import threading
import time
import socket
import json

app = Flask(__name__)


def get_mock_server():
    """
    return windmill mock server url
    :return:
    """
    port = find_port()
    server_thread = threading.Thread(target=app.run, kwargs={"port": port})
    server_thread.daemon = True
    server_thread.start()
    time.sleep(1)  # Give the server time to start
    return f"http://127.0.0.1:{port}"


def find_port():
    """
    find a port
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def get_bce_response(response):
    """
    get_bce_response
    """
    bce_response = BceResponse()  # 实例化 BceResponse
    bce_response.__dict__.update(response)
    return bce_response


@app.route('/v1/workspaces/<workspace_id>/projects/<project_name>', methods=['GET', 'POST'])
def get_project(workspace_id, project_name):
    """
    get project info
    :param workspace_id:
    :param project_name:
    :return:
    """
    if request.method == 'GET':
        response = {"name": "workspaces/ws1/projects/proj1", "localName": "proj-DO6jCYXh",
                    "displayName": "yxdTestPipeline", "description": "", "tags": {},
                    "workspaceID": "qaVistudio"}
        return jsonify(response)
    elif request.method == 'POST':
        return jsonify({"status": "success"}), 200


@app.route('/v1/workspaces/<workspace_id>/projects/<project_name>/pipelines', methods=['POST'])
def create_pipeline(workspace_id, project_name):
    """
    create pipeline
    :param workspace_id:
    :param project_name:
    :return:
    """
    if request.method == 'POST':
        request_data = request.json
        local_name = request_data.get('localName', "ppl1")
        # 这里是mock的数据
        mocked_data = {
            "artifact_name": f"workspaces/{workspace_id}/projects/{project_name}/pipelines/{local_name}/versions/1"
        }
        # 返回创建的 Job 数据作为 JSON 响应
        return jsonify(mocked_data), 200


@app.route('/v1/workspaces/<workspace_id>/projects/<project_name>/jobs', methods=['POST'])
def create_job(workspace_id, project_name):
    """
    create job
    :param workspace_id:
    :param project_name:
    :return:
    """
    if request.method == 'POST':
        # 这里是mock的数据
        # 返回创建的 Job 数据作为 JSON 响应
        return 200


@app.route('/v1/workspaces/<workspace_id>/projects/<project_name>/datasets', methods=['GET'])
def list_dataset(workspace_id, project_name):
    """
    list dataset
    :param workspace_id:
    :param project_name:
    :return:
    """
    if request.method == 'GET':
        # 这里是mock的数据
        mocked_data = {"totalCount": 1, "result": [
            {"name": "workspaces/ws1/projects/proj1/datasets/ds1", "localName": "ds-DrjVoyjV",
             "displayName": "测试数据集", "description": "",
             "annotationFormat": "ImageNet", "artifact": {"objectType": "dataset",
                                                          "objectName": "workspaces/ws1/projects/proj1/datasets/ds1",
                                                          "parentType": "project",
                                                          "parentName": "workspaces/ws1/projects/proj1",
                                                          "workspaceID": "qaVistudio",
                                                          "name":
                                                              "workspaces/ws1/projects/proj1/datasets/ds1/versions/1",
                                                          "version": 1},
             "category": {"objectType": "dataset",
                          "objectName": "workspaces/ws1/projects/proj1/datasets/ds1",
                          "parentType": "project", "parentName": "workspaces/ws1/projects/proj1",
                          "workspaceID": "qaVistudio", "name": "workspaces/qaVistudio/categories/category-pdrtjgm3",
                          "localName": "category-pdrtjgm3", "category": "Image/ImageClassification/MultiClass",
                          "createdAt": "2024-04-30T17:31:40.709Z", "updatedAt": "2024-04-30T17:31:40.709Z"}}]}
        # 返回创建的 Job 数据作为 JSON 响应
        return jsonify(mocked_data), 200


@app.route('/v1/workspaces/<workspace_id>/projects/<project_name>/pipelines/<local_name>', methods=['GET'])
def get_pipeline(workspace_id, project_name, local_name):
    """
    get pipeline
    :param workspace_id:
    :param project_name:
    :param local_name:
    :return:
    """
    if request.method == 'GET':
        # 这里是mock的数据
        mocked_data = {'name': 'workspaces/ws1/projects/proj1/pipelines/ppl-xP7XfRUP',
                       'localName': 'ppl-xP7XfRUP',
                       'displayName': 'ppl-图像-图像分类-38zPQhMc', 'description': '',
                       'category': {'objectType': 'pipeline',
                                    'objectName': 'workspaces/ws1/projects/proj1/pipelines/ppl-xP7XfRUP',
                                    'parentType': 'project',
                                    'parentName': 'workspaces/ws1/projects/proj1',
                                    'workspaceID': 'qaVistudio',
                                    'name': 'workspaces/qaVistudio/categories/category-bqfapj8n',
                                    'localName': 'category-bqfapj8n',
                                    'category': 'Image/ImageClassification/MultiClass'}}
        # 返回创建的 Job 数据作为 JSON 响应
        return jsonify(mocked_data), 200


@app.route('/v1/workspaces/<workspace_id>/projects/<project_name>/experiments', methods=['GET'])
def list_experiment(workspace_id, project_name):
    """
    list experiment
    :param workspace_id:
    :param project_name:
    :return:
    """
    if request.method == 'GET':
        # 这里是mock的数据
        mocked_data = {'totalCount': 21, 'result': [
            {'name': 'workspaces/ws1/projects/proj1/experiments/exp1'}]}
        # 返回创建的 Job 数据作为 JSON 响应
        return jsonify(mocked_data), 200


@app.route('/v1/versions', methods=['GET'])
def list_artifact():
    """
    list artifact
    :return:
    """
    if request.method == 'GET':
        # 这里是mock的数据
        mocked_data = {'totalCount': 1, 'result': [
            {'objectType': 'dataset', 'objectName': 'workspaces/ws1/projects/proj1/datasets/ds1',
             'parentType': 'project', 'parentName': 'workspaces/ws1/projects/proj1',
             'workspaceID': 'qaVistudio', 'id': 'artifact-iwdrasb7',
             'name': 'workspaces/ws1/projects/proj1/datasets/ds1/versions/1', 'version': 1,
             'tags': {'sourceVersion': '1'}, 'createdAt': '2024-04-30T17:31:40.678Z',
             'updatedAt': '2024-04-30T17:31:40.678Z', 'deletedAt': '0001-01-01T00:00:00Z'}]}
        # 返回创建的 Job 数据作为 JSON 响应
        return jsonify(mocked_data), 200


@app.route('/v1/versions/<version>', methods=['GET'])
def get_artifact(version):
    """
    get artifact
    :param version:
    :return:
    """
    if request.method == 'GET':
        # 这里是mock的数据
        mocked_data = {'objectType': 'pipeline',
                       'objectName': 'workspaces/ws1/projects/proj1/pipelines/ppl-xP7XfRUP',
                       'parentType': 'project', 'parentName': 'workspaces/ws1/projects/proj1',
                       'workspaceID': 'qaVistudio', 'id': 'artifact-9rfkicv7',
                       'name': 'workspaces/ws1/projects/proj1/pipelines/ppl-xP7XfRUP/versions/1',
                       'version': 1,
                       'uri': 's3://windmill/store/68b4691df5fd48a7a23742fed8d39c36/workspaces/qaVistudio/projects/'
                              'proj-DO6jCYXh/pipelines/ppl-xP7XfRUP/versions/1/',
                       'metadata': None, 'tags': {'sourceVersion': '1'}, 'createdAt': '2024-05-15T06:03:24.213Z',
                       'updatedAt': '2024-05-15T06:03:24.213Z', 'deletedAt': '0001-01-01T00:00:00Z'}
        # 返回创建的 Job 数据作为 JSON 响应
        return jsonify(mocked_data), 200


@app.route('/v1/workspaces/<workspace_id>/modelstores', methods=['GET'])
def list_model_store(workspace_id):
    """
    list modelstore
    :param workspace_id:
    :return:
    """
    if request.method == 'GET':
        # 这里是mock的数据
        mocked_data = {'totalCount': 1, 'result': [
            {'name': 'workspaces/ws1/modelstores/ms1', 'localName': 'ms1',
             'displayName': 'ms1', 'description': '', 'ws1': 'qaVistudio'}]}
        # 返回创建的 Job 数据作为 JSON 响应
        return jsonify(mocked_data), 200


@app.route('/v1/workspaces/<workspace_id>/modelstores/<modelstore>/models', methods=['GET'])
def list_model(workspace_id, modelstore):
    """
    list model
    :param workspace_id:
    :param modelstore:
    :return:
    """
    if request.method == 'GET':
        # 这里是mock的数据
        mocked_data = {'name': 'workspaces/qaVistudio/modelstores/ms-vvk7A7gp/models/modelenwoKlu8',
                       'localName': 'modelenwoKlu8', 'displayName': 'ppl-图像-图像分类-38zPQhMc-模型',
                       'description': '', 'category': {'objectType': 'model',
                                                       'objectName':
                                                           'workspaces/qaVistudio/modelstores/'
                                                           'ms-vvk7A7gp/models/modelenwoKlu8',
                                                       'parentType': 'modelstore',
                                                       'parentName': 'workspaces/qaVistudio/modelstores/ms-vvk7A7gp',
                                                       'workspaceID': 'qaVistudio',
                                                       'name': 'workspaces/qaVistudio/categories/category-a14ikjjs',
                                                       'localName': 'category-a14ikjjs',
                                                       'category': 'Image/ImageClassification/MultiClass',
                                                       'createdAt': '2024-05-15T06:22:34.615Z',
                                                       'updatedAt': '2024-05-15T06:22:34.615Z'},
                       'modelFormats': ['PaddlePaddle'], 'schemaUri': '', 'preferModelServerKind': 'Triton',
                       'artifact': {'objectType': 'model',
                                    'objectName': 'workspaces/qaVistudio/modelstores/ms-vvk7A7gp/models/modelenwoKlu8',
                                    'parentType': 'modelstore',
                                    'parentName': 'workspaces/qaVistudio/modelstores/ms-vvk7A7gp',
                                    'workspaceID': 'qaVistudio', 'id': 'artifact-t3skxjhh',
                                    'name':
                                        'workspaces/qaVistudio/modelstores/ms-vvk7A7gp/models/modelenwoKlu8/versions/1',
                                    'version': 1, 'alias': ['best'],
                                    'tags': {'accuracy': '0.3333333432674408',
                                             'bestReason': 'current.score({current_score})', 'sourceVersion': '1'}},
                       'modelStoreName': 'ms-vvk7A7gp',
                       'workspaceID': 'qaVistudio', 'createdAt': '2024-05-15T06:22:34.623Z',
                       'updatedAt': '2024-05-15T06:22:34.623Z'}
        # 返回创建的 Job 数据作为 JSON 响应
        return jsonify(mocked_data), 200


@app.route('/v1/workspaces/<workspace_id>/modelstores/<model_store>/models/<model_name>', methods=['GET'])
def get_model(workspace_id, model_store, model_name):
    """
    get model
    :param workspace_id:
    :param model_store:
    :param model_name:
    :return:
    """
    mocked_data = {"metadata": {
        "content_type": "application/json; charset=utf-8",
        "date": "Wed, 15 May 2024 11:51:38 GMT",
        "transfer_encoding": "chunked",
        "name":
            "workspaces/qaVistudio/modelstores/ms-vvk7A7gp/models/modelenwoKlu8-V100-ensemble",
        "localName": "modelenwoKlu8-V100-ensemble",
        "displayName": "ppl-图像-图像分类-38zPQhMc-模型-V100-模型包",
        "description": "",
        "category": {
            "objectType": "model",
            "objectName":
                "workspaces/qaVistudio/modelstores/ms-vvk7A7gp/models/modelenwoKlu8-V100-ensemble",
            "parentType": "modelstore",
            "parentName": "workspaces/qaVistudio/modelstores/ms-vvk7A7gp",
            "workspaceID": "qaVistudio",
            "name": "workspaces/qaVistudio/categories/category-8uejbeg7",
            "localName": "category-8uejbeg7",
            "category": "Image/Ensemble",
            "createdAt": "2024-05-15T06:25:49.587Z",
            "updatedAt": "2024-05-15T06:25:49.587Z"
        },
        "modelFormats": ["Python"],
        "schemaUri": "",
        "preferModelServerKind": "Triton",
        "preferModelServerParameters": {
            "image": "iregistry.baidu-int.com/windmill-public/inference/nvidia:v4.1.2-dev1",
            "env": {
                "LD_LIBRARY_PATH": "/usr/local/cuda/compat/lib:/usr/local/nvidia/lib:"
                                   "/usr/local/nvidia/lib64:/opt/tritonserver/lib",
                "PATH": "/opt/tritonserver/bin:/usr/local/mpi/bin:/usr/local/nvidia/bin:"
                        "/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:"
                        "/usr/bin:/sbin:/bin:/usr/local/ucx/bin"
            },
            "args": {
                "backend-config": "tensorrt,plugins=/opt/tritonserver/lib/libmmdeploy_tensorrt_ops.so"
            },
            "resource": {
                "accelerator": "V100",
                "gpu": "75",
                "limits": {
                    "cpu": "10",
                    "mem": "10Gi"
                },
                "requests": {
                    "cpu": "100m",
                    "mem": "50Mi"
                }
            }
        },
        "artifact": {
            "objectType": "model",
            "objectName": "workspaces/qaVistudio/modelstores/ms-vvk7A7gp/models/modelenwoKlu8-V100-ensemble",
            "parentType": "modelstore",
            "parentName": "workspaces/qaVistudio/modelstores/ms-vvk7A7gp",
            "workspaceID": "qaVistudio",
            "id": "artifact-8p367q26",
            "name": "workspaces/qaVistudio/modelstores/ms-vvk7A7gp/models/modelenwoKlu8-V100-ensemble/versions/1",
            "version": 1,
            "uri": "s3://windmill/store/68b4691df5fd48a7a23742fed8d39c36/workspaces/qaVistudio"
                   "/modelstores/ms-vvk7A7gp/models/modelenwoKlu8-V100-ensemble/versions/1",
            "metadata": {
                "algorithmParameters": None,
                "experimentName": "",
                "experimentRunID": "",
                "extraModels": None,
                "inputSize": {
                    "height": 0,
                    "width": 0
                },
                "jobName": "",
                "labels": None,
                "maxBoxNum": 0,
                "subModels": {
                    "modelenwoKlu8-V100": "1",
                    "modelenwoKlu8-V100-post": "1",
                    "modelenwoKlu8-V100-pre": "1"
                }
            },
            "tags": {
                "model_type": "model",
                "sourceVersion": "1"
            }},
        "modelStoreName": "ms-vvk7A7gp",
        "workspaceID": "qaVistudio"
    }}
    return jsonify(mocked_data), 200


@app.route('/v1/workspaces/<workspace_id>/computes/suggest', methods=['POST'])
def suggest_compute(workspace_id):
    """
    suggest compute
    :param workspace_id:
    :return:
    """
    if request.method == 'POST':
        # 这里是mock的数据
        mocked_data = {'computes': [
            {'name': 'workspaces/qaVistudio/computes/qtrain', 'localName': 'qtrain', 'displayName': '',
             'description': '', 'kind': 'PaddleFlowQueue', 'parentName': '', 'host': 'https://10.222.123.144:6443',
             'config': {'clusterName': 'vistudio',
                        'maxResources': '{"cpu":"96","mem":"512Gi","scalarResources":{"nvidia.com/gpu":"8"}}',
                        'minResources': '{"cpu":"1","mem":"2Gi","scalarResources":{"nvidia.com/gpu":"1"}}'},
             'namespace': 'train', 'tags': {'usage': 'train'}, 'userID': '8b975ca41a6640098e72991a65eca7a6',
             'orgID': '68b4691df5fd48a7a23742fed8d39c36', 'workspaceID': 'qaVistudio',
             'createdAt': '2024-04-30T17:19:31.546Z', 'updatedAt': '2024-04-30T17:19:31.546Z'}]}
        # 返回创建的 Job 数据作为 JSON 响应
        return jsonify(mocked_data), 200


@app.route('/v1/workspaces/<workspace_id>/filesystems/suggest', methods=['POST'])
def suggest_filesystem(workspace_id):
    """
    suggest filesystem
    :param workspace_id:
    :return:
    """
    if request.method == 'POST':
        # 这里是mock的数据
        mocked_data = {"fileSystems": [
            {"name": "workspaces/public/filesystems/defaultfs", "localName": "defaultfs", "displayName": "",
             "description": "", "isDisabled": False, "kind": "s3", "parentName": "", "host": "10.20.240.49:0000",
             "endpoint": "windmill/store/68b4691df5fd48a7a23742fed8d39c36",
             "credential": {"accessKey": "test_ak", "secretKey": "test_sk",
                            "token": ""}, "mountPath": "/home/paddleflow/storage/mnt",
             "config": {"ak": "test_ak", "allowcors": "false", "disableSSL": "true", "provider": "Minio",
                        "region": "bj", "s3ForcePathStyle": "true", "sk": "test_sk",
                        "token": ""}, "tags": {}, "userID": "", "orgID": "public", "workspaceID": "public",
             "createdAt": "2024-02-23T14:42:13.871Z", "updatedAt": "2024-02-23T14:42:13.871Z"}]}
        # 返回创建的 Job 数据作为 JSON 响应
        return jsonify(mocked_data), 200


@app.route('/v1/workspaces/<workspace_id>/filesystems/<local_name>', methods=['GET'])
def get_filesystem(workspace_id, local_name):
    """
    get filesystem
    :param workspace_id:
    :param local_name:
    :return:
    """
    if request.method == 'GET':
        # 这里是mock的数据
        mocked_data = {"name": "workspaces/public/filesystems/defaultfs", "localName": "defaultfs", "displayName": "",
                       "description": "", "isDisabled": False, "kind": "s3", "parentName": "",
                       "host": "10.20.240.40:8000",
                       "endpoint": "windmill/store/68b4691df5fd48a7a23742fed8d39c36",
                       "credential": {"accessKey": "test_ak",
                                      "secretKey": "test_sk",
                                      "token": ""}, "mountPath": "/home/paddleflow/storage/mnt",
                       "config": {"ak": "test_ak", "allowcors": "false", "disableSSL": "true",
                                  "provider": "Minio",
                                  "region": "bj", "s3ForcePathStyle": "true", "sk": "test_sk",
                                  "token": ""}, "tags": {}, "userID": "", "orgID": "public", "workspaceID": "public",
                       "createdAt": "2024-02-23T14:42:13.871Z", "updatedAt": "2024-02-23T14:42:13.871Z"}
        # 返回创建的 Job 数据作为 JSON 响应
        return jsonify(mocked_data), 200


@app.route('/v1/usersettings/', methods=['GET'])
def get_user_setting():
    """
    get user setting
    :return:
    """
    if request.method == 'GET':
        # 这里是mock的数据
        mocked_data = {'settingValue': 'test'}
        # 返回创建的 Job 数据作为 JSON 响应
        return jsonify(mocked_data), 200
