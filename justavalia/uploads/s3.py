"""Cliente S3/MinIO para o fluxo de multipart presigned.

MinIO exige SigV4 explícito e path-style addressing (confirmado na pesquisa da Fase 4).

Dois endpoints: o *interno* (ex.: http://minio:9000) para operações do backend, e o
*público* (ex.: http://localhost:9000) usado só ao gerar URLs presigned — porque a
URL precisa ser alcançável pelo NAVEGADOR, não pela rede interna do compose. A
assinatura SigV4 embute o host, então a URL presign é gerada por um client apontando
para o endpoint público.
"""

from __future__ import annotations

import boto3
from botocore.config import Config
from django.conf import settings


def _opts() -> dict:
    return settings.STORAGES["default"].get("OPTIONS", {})


def bucket() -> str:
    return _opts().get("bucket_name", "justavalia-media")


def s3_client(*, public: bool = False):
    opts = _opts()
    interno = opts.get("endpoint_url") or None
    if public:
        endpoint = getattr(settings, "AWS_S3_PUBLIC_ENDPOINT_URL", "") or interno
    else:
        endpoint = interno
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        region_name=opts.get("region_name", "us-east-1"),
        aws_access_key_id=opts.get("access_key") or None,
        aws_secret_access_key=opts.get("secret_key") or None,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )
