import shutil
import zipfile
import os
from os.path import expanduser
import tempfile
import hashlib

class RenderPacker():

    def __init__(self):
        self.workdir = expanduser('~/rendering/packages')

        if not os.path.exists(self.workdir):
            os.mkdir(self.workdir)

    def pack(self, blend_path, additional_files):
        with tempfile.TemporaryDirectory() as tmpdirname:
            blend_for_zip = os.path.join(tmpdirname, 'job.blend')
            shutil.copy2(blend_path, blend_for_zip)

            job_file = 'temp.zip'
            zip_path = os.path.join(tmpdirname, job_file)    

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(blend_for_zip, arcname='job.blend')

                # TODO Support directories
                for f in additional_files:
                    zipf.write(f, arcname=os.path.basename(f))
            
            package_name = f"{self._get_file_hash(zip_path)}"
            package_filename = f"Job.{package_name}.zip"

            output_package = os.path.join(self.workdir, package_filename)
            shutil.copy2(zip_path, output_package)
            
            print(f"Created output package {output_package}")
            return package_name
    
    def _get_file_hash(self, path):
        with open(path, 'rb') as f:
            bytes = f.read()
            readable_hash = hashlib.sha256(bytes).hexdigest()
            return readable_hash[:16]

    