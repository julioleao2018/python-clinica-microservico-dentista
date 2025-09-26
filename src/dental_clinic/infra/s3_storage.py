# infra/s3_storage.py
import os
import re
import config
import boto3

from datetime import datetime
from botocore.exceptions import ClientError

AWS_REGION = os.getenv("AWS_REGION", "sa-east-1")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET_LOGOS", "clinicas-logos-sp")
AWS_S3_PUBLIC = os.getenv("AWS_S3_PUBLIC", "true").lower() == "true"
AWS_S3_BASEURL = os.getenv("AWS_S3_BASEURL", "").strip()

_s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=config.get_aws_key(),
    aws_secret_access_key=config.get_aws_secret_key(),
)

def _sanitize_filename(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", name)

def make_logo_key(clinica_id: str, filename: str) -> str:
    safe = _sanitize_filename(filename or "logo.png")
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    return f"clinicas/{clinica_id}/logo/{ts}_{safe}"

def upload_fileobj(fileobj, key: str, content_type: str | None = None):
    extra = {}
    if content_type:
        extra["ContentType"] = content_type
    # if AWS_S3_PUBLIC:
    #     extra["ACL"] = "public-read"
    _s3.upload_fileobj(fileobj, AWS_S3_BUCKET, key, ExtraArgs=extra)

def delete_object_safe(key: str):
    try:
        _s3.delete_object(Bucket=AWS_S3_BUCKET, Key=key)
    except ClientError:
        # silencioso para não quebrar o fluxo
        pass

def public_url(key: str) -> str | None:
    if not key:
        return None
    if AWS_S3_PUBLIC:
        if AWS_S3_BASEURL:
            # CDN/CloudFront
            return f"https://{AWS_S3_BASEURL}/{key}"
        # URL pública nativa do S3
        return f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"
    return None

def presigned_url(key: str, expires_seconds: int = 3600) -> str:
    return _s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": AWS_S3_BUCKET, "Key": key},
        ExpiresIn=expires_seconds,
    )
