from rb_commons.configs.config import configs

class MediaUtils:

    @staticmethod
    def url_builder(key: str):
        return "{endpoint_url}/{bucket_name}/{key}" \
            .format(endpoint_url=configs.DIGITALOCEAN_S3_ENDPOINT_URL,
                    bucket_name=configs.DIGITALOCEAN_STORAGE_BUCKET_NAME, key=key)
