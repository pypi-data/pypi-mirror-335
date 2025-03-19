import lzma
import os
import tarfile
import zipfile


def decompress_zip(zip_path: str, out_dir: str):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(out_dir)


def decompress_tar_gz(tar_gz_path: str, out_dir: str):
    tar_gz = tarfile.open(tar_gz_path, "r:gz")
    tar_gz.extractall(path=out_dir)
    tar_gz.close()


def decompress_xz(
        xz_path: str,
        out_path: str,
        clobber: bool = False,
        chunk_size: int = 2 ** 20,
):
    assert chunk_size > 0

    if os.path.exists(out_path):
        if clobber:
            os.remove(out_path)
        else:
            return

    with lzma.open(xz_path, "rb") as f_in, open(out_path, "xb") as f_out:
        while True:
            chunk = f_in.read(size=chunk_size)
            if len(chunk) == 0:
                break
            f_out.write(chunk)
