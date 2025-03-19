# -*- coding: utf-8 -*-
"""
Copyright(C) 2023 baidu, Inc. All Rights Reserved
"""
import os

GET_LOCAL_FILESYSTEM = {
    "name": "workspaces/public/filesystems/defaultfs",
    "localName": "defaultfs",
    "isDisabled": False,
    "kind": "file",
    "host": "",
    "endpoint": os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/store/",
    "config": {
        "ak": "test-ak",
        "sk": "test-sk"
    },
    "userID": "test-org-id",
    "orgID": "test-user-id",
    "workspaceID": "public",
}


GET_ANNOTATION_SET_RESPONSE_WITHOUT_ATTR = {
    "id": "as-01",
    "name": "workspaces/default/projects/proj-vistudio-ut/annotationsets/as-vistudio-ut",
    "localName": "as-vistudio-ut",
    "displayName": "标注集01",
    "description": "",
    "category": {
        "category": "Image/ImageClassification/MultiTask",
    },
    "labels": [
        {
            "localName": "0",
            "id": "╔",
            "displayName": "铁轨",
            "color": "#4764ec",
            "parentID": "",
            "confidence": 0,
        },
    ],
    "imageCount": 2,
    "annotatedImageCount": 2,
    "inferedImageCount": 0,
    "size": "67.85kB",
    "uri": "s3://windmill/store/workspaces/default/projects/proj-vistudio-ut/annotationsets/as-vistudio-ut",
    "jobs": [],
    "orgID": "test-org-id",
    "userID": "test-user-id",
    "projectName": "proj-vistudio-ut",
    "workspaceID": "default",
}


CREATE_LOCATION_RESPONSE = {
    "location": os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/store/versions/1"
}


GET_ARTIFACT_RESPONSE = {
    "objectType": "model",
    "objectName": "workspaces/wsicykvi/modelstores/test-dl/models/paomaodilou-T4-moxingbao",
    "parentType": "modelstore",
    "parentName": "workspaces/wsicykvi/modelstores/test-dl",
    "workspaceID": "wsicykvi",
    "id": "artifact-iruucz0v",
    "name": "workspaces/wsicykvi/modelstores/test-dl/models/paomaodilou-T4-moxingbao/versions/1",
    "version": 1,
    "uri": "s3://windmill/store/7957b155b5cf4e43833527b10132a928/workspaces/wsicykvi/modelstores/test-dl/models/paomaodilou-T4-moxingbao/versions/1",
    "metadata": {
        "algorithmParameters": {},
        "experimentName": "paomaodilou",
        "experimentRunID": "d406ebc8d3574fc4817382a7",
        "jobName": "workspaces/internal/projects/spiproject/jobs/jobBd2yFtQ2",
        "labels": [
            {
                "displayName": "liquid",
                "id": 0,
                "name": "liquid"
            },
            {
                "displayName": "mud",
                "id": 1,
                "name": "mud"
            }
        ],
        "maxBoxNum": 0,
        "subModels": {
            "paomaodilou-T4": "1",
            "paomaodilou-T4-post": "1",
            "paomaodilou-T4-pre": "1"
        }
    },
    "tags": {
        "algorithm": "PPYOLOEPLUS/Ensemble",
        "model_type": "model",
        "scene": "",
        "sourceVersion": "1"
    },
    "forbidDelete": False,
}


GET_ENDPOINT_RESPONSE = {
    "name": "workspaces/wsicykvi/endpointhubs/test-dl/endpoints/zhibiaoduiqiyty2-R200-moxingbao1",
    "localName": "zhibiaoduiqiyty2-R200-moxingbao1",
    "displayName": "zhibiaoduiqiyty2-R200-moxingbao1",
    "description": "auto created by data processing",
    "kind": "Endpoint",
    "uri": "http://10.93.32.12:8412/ep-mmzifwgr",
    "computeName": "workspaces/wsicykvi/computes/r200new",
    "tags": {
        "artifact": "workspaces/wsicykvi/modelstores/test-dl/models/zhibiaoduiqiyty2-R200-moxingbao/versions/1",
        "deployment": "workspaces/public/endpointhubs/default/deployments/triton-kunlun/versions/latest",
        "skill-as-dsf780kr": "Using"
    },
    "lastJob": {
        "name": "workspaces/wsicykvi/endpointhubs/test-dl/jobs/deployjob-qmx7a3v9",
        "localName": "deployjob-qmx7a3v9",
        "displayName": "",
        "description": "",
        "kind": "Deploy",
        "jobComputeName": "workspaces/wsicykvi/computes/qyijian",
        "endpointKind": "Endpoint",
        "endpointName": "zhibiaoduiqiyty2-R200-moxingbao1",
        "endpointHubName": "test-dl",
        "endpointComputeName": "workspaces/wsicykvi/computes/r200new",
        "modelName": "workspaces/wsicykvi/modelstores/test-dl/models/zhibiaoduiqiyty2-R200-moxingbao/versions/1",
        "artifactName": "workspaces/wsicykvi/modelstores/test-dl/models/zhibiaoduiqiyty2-R200-moxingbao/versions/1",
        "specKind": "Helm",
        "specName": "workspaces/public/endpointhubs/default/deployments/triton-kunlun/versions/latest",
        "specFilesystemName": "workspaces/public/filesystems/defaulttest",
        "templateParameters": {
            "args.backend-config": "tensorrt,plugins=/opt/tritonserver/lib/libmmdeploy_tensorrt_ops.so",
            "artifact.name": "zhibiaoduiqiyty2-R200-moxingbao",
            "artifact.parentName": "test-dl",
            "artifact.version": "1",
            "artifact.workspaceID": "wsicykvi",
            "endpoint.endpointHubName": "test-dl",
            "endpoint.endpointName": "zhibiaoduiqiyty2-R200-moxingbao1",
            "endpoint.workspaceID": "wsicykvi",
            "env.LD_LIBRARY_PATH": "/opt/tritonserver/lib",
            "env.XTCL_L3_SIZE": "67104768",
            "hpa.enabled": "true",
            "image.imageName": "iregistry.baidu-int.com/acg_aiqp_algo/triton-inference-server/triton_r22_12_kunlun_infer:2.2.7.2",
            "image.modelRepositoryPath": "s3://http://10.27.240.49:8077/windmill/store/7957b155b5cf4e43833527b10132a928/workspaces/wsicykvi/modelstores/test-dl/models",
            "mountPath": "/home/windmill",
            "resource.accelerator": "R200",
            "resource.gpu": "7500",
            "resource.limits.cpu": "10",
            "resource.limits.mem": "10Gi",
            "resource.requests.cpu": "100m",
            "resource.requests.mem": "50Mi",
            "windmill.ak": "a85c0911e8314d0ea4429129b1724f78",
            "windmill.endpoint": "10.27.240.49:8340",
            "windmill.org_id": "7957b155b5cf4e43833527b10132a928",
            "windmill.sk": "4a97c6bf511c48bc90f4c87aa9f52146",
            "windmill.user_id": "419b412dd5ff43c7b809960dfaf355e7"
        },
        "runID": "run-037813",
        "run": {
            "runID": "run-037813",
            "name": "deploy",
            "source": "aea58704b6125007cd82d0952ce9691c",
            "username": "root",
            "fsname": "",
            "description": "",
            "postProcess": {},
            "failureOptions": {
                "strategy": "fail_fast"
            },
            "dockerEnv": "",
            "entry": "",
            "disabled": "",
            "scheduleID": "",
            "runMsg": "Run successfully",
            "status": "succeeded",
            "runCachedIDs": "",
            "createTime": "2024-10-24 14:40:31",
            "activateTime": "2024-10-24 14:40:31",
            "updateTime": "2024-10-24 14:40:43"
        },
        "workspaceID": "wsicykvi",
    },
    "orgID": "test-org-id",
    "userID": "test-user-id",
    "endpointHubName": "test-dl",
    "workspaceID": "wsicykvi",
}


GET_ENDPOINT_STATUS_RESPONSE = {
    "endpointName": "workspaces/wsicykvi/endpointhubs/test-dl/endpoints/zhibiaoduiqiyty2-R200-moxingbao1",
    "replicas": 1,
    "availableReplicas": 1,
    "status": "Available",
    "reason": "MinimumReplicasAvailable",
    "message": "Deployment has minimum availability.",
    "lastUpdateTime": "2024-10-24T14:40:58+08:00",
    "deploymentStatus": "Completed",
    "deploymentReason": "NewReplicaSetAvailable",
    "deploymentMessage": "ReplicaSet \"ep-mmzifwgr-6cffd558c7\" has successfully progressed.",
    "deploymentLastUpdateTime": "2024-10-24T14:40:39+08:00",
    "deploymentCondition": [
        {
            "type": "Available",
            "status": "True",
            "lastUpdateTime": "2024-10-24T14:40:58+08:00",
            "lastTransitionTime": "2024-10-24T14:40:58+08:00",
            "reason": "MinimumReplicasAvailable",
            "message": "Deployment has minimum availability."
        },
        {
            "type": "Progressing",
            "status": "True",
            "lastUpdateTime": "2024-10-24T14:40:58+08:00",
            "lastTransitionTime": "2024-10-24T14:40:39+08:00",
            "reason": "NewReplicaSetAvailable",
            "message": "ReplicaSet \"ep-mmzifwgr-6cffd558c7\" has successfully progressed."
        }
    ],
    "extraData": {
        "observedGeneration": 1,
        "readyReplicas": 1,
        "unavailableReplicas": 0,
        "updatedReplicas": 1
    }
}

GET_ENDPOINT_STATUS_FAILED_RESPONSE = {
    "endpointName": "workspaces/wsicykvi/endpointhubs/test-dl/endpoints/zhibiaoduiqiyty2-R200-moxingbao1",
    "replicas": 1,
    "availableReplicas": 1,
    "status": "NotAvailable",
    "reason": "MinimumReplicasAvailable",
    "message": "Deployment has minimum availability.",
    "lastUpdateTime": "2024-10-24T14:40:58+08:00",
    "deploymentStatus": "Failed",
    "deploymentReason": "",
    "deploymentMessage": "",
    "deploymentCondition": [],
    "extraData": {}
}


GET_JOB_RESPONSE = {
    'tags': {},
    'createdAt': '2024-10-24T14:40:58+08:00'
}

GET_MODEL_RESPONSE = {
    "category": {
        "category": "Image/ImageClassification/MultiTask",
    },
    "preferModelServerParameters": {'resource': {'accelerator': 'R200'}}
}

GET_DEPLOYMENT_RESPONSE = {
    "serverKind": 'Triton'
}

CREATE_ANNOTATION_LABEL_RESPONSE = {
    "localName": "1",
}

LIST_DEPLOY_JOBS_RESPONSE = {
    "result": [{
        "workspaceID": "public",
        "endpointHubName": "default",
        "endpointName": "test-endpoint",
    }],
    "totalCount": 1
}

GET_ANNOTATION_SET_RESPONSE_WITH_MULTIMODAL = {
    "id": "as-01",
    "name": "workspaces/default/projects/proj-vistudio-ut/annotationsets/as-vistudio-ut",
    "localName": "as-vistudio-ut",
    "displayName": "标注集01",
    "description": "",
    "category": {
        "category": "Multimodal/VQA",
    },
    "labels": [
        {
            "localName": "0",
            "id": "╔",
            "displayName": "铁轨",
            "color": "#4764ec",
            "parentID": "",
            "confidence": 0,
        },
    ],
    "imageCount": 2,
    "annotatedImageCount": 2,
    "inferedImageCount": 0,
    "size": "67.85kB",
    "uri": "s3://windmill/store/workspaces/default/projects/proj-vistudio-ut/annotationsets/as-vistudio-ut",
    "jobs": [],
    "orgID": "test-org-id",
    "userID": "test-user-id",
    "projectName": "proj-vistudio-ut",
    "workspaceID": "default",
}