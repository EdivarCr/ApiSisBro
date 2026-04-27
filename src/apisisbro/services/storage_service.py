from dataclasses import dataclass
from http import HTTPStatus
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from apisisbro.core.settings import settings
from apisisbro.services.supabase_client import supabase

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


@dataclass
class UploadedImage:
    bucket: str
    path: str


class StorageService:
    def __init__(self):
        self.bucket = settings.STORAGE_BUCKET_PRODUTOS

    async def upload_product_image(
        self,
        file: UploadFile,
        product_id: int,
    ) -> UploadedImage:
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Formato inválido. Envie JPG, PNG ou WEBP.',
            )

        content = await file.read()

        if len(content) > settings.max_upload_size_bytes:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=(
                    f'Imagem muito grande. '
                    f'Limite de {settings.MAX_UPLOAD_SIZE_MB}MB.'
                ),
            )

        extension = ALLOWED_CONTENT_TYPES[file.content_type]
        path = f'produtos/{product_id}/{uuid4()}{extension}'

        try:
            supabase.storage.from_(self.bucket).upload(
                path=path,
                file=content,
                file_options={
                    'content-type': file.content_type,
                    'cache-control': '3600',
                    'upsert': False,
                },
            )
        except Exception as exc:
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=f'Erro ao enviar imagem para o Supabase Storage: {exc}',
            ) from exc

        return UploadedImage(
            bucket=self.bucket,
            path=path,
        )

    def get_public_url(self, bucket: str, path: str) -> str:
        return supabase.storage.from_(bucket).get_public_url(path)

    def remove_file(self, bucket: str, path: str) -> None:
        supabase.storage.from_(bucket).remove([path])
